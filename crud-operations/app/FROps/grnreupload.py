import json, os
import re
from collections import Counter
import pandas as pd
import sys
import traceback
import datetime

sys.path.append("..")
import model
from session.session import DB
from dateutil import parser
from logModule import applicationlogging, email_sender
from session import SQLALCHEMY_DATABASE_URL, DB, engine
from session import Session as SessionLocal
from session.notificationsession import client as mqtt
from fuzzywuzzy import fuzz
import time

SQL_DB = DB
import pytz as tz

tz_region_name = os.getenv("serina_tz", "Asia/Dubai")
tz_region = tz.timezone(tz_region_name)


def tab_to_dict(new_invoLineData_df, itemCode, typ=''):
    invo_NW_itemDict = {}
    des = ''
    for itmId in list(new_invoLineData_df[itemCode].unique()):
        tmpdf = new_invoLineData_df[new_invoLineData_df[itemCode] == itmId].reset_index(drop=True)
        tmpdict = {}
        for ch in range(0, len(tmpdf)):
            val = tmpdf['Value'][ch]
            tg_nm = tmpdf['TagName'][ch]
            if tg_nm in ['Description', 'Quantity']:
                if tg_nm == 'Description':
                    des = val
                tmpdict[tg_nm] = val
        if typ == 'grn':
            invo_NW_itemDict[itmId] = tmpdict
        else:
            invo_NW_itemDict[itmId + "__" + des] = tmpdict
    return invo_NW_itemDict


def grn_reuploadINVO(grnreuploadID):
    msg = ''
    print("IN GRNREUPLOAD FN")
    uploadStatus = 0
    grnreupload_str = "SELECT * FROM " + DB + ".grnreupload where grnreuploadID =" + str(grnreuploadID) + ";"
    grnreupload_df = pd.read_sql(grnreupload_str, SQLALCHEMY_DATABASE_URL)
    old_invo_docId = grnreupload_df['documentIDInvoice']
    grnDocId = grnreupload_df['documentIDgrn']
    new_invo_docID = grnreupload_df['reuploadedInvoId']

    grnData_str = "SELECT * FROM " + DB + ".documentlineitems where documentID ='" + str(grnDocId[0]) + "';"
    grnData_df = pd.read_sql(grnData_str, SQLALCHEMY_DATABASE_URL)
    try:
        old_invoLineData_str = "SELECT * FROM " + DB + ".documentlineitems where documentID ='" + str(
            old_invo_docId[0]) + "';"
        old_invoLineData_df = pd.read_sql(old_invoLineData_str, SQLALCHEMY_DATABASE_URL)

        new_invoLineData_str = "SELECT * FROM " + DB + ".documentlineitems where documentID ='" + str(
            new_invo_docID[0]) + "';"
        new_invoLineData_df = pd.read_sql(new_invoLineData_str, SQLALCHEMY_DATABASE_URL)

        new_invoHeaderData_str = "SELECT * FROM " + DB + ".documentdata where documentID ='" + str(
            new_invo_docID[0]) + "';"
        new_invoHeaderData_df = pd.read_sql(new_invoHeaderData_str, SQLALCHEMY_DATABASE_URL)

        old_invoHeaderData_str = "SELECT * FROM " + DB + ".documentdata where documentID ='" + str(
            old_invo_docId[0]) + "';"
        old_invoHeaderData_df = pd.read_sql(old_invoHeaderData_str, SQLALCHEMY_DATABASE_URL)

        grn_modelID_str = "SELECT documentModelID FROM  " + DB + ".document where idDocument ='" + str(
            grnDocId[0]) + "';"
        grn_modelID_df = pd.read_sql(grn_modelID_str, SQLALCHEMY_DATABASE_URL)

        invo_modelID_str = "SELECT documentModelID FROM  " + DB + ".document where idDocument ='" + str(
            old_invo_docId[0]) + "';"
        invo_modelID_df = pd.read_sql(invo_modelID_str, SQLALCHEMY_DATABASE_URL)

        new_invoModelId_str = "SELECT documentModelID FROM  " + DB + ".document where idDocument ='" + str(
            new_invo_docID[0]) + "';"
        new_invoModelId_df = pd.read_sql(new_invoModelId_str, SQLALCHEMY_DATABASE_URL)
        new_invoLineData_df = new_invoLineData_df[['Value', 'lineItemtagID', 'itemCode']]

        grn_modelID = grn_modelID_df['documentModelID'][0]
        documentLineitemtags_String = "SELECT * FROM " + str(
            SQL_DB) + ".documentlineitemtags WHERE idDocumentModel in (" + str(grn_modelID) + "," + str(
            list(new_invoModelId_df['documentModelID'])[0]) + ");"
        documentLineitemtags_df = pd.read_sql(documentLineitemtags_String, SQLALCHEMY_DATABASE_URL)

        doc_inline_tags = documentLineitemtags_df[[
            'idDocumentLineItemTags', 'TagName']]

        doc_inline_tags.columns = ['lineItemtagID', 'TagName']
        old_invoLineData_df = old_invoLineData_df.merge(
            doc_inline_tags, on='lineItemtagID', how='left')

        old_invoLineData_df = old_invoLineData_df[['Value', 'TagName', 'itemCode', 'invoice_itemcode']]

        grnData_df = grnData_df.merge(
            doc_inline_tags, on='lineItemtagID', how='left')

        new_invoLineData_df = new_invoLineData_df.merge(
            doc_inline_tags, on='lineItemtagID', how='left')

        grnData_df = grnData_df[['Value', 'TagName', 'invoice_itemcode']]
        new_invoModelId = new_invoModelId_df['documentModelID'][0]

        headertags_str = "SELECT * FROM  " + DB + ".documenttagdef where idDocumentModel =" + str(
            new_invoModelId) + " ; "
        headertags_df = pd.read_sql(headertags_str, SQLALCHEMY_DATABASE_URL)

        invo_NW_itemDict = tab_to_dict(new_invoLineData_df, 'itemCode')
        invo_New_data = tab_to_dict(new_invoLineData_df, 'itemCode', 'grn')
        grn_itemDict = tab_to_dict(grnData_df, 'invoice_itemcode', 'grn')
        old_invoDict = tab_to_dict(old_invoLineData_df, 'invoice_itemcode')

        new_invoHeaderData_df = new_invoHeaderData_df[['documentTagDefID', 'Value']]
        new_invoHeaderData_df.columns = ['idDocumentTagDef', 'Value']
        new_invoHeaderData_df = new_invoHeaderData_df.merge(
            headertags_df, on='idDocumentTagDef', how='left')

        old_invoHeaderData_df = old_invoHeaderData_df[['documentTagDefID', 'Value']]
        old_invoHeaderData_df.columns = ['idDocumentTagDef', 'Value']
        old_invoHeaderData_df = old_invoHeaderData_df.merge(
            headertags_df, on='idDocumentTagDef', how='left')

        nw_invo_po = list(new_invoHeaderData_df[new_invoHeaderData_df['TagLabel'] == 'PurchaseOrder']['Value'])[0]
        old_invo_po = list(old_invoHeaderData_df[old_invoHeaderData_df['TagLabel'] == 'PurchaseOrder']['Value'])[0]
        accept = 0
        fr_bh_String = "SELECT batchmap,erprule,QtyTol_percent,UnitPriceTol_percent, GrnCreationType,AccuracyFeild FROM " + DB + ".frmetadata WHERE idInvoiceModel=" + str(
            list(new_invoModelId_df['documentModelID'])[0]) + ";"
        fr_bh_df = pd.read_sql(fr_bh_String, SQLALCHEMY_DATABASE_URL)
        qty_tol_percent = list(fr_bh_df['QtyTol_percent'])[0]

        if nw_invo_po != old_invo_po:
            if nw_invo_po in old_invo_po:
                pfx = old_invo_po.replace(nw_invo_po, '')
                if pfx in ['RTC-PO-']:
                    nw_invo_po = pfx + nw_invo_po
                    if nw_invo_po == old_invo_po:
                        print("Accept: ")
                        accept = 1
                else:
                    print("reject: PO not matching")
            else:
                print("reject")
        elif nw_invo_po == old_invo_po:
            accept = 1
        if accept == 1:
            fuz_scrGRN = {}
            for ky in old_invoDict:
                Description = old_invoDict[ky]['Description']
                Quantity = old_invoDict[ky]['Quantity']
                grnTmp = {}
                for invItm in list(invo_NW_itemDict.keys()):
                    invo_Desc = invItm.split("__")[1]
                    invo_itmId = invItm.split("__")[0]
                    tmpFuzz_scr = fuzz.ratio(invo_Desc.lower(), Description.lower())
                    grnTmp[invo_itmId] = tmpFuzz_scr

                fuz_scrGRN[ky.split("__")[0]] = grnTmp

            grn_fl = []
            invoMap = {}
            #     invo_New_data = {'1': {'Description': 'WHOLEMEAL BREAD 1.1KG', 'Quantity': '4.0'},
            #      '2': {'Description': 'BREAD WHITE SUPER JUMBO 1.1KG', 'Quantity': '8.0'},
            #      '3': {'Description': 'ARABIC BREAD WHITE LARGE', 'Quantity': '10.0'}}

            for mxscr in fuz_scrGRN:
                mx_scr_item_invo = max(fuz_scrGRN[mxscr], key=fuz_scrGRN[mxscr].get)
                print(mx_scr_item_invo)
                print("invo_qty: ", invo_New_data[mx_scr_item_invo]['Quantity'], " GRN_qty: ",
                      grn_itemDict[mxscr]['Quantity'])
                nw_invoQty = float(invo_New_data[mx_scr_item_invo]['Quantity'])
                grnQty = float(grn_itemDict[mxscr]['Quantity'])
                qty_threshold = (nw_invoQty * (int(qty_tol_percent) / 100))
                # abs(invo_qty - po_qty) > qty_threshold:
                if abs(nw_invoQty - grnQty) > qty_threshold:
                    # if float(invo_New_data[mx_scr_item_invo]['Quantity']) != float(grn_itemDict[mxscr]['Quantity']):
                    grn_fl.append(mxscr)
                else:
                    invoMap[mx_scr_item_invo] = mxscr
                    map_update_qty = "update rove_hotels.documentlineitems set invoice_itemcode =" + str(
                        mxscr) + " where documentID in (" + str(list(new_invo_docID)[0]) + ") and itemCode = " + str(
                        mx_scr_item_invo) + ";"
                    with engine.begin() as conn:  # TRANSACTION
                        conn.execute(map_update_qty)
                        time.sleep(1)
            if len(grn_fl) > 0:
                msg = "Quantity Mismatch with GRN data"
                print('reject invoice')
                uploadStatus = 0
                update_DocID = "update rove_hotels.document set documentStatusID =10, documentsubstatusID = 47  where idDocument =" + str(
                    list(new_invo_docID)[0]) + ";"
                with engine.begin() as conn:  # TRANSACTION
                    conn.execute(update_DocID)
                    time.sleep(1)
            else:
                uploadStatus = 1
                print("Accepted")
                msg = "Invoice reupload Accepted."
                grn_update_qry = "update rove_hotels.grnreupload set RejectStatus=0 where grnreuploadID = " + str(
                    grnreuploadID) + ";"
                with engine.begin() as conn:  # TRANSACTION
                    conn.execute(grn_update_qry)
                    time.sleep(1)
                invo_id = list(new_invoHeaderData_df[new_invoHeaderData_df['TagLabel']=='InvoiceId']['Value'])[0]
                update_grn_no = 'GRN-' + invo_id
                update_grnNO_qty = "update rove_hotels.document set docheaderID = '" + str(
                    update_grn_no) + "' where idDocument =" + str(list(grnDocId)[0]) + ";"
                update_DocID = "update rove_hotels.document set documentStatusID =4, documentsubstatusID = 39  where " \
                               "idDocument =" + str(
                    list(new_invo_docID)[0]) + ";"

                old_update_DocID = "update rove_hotels.document set documentStatusID =10, documentsubstatusID = 46  where " \
                                   "idDocument =" + str(old_invo_docId[0]) + ";"

                # update_DocID = "update rove_hotels.document set documentStatusID =4, documentsubstatusID = 39  where idDocument ="+str(new_invo_docID)+";"
                with engine.begin() as conn:  # TRANSACTION
                    conn.execute(update_grnNO_qty)
                    time.sleep(0.2)
                    conn.execute(old_update_DocID)
                    time.sleep(0.2)
                with engine.begin() as conn:  # TRANSACTION
                    conn.execute(update_DocID)
                    time.sleep(0.2)
                grn_update_DocID = "update rove_hotels.document set documentStatusID =20 where idDocument =" + str(
                    list(grnDocId)[0]) + ";"
                with engine.begin() as conn:  # TRANSACTION
                    conn.execute(grn_update_DocID)

        else:
            msg = "Rejected: PO Number not matching with "+old_invo_po+"."
            print(" PO mismatch with metadata: ", old_invo_po)
            #msg = "Rejected: PO not matching (" + str(old_invo_po) + "!=" + str(nw_invo_po) + "       ."
            update_DocID = "update rove_hotels.document set documentStatusID =10, documentsubstatusID = 47  where " \
                           "idDocument =" + str(
                list(new_invo_docID)[0]) + ";"
            with engine.begin() as conn:  # TRANSACTION
                conn.execute(update_DocID)
                time.sleep(0.2)

    except Exception as gn:
        msg = "Rejected: "+str(gn)
        print(str(gn))
        uploadStatus = 0
        update_DocID = "update rove_hotels.document set documentStatusID =10, documentsubstatusID = 47  where idDocument =" + str(
            list(new_invo_docID)[0]) + ";"
        with engine.begin() as conn:  # TRANSACTION
            conn.execute(update_DocID)
        time.sleep(0.2)
    if uploadStatus==0 and msg == '':
        msg="Rejected: Please verify metadata"
    try:
        if uploadStatus==1:
            docDesc="Document reupload accepted"
            docStatus = 4
            docSubStatus = 39
        else:
            docDesc = msg
            docStatus = 10
            docSubStatus = 47
        #update history log:
        created_date = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        his_qry = 'INSERT INTO ' + str(
            SQL_DB) + '.documenthistorylog (documentID, documentdescription, documentStatusID,documentSubStatusID,CreatedOn) values ('+str(
                list(new_invo_docID)[0]) + ', "' + docDesc + '",' + str(docStatus) + ','+str(docSubStatus)+',"' + str(created_date) + '")'
        print("his_qry: ",his_qry)
        with engine.begin() as conn:  # TRANSACTION
            conn.execute(his_qry)
        time.sleep(0.2)
        #update old doc:
        if uploadStatus==1:
            docDesc="Document reupload accepted"
            docStatus = 46
            #update history log:
            created_date = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            his_qry = 'INSERT INTO ' + str(
                SQL_DB) + '.documenthistorylog (documentID, documentdescription, documentStatusID,documentSubStatusID,CreatedOn) values (' + str(
                old_invo_docId[0]) + ', "' + docDesc + '",' + str(docStatus) + ',' + str(docSubStatus) + ',"' + str(
                created_date) + '");'

            with engine.begin() as conn:  # TRANSACTION
                conn.execute(his_qry)

    except Exception as e:
        print(str(e))

    print("GRN reupload final status: ", uploadStatus, ", ", msg)
    return [uploadStatus, msg]
