from datetime import datetime
import pandas as pd
import time
import model
from fuzzywuzzy import fuzz
import re
import json
from session.notificationsession import client as mqtt
from session import SQLALCHEMY_DATABASE_URL, DB, engine
from session import Session as SessionLocal
from sqlalchemy.orm import Session, load_only, Load
from datetime import datetime
# from session import Session as SessionLocal
from sqlalchemy import MetaData
import sys

sys.path.append("..")
# from session import engine
# SQL_USER = 'serina'
# SQL_PASS = 'dsserina'
# # localhost = '20.198.76.113'
# localhost = 'serina-qa-server.mysql.database.azure.com'
# # localhost = '20.204.241.92'
# # 20.204.241.92
SQL_DB = DB


# SQL_PORT = '3306'
# ck_threshold = 90


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


# Background task publisher
def meta_data_publisher(msg):
    try:
        mqtt.publish("notification_processor", json.dumps(msg), qos=2, retain=True)
    except Exception as e:
        pass


# po_tag_map = {'PurchQty':'Quantity','Name':'Description', 'PurchId':'PO_HEADER_ID','Qty':'Quantity','POLineNumber':'PO_LINE_ID'}

def batch_update_db(data, Over_all_ck_data_status, invo_doc_id, GrnCreationType, grn_found, doc_sel_rulid):
    global desc, error
    meta = MetaData()
    if Over_all_ck_data_status == 34:
        # PO line item issue:
        docStatus = 4
        doc_substatus = 34
        docDesc = 'PO lines less than invoice'
        qry = "update " + str(SQL_DB) + ".document set documentStatusID = " + str(
            docStatus) + ", documentsubstatusID = " + str(
            doc_substatus) + " where idDocument = " + str(invo_doc_id)
        with engine.begin() as conn:  # TRANSACTION
            conn.execute(qry)

        doc_substatus = 34
        type_s = "PO lines less than invoice"
        dochist1 = 'INSERT INTO ' + str(
            SQL_DB) + '.documentruleshistorylog (documentID, documentSubStatusID, IsActive,type) values (' + str(
            invo_doc_id) + ',' + str(doc_substatus) + ',' + str(1) + ',"' + type_s + '")'
        with engine.begin() as conn:  # TRANSACTION
            conn.execute(dochist1)

    if Over_all_ck_data_status == 1:

        if GrnCreationType == 1:
            docStatus = 4
            doc_substatus = 35
            Over_all_ck_data_status = 5

        else:
            docStatus = 2
            doc_substatus = 23
            docDesc = 'success'
        qry = "update " + str(SQL_DB) + ".document set documentStatusID = " + str(
            docStatus) + ", documentsubstatusID = " + str(
            doc_substatus) + " where idDocument = " + str(invo_doc_id)
        with engine.begin() as conn:  # TRANSACTION
            conn.execute(qry)
    elif Over_all_ck_data_status == 2:
        # reference mapping issue for type 2(Stationary):

        docStatus = 4
        doc_substatus = 33
        docDesc = 'Price mismatch issue'
        qry = "update " + str(SQL_DB) + ".document set documentStatusID = " + str(
            docStatus) + ", documentsubstatusID = " + str(
            doc_substatus) + " where idDocument = " + str(invo_doc_id)
        with engine.begin() as conn:  # TRANSACTION
            conn.execute(qry)

        doc_substatus = 33
        type_s = "Unitprice mismatch issue"
        dochist1 = 'INSERT INTO ' + str(
            SQL_DB) + '.documentruleshistorylog (documentID, documentSubStatusID, IsActive,type) values (' + str(
            invo_doc_id) + ',' + str(doc_substatus) + ',' + str(1) + ',"' + type_s + '")'
        with engine.begin() as conn:  # TRANSACTION
            conn.execute(dochist1)

    else:
        for key, value in data.items():
            po_and_grn_status_hard_tag = 0
            po_and_grn_status_qty = 0
            po_and_grn_status_unit_price = 0
            po_ck_status_ut = 1
            over_all_status = 1

            inv_id = key
            data1 = value['po_grn_data']
            data2 = value['map_item']
            #print(data2)
            for key, value in data2.items():
                update_fuz_scr = " UPDATE documentlineitems SET invoice_itemcode='" + str(key) + "', Fuzzy_scr=" + str(
                    value['fuzz_scr']) + " WHERE documentID=" + str(inv_id) + " AND itemCode='" + str(
                    value['invo_itm_code']) + "'"
                # print(update_fuz_scr)
                with engine.begin() as conn:  # TRANSACTION
                    conn.execute(update_fuz_scr)
                    time.sleep(1)
                # conn.close()
            po_item_check = 1
            grn_item_ck = 1
            po_ch_qty = 1
            grn_ch_qty = 1
            unitpr_ch_qty = 1
            ut_yes = 0
            doc_substatus = 27
            try:
                db: Session = next(get_db())
            except Exception as ER:
                print(str(ER))
            for key, value in data1.items():
                # print(key)
                data2 = value
                for key, value in data2.items():  # item check PO n GRn
                    # print(key, value)
                    print("GrnCreationType: ", GrnCreationType, type(GrnCreationType))
                    if GrnCreationType == 1:
                        if key == 'item':
                            if value['po_status'] == 1:
                                error = 0
                                desc = None

                            elif value['po_status'] == 0:
                                error = 1
                                po_item_check = po_item_check * 0
                                desc = key + " is not matching with PO"
                                po_and_grn_status_hard_tag = 2
                                update_val = " UPDATE documentlineitems SET isError=" + str(
                                    error) + ", CK_status=" + str(
                                    value['ck_status']) + ", ErrorDesc='" + str(
                                    desc) + "' WHERE idDocumentLineItems=" + str(
                                    value['idDocumentLineItems'])
                                # print(update_val)
                                with engine.begin() as conn:  # TRANSACTION
                                    conn.execute(update_val)
                                    time.sleep(1)


                        elif key == 'qty':
                            if value['po_status'] == 1:
                                error = 0
                                desc = None

                            elif value['po_status'] == 0:
                                error = 1
                                po_ch_qty = po_ch_qty * 0
                                desc = key + " is not matching with PO"
                                po_and_grn_status_qty = 2
                                update_val = " UPDATE documentlineitems SET isError=" + str(
                                    error) + ", CK_status=" + str(
                                    value['ck_status']) + ", ErrorDesc='" + str(
                                    desc) + "' WHERE idDocumentLineItems=" + str(
                                    value['idDocumentLineItems'])
                                # print(update_val)
                                with engine.begin() as conn:  # TRANSACTION
                                    conn.execute(update_val)
                                    time.sleep(1)

                        elif key == 'unit_price':
                            if value['po_status'] == 0:  # Unitprice PO
                                po_ck_status_ut = po_ck_status_ut * 0
                                error = 1
                                ut_yes = 1
                                desc = key + " is not matching with PO"
                                po_and_grn_status_unit_price = 1
                                unitpr_ch_qty = unitpr_ch_qty * 0
                                update_val = " UPDATE documentlineitems SET isError=" + str(
                                    error) + ", CK_status=" + str(
                                    value['ck_status']) + ", ErrorDesc='" + str(
                                    desc) + "' WHERE idDocumentLineItems=" + str(
                                    value['idDocumentLineItems'])
                                # print(update_val)
                                with engine.begin() as conn:  # TRANSACTION
                                    conn.execute(update_val)
                                    time.sleep(1)
                            else:
                                error = 0
                                desc = "Unit price matching"

                        if value['ck_status'] == 7:
                            error = 0

                        # update_val = " UPDATE documentlineitems SET isError=" + str(error) + ", CK_status=" + str(
                        #     value['ck_status']) + ", ErrorDesc='" + str(desc) + "' WHERE idDocumentLineItems=" + str(
                        #     value['idDocumentLineItems'])
                        # # print(update_val)
                        # with engine.begin() as conn:  # TRANSACTION
                        #     conn.execute(update_val)
                        #     time.sleep(1)

                    if GrnCreationType == 2:
                        if key == 'item':
                            if value['po_status'] == 1 and value['grn_status'] == 1:
                                error = 0
                                desc = None

                            elif value['po_status'] == 1 and value['grn_status'] == 0:
                                error = 1
                                grn_item_ck = grn_item_ck * 0
                                desc = key + " is not matching with GRN"
                                po_and_grn_status_hard_tag = 1

                            elif value['po_status'] == 0 and value['grn_status'] == 1:
                                error = 1
                                grn_item_ck = grn_item_ck * 1
                                po_item_check = po_item_check * 0
                                desc = key + " is not matching with PO"
                                po_and_grn_status_hard_tag = 2
                            elif value['po_status'] == 0 and value['grn_status'] == 0:
                                error = 1
                                grn_item_ck = grn_item_ck * 0
                                po_item_check = po_item_check * 0
                                desc = key + " is not matching with PO and GRN"
                                po_and_grn_status_hard_tag = 3


                        elif key == 'qty':
                            if value['po_status'] == 1 and value['grn_status'] == 1:
                                error = 0
                                desc = None

                            elif value['po_status'] == 1 and value['grn_status'] == 0:
                                error = 1
                                # grn_item_ck = grn_item_ck*0
                                desc = key + " is not matching with GRN"
                                po_and_grn_status_qty = 1
                                grn_ch_qty = grn_ch_qty * 0

                            elif value['po_status'] == 0 and value['grn_status'] == 1:
                                error = 1

                                po_ch_qty = po_ch_qty * 0
                                desc = key + " is not matching with PO"
                                po_and_grn_status_qty = 2
                            elif value['po_status'] == 0 and value['grn_status'] == 0:
                                error = 1
                                grn_ch_qty = grn_ch_qty * 0
                                po_ch_qty = po_ch_qty * 0
                                desc = key + " is not matching with PO and GRN"
                                po_and_grn_status_qty = 3
                        elif key == 'unit_price':
                            if value['po_status'] == 0:  # Unitprice PO
                                po_ck_status_ut = po_ck_status_ut * 0
                                error = 1
                                ut_yes = 1
                                desc = key + " is not matching with PO"
                                po_and_grn_status_unit_price = 1
                                unitpr_ch_qty = unitpr_ch_qty * 0
                            else:
                                error = 0
                                desc = ""

                        if value['ck_status'] == 7:
                            error = 0

                        update_val = " UPDATE documentlineitems SET isError=" + str(error) + ", CK_status=" + str(
                            value['ck_status']) + ", ErrorDesc='" + str(desc) + "' WHERE idDocumentLineItems=" + str(
                            value['idDocumentLineItems'])
                        # print(update_val)
                        with engine.begin() as conn:  # TRANSACTION
                            conn.execute(update_val)
                            time.sleep(1)
                            # conn.close()
            type_s = 'error'

            if doc_sel_rulid == 8:
                if po_item_check == 1 and po_ch_qty == 1 and unitpr_ch_qty == 1:
                    docStatus = 4
                    docDesc = 'Ready for GRN creation!'
                    doc_substatus = 35
                    qry = "update " + str(SQL_DB) + ".document set documentStatusID = " + str(
                        docStatus) + ", documentsubstatusID = " + str(doc_substatus) + " where idDocument = " + str(
                        inv_id)
                    # qry = "update " + str(SQL_DB) + ".document set documentStatusID = " + \
                    #       str(docStatus) + " where idDocument = " + str(inv_id)
                    with engine.begin() as conn:  # TRANSACTION
                        conn.execute(qry)
                elif po_item_check == 0:
                    doc_substatus = 8
                    over_all_status = over_all_status * 0
                    dochist1 = 'INSERT INTO ' + str(
                        SQL_DB) + '.documentruleshistorylog (documentID, documentSubStatusID, IsActive,type) values (' + str(
                        inv_id) + ',' + str(doc_substatus) + ',' + str(1) + ',"' + type_s + '")'
                    with engine.begin() as conn:  # TRANSACTION
                        conn.execute(dochist1)
                elif po_ch_qty == 0:
                    doc_substatus = 21
                    over_all_status = over_all_status * 0
                    # UPDATE query here
                    dochist1 = 'INSERT INTO ' + str(
                        SQL_DB) + '.documentruleshistorylog (documentID, documentSubStatusID, IsActive,type) values (' + str(
                        inv_id) + ',' + str(doc_substatus) + ',' + str(1) + ',"' + type_s + '")'
                    with engine.begin() as conn:  # TRANSACTION
                        conn.execute(dochist1)
                elif unitpr_ch_qty == 0:

                    doc_substatus = 16
                    over_all_status = over_all_status * 0
                    # UPDATE query here
                    dochist3 = 'INSERT INTO ' + str(
                        SQL_DB) + '.documentruleshistorylog (documentID, documentSubStatusID, IsActive,type) values (' + str(
                        inv_id) + ',' + str(doc_substatus) + ',' + str(1) + ',"' + type_s + '")'
                    with engine.begin() as conn:  # TRANSACTION
                        conn.execute(dochist3)
                else:
                    # Value mismatch:
                    doc_substatus = 27

                docStatus = 4
                # doc_substatus = 33
                qry = "update " + str(SQL_DB) + ".document set documentStatusID = " + str(
                    docStatus) + ", documentsubstatusID = " + str(
                    doc_substatus) + " where idDocument = " + str(invo_doc_id)
                with engine.begin() as conn:  # TRANSACTION
                    conn.execute(qry)
            else:
                if po_item_check == 0:
                    doc_substatus = 8
                    over_all_status = over_all_status * 0
                    dochist1 = 'INSERT INTO ' + str(
                        SQL_DB) + '.documentruleshistorylog (documentID, documentSubStatusID, IsActive,type) values (' + str(
                        inv_id) + ',' + str(doc_substatus) + ',' + str(1) + ',"' + type_s + '")'
                    with engine.begin() as conn:  # TRANSACTION
                        conn.execute(dochist1)
                if GrnCreationType == 2:
                    if grn_item_ck == 0:
                        doc_substatus = 8
                        over_all_status = over_all_status * 0
                        dochist1 = 'INSERT INTO ' + str(
                            SQL_DB) + '.documentruleshistorylog (documentID, documentSubStatusID, IsActive,type) values (' + str(
                            inv_id) + ',' + str(doc_substatus) + ',' + str(1) + ',"' + type_s + '")'
                        with engine.begin() as conn:  # TRANSACTION
                            conn.execute(dochist1)

                if po_ch_qty == 0 and (value['ck_status'] == 1 or value['ck_status'] == 2):  # Substatus check
                    doc_substatus = 21
                    over_all_status = over_all_status * 0
                    # UPDATE query here
                    dochist1 = 'INSERT INTO ' + str(
                        SQL_DB) + '.documentruleshistorylog (documentID, documentSubStatusID, IsActive,type) values (' + str(
                        inv_id) + ',' + str(doc_substatus) + ',' + str(1) + ',"' + type_s + '")'
                    with engine.begin() as conn:  # TRANSACTION
                        conn.execute(dochist1)

                if GrnCreationType == 2:
                    if grn_ch_qty == 0 and (value['ck_status'] == 1 or value['ck_status'] == 3):
                        doc_substatus = 17
                        over_all_status = over_all_status * 0
                        # UPDATE query here
                        dochist2 = 'INSERT INTO ' + str(
                            SQL_DB) + '.documentruleshistorylog (documentID, documentSubStatusID, IsActive,type) values (' + str(
                            inv_id) + ',' + str(doc_substatus) + ',' + str(1) + ',"' + type_s + '")'
                        with engine.begin() as conn:  # TRANSACTION
                            conn.execute(dochist2)

                if unitpr_ch_qty == 0 and (value['ck_status'] == 1 or value['ck_status'] == 2):
                    doc_substatus = 16
                    over_all_status = over_all_status * 0
                    # UPDATE query here
                    dochist3 = 'INSERT INTO ' + str(
                        SQL_DB) + '.documentruleshistorylog (documentID, documentSubStatusID, IsActive,type) values (' + str(
                        inv_id) + ',' + str(doc_substatus) + ',' + str(1) + ',"' + type_s + '")'
                    with engine.begin() as conn:  # TRANSACTION
                        conn.execute(dochist3)
                if GrnCreationType == 1:

                    if (po_ch_qty == 1) and (value['ck_status'] == 1):
                        doc_substatus = 35
                        Over_all_ck_data_status = 5
                    elif (po_ch_qty == 1) and (value['ck_status'] == 2):
                        doc_substatus = 35
                        Over_all_ck_data_status = 5
                    elif over_all_status == 1:
                        doc_substatus = 35
                        Over_all_ck_data_status = 5

                    else:
                        doc_substatus = 27  # value mismatch
                    dochist4 = 'INSERT INTO ' + str(
                        SQL_DB) + '.documentruleshistorylog (documentID, documentSubStatusID, IsActive,type) values (' + str(
                        inv_id) + ',' + str(doc_substatus) + ',' + str(1) + ',"' + type_s + '")'
                    with engine.begin() as conn:  # TRANSACTION
                        conn.execute(dochist4)

                if GrnCreationType == 2:
                    if (po_ch_qty == 1 and grn_ch_qty == 1) and (value['ck_status'] == 1):
                        doc_substatus = 23
                    if (po_ch_qty == 1) and (value['ck_status'] == 2):
                        doc_substatus = 23

                    if (grn_ch_qty == 1) and (value['ck_status'] == 3):
                        doc_substatus = 23  # success

                    if over_all_status == 1:
                        doc_substatus = 23
                    else:
                        doc_substatus = 27  # value mismatch
                    dochist4 = 'INSERT INTO ' + str(
                        SQL_DB) + '.documentruleshistorylog (documentID, documentSubStatusID, IsActive,type) values (' + str(
                        inv_id) + ',' + str(doc_substatus) + ',' + str(1) + ',"' + type_s + '")'
                    with engine.begin() as conn:  # TRANSACTION
                        conn.execute(dochist4)

                if over_all_status == 1:
                    if GrnCreationType == 1:
                        docStatus = 4
                        doc_substatus = 35
                        docDesc = "Ready for GRN"
                    else:
                        # status to 2
                        if grn_found == 1:
                            docStatus = 2
                            docDesc = 'success'
                            doc_substatus = 23
                        else:
                            docStatus = 4
                            docDesc = 'GRN not found'
                            doc_substatus = 38

                    qry = "update " + str(SQL_DB) + ".document set documentStatusID = " + str(
                        docStatus) + ", documentsubstatusID = " + str(doc_substatus) + " where idDocument = " + str(
                        inv_id)
                    # qry = "update " + str(SQL_DB) + ".document set documentStatusID = " + \
                    #       str(docStatus) + " where idDocument = " + str(inv_id)
                    with engine.begin() as conn:  # TRANSACTION
                        conn.execute(qry)
                else:
                    if Over_all_ck_data_status == 4:
                        docStatus = 4
                        doc_substatus = 33
                        docDesc = 'Price mismatch issue'
                        qry = "update " + str(SQL_DB) + ".document set documentStatusID = " + str(
                            docStatus) + ", documentsubstatusID = " + str(
                            doc_substatus) + " where idDocument = " + str(invo_doc_id)
                        with engine.begin() as conn:  # TRANSACTION
                            conn.execute(qry)

                        doc_substatus = 33
                        type_s = "Unitprice mismatch issue"
                        dochist1 = 'INSERT INTO ' + str(
                            SQL_DB) + '.documentruleshistorylog (documentID, documentSubStatusID, IsActive,type) values (' + str(
                            invo_doc_id) + ',' + str(doc_substatus) + ',' + str(1) + ',"' + type_s + '")'
                        with engine.begin() as conn:  # TRANSACTION
                            conn.execute(dochist1)

                    else:

                        # docStatus = 4
                        # doc_substatus = 35
                        # docDesc = "ready for GRN creation!"

                        docStatus = 4
                        doc_substatus = 27
                        docDesc = 'Value mismatch'
                        qry = "update " + str(SQL_DB) + ".document set documentStatusID = " + str(
                            docStatus) + ", documentsubstatusID = " + str(
                            doc_substatus) + " where idDocument = " + str(inv_id)
                        with engine.begin() as conn:  # TRANSACTION
                            conn.execute(qry)
                created_date = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                his_qry = 'INSERT INTO ' + str(
                    SQL_DB) + '.documenthistorylog (documentID, documentdescription, documentStatusID,CreatedOn) values (' + str(
                    inv_id) + ', "' + docDesc + '",' + str(docStatus) + ',"' + str(created_date) + '")'
                with engine.begin() as conn:  # TRANSACTION
                    conn.execute(his_qry)
                if po_and_grn_status_hard_tag:
                    try:
                        ############ start of notification trigger #############
                        # getting recipients for sending notification
                        db: Session = next(get_db())
                        entityID = db.query(model.Document.entityID).filter_by(idDocument=inv_id).scalar()
                        recepients = db.query(model.UserAccess.UserID).filter_by(EntityID=entityID,
                                                                                 isActive=1).distinct()
                        recepients = db.query(model.User.idUser, model.User.email, model.User.firstName,
                                              model.User.lastName).filter(model.User.idUser.in_(recepients)).all()
                        user_ids, *email = zip(*list(recepients))
                        # just format update
                        email_ids = list(zip(email[0], email[1], email[2]))
                        cust_id = db.query(model.Entity.customerID).filter_by(idEntity=entityID).scalar()
                        details = {"user_id": user_ids, "trigger_code": 7020, "cust_id": cust_id, "inv_id": inv_id,
                                   "additional_details": {"subject": "Item not Found", "recipients": email_ids}}
                        # meta_data_publisher(details)
                        ############ End of notification trigger #############
                    except Exception as e:
                        print(str(e))

                if po_and_grn_status_qty:
                    try:
                        ############ start of notification trigger #############
                        # getting recipients for sending notification
                        entityID = db.query(model.Document.entityID).filter_by(idDocument=inv_id).scalar()
                        recepients = db.query(model.UserAccess.UserID).filter_by(EntityID=entityID,
                                                                                 isActive=1).distinct()
                        recepients = db.query(model.User.idUser, model.User.email, model.User.firstName,
                                              model.User.lastName).filter(model.User.idUser.in_(recepients)).all()
                        user_ids, *email = zip(*list(recepients))
                        # just format update
                        email_ids = list(zip(email[0], email[1], email[2]))
                        cust_id = db.query(model.Entity.customerID).filter_by(idEntity=entityID).scalar()
                        details = {"user_id": user_ids, "trigger_code": 7022, "cust_id": cust_id, "inv_id": inv_id,
                                   "additional_details": {"subject": "Item Quantity Mismatch with PO",
                                                          "recipients": email_ids}}
                        meta_data_publisher(details)
                        ############ End of notification trigger #############
                    except Exception as e:
                        print(e)
                if po_and_grn_status_unit_price:
                    try:
                        ############ start of notification trigger #############
                        # getting recipients for sending notification
                        entityID = db.query(model.Document.entityID).filter_by(idDocument=inv_id).scalar()
                        recepients = db.query(model.UserAccess.UserID).filter_by(EntityID=entityID,
                                                                                 isActive=1).distinct()
                        recepients = db.query(model.User.idUser, model.User.email, model.User.firstName,
                                              model.User.lastName).filter(model.User.idUser.in_(recepients)).all()
                        user_ids, *email = zip(*list(recepients))
                        # just format update
                        email_ids = list(zip(email[0], email[1], email[2]))
                        cust_id = db.query(model.Entity.customerID).filter_by(idEntity=entityID).scalar()
                        details = {"user_id": user_ids, "trigger_code": 7021, "cust_id": cust_id, "inv_id": inv_id,
                                   "additional_details": {"subject": "Item Unit Price Mismatch with PO",
                                                          "recipients": email_ids}}
                        meta_data_publisher(details)
                        ############ End of notification trigger #############
                    except Exception as e:
                        print(e)
            # docDesc = ''

        if Over_all_ck_data_status == 3:
            # po < invo

            docStatus = 4
            doc_substatus = 33
            qry = "update " + str(SQL_DB) + ".document set documentStatusID = " + str(
                docStatus) + ", documentsubstatusID = " + str(
                doc_substatus) + " where idDocument = " + str(invo_doc_id)
            with engine.begin() as conn:  # TRANSACTION
                conn.execute(qry)

            doc_substatus = 33
            type_s = "Po Lineitems < Invo Line Items"
            dochist1 = 'INSERT INTO ' + str(
                SQL_DB) + '.documentruleshistorylog (documentID, documentSubStatusID, IsActive,type) values (' + str(
                invo_doc_id) + ',' + str(doc_substatus) + ',' + str(1) + ',"' + type_s + '")'
            with engine.begin() as conn:  # TRANSACTION
                conn.execute(dochist1)


def cln_amt(amt):
    amt = str(amt)
    if len(amt) > 0:
        if len(re.findall("\d+\,\d+\d+\.\d+", amt)) > 0:
            cl_amt = re.findall("\d+\,\d+\d+\.\d+", amt)[0]
            cl_amt = float(cl_amt.replace(",", ""))
        elif len(re.findall("\d+\.\d+", amt)) > 0:
            cl_amt = re.findall("\d+\.\d+", amt)[0]
            cl_amt = float(cl_amt)
        elif len(re.findall("\d+", amt)) > 0:
            cl_amt = re.findall("\d+", amt)[0]
            cl_amt = float(cl_amt)
        else:
            cl_amt = amt
    else:
        cl_amt = amt
    return cl_amt


def cl_df_col(df_col):
    cl_up = []
    # print(df_col)
    for up in range(len(df_col)):
        # print(df_col[up])
        cl_up.append(cln_amt(df_col[up]))
    return cl_up


def invo_process(po_doc_id, invo_doc_id, documentLineitem_po_df, doc_header_po_df, documentLineitem_invo_df,
                 doc_header_invo_df, documentLineitem_grn_df, doc_inline_tags, ck_threshold,
                 req_rul_df, document_df, itemusermap_df, erp_vd_status, qty_tol_percent, ut_tol_percent,
                 GrnCreationType):
    invo_stst_ck = 0
    doc_sel_rulid = 0
    po_grn_data = {}
    new_itm_mh = {}
    po_inlinedf = documentLineitem_po_df[documentLineitem_po_df['documentID'] == po_doc_id]
    po_header_df = doc_header_po_df[doc_header_po_df['documentID'] == po_doc_id]

    invo_inlinedf = documentLineitem_invo_df[documentLineitem_invo_df['documentID'] == invo_doc_id]
    invo_header_df = doc_header_invo_df[doc_header_invo_df['documentID'] == invo_doc_id]
    req_invo_inline = invo_inlinedf[['idDocumentLineItems', 'lineItemtagID', 'Value', 'itemCode']].merge(
        doc_inline_tags, on='lineItemtagID', how='left')
    req_po_inline = po_inlinedf[['idDocumentLineItems', 'lineItemtagID', 'Value', 'itemCode']].merge(
        doc_inline_tags,
        on='lineItemtagID',
        how='left')

    # PO DATA
    po_grouped_df = req_po_inline.groupby('TagName')
    po_desc = po_grouped_df.get_group('Description')['Value']
    po_item_code = po_grouped_df.get_group('Description')['itemCode']
    po_desc_df = pd.DataFrame(list(zip(po_desc, po_item_code)), columns=[
        'Description', 'itemCode'])
    po_desc_df['itemCode'] = po_desc_df['itemCode'].astype('str')
    po_qty = po_grouped_df.get_group('Quantity')['Value']
    po_qty_item_code = po_grouped_df.get_group('Quantity')['itemCode']
    po_qty_df = pd.DataFrame(list(zip(po_qty, po_qty_item_code)), columns=[
        'Quantity', 'itemCode'])
    po_qty_df['itemCode'] = po_qty_df['itemCode'].astype('str')
    po_Uty_price = po_grouped_df.get_group('UnitPrice')['Value']
    po_Uty_price_item_code = po_grouped_df.get_group('UnitPrice')[
        'itemCode']
    po_Uty_price_df = pd.DataFrame(list(
        zip(po_Uty_price, po_Uty_price_item_code)), columns=['UnitPrice', 'itemCode'])
    po_Uty_price_df['itemCode'] = po_Uty_price_df['itemCode'].astype('str')
    po_tab = po_desc_df.merge(po_qty_df, on='itemCode').merge(
        po_Uty_price_df, on='itemCode')

    po_tab['Quantity'] = cl_df_col(po_tab['Quantity'])
    po_tab['UnitPrice'] = cl_df_col(po_tab['UnitPrice'])

    # INVO DATA
    if erp_vd_status != 2:
        inv_grouped_df = req_invo_inline.groupby('TagName')
        desc = inv_grouped_df.get_group('Description')['Value']
        item_code = inv_grouped_df.get_group('Description')['itemCode']
        desc_df = pd.DataFrame(list(zip(desc, item_code)), columns=[
            'Description', 'itemCode'])

        qty = inv_grouped_df.get_group('Quantity')['Value']
        qty_item_code = inv_grouped_df.get_group('Quantity')['itemCode']
        qty_df = pd.DataFrame(list(zip(qty, qty_item_code)),
                              columns=['Quantity', 'itemCode'])
        Uty_price = inv_grouped_df.get_group('UnitPrice')['Value']
        Uty_price_item_code = inv_grouped_df.get_group('UnitPrice')['itemCode']
        Uty_price_df = pd.DataFrame(list(zip(Uty_price, Uty_price_item_code)), columns=[
            'UnitPrice', 'itemCode'])

        if 'Amount' in list(req_invo_inline['TagName']):
            Amt = inv_grouped_df.get_group('Amount')['Value']
            Amt_item_code = inv_grouped_df.get_group('Amount')['itemCode']
            Amt_df = pd.DataFrame(list(zip(Amt, Amt_item_code)),
                                  columns=['Amount', 'itemCode'])

            Amt_df['Amount'] = cl_df_col(Amt_df['Amount'])

            # Amt = inv_grouped_df.get_group('Amount')['Value']
            # Amt_item_code = inv_grouped_df.get_group('Amount')['itemCode']
            # Amt_df = pd.DataFrame(list(zip(Amt, Amt_item_code)),
            #                       columns=['Amount', 'itemCode'])
            #
            # Amt_df['Amount'] = cl_df_col(Amt_df['Amount'])

            invo_tab = desc_df.merge(qty_df, on='itemCode').merge(
                Uty_price_df, on='itemCode').merge(Amt_df, on='itemCode')
        else:
            invo_tab = desc_df.merge(qty_df, on='itemCode').merge(
                Uty_price_df, on='itemCode')
        invo_tab['Quantity'] = cl_df_col(invo_tab['Quantity'])
        invo_tab['UnitPrice'] = cl_df_col(invo_tab['UnitPrice'])
        # print(invo_tab.head(2))

        PO_HEADER_ID = list(
            po_header_df[po_header_df['TagLabel'] == 'PO_HEADER_ID']['Value'])[0]
        # GRN DATA
        if GrnCreationType == 2:

            # [documentLineitem_grn_df['documentID'] == 2737793]
            if len(documentLineitem_grn_df) > 0:
                grn_inlinedf = documentLineitem_grn_df
                req_grn_df = grn_inlinedf[
                    ['idDocumentLineItems', 'documentID', 'lineItemtagID', 'Value', 'itemCode']].merge(
                    doc_inline_tags, on='lineItemtagID', how='left')
                temp_grndf = req_grn_df[req_grn_df['TagName'] == 'PO_HEADER_ID']
                req_grn_docID = temp_grndf[temp_grndf['Value']
                                           == PO_HEADER_ID]['documentID'].unique()[0]
                grn_df = req_grn_df[req_grn_df['documentID'] == req_grn_docID]

                grn_grouped_df = grn_df.groupby('TagName')
                grn_po_unit_price = grn_grouped_df.get_group('UnitPrice')['Value']
                grn_po_item_code = grn_grouped_df.get_group('UnitPrice')[
                    'itemCode']
                grn_po_unitprice_df = pd.DataFrame(list(zip(grn_po_unit_price, grn_po_item_code)),
                                                   columns=['UnitPrice', 'itemCode'])
                grn_qty = grn_grouped_df.get_group('Quantity')['Value']
                grn_qty_item_code = grn_grouped_df.get_group('Quantity')['itemCode']
                grn_qty_df = pd.DataFrame(list(zip(grn_qty, grn_qty_item_code)), columns=[
                    'Quantity', 'itemCode'])
                grn_qty_accepted = grn_grouped_df.get_group(
                    'Quantity')['Value']
                grn_qty_accepted_item_code = grn_grouped_df.get_group('Quantity')[
                    'itemCode']
                grn_qty_accepted_df = pd.DataFrame(list(zip(grn_qty_accepted, grn_qty_accepted_item_code)),
                                                   columns=['Quantity', 'itemCode'])
                # grn_qty_cancelled = grn_grouped_df.get_group(
                #     'QUANTITY_CANCELLED')['Value']
                # grn_qty_cancelled_item_code = grn_grouped_df.get_group('QUANTITY_CANCELLED')[
                #     'itemCode']
                # grn_qty_cancelled_df = pd.DataFrame(list(zip(grn_qty_cancelled, grn_qty_cancelled_item_code)),
                #                                     columns=['QUANTITY_CANCELLED', 'itemCode'])
                grn_qty_received = grn_grouped_df.get_group(
                    'Quantity')['Value']
                grn_qty_received_item_code = grn_grouped_df.get_group('Quantity')[
                    'itemCode']
                grn_qty_received_df = pd.DataFrame(list(zip(grn_qty_received, grn_qty_received_item_code)),
                                                   columns=['Quantity', 'itemCode'])

                grn_po_line_id = grn_grouped_df.get_group('PO_LINE_ID')['Value']
                grn_po_line_id_item_code = grn_grouped_df.get_group('PO_LINE_ID')[
                    'itemCode']
                grn_po_line_id_df = pd.DataFrame(list(zip(grn_po_line_id, grn_po_line_id_item_code)),
                                                 columns=['PO_LINE_ID', 'itemCode'])

                grn_tab = grn_po_unitprice_df.merge(grn_qty_df, on='itemCode').merge(grn_qty_accepted_df,
                                                                                     on='itemCode').merge(
                    grn_qty_received_df, on='itemCode').merge(grn_po_line_id_df,
                                                              on='itemCode')
            else:
                grn_tab = pd.DataFrame()
        else:
            grn_tab = pd.DataFrame()

    document_df = document_df.where(pd.notnull(document_df), 'null')
    invo_documentStatusID = document_df[document_df['idDocument'] == invo_doc_id]['documentStatusID'].reset_index(
        drop=True)
    invo_documentsubstatusID = document_df[document_df['idDocument'] == invo_doc_id][
        'documentsubstatusID'].reset_index(drop=True)
    print("invo_documentsubstatusID: ", invo_documentsubstatusID)
    Over_all_ck_data_status = 0
    if erp_vd_status == 2:
        # No Line items - only headers data check
        invo_ck_df_1 = pd.DataFrame()
        for ut_PO in range(0, len(po_tab['UnitPrice'])):

            try:
                for up_flt in range(len(invo_header_df)):
                    if invo_header_df['TagLabel'][up_flt] == 'SubTotal':
                        invo_header_df['Value'][up_flt] = str(float(invo_header_df['Value'][up_flt]))
                    if invo_header_df['TagLabel'][up_flt] == 'InvoiceTotal':
                        invo_header_df['Value'][up_flt] = str(float(invo_header_df['Value'][up_flt]))
            except Exception as et:
                print(str(et))

            if len(invo_header_df[invo_header_df['Value'] == str(float(po_tab['UnitPrice'][ut_PO]))]) > 0:
                try:
                    invo_ck_df_1 = invo_header_df[
                        invo_header_df['Value'] == str(float(po_tab['UnitPrice'][ut_PO]))].reset_index(
                        drop=True)
                except Exception as e:
                    print(str(e))

        if len(invo_ck_df_1) > 0:
            prd_tg_iv = invo_ck_df_1['TagLabel'][0]
            if (prd_tg_iv == 'SubTotal') or (prd_tg_iv == 'InvoiceTotal'):
                # print(prd_tg_iv)
                Over_all_ck_data_status = 1
            else:
                Over_all_ck_data_status = 2
                # metadata issue:
        else:
            Over_all_ck_data_status = 2
            # metadata issue:

    elif erp_vd_status != 2:
        ck_matrix = {}
        if len(po_tab) >= len(invo_tab):
            skip_fuzz = 0
            if (([invo_documentStatusID[0] == 1]) and (invo_documentsubstatusID[0] == 24)) or (
                    ([invo_documentStatusID[0] == 1]) and (invo_documentsubstatusID[0] == 33)):
                # User mapping DONE!!
                # Update iserror to 0

                update_val2 = " UPDATE documentdata SET isError=" + str('0') + " WHERE documentID=" + str(invo_doc_id)
                # print(update_val)
                with engine.begin() as conn:  # TRANSACTION
                    conn.execute(update_val2)
                    time.sleep(1)
                update_val = " UPDATE documentlineitems SET isError=" + str('0') + " WHERE documentID=" + str(
                    invo_doc_id)
                # print(update_val)
                with engine.begin() as conn:  # TRANSACTION
                    conn.execute(update_val)
                    time.sleep(1)
                print("rest isError to 0 Done!")

                invo_stst_ck = 1
                skip_fuzz = 1

                print("Skip_fuzz = ", skip_fuzz)
                ck_matrix = {}
                temp_invo_df = documentLineitem_invo_df[
                    documentLineitem_invo_df['documentID'] == invo_doc_id].reset_index(
                    drop=True)
                for cmp in range(len(invo_tab)):
                    ck_decp = invo_tab['Description'][cmp]

                    tmp_mxt = {}
                    po_assigned_item = list(temp_invo_df[temp_invo_df['Value'] == ck_decp]['invoice_itemcode'])[0]
                    ck_po_decp = list(po_tab[po_tab['itemCode'] == po_assigned_item]['Description'])[0]
                    fuz_ratio = fuzz.ratio(ck_decp.lower(), ck_po_decp.lower())
                    tmp_mxt[po_assigned_item] = fuz_ratio
                    ck_matrix[invo_tab['itemCode'][cmp]] = tmp_mxt
                # new_itm_mh = ck_matrix



            elif ([invo_documentStatusID[0] == 1]) and (invo_documentsubstatusID[0] == 1) or (
                    [invo_documentStatusID[0] == 1]) and (invo_documentsubstatusID[0] == 3):
                update_val = " UPDATE documentlineitems SET isError=" + str('0') + " WHERE documentID=" + str(
                    invo_doc_id)
                # print(update_val)
                with engine.begin() as conn:  # TRANSACTION
                    conn.execute(update_val)
                    time.sleep(1)
                update_val2 = " UPDATE documentdata SET isError=" + str('0') + " WHERE documentID=" + str(invo_doc_id)
                # print(update_val)
                with engine.begin() as conn:  # TRANSACTION
                    conn.execute(update_val2)
                    time.sleep(1)

                invo_stst_ck = 1
                if skip_fuzz == 0:
                    ck_matrix = {}
                    for cmp in range(len(invo_tab)):
                        ck_decp = invo_tab['Description'][cmp]
                        tmp_mxt = {}
                        for cmp_po in range(len(po_tab)):
                            ck_po_decp = po_tab['Description'][cmp_po]
                            fuz_ratio = fuzz.ratio(ck_decp.lower(), ck_po_decp.lower())
                            tmp_mxt[po_tab['itemCode'][cmp_po]] = fuz_ratio
                        ck_matrix[invo_tab['itemCode'][cmp]] = tmp_mxt

            if invo_stst_ck == 1:
                po_ = {}
                new_itm_mh = {}
                leftout_mh = []

                # status_scr = 0
                for invo_itm_cd in ck_matrix:  # invo_itm_cd == invo itemCode
                    # temp_code_map = {}
                    mx_scr_item = max(ck_matrix[invo_itm_cd],
                                      key=ck_matrix[invo_itm_cd].get)
                    # print("mx_scr_item: line 701 ", mx_scr_item)
                    mx_scr = ck_matrix[invo_itm_cd][mx_scr_item]
                    # print(mx_scr_item,mx_scr)
                    if mx_scr_item in new_itm_mh.keys():
                        # print(new_itm_mh[mx_scr_item]['fuzz_scr'])
                        if new_itm_mh[mx_scr_item]['fuzz_scr'] < mx_scr:
                            new_itm_mh[mx_scr_item] = {'invo_itm_code': invo_itm_cd, 'fuzz_scr': mx_scr}
                        elif new_itm_mh[mx_scr_item]['fuzz_scr'] >= mx_scr:
                            leftout_mh.append(invo_itm_cd)

                    else:
                        new_itm_mh[mx_scr_item] = {'invo_itm_code': invo_itm_cd, 'fuzz_scr': mx_scr}
                tmp_mapIt = []
                for nwIt in new_itm_mh:
                    # print(new_itm_mh[nwIt]['invo_itm_code'])
                    tmp_mapIt.append(new_itm_mh[nwIt]['invo_itm_code'])

                leftout_mh = list(set(list(ck_matrix.keys())) - set(tmp_mapIt))
                for LTinv in leftout_mh:
                    # print(LTinv)
                    leftPOitm = list(set(ck_matrix[LTinv].keys()) - set(new_itm_mh.keys()))
                    if len(leftPOitm) > 0:
                        temp_ckMtx = {}
                        for tmp_itM in leftPOitm:
                            temp_ckMtx[tmp_itM] = ck_matrix[LTinv][tmp_itM]
                        mx_scr_item = max(temp_ckMtx,
                                          key=temp_ckMtx.get)
                        mx_scr = ck_matrix[LTinv][mx_scr_item]
                        new_itm_mh[mx_scr_item] = {'invo_itm_code': LTinv, 'fuzz_scr': mx_scr}


                poItemCode_Tab = req_po_inline[req_po_inline['TagName'] == 'ItemId']
                itemusermap_df['description'] = itemusermap_df['description'].str.lower()
                invo_tab['Description'] = invo_tab['Description'].str.lower()
                po_tab['Description'] = po_tab['Description'].str.lower()
                itemusermap_df['mappedinvoitemdescription'] = itemusermap_df['mappedinvoitemdescription'].str.lower()
                ref_map_itm_mh = {}
                for itm_fuz in new_itm_mh:
                    invo_itmCd = new_itm_mh[itm_fuz]['invo_itm_code']
                    fuzSR = new_itm_mh[itm_fuz]['fuzz_scr']
                    invo_desc = list(invo_tab[invo_tab['itemCode'] == invo_itmCd]['Description'])[0]
                    mp_invo_dt = itemusermap_df[itemusermap_df['mappedinvoitemdescription'] == invo_desc].reset_index(
                        drop=True)
                    if len(mp_invo_dt) > 0:
                        if mp_invo_dt['itemcode'][0] in list(poItemCode_Tab['Value']):
                            mapped_po_itmCd = \
                            list(poItemCode_Tab[poItemCode_Tab['Value'] == mp_invo_dt['itemcode'][0]]['itemCode'])[0]
                            ref_map_itm_mh[mapped_po_itmCd] = {'invo_itm_code': invo_itmCd, 'fuzz_scr': 100}
                        elif (mp_invo_dt['itemcode'][0])[:3].lower() == 'ser':
                            # SERINA ITEMCODE
                            InvPO_desc = list(po_tab[po_tab['itemCode'] == itm_fuz]['Description'])[0].lower()
                            if (InvPO_desc == list(mp_invo_dt['description'])[0]):
                                mapped_po_itmCd = list(po_tab[po_tab['Description'] == InvPO_desc]['itemCode'])[0]
                                ref_map_itm_mh[mapped_po_itmCd] = {'invo_itm_code': invo_itmCd, 'fuzz_scr': 100}

                tmp_mapIt = []
                for nwIt in ref_map_itm_mh:
                    # print(ref_map_itm_mh[nwIt]['invo_itm_code'])
                    tmp_mapIt.append(ref_map_itm_mh[nwIt]['invo_itm_code'])
                leftout_mh = list(set(list(ck_matrix.keys())) - set(tmp_mapIt))

                if len(leftout_mh) > 0:
                    for LTinv in leftout_mh:
                        # print("LTinv: ", LTinv)
                        leftPOitm = list(set(ck_matrix['1'].keys()) - set(ref_map_itm_mh.keys()))
                        if len(leftPOitm) > 0:
                            temp_ckMtx = {}
                            for tmp_itM in leftPOitm:
                                temp_ckMtx[tmp_itM] = ck_matrix[LTinv][tmp_itM]
                            mx_scr_item = max(temp_ckMtx,
                                              key=temp_ckMtx.get)
                            mx_scr = ck_matrix[LTinv][mx_scr_item]
                            ref_map_itm_mh[mx_scr_item] = {'invo_itm_code': LTinv, 'fuzz_scr': mx_scr}
                new_itm_mh = ref_map_itm_mh

                for fz in new_itm_mh:
                    if new_itm_mh[fz]['fuzz_scr'] >= ck_threshold:
                        new_itm_mh[fz]['item_status'] = 1
                    else:
                        new_itm_mh[fz]['item_status'] = 0
                # for itm_fuz in new_itm_mh:
                #     if new_itm_mh[itm_fuz]['fuzz_scr'] < ck_threshold:
                #         # print(new_itm_mh[itm_fuz]['fuzz_scr'])
                #         invo_desc_ = \
                #             list(invo_tab[invo_tab['itemCode'] == new_itm_mh[itm_fuz]['invo_itm_code']]['Description'])[
                #                 0]
                #         if invo_desc_ in itemusermap_df.values:
                #             tmp__ = itemusermap_df[itemusermap_df['mappedinvoitemdescription'] == invo_desc_]
                #             if list(tmp__['itemcode'])[0] == itm_fuz:
                #                 new_itm_mh[itm_fuz]['item_status'] = 1
                #                 new_itm_mh[itm_fuz]['fuzz_scr'] = 100
                #
                #             elif list(tmp__['itemcode'])[0] in itemusermap_df.values:
                #                 tmp__2 = itemusermap_df[itemusermap_df['itemcode'] == list(tmp__['itemcode'])[0]]
                #                 # print("if yes: ")
                #                 swp_1 = new_itm_mh[itm_fuz]
                #                 new_itm_mh[itm_fuz] = new_itm_mh[list(tmp__2['itemcode'])[0]]
                #                 new_itm_mh[list(tmp__2['itemcode'])[0]] = swp_1
                #                 new_itm_mh[list(tmp__2['itemcode'])[0]]['item_status'] = 0

            po_grn_data = {}
            for mt_ in new_itm_mh:
                # print(mt_)
                po_itm_cd = mt_
                invo_itm_cd = new_itm_mh[mt_]['invo_itm_code']

                fuzz_scr = new_itm_mh[mt_]['fuzz_scr']
                po_qty = float(
                    po_tab[po_tab['itemCode'] == po_itm_cd]['Quantity'])
                invo_qty = float(
                    invo_tab[invo_tab['itemCode'] == invo_itm_cd]['Quantity'])

                qty_threshold = (po_qty * (int(qty_tol_percent) / 100))

                po_unitprice = round(float(po_tab[po_tab['itemCode'] == po_itm_cd]['UnitPrice']),2)
                invo_unitprice = round(float(invo_tab[invo_tab['itemCode'] == invo_itm_cd]['UnitPrice']),2)
                # po_[mx_scr_item] = {}
                # print("ut_tol_percent: ", ut_tol_percent)
                unitprice_threshold = (po_unitprice * (int(ut_tol_percent) / 100))

                # unitprice check
                # print("po_unitprice - invo_unitprice : ", po_unitprice - invo_unitprice)
                if (abs(po_unitprice - invo_unitprice) <= unitprice_threshold):

                    unitprice_status = 1
                else:
                    unitprice_status = 0
                # print("unitprice_status: ", unitprice_status)

                # qty check
                # if (po_qty == invo_qty) or ((po_qty - invo_qty) <= qty_threshold):
                #     po_qty_status = 1
                # else:
                #     po_qty_status = 0
                try:
                    temp_req_po_inline = req_po_inline[req_po_inline['itemCode'] == invo_itm_cd]
                    remInvPy = list(
                        temp_req_po_inline[temp_req_po_inline['TagName'] == 'RemainInventPhysical']['Value'])
                    if len(remInvPy) > 0:
                        PO_bal = float(remInvPy[0])
                    else:
                        PO_bal = 0
                    # RemainInventPhysical_PO = float(
                    #     req_po_inline[req_po_inline[req_po_inline['itemCode'] == invo_itm_cd][
                    #                       'TagName'] == 'RemainInventPhysical']['Value'])

                except Exception as er:
                    PO_bal = 0
                    # print("failed to fetch RemainInventPhysical_PO,PO balance not found")
                if (PO_bal == invo_qty):
                    po_qty_status = 1
                elif invo_qty > PO_bal:
                    if abs(invo_qty - po_qty) > qty_threshold:
                        po_qty_status = 0
                    else:
                        po_qty_status = 1
                elif PO_bal > invo_qty:
                    # if abs(po_qty - invo_qty) <= (RemainInventPhysical_PO + qty_threshold):
                    po_qty_status = 1
                    # else:
                    #     po_qty_status = 0
                else:
                    po_qty_status = 0

                # print("po_qty_status: ", po_qty_status)

                if GrnCreationType == 2:
                    if len(documentLineitem_grn_df) > 0:
                        # grn item check
                        if po_itm_cd in list(grn_qty_received_df['itemCode']):
                            grn_itm_status = 1
                            grn_qty_ = float(
                                grn_qty_received_df[grn_qty_received_df['itemCode'] == po_itm_cd]['Quantity'])

                            # grn qty check
                            if float(grn_qty_) == invo_qty:
                                grn_qty_ = 1
                            else:
                                grn_qty_ = 0

                        else:
                            grn_itm_status = 0
                            grn_qty_ = 0
                    else:
                        grn_itm_status = 0
                        grn_qty_ = 0

                else:
                    grn_itm_status = 0
                    grn_qty_ = 0
                if skip_fuzz == 1:
                    po_itm_status = 1
                    # print("in skip line 830")

                elif (fuzz_scr >= ck_threshold):
                    po_itm_status = 1
                    # print("fuzz_scr----", fuzz_scr)

                else:
                    po_itm_status = 0
                    Over_all_ck_data_status = 4
                    # print("in else po line status 0 ")
                    # po_qty_status = 0
                    # unitprice_status = 0
                    # grn_itm_status = 0
                    # grn_qty_ = 0
                # print("PO status: ", po_itm_status)

                tmp_df = req_invo_inline[req_invo_inline['itemCode'] == invo_itm_cd]
                unitprice_tag = int(tmp_df[tmp_df['TagName'] == 'UnitPrice']['idDocumentLineItems'])
                desc_tag = int(tmp_df[tmp_df['TagName'] == 'Description']['idDocumentLineItems'])
                qty_tag = int(tmp_df[tmp_df['TagName'] == 'Quantity']['idDocumentLineItems'])
                po_grn_data[po_itm_cd] = {
                    'qty': {'po_status': po_qty_status, 'grn_status': grn_qty_, 'idDocumentLineItems': qty_tag,
                            'ck_status': 0},
                    'unit_price': {'po_status': unitprice_status, 'idDocumentLineItems': unitprice_tag,
                                   'ck_status': 0},
                    'item': {'po_status': po_itm_status, 'grn_status': grn_itm_status,
                             'idDocumentLineItems': desc_tag,
                             'ck_status': 0}}
                # print("po_grn_data: ", po_grn_data)
                doc_sel_rulid = list(doc_header_invo_df[doc_header_invo_df['documentID'] == invo_doc_id]['ruleID'])[
                    0]
                sel_rul_ck = list(req_rul_df[req_rul_df['DocumentRulesID'] == doc_sel_rulid]['status'])
                # print("sel_rul_ck: ", sel_rul_ck)
                # item rule check:
                if ('PO Item check' and 'GRN Item Check') in sel_rul_ck:
                    po_grn_data[po_itm_cd]['item']['ck_status'] = 1
                    # print("PO Item check and GRN Item Check DONE!")

                elif ('PO Item check') in sel_rul_ck:
                    po_grn_data[po_itm_cd]['item']['ck_status'] = 2
                    # print('PO Item check DONE')

                elif ('GRN Item Check') in sel_rul_ck:
                    po_grn_data[po_itm_cd]['item']['ck_status'] = 3
                    # print("GRN Item Check DONE")
                else:
                    po_grn_data[po_itm_cd]['item']['ck_status'] = 7

                # qty rule check:
                if ('Po Qty Check' and 'GRN Qty Check') in sel_rul_ck:
                    po_grn_data[po_itm_cd]['qty']['ck_status'] = 1

                elif ('Po Qty Check') in sel_rul_ck:
                    po_grn_data[po_itm_cd]['qty']['ck_status'] = 2

                elif ('GRN Qty Check') in sel_rul_ck:
                    po_grn_data[po_itm_cd]['qty']['ck_status'] = 3
                else:
                    po_grn_data[po_itm_cd]['qty']['ck_status'] = 7

                # unitprice rule check:
                if ('Unit Price Mismatch') in sel_rul_ck:
                    po_grn_data[po_itm_cd]['unit_price']['ck_status'] = 2
                else:
                    po_grn_data[po_itm_cd]['unit_price']['ck_status'] = 7

        else:
            Over_all_ck_data_status = 34
            doc_sel_rulid = 0
            # metadata issue, - PO lines less than  invo line item!

    return po_grn_data, new_itm_mh, Over_all_ck_data_status, doc_sel_rulid


def single_doc_prc(id_doc):
    db: Session = next(get_db())
    invo_pro_data = {}
    po_tag_map = {}
    grn_found = 0
    erp_tag_map = "SELECT * FROM " + str(SQL_DB) + ".erp_tag_map;"
    erp_tag_map_df = pd.read_sql(erp_tag_map, SQLALCHEMY_DATABASE_URL)
    for erpmp in range(0, len(erp_tag_map_df)):
        # print(erp_tag_map_df['serina_tag'][erpmp])
        po_tag_map[erp_tag_map_df['cust_tag'][erpmp]] = erp_tag_map_df['serina_tag'][erpmp]

    get_po_model_id_str = "SELECT documentModelID FROM " + str(
        SQL_DB) + ".document WHERE idDocumentType= " + str(
        1) + " LIMIT 1;"
    get_grn_model_id_str = "SELECT documentModelID FROM " + str(
        SQL_DB) + ".document WHERE idDocumentType= " + str(
        2) + " LIMIT 1;"

    get_po_model_id_df = pd.read_sql(get_po_model_id_str, SQLALCHEMY_DATABASE_URL)
    get_grn_model_id_df = pd.read_sql(get_grn_model_id_str, SQLALCHEMY_DATABASE_URL)

    if len(list(get_po_model_id_df['documentModelID'])) > 0:
        po_lineItemtagID_ = list(get_po_model_id_df['documentModelID'])[0]
        # print("po_lineItemtagID_: ", po_lineItemtagID_)
    else:
        po_lineItemtagID_ = 0
        # print("No PO model found!")

    if len(list(get_grn_model_id_df['documentModelID'])) > 0:
        grn_lineItemtagID_ = list(get_grn_model_id_df['documentModelID'])[0]
        # print("grn_lineItemtagID_: ", grn_lineItemtagID_)
    else:
        grn_lineItemtagID_ = 0
        # print("No GRN model found!")

    document_String = "SELECT * FROM " + str(SQL_DB) + ".document where idDocument = " + str(id_doc) + ";"
    document_df = pd.read_sql(document_String, SQLALCHEMY_DATABASE_URL)
    if len(document_df) > 0:
        # document found:
        # get vendor metadata:
        vendor_id = int(document_df['vendorAccountID'][0])
        v_model_id = int(document_df['documentModelID'][0])

        # get template based meta data: w.r.t model id
        fr_bh_String = "SELECT batchmap,erprule,QtyTol_percent,UnitPriceTol_percent, GrnCreationType,AccuracyFeild FROM " + DB + ".frmetadata WHERE idInvoiceModel=" + str(
            v_model_id) + ";"
        fr_bh_df = pd.read_sql(fr_bh_String, SQLALCHEMY_DATABASE_URL)
        bh_vd_status = list(fr_bh_df['batchmap'])[0]
        erp_vd_status = list(fr_bh_df['erprule'])[0]
        qty_tol_percent = list(fr_bh_df['QtyTol_percent'])[0]
        ut_tol_percent = list(fr_bh_df['UnitPriceTol_percent'])[0]
        GrnCreationType = list(fr_bh_df['GrnCreationType'])[0]
        ck_threshold = int(list(fr_bh_df['AccuracyFeild'])[0])
        if bh_vd_status == 1:
            # PO base invo processing:
            documentdata_String = "SELECT * FROM " + str(SQL_DB) + ".documentdata where documentID = " + str(
                id_doc) + ";"
            documentdata_df = pd.read_sql(documentdata_String, SQLALCHEMY_DATABASE_URL)
            itemmetadata_String = "SELECT * FROM " + str(SQL_DB) + ".itemmetadata WHERE vendoraccountID = " + str(
                vendor_id) + ";"
            itemmetadata_df = pd.read_sql(itemmetadata_String, SQLALCHEMY_DATABASE_URL)

            documentTagdef_String = "SELECT * FROM " + str(
                SQL_DB) + ".documenttagdef WHERE idDocumentModel in (" + str(po_lineItemtagID_) + "," + str(
                grn_lineItemtagID_) + "," + str(
                v_model_id) + ");"

            documentTagdef_df = pd.read_sql(documentTagdef_String, SQLALCHEMY_DATABASE_URL)

            # itemusermap_String =  "SELECT  " + str(SQL_DB) + ".itemusermap.mappedinvoitemdescription, " + str(SQL_DB) + ".itemmetadata.description FROM " + str(SQL_DB) + ".itemusermap INNER JOIN " + str(SQL_DB) + ".itemmetadata ON " + str(SQL_DB) + ".itemmetadata.iditemmetadata = " + str(SQL_DB) + ".itemusermap.itemmetadataid WHERE " + str(SQL_DB) + ".itemusermap.vendoraccountID = 1510 and " + str(SQL_DB) + ".itemusermap.batcherrortype in (1,5);"

            itemusermap_String = "SELECT  " + str(SQL_DB) + ".itemusermap.mappedinvoitemdescription, " + str(
                SQL_DB) + ".itemmetadata.description, " + str(SQL_DB) + ".itemmetadata.itemcode FROM " + str(
                SQL_DB) + ".itemusermap INNER JOIN " + str(
                SQL_DB) + ".itemmetadata ON " + str(SQL_DB) + ".itemmetadata.iditemmetadata = " + str(
                SQL_DB) + ".itemusermap.itemmetadataid WHERE " + str(SQL_DB) + ".itemusermap.vendoraccountID = " + str(
                vendor_id) + " and " + str(SQL_DB) + ".itemusermap.batcherrortype in (1,5);"
            itemusermap_df = pd.read_sql(itemusermap_String, SQLALCHEMY_DATABASE_URL)

            doc_tags_ids = documentTagdef_df[['idDocumentTagDef', 'TagLabel']]
            doc_data = documentdata_df[['documentTagDefID', 'Value', 'documentID']]
            doc_data.columns = ['idDocumentTagDef', 'Value', 'documentID']
            doc_header_data = doc_data.merge(
                doc_tags_ids, on='idDocumentTagDef', how='left')

            documentType_df = pd.read_sql_table(
                "documenttype", SQLALCHEMY_DATABASE_URL)

            docType_df = documentType_df[['idDocumentType', 'Name']]
            doc_df = document_df[['idDocumentType',
                                  'idDocument', 'documentStatusID', 'PODocumentID', 'ruleID']]

            doc_ipType_df = docType_df.merge(
                doc_df, on='idDocumentType', how='left')

            doc_ipType_df.columns = ['idDocumentType', 'Name',
                                     'documentID', 'documentStatusID', 'PODocumentID', 'ruleID']

            doc_header_data_df = doc_header_data.merge(
                doc_ipType_df, on='documentID', how='left')

            documentLineitems_String = "SELECT * FROM " + str(
                SQL_DB) + ".documentlineitems WHERE documentID =" + str(id_doc) + ";"
            documentLineitems_df = pd.read_sql(documentLineitems_String, SQLALCHEMY_DATABASE_URL)

            documentLineitemtags_String = "SELECT * FROM " + str(
                SQL_DB) + ".documentlineitemtags WHERE idDocumentModel in (" + str(po_lineItemtagID_) + "," + str(
                grn_lineItemtagID_) + "," + str(
                v_model_id) + ");"
            documentLineitemtags_df = pd.read_sql(documentLineitemtags_String, SQLALCHEMY_DATABASE_URL)

            doc_inline_tags = documentLineitemtags_df[[
                'idDocumentLineItemTags', 'TagName']]
            doc_inline_data = documentLineitems_df[[
                'lineItemtagID', 'Value', 'documentID']]
            doc_inline_tags.columns = ['lineItemtagID', 'TagName']
            doc_inline_data = doc_inline_data.merge(
                doc_inline_tags, on='lineItemtagID', how='left')
            documentLineitem_df = documentLineitems_df.merge(
                doc_ipType_df, on='documentID', how='left')

            pnt_tag_lst_tab = list(doc_inline_tags['TagName'])

            for mp_tag in list(po_tag_map.keys()):
                if mp_tag in pnt_tag_lst_tab:
                    ch_val_ = po_tag_map[mp_tag]
                    # print(ch_val_)
                    doc_inline_tags.loc[doc_inline_tags['TagName'] == mp_tag, 'TagName'] = ch_val_

            PODocumentID = str(document_df['PODocumentID'][0])
            ponum_String = "SELECT * FROM " + str(
                SQL_DB) + ".document where PODocumentID='" + PODocumentID + "' and  idDocumentType=1;"
            ponum_df = pd.read_sql(ponum_String, SQLALCHEMY_DATABASE_URL)

            if len(ponum_df) > 0:
                # PO FOUND:
                po_doc_id = int(ponum_df['idDocument'][0])
                documentLineitem_po_String = "SELECT * FROM " + str(
                    SQL_DB) + ".documentlineitems WHERE documentID= " + str(
                    po_doc_id) + ";"
                documentLineitem_po_df = pd.read_sql(documentLineitem_po_String, SQLALCHEMY_DATABASE_URL)

                doc_tags_ids = documentTagdef_df[['idDocumentTagDef', 'TagLabel']]
                # doc_data = documentdata_df[['documentTagDefID', 'Value', 'documentID']]
                doc_data.columns = ['idDocumentTagDef', 'Value', 'documentID']
                doc_header_data = doc_data.merge(
                    doc_tags_ids, on='idDocumentTagDef', how='left')
                documentType_df = pd.read_sql_table(
                    "documenttype", SQLALCHEMY_DATABASE_URL)
                time.sleep(1)
                # document_df = pd.read_sql_table("document", SQLALCHEMY_DATABASE_URL)

                docType_df = documentType_df[['idDocumentType', 'Name']]
                doc_df = document_df[['idDocumentType',
                                      'idDocument', 'documentStatusID', 'PODocumentID', 'ruleID']]

                doc_ipType_df = docType_df.merge(
                    doc_df, on='idDocumentType', how='left')

                doc_ipType_df.columns = ['idDocumentType', 'Name',
                                         'documentID', 'documentStatusID', 'PODocumentID', 'ruleID']

                doc_header_data_df = doc_header_data.merge(
                    doc_ipType_df, on='documentID', how='left')

                doc_header_po_String = "SELECT * FROM " + str(SQL_DB) + ".documentdata where documentID = " + str(
                    po_doc_id) + ";"
                po_doc_data = pd.read_sql(doc_header_po_String, SQLALCHEMY_DATABASE_URL)

                po_doc_data = po_doc_data[['documentTagDefID', 'Value', 'documentID']]
                po_doc_data.columns = ['idDocumentTagDef', 'Value', 'documentID']
                doc_header_po_df = po_doc_data.merge(
                    doc_tags_ids, on='idDocumentTagDef', how='left')

                pnt_tag_lst = list(doc_header_po_df['TagLabel'])
                for mp_tag in list(po_tag_map.keys()):
                    if mp_tag in pnt_tag_lst:
                        ch_val_ = po_tag_map[mp_tag]
                        # print(ch_val_)
                        doc_header_po_df.loc[doc_header_po_df['TagLabel'] == mp_tag, 'TagLabel'] = ch_val_

                PO_HEADER_ID = list(doc_header_po_df[doc_header_po_df['TagLabel'] == 'PO_HEADER_ID']['Value'])[0]
                if GrnCreationType == 2:
                    grn_getDocID_Str = "SELECT idDocument FROM " + str(
                        SQL_DB) + ".document WHERE idDocumentType=2 and PODocumentID ='" + str(PO_HEADER_ID) + "';"
                    grn_getDocID_df = pd.read_sql(grn_getDocID_Str, SQLALCHEMY_DATABASE_URL)
                    try:

                        if len(grn_getDocID_df) > 0:
                            # GRN doc ID found!
                            grn_doc_id = int(list(grn_getDocID_df['idDocument'])[0])

                            grn_doc_id_String = "SELECT * FROM " + str(
                                SQL_DB) + ".documentlineitems WHERE documentID = " + str(grn_doc_id
                                                                                         ) + ";"
                            grn_doc_id_df = pd.read_sql(grn_doc_id_String, SQLALCHEMY_DATABASE_URL)

                            if len(grn_doc_id_df) > 0:
                                # GRN data found
                                grn_found = 1
                                grn_doc_id = int(grn_doc_id_df['documentID'].unique()[0])
                                grn_inline_String = "SELECT * FROM " + str(
                                    SQL_DB) + ".documentlineitems WHERE documentID = " + str(
                                    grn_doc_id) + ";"
                                # grn_inline_String = "SELECT * FROM documentlineitems WHERE documentID = 2738295;"
                                grn_inlinedf = pd.read_sql(grn_inline_String, SQLALCHEMY_DATABASE_URL)
                                req_grn_df = grn_inlinedf[
                                    ['idDocumentLineItems', 'documentID', 'lineItemtagID', 'Value', 'itemCode']].merge(
                                    doc_inline_tags, on='lineItemtagID', how='left')
                            else:
                                # GRN data not found:
                                req_grn_df = pd.DataFrame()
                                grn_found = 0
                        else:
                            # GRN data not found:
                            req_grn_df = pd.DataFrame()
                            grn_found = 0
                    except Exception as e:
                        # print("EXCEPTION with GRN in 3 way: ", str(e))
                        req_grn_df = pd.DataFrame()
                        grn_found = 0
                else:
                    req_grn_df = pd.DataFrame()
                    grn_found = 2

                documentLineitem_grn_df = req_grn_df

                documentSubStatus_df = pd.read_sql_table("documentsubstatus", SQLALCHEMY_DATABASE_URL)
                documentRules_df = pd.read_sql_table("documentrules", SQLALCHEMY_DATABASE_URL)
                docrulestatusmapping_df = pd.read_sql_table("docrulestatusmapping", SQLALCHEMY_DATABASE_URL)

                docrulestatusmapping_df.columns = ['iddocrulestatusmapping', 'idDocumentSubstatus',
                                                   'DocumentRulesID',
                                                   'createdOn', 'statusorder']

                tmp = pd.merge(documentSubStatus_df, docrulestatusmapping_df, on='idDocumentSubstatus')
                req_rul_df = tmp[['status', 'iddocrulestatusmapping', 'DocumentRulesID', 'statusorder']]
                # itemusermap_df.columns = ['iditemusermap', 'documentID', 'iditemmetadata', 'vendoraccountID',
                #                           'mappedinvoiceitemcode', 'mappedinvoitemdescription', 'batcherrortype',
                #                           'previousitemmetadataid', 'UserID', 'createdOn']

                # -------------------------------------------
                # User map issue with rove:
                # map_df = itemusermap_df.merge(
                #     itemmetadata_df, on='iditemmetadata')
                # req_user_map = map_df[
                #     ['iditemusermap', 'iditemmetadata', 'vendoraccountID_x', 'mappedinvoiceitemcode',
                #      'mappedinvoitemdescription', 'batcherrortype', 'itemcode']]
                # # req_user_map = map_df#[map_df['vendoraccountID_x'] == vendor_acc_id].reset_index(drop=True)
                # # req_user_map = itemusermap_df
                # req_user_map = pd.DataFrame()

                vendor_acc_id = vendor_id
                invo_doc_id = id_doc
                documentLineitem_invo_df = documentLineitems_df
                doc_header_invo_df = doc_header_data
                # list(document_df[document_df['idDocument'] == id_doc]['ruleID'])[0]
                doc_header_invo_df['ruleID'] = list(document_df[document_df['idDocument'] == id_doc]['ruleID'])[0]
                po_grn_data, new_itm_mh, Over_all_ck_data_status, doc_sel_rulid = invo_process(po_doc_id, invo_doc_id,
                                                                                               documentLineitem_po_df,
                                                                                               doc_header_po_df,
                                                                                               documentLineitem_invo_df,
                                                                                               doc_header_invo_df,
                                                                                               documentLineitem_grn_df,
                                                                                               doc_inline_tags,
                                                                                               ck_threshold,
                                                                                               req_rul_df,
                                                                                               document_df,
                                                                                               itemusermap_df,
                                                                                               erp_vd_status,
                                                                                               qty_tol_percent,
                                                                                               ut_tol_percent,
                                                                                               GrnCreationType)
                invo_pro_data[invo_doc_id] = {'map_item': new_itm_mh, 'po_grn_data': po_grn_data, 'inline_rule': 1}
                batch_update_db(invo_pro_data, Over_all_ck_data_status, invo_doc_id, GrnCreationType, grn_found,
                                doc_sel_rulid)

            else:
                # PO NOT FOUND!
                docStatus = 4
                doc_substatus = 7
                qry = "update " + str(SQL_DB) + ".document set documentStatusID = " + str(
                    docStatus) + ", documentsubstatusID = " + str(
                    doc_substatus) + " where idDocument = " + str(id_doc)
                with engine.begin() as conn:  # TRANSACTION
                    conn.execute(qry)

                doc_substatus = 7
                type_s = "Po Not Found - " + str(PODocumentID)
                dochist1 = 'INSERT INTO ' + str(
                    SQL_DB) + '.documentruleshistorylog (documentID, documentSubStatusID, IsActive,type) values (' + str(
                    id_doc) + ',' + str(doc_substatus) + ',' + str(1) + ',"' + type_s + '")'
                with engine.begin() as conn:  # TRANSACTION
                    conn.execute(dochist1)

        else:
            # non po processing:
            docStatus = 2
            doc_substatus = 31
            docDesc = 'No Batch required'

            qry = "update " + str(SQL_DB) + ".document set documentStatusID = " + str(
                docStatus) + ", documentsubstatusID = " + str(doc_substatus) + " where idDocument = " + str(id_doc)
            with engine.begin() as conn:  # TRANSACTION
                conn.execute(qry)
                time.sleep(1)
            created_date = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            his_qry = 'INSERT INTO ' + str(
                SQL_DB) + '.documenthistorylog (documentID, documentdescription, documentStatusID,CreatedOn) values (' + str(
                id_doc) + ', "' + docDesc + '",' + str(docStatus) + ',"' + str(created_date) + '")'
            with engine.begin() as conn:  # TRANSACTION
                conn.execute(his_qry)
    else:
        print("NO invo docId FOUND!")

        # document not found!
        # Notification to backend team
    # print("invo_pro_data: ", invo_pro_data)
    return invo_pro_data
