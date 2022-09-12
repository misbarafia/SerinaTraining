import traceback
import requests, os, traceback, base64
from sqlalchemy.orm import Session, load_only, Load
from sqlalchemy import func, case, or_, and_
from fastapi.responses import Response
import pytz as tz
from datetime import datetime
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from sqlalchemy.sql import func

import sys

sys.path.append("..")
from logModule import applicationlogging
import model
import schemas

tz_region_name = os.getenv("serina_tz", "Asia/Dubai")
tz_region = tz.timezone(tz_region_name)


async def readbatchprocessdetails(u_id: int, db: Session):
    """
     This function read a service provider account. It contains 2 parameter.
     :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
     :return: It return a result of dictionary type.
     """
    try:
        iscust = db.query(model.User.isCustomerUser).filter_by(idUser=u_id, isActive=1).scalar()
        data = db.query(model.Document, model.DocumentSubStatus, model.Rule, model.VendorAccount, model.Vendor).options(
            Load(model.Document).load_only("docheaderID", "CreatedOn", "PODocumentID", "totalAmount",
                                           "documentStatusID", "documentsubstatusID"),
            Load(model.DocumentSubStatus).load_only("status"),
            Load(model.VendorAccount).load_only("AccountType"),
            Load(model.Vendor).load_only("VendorName")).filter(
            model.Document.documentsubstatusID == model.DocumentSubStatus.idDocumentSubstatus).filter(
            model.Document.ruleID == model.Rule.idDocumentRules).filter(
            model.Document.vendorAccountID == model.VendorAccount.idVendorAccount).filter(
            model.VendorAccount.vendorID == model.Vendor.idVendor).filter(
            model.Document.documentStatusID == 4).filter(
            model.Document.documentsubstatusID != 4).filter(
            model.Document.documentsubstatusID != 31).filter(
            model.Document.documentsubstatusID != 35).filter(
            model.Document.documentsubstatusID != 36).filter(
            model.Document.documentsubstatusID != 38).filter(
            model.Document.documentsubstatusID != 39)
        if iscust == 1:
            sub_query_ent = db.query(model.UserAccess.EntityID).filter_by(UserID=u_id, isActive=1).distinct()
            data = data.filter(
                model.Document.entityID.in_(sub_query_ent)).all()
        else:
            sub_query_ent = db.query(model.VendorUserAccess.vendorAccountID).filter_by(vendorUserID=u_id,
                                                                                       isActive=1).distinct()
            data = data.filter(
                model.Document.vendorAccountID.in_(sub_query_ent)).all()

        # for row in data:
        #     allsubstatus = db.query(model.DocumentRuleupdates.documentSubStatusID).filter_by(
        #         documentID=row[0].idDocument,IsActive=1,type='error').distinct()

        #     allsubstatus_ord = db.query(model.DocumentRulemapping.statusorder).filter(
        #         model.DocumentRulemapping.DocumentstatusID.in_(allsubstatus)).filter(
        #             model.DocumentRulemapping.DocumentRulesID==row[0].ruleID).all()
        #     l1=[]
        #     sub_status_id = db.query(model.Document.documentsubstatusID).filter(
        #         model.Document.idDocument == row[0].idDocument).scalar()
        #     for row11 in allsubstatus_ord:
        #         l1.append(row11.statusorder)
        #     ord_id = db.query(model.DocumentRulemapping.statusorder).filter_by(DocumentRulesID=row[0].ruleID,DocumentstatusID=23).all()
        #     # print(allsubstatus_ord,l1)
        #     if sub_status_id ==29:
        #         payment_case = case(
        #             [                    
        #                 (model.DocumentRulemapping.statusorder.in_(l1), "In progress")
        #                 # (model.DocumentRulemapping.statusorder ==ord_id[0][0], "Not passed")

        #             ],else_="Not passed"
        #         ).label("documentStatus")
        #     else:
        #         payment_case = case(
        #             [                    
        #                 (model.DocumentRulemapping.statusorder.in_(l1), "In progress"),
        #                 (model.DocumentRulemapping.statusorder ==ord_id[0][0], "Not passed")

        #             ],else_="Passed"
        #         ).label("documentStatus")
        #     status_history = db.query(model.DocumentRulemapping , model.DocumentSubStatus,payment_case).options(
        #         Load(model.DocumentRulemapping).load_only("DocumentRulesID","statusorder"),Load(model.DocumentSubStatus).load_only("status")).filter(model.DocumentRulemapping.DocumentRulesID==row[0].ruleID).filter(model.DocumentRulemapping.DocumentstatusID == model.DocumentSubStatus.idDocumentSubstatus).order_by(model.DocumentRulemapping.statusorder.asc()).all()

        #     setattr(row[0], "All_Status", status_history)  
        # ord_id = db.query(model.DocumentRulemapping.statusorder).filter_by(DocumentRulesID=row[0].ruleID,DocumentstatusID=row[0].documentsubstatusID).all()
        # if len(ord_id)==1:

        #     payment_case = case(
        #     [
        #         (model.DocumentRulemapping.statusorder < ord_id[0][0], "Passed"),
        #         (model.DocumentRulemapping.statusorder == ord_id[0][0], "In progress"),
        #         (model.DocumentRulemapping.statusorder > ord_id[0][0], "Not passed")

        #     ]
        # ).label("documentStatus")

        #     status_history = db.query(model.DocumentRulemapping , model.DocumentSubStatus,payment_case).options(
        #     Load(model.DocumentRulemapping).load_only("DocumentRulesID","statusorder"),Load(model.DocumentSubStatus).load_only("status")).filter(model.DocumentRulemapping.DocumentRulesID==row[0].ruleID).filter(model.DocumentRulemapping.DocumentstatusID == model.DocumentSubStatus.idDocumentSubstatus).order_by(model.DocumentRulemapping.statusorder.asc()).all()

        #     setattr(row[0], "All_Status", status_history)

        return data
    except Exception as e:
        print(traceback.format_exc())
        applicationlogging.logException("ROVE HOTEL DEV", "BatchexceptionCrud.py readbatchprocessdetails", str(e))
        return Response(status_code=500, headers={"Error": "Server error", "Desc": "Invalid result"})


async def send_to_batch_approval(u_id: int, rule_id: int, inv_id: int, db: Session):
    try:
        sub_status_id = db.query(model.DocumentSubStatus.idDocumentSubstatus).filter(
            model.DocumentSubStatus.status == "Batch Edit").one()
        old_r_id = db.query(model.Document.ruleID).filter(model.Document.idDocument == inv_id).one()
        old_rule = db.query(model.Rule.Name).filter(model.Rule.idDocumentRules == old_r_id[0]).one()
        new_rule = db.query(model.Rule.Name).filter(model.Rule.idDocumentRules == rule_id).one()

        db.query(model.Document).filter_by(idDocument=inv_id).update(
            {"documentsubstatusID": sub_status_id[0]})

        inv_up_id = db.query(model.DocumentRuleupdates.idDocumentRulehistorylog).filter_by(
            documentID=inv_id, type='rule').all()
        if len(inv_up_id) > 0:
            db.query(model.DocumentRuleupdates).filter_by(documentID=inv_id,
                                                          IsActive=1, type='rule').update({"IsActive": 0})
        if old_r_id[0] != rule_id:
            db.query(model.Document).filter_by(idDocument=inv_id).update(
                {"ruleID": rule_id, "IsRuleUpdated": 1})
            c4 = model.DocumentRuleupdates(documentID=inv_id, oldrule=old_rule[0], newrule=new_rule[0], userID=u_id,
                                           IsActive=1, type='rule',
                                           createdOn=datetime.now(tz_region).strftime("%Y-%m-%d %H:%M:%S"))
            db.add(c4)
        db.commit()
        return {"result": "success"}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV", "BatchexceptionCrud.py send_to_batch_approval", str(e))
        return Response(status_code=500, headers={"Error": "Server error", "Desc": "Invalid result"})


async def send_to_manual_approval(u_id: int, inv_id: int, db: Session):
    try:
        sub_status_id = db.query(model.DocumentSubStatus.idDocumentSubstatus).filter(
            model.DocumentSubStatus.status == "Manual Check").one()

        db.query(model.Document).filter_by(idDocument=inv_id).update(
            {"documentsubstatusID": sub_status_id[0], 'documentStatusID': 2})

        db.commit()
        return {"result": "success"}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV", "BatchexceptionCrud.py send_to_manual_approval", str(e))
        return Response(status_code=500, headers={"Error": "Server error", "Desc": "Invalid result"})


async def readbatchprocessdetailsAdmin(u_id: int, db: Session):
    """
     This function read a service provider account. It contains 2 parameter.
     :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
     :return: It return a result of dictionary type.
     """
    try:
        sub_query_ent = db.query(model.UserAccess.EntityID).filter_by(UserID=u_id, isActive=1).distinct()
        sub_status = db.query(model.DocumentSubStatus.idDocumentSubstatus).filter(
            model.DocumentSubStatus.status.in_(['Batch Edit', 'Manual Check'])).distinct()
        approval_type = case(
            [
                (model.DocumentSubStatus.idDocumentSubstatus == 4, "Batch Approval"),
                (model.DocumentSubStatus.idDocumentSubstatus == 6, "Manual Approval")
            ]
        ).label("Approvaltype")

        data = db.query(model.Document, model.DocumentSubStatus, model.Rule, model.VendorAccount, model.Vendor,
                        model.DocumentRuleupdates, approval_type).options(
            Load(model.VendorAccount).load_only("AccountType"),
            Load(model.Vendor).load_only("VendorName"),
            Load(model.DocumentRuleupdates).load_only("oldrule", "createdOn")).filter(
            model.Document.entityID.in_(sub_query_ent)).filter(
            model.Document.documentsubstatusID.in_(sub_status)).filter(
            model.Document.documentsubstatusID == model.DocumentSubStatus.idDocumentSubstatus).filter(
            model.Document.ruleID == model.Rule.idDocumentRules).filter(
            model.Document.vendorAccountID == model.VendorAccount.idVendorAccount).filter(
            model.VendorAccount.vendorID == model.Vendor.idVendor).join(
            model.DocumentRuleupdates,
            and_(model.DocumentRuleupdates.documentID == model.Document.idDocument,
                 model.DocumentRuleupdates.type == 'rule'),
            isouter=True).filter(or_(model.Document.IsRuleUpdated == 0, model.DocumentRuleupdates.IsActive == 1)).all()

        return data
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV", "BatchexceptionCrud.py readbatchprocessdetailsAdmin", str(e))
        return Response(status_code=500, headers={"Error": "Server error", "Desc": "Invalid result"})


async def send_to_batch_approval_Admin(u_id: int, inv_id: int, db: Session):
    try:
        sub_statusid = db.query(model.Document.documentsubstatusID).filter(
            model.Document.idDocument == inv_id).scalar()
        if sub_statusid == 7:
            sub_status_idt = 3
        else:
            sub_status_idt = 24
        sub_status_id = db.query(model.DocumentSubStatus.idDocumentSubstatus).filter(
            model.DocumentSubStatus.status == "Batch Edit Approved").one()

        db.query(model.Document).filter_by(idDocument=inv_id).update(
            {"documentsubstatusID": sub_status_idt, 'documentStatusID': 1})
        db.query(model.DocumentRuleupdates).filter_by(documentID=inv_id, type='error').update(
            {"IsActive": 0})
        db.commit()
        return {"result": "success"}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV", "BatchexceptionCrud.py send_to_batch_approval_Admin", str(e))
        return Response(status_code=500, headers={"Error": "Server error", "Desc": "Invalid result"})


async def send_to_manual_approval_Admin(u_id: int, inv_id: int, db: Session):
    try:
        sub_status_id = db.query(model.DocumentSubStatus.idDocumentSubstatus).filter(
            model.DocumentSubStatus.status == "Manual Check Approved").one()

        db.query(model.Document).filter_by(idDocument=inv_id).update(
            {"documentsubstatusID": sub_status_id[0], 'documentStatusID': 2})

        db.commit()
        return {"result": "success"}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV", "BatchexceptionCrud.py send_to_manual_approval_Admin", str(e))
        return Response(status_code=500, headers={"Error": "Server error", "Desc": "Invalid result"})


async def readInvokebatchsummary(u_id: int, db: Session):
    """
     This function read a service provider account. It contains 2 parameter.
     :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
     :return: It return a result of dictionary type.
     """
    try:
        sub_query_ent = db.query(model.UserAccess.EntityID).filter_by(UserID=u_id, isActive=1).distinct()
        sub_status_id = db.query(model.DocumentSubStatus.idDocumentSubstatus).filter(
            model.DocumentSubStatus.status == 'Batch Edit Approved').one()
        status_id = db.query(model.DocumentSubStatus.DocumentstatusID).filter(
            model.DocumentSubStatus.status == 'Batch Edit Approved').one()

        data = db.query(model.Document, model.DocumentSubStatus, model.Rule, model.VendorAccount, model.Vendor).options(
            Load(model.VendorAccount).load_only("AccountType"),
            Load(model.Vendor).load_only("VendorName")).filter(
            model.Document.entityID.in_(sub_query_ent)).filter(
            model.Document.documentsubstatusID == model.DocumentSubStatus.idDocumentSubstatus).filter(
            model.Document.ruleID == model.Rule.idDocumentRules).filter(
            model.Document.vendorAccountID == model.VendorAccount.idVendorAccount).filter(
            model.VendorAccount.vendorID == model.Vendor.idVendor).filter(
            model.Document.documentsubstatusID == sub_status_id[0],
            model.Document.documentStatusID == status_id[0]).all()

        return data
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV", "BatchexceptionCrud.py readInvokebatchsummary", str(e))
        return Response(status_code=500, headers={"Error": "Server error", "Desc": "Invalid result"})


async def readfinancialapprovalsummary(u_id: int, db: Session):
    """
     This function read a service provider account. It contains 2 parameter.
     :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
     :return: It return a result of dictionary type.
     """
    try:
        sub_query_ent = db.query(model.UserAccess.EntityID).filter_by(UserID=u_id, isActive=1).distinct()
        sub_status = db.query(model.DocumentSubStatus.idDocumentSubstatus).filter(model.DocumentSubStatus.status.in_(
            ['System Check', 'Batch Edit Approved', 'Manual Check Approved'])).distinct()
        approval_type = case(
            [
                (model.DocumentSubStatus.idDocumentSubstatus == 5, "Batch Approval"),
                (model.DocumentSubStatus.idDocumentSubstatus == 27, "Batch Approval"),
                (model.DocumentSubStatus.idDocumentSubstatus == 25, "Manual Approval")
            ]
        ).label("Approvaltype")
        data1 = db.query(model.Document, model.Rule, model.VendorAccount, model.Vendor, approval_type).options(
            Load(model.VendorAccount).load_only("AccountType"),
            Load(model.Vendor).load_only("VendorName")).filter(
            model.Document.entityID.in_(sub_query_ent)).filter(
            model.Document.ruleID == model.Rule.idDocumentRules).filter(
            model.Document.vendorAccountID == model.VendorAccount.idVendorAccount).filter(
            model.VendorAccount.vendorID == model.Vendor.idVendor).filter(model.Document.documentStatusID == 2).all()

        return data1
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV", "BatchexceptionCrud.py readfinancialapprovalsummary", str(e))
        return Response(status_code=500, headers={"Error": "Server error", "Desc": "Invalid result"})


async def test_batchdata(u_id: int, db: Session):
    try:
        data = {2738459: {'map_item': {'467070': {'invo_itm_code': '1',
                                                  'fuzz_scr': 100,
                                                  'item_status': 1},
                                       '467071': {'invo_itm_code': '2', 'fuzz_scr': 100, 'item_status': 1}},
                          'po_grn_data': {'467070': {'qty': {'po_status': 0,
                                                             'grn_status': 0,
                                                             'idDocumentLineItems': 259228,
                                                             'ck_status': 2},
                                                     'unit_price': {'po_status': 0,
                                                                    'idDocumentLineItems': 259233,
                                                                    'ck_status': 1},
                                                     'item': {'po_status': 1,
                                                              'grn_status': 1,
                                                              'idDocumentLineItems': 259226,
                                                              'ck_status': 2}},
                                          '467071': {'qty': {'po_status': 0,
                                                             'grn_status': 0,
                                                             'idDocumentLineItems': 259236,
                                                             'ck_status': 2},
                                                     'unit_price': {'po_status': 0,
                                                                    'idDocumentLineItems': 259241,
                                                                    'ck_status': 1},
                                                     'item': {'po_status': 1,
                                                              'grn_status': 1,
                                                              'idDocumentLineItems': 259234,
                                                              'ck_status': 2}}},
                          'inline_rule': 2},
                2738466: {'map_item': {'467070': {'invo_itm_code': '1',
                                                  'fuzz_scr': 100,
                                                  'item_status': 1},
                                       '467071': {'invo_itm_code': '2', 'fuzz_scr': 100, 'item_status': 1}},
                          'po_grn_data': {'467070': {'qty': {'po_status': 0,
                                                             'grn_status': 0,
                                                             'idDocumentLineItems': 259365,
                                                             'ck_status': 2},
                                                     'unit_price': {'po_status': 0,
                                                                    'idDocumentLineItems': 259370,
                                                                    'ck_status': 1},
                                                     'item': {'po_status': 1,
                                                              'grn_status': 1,
                                                              'idDocumentLineItems': 259363,
                                                              'ck_status': 2}},
                                          '467071': {'qty': {'po_status': 0,
                                                             'grn_status': 0,
                                                             'idDocumentLineItems': 259373,
                                                             'ck_status': 2},
                                                     'unit_price': {'po_status': 0,
                                                                    'idDocumentLineItems': 259378,
                                                                    'ck_status': 1},
                                                     'item': {'po_status': 1,
                                                              'grn_status': 1,
                                                              'idDocumentLineItems': 259371,
                                                              'ck_status': 2}}},
                          'inline_rule': 2},
                2738467: {'map_item': {'467069': {'invo_itm_code': '1',
                                                  'fuzz_scr': 75,
                                                  'item_status': 1}},
                          'po_grn_data': {'467069': {'qty': {'po_status': 1,
                                                             'grn_status': 1,
                                                             'idDocumentLineItems': 259381,
                                                             'ck_status': 2},
                                                     'unit_price': {'po_status': 1,
                                                                    'idDocumentLineItems': 259382,
                                                                    'ck_status': 1},
                                                     'item': {'po_status': 1,
                                                              'grn_status': 1,
                                                              'idDocumentLineItems': 259379,
                                                              'ck_status': 2}}},
                          'inline_rule': 2},
                2738470: {'map_item': {'462120': {'invo_itm_code': '1',
                                                  'fuzz_scr': 74,
                                                  'item_status': 1}},
                          'po_grn_data': {'462120': {'qty': {'po_status': 1,
                                                             'grn_status': 1,
                                                             'idDocumentLineItems': 259427,
                                                             'ck_status': 2},
                                                     'unit_price': {'po_status': 1,
                                                                    'idDocumentLineItems': 259428,
                                                                    'ck_status': 1},
                                                     'item': {'po_status': 1,
                                                              'grn_status': 1,
                                                              'idDocumentLineItems': 259426,
                                                              'ck_status': 2}}},
                          'inline_rule': 2},
                2738564: {'map_item': {'415086': {'invo_itm_code': '1',
                                                  'fuzz_scr': 81,
                                                  'item_status': 1},
                                       '415088': {'invo_itm_code': '3', 'fuzz_scr': 90, 'item_status': 1},
                                       '415087': {'invo_itm_code': '2', 'fuzz_scr': 74, 'item_status': 1}},
                          'po_grn_data': {'415086': {'qty': {'po_status': 1,
                                                             'grn_status': 1,
                                                             'idDocumentLineItems': 262335,
                                                             'ck_status': 2},
                                                     'unit_price': {'po_status': 1,
                                                                    'idDocumentLineItems': 262336,
                                                                    'ck_status': 1},
                                                     'item': {'po_status': 1,
                                                              'grn_status': 1,
                                                              'idDocumentLineItems': 262334,
                                                              'ck_status': 2}},
                                          '415088': {'qty': {'po_status': 1,
                                                             'grn_status': 1,
                                                             'idDocumentLineItems': 262345,
                                                             'ck_status': 2},
                                                     'unit_price': {'po_status': 1,
                                                                    'idDocumentLineItems': 262346,
                                                                    'ck_status': 1},
                                                     'item': {'po_status': 1,
                                                              'grn_status': 1,
                                                              'idDocumentLineItems': 262343,
                                                              'ck_status': 2}},
                                          '415087': {'qty': {'po_status': 1,
                                                             'grn_status': 1,
                                                             'idDocumentLineItems': 262340,
                                                             'ck_status': 2},
                                                     'unit_price': {'po_status': 1,
                                                                    'idDocumentLineItems': 262341,
                                                                    'ck_status': 1},
                                                     'item': {'po_status': 1,
                                                              'grn_status': 1,
                                                              'idDocumentLineItems': 262338,
                                                              'ck_status': 2}}},
                          'inline_rule': 2}}

        for key, value in data.items():
            print(key)
            inv_id = key
            data1 = value['po_grn_data']
            data2 = value['map_item']
            for key, value in data2.items():
                print(value['fuzz_scr'])
                db.query(model.DocumentLineItems).filter_by(documentID=inv_id, itemCode=value['invo_itm_code']).update(
                    {"invoice_itemcode": key, "Fuzzy_scr": value['fuzz_scr']})

            for key, value in data1.items():
                print(key)
                data2 = value
                for key, value in data2.items():
                    print(key, value)
                    if key != 'unit_price':
                        if value['po_status'] == 1 and value['grn_status'] == 1:
                            error = 0
                            desc = None
                        elif value['po_status'] == 1 and value['grn_status'] == 0:
                            error = 1
                            desc = key + " is not matching with GRN"
                        elif value['po_status'] == 0 and value['grn_status'] == 1:
                            error = 1
                            desc = key + " is not matching with PO"
                        elif value['po_status'] == 0 and value['grn_status'] == 0:
                            error = 1
                            desc = key + " is not matching with PO and GRN"
                    else:
                        if value['po_status'] == 0:
                            error = 1
                            desc = key + " is not matching with PO"
                        else:
                            error = 0
                            desc = None

                    db.query(model.DocumentLineItems).filter_by(
                        idDocumentLineItems=value['idDocumentLineItems']).update(
                        {"isError": error, 'CK_status': value['ck_status'], 'ErrorDesc': desc})

        db.commit()
        return {"result": "success"}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV", "BatchexceptionCrud.py test_batchdata", str(e))
        return Response(status_code=500, headers={"Error": "Server error", "Desc": "Invalid result"})


#################################################################################################

async def readlinedatatest(u_id: int, inv_id: int, db: Session):
    try:
        invdat = db.query(model.Document).options(
            load_only("docPath", "supplierAccountID", "vendorAccountID")).filter_by(
            idDocument=inv_id).one()
        rule_data = db.query(model.Rule).filter(model.Rule.idDocumentRules == invdat.ruleID).all()
        all_po = db.query(model.Document).options(
            load_only("PODocumentID")).filter_by(vendorAccountID=invdat.vendorAccountID, idDocumentType=1).all()

        vendordata = db.query(model.Vendor, model.VendorAccount).options(
            Load(model.Vendor).load_only("VendorName", "VendorCode", "Email", "Contact", "TradeLicense",
                                         "VATLicense",
                                         "TLExpiryDate", "VLExpiryDate", "TRNNumber"),
            Load(model.VendorAccount).load_only("AccountType", "Account")).filter(
            model.VendorAccount.idVendorAccount == invdat.vendorAccountID).join(model.VendorAccount,
                                                                                model.VendorAccount.vendorID == model.Vendor.idVendor,
                                                                                isouter=True).all()

        headerdata = db.query(model.DocumentData, model.DocumentTagDef, model.DocumentUpdates).options(
            Load(model.DocumentData).load_only("Value", "isError", "ErrorDesc", "IsUpdated", "Xcord", "Ycord", "Width",
                                               "Height"),
            Load(model.DocumentTagDef).load_only("TagLabel"),
            Load(model.DocumentUpdates).load_only("OldValue", "UpdatedOn")).filter(
            model.DocumentData.documentTagDefID == model.DocumentTagDef.idDocumentTagDef,
            model.DocumentData.documentID == inv_id).join(
            model.DocumentUpdates,
            model.DocumentUpdates.documentDataID == model.DocumentData.idDocumentData,
            isouter=True).filter(
            or_(model.DocumentData.IsUpdated == 0, model.DocumentUpdates.IsActive == 1))
        headerdata = headerdata.all()
        doc_model = db.query(model.Document.documentModelID).filter(model.Document.idDocument == inv_id).one()
        erp_rule = db.query(model.FRMetaData.erprule).filter(model.FRMetaData.idInvoiceModel == doc_model[0]).one()
        itemdata = {'Result': []}
        if erp_rule[0] != 2:
            po_number = db.query(model.Document.PODocumentID).filter(model.Document.idDocument == inv_id).one()
            po_doc_id = db.query(model.Document.idDocument).filter(model.Document.PODocumentID == po_number[0],
                                                                   model.Document.idDocumentType == 1).scalar()
            # to find grn document id
            # po_header_id = db.query(model.Document.docheaderID).filter(model.Document.idDocument==po_doc_id).one()
            # grn_doc_id = db.query(model.DocumentLineItems.documentID).filter(model.DocumentLineItems.lineItemtagID==37,model.DocumentLineItems.Value==po_header_id[0]).first()
            # grn_doc_id = db.query(model.Document.idDocument).filter(model.Document.PODocumentID==po_number[0],model.Document.idDocumentType==2).one()
            # po_doc_id = db.query(model.Document.idDocument).filter(model.Document.PODocumentID==po_number[0],model.Document.idDocumentType==1).one()
            subquery1 = db.query(model.DocumentLineItems.invoice_itemcode).filter_by(documentID=inv_id).distinct().all()
            subquery2 = db.query(model.DocumentLineItems.itemCode).filter_by(documentID=inv_id).distinct().all()
            print(po_doc_id, po_number)
            subquery = db.query(model.DocumentLineItems.lineItemtagID).filter_by(documentID=inv_id).distinct()
            doclinetags = db.query(model.DocumentLineItemTags).options(load_only("TagName")).filter(
                model.DocumentLineItemTags.idDocumentLineItemTags.in_(subquery)).all()
            i = 0
            taglist = ['Description', 'Quantity', 'UnitPrice']

            for row in doclinetags:
                if row.TagName in taglist:
                    itemdata['Result'].append({"tagname": row.TagName, "items": []})
                    # itemdata['Result']['itemcode'].append(({"abc":123}))
                    for row1, row2 in zip(subquery1, subquery2):
                        print(row.TagName, row.idDocumentLineItemTags, row1.invoice_itemcode)
                        linedata = db.query(model.DocumentLineItems, model.DocumentUpdates).options(
                            Load(model.DocumentLineItems).load_only("Value", "isError", "ErrorDesc", "itemCode"),
                            Load(model.DocumentUpdates).load_only("OldValue", "UpdatedOn")).filter(
                            model.DocumentLineItems.invoice_itemcode == row1.invoice_itemcode).filter(
                            model.DocumentLineItems.lineItemtagID == row.idDocumentLineItemTags,
                            model.DocumentLineItems.documentID == inv_id).join(
                            model.DocumentUpdates,
                            model.DocumentUpdates.documentLineItemID == model.DocumentLineItems.idDocumentLineItems,
                            isouter=True).filter(
                            or_(model.DocumentLineItems.IsUpdated == 0, model.DocumentUpdates.IsActive == 1)).all()
                        print("helo1")
                        # ckstatus = db.query(model.DocumentLineItems.CK_status).filter(model.DocumentLineItems.invoice_itemcode == row1.invoice_itemcode,model.DocumentLineItems.lineItemtagID == row.idDocumentLineItemTags,model.DocumentLineItems.documentID == inv_id).all()  
                        print("helo2")
                        ckstatus = 1
                        if row.TagName == "Description":
                            idpolinetag = 5230
                            idgrnlinetag = 513
                        elif row.TagName == "Quantity":
                            idpolinetag = 5218
                            idgrnlinetag = 531
                        elif row.TagName == "UnitPrice":
                            idpolinetag = 5225
                            idgrnlinetag = 613
                        else:
                            idpolinetag = 5225

                        if ckstatus not in [3, 7]:
                            polinedata = db.query(model.DocumentLineItems).options(
                                load_only("Value", "isError")).filter(
                                model.DocumentLineItems.itemCode == row1.invoice_itemcode,
                                model.DocumentLineItems.lineItemtagID == idpolinetag,
                                model.DocumentLineItems.documentID == po_doc_id).all()

                        else:
                            polinedata = []

                        itemdata['Result'][i]['items'].append({"itemcode": row1.invoice_itemcode, "linedetails": [
                            {"invline": linedata, "poline": polinedata}]})
                    i = i + 1

        return {"Vendordata": vendordata, "headerdata": headerdata, "ruledata": rule_data, "all_pos": all_po,
                "linedata": itemdata}

    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV", "BatchexceptionCrud.py readlinedatatest", str(e))
        return Response(status_code=500, headers={"Error": "Server error", "Desc": "Invalid result"})


# to get file path

async def readinvoicefilepath(u_id: int, inv_id: int, db: Session):
    try:
        content_type = "application/pdf"
        invdat = db.query(model.Document).options(
            load_only("docPath", "supplierAccountID", "vendorAccountID")).filter_by(
            idDocument=inv_id).one()

        # check if file path is present and give base64 coded image url
        if invdat.docPath:
            try:
                cust_id = db.query(model.User.customerID).filter_by(idUser=u_id).scalar()
                fr_data = db.query(model.FRConfiguration).options(
                    load_only("ConnectionString", "ContainerName", "ServiceContainerName")).filter_by(
                    idCustomer=cust_id).one()

                # Create the BlobServiceClient object which will be used to create a container client
                blob_service_client = BlobServiceClient.from_connection_string(fr_data.ConnectionString)

                if invdat.supplierAccountID:
                    blob_client = blob_service_client.get_blob_client(container=fr_data.ServiceContainerName,
                                                                      blob=invdat.docPath)
                if invdat.vendorAccountID:
                    blob_client = blob_service_client.get_blob_client(container=fr_data.ContainerName,
                                                                      blob=invdat.docPath)

                # invdat.docPath = str(list(blob_client.download_blob().readall()))
                try:
                    filetype = os.path.splitext(invdat.docPath)[1]
                    if filetype == ".png":
                        content_type = "image/png"
                    elif filetype == ".jpg" or filetype == ".jpeg":
                        content_type = "image/jpg"
                    else:
                        content_type = "application/pdf"
                except:
                    pass
                invdat.docPath = base64.b64encode(blob_client.download_blob().readall())

            except:
                invdat.docPath = f""
        return {"filepath": invdat.docPath, "content_type": content_type}

    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV", "BatchexceptionCrud.py readinvoicefilepath", str(e))
        return Response(status_code=500, headers={"Error": "Server error", "Desc": "Invalid result"})


# to update po number
async def update_po_number(inv_id: int, po_num: str, db: Session):
    try:

        db.query(model.Document).filter_by(idDocument=inv_id).update(
            {"PODocumentID": po_num})

        db.commit()
        return {"result": "success"}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV", "BatchexceptionCrud.py update_po_number", str(e))
        return Response(status_code=500, headers={"Error": "Server error", "Desc": "Invalid result"})


#############################
async def get_all_itemcode(inv_id: int, db: Session):
    try:
        po_number = db.query(model.Document.PODocumentID).filter(model.Document.idDocument == inv_id).one()
        po_doc_id = db.query(model.Document.idDocument).filter(model.Document.PODocumentID == po_number[0],
                                                               model.Document.idDocumentType == 1).one()
        # subquery1 = db.query(model.DocumentLineItems.itemCode).filter_by(documentID=po_doc_id[0]).distinct().all()

        all_description = db.query(model.DocumentLineItems).options(
            load_only("Value", "itemCode")).filter_by(documentID=po_doc_id[0], lineItemtagID=5230).all()
        # all_description = db.query(model.AGIPOLine).options(
        #     load_only("Name","LineNumber")).filter_by(PurchId=po_number[0]).all()

        return {"description": all_description}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV", "BatchexceptionCrud.py get_all_itemcode", str(e))
        return Response(status_code=500, headers={"Error": "Server error", "Desc": "Invalid result"})


async def get_all_errortypes(db: Session):
    try:
        error_type = db.query(model.BatchErrorType).options(
            load_only("name")).all()
        return {"description": error_type}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV", "BatchexceptionCrud.py get_all_errortypes", str(e))
        return Response(status_code=500, headers={"Error": "Server error", "Desc": "Invalid result"})


async def update_line_mapping(inv_id: int, inv_itemcode: str, po_itemcode: str, errotypeid: int, vendoraccountID: int,
                              uid: int, db: Session):
    try:
        present_itemcode = db.query(model.DocumentLineItems.invoice_itemcode).filter_by(
            documentID=inv_id).distinct().all()
        po_itemcode1 = (po_itemcode,)
        # for itemusermap table insert
        model_id = db.query(model.Document.documentModelID).filter_by(idDocument=inv_id).distinct().one()
        descline_id = db.query(model.DocumentLineItemTags.idDocumentLineItemTags).filter_by(idDocumentModel=model_id[0],
                                                                                            TagName='Description').distinct().one()
        po_num = db.query(model.Document.PODocumentID).filter_by(idDocument=inv_id).scalar()
        podoc_id = db.query(model.Document.idDocument).filter_by(idDocumentType=1, PODocumentID=po_num).scalar()
        itemid = db.query(model.DocumentLineItems.invoice_itemcode).filter_by(documentID=podoc_id,
                                                                              itemCode=po_itemcode).distinct().scalar()

        item_metadata_id = db.query(model.ItemMetaData.iditemmetadata).filter_by(itemcode=itemid).distinct().scalar()
        mapped_invoitem_description = db.query(model.DocumentLineItems.Value).filter_by(documentID=inv_id,
                                                                                        itemCode=inv_itemcode,
                                                                                        lineItemtagID=descline_id[
                                                                                            0]).distinct().one()
        # to insert prev itemcode meta data id
        prev_inv_item_code = db.query(model.DocumentLineItems.invoice_itemcode).filter_by(documentID=inv_id,
                                                                                          itemCode=inv_itemcode).distinct().scalar()
        previtemid = db.query(model.DocumentLineItems.invoice_itemcode).filter_by(documentID=podoc_id,
                                                                                  itemCode=prev_inv_item_code).distinct().scalar()

        prev_itemmeta_id = db.query(model.ItemMetaData.iditemmetadata).filter_by(
            itemcode=previtemid).distinct().scalar()
        #    if itemcode is null then insert in itemmetadata       
        if item_metadata_id is None:
            if itemid=='':
                itemcode_generated="SER-"+str(inv_id)+"-"+po_itemcode
            else:
                itemcode_generated=itemid
            poitemdesc2 = db.query(model.DocumentLineItems.Value).filter_by(documentID=podoc_id,lineItemtagID=5230,
                                                                                itemCode=po_itemcode).distinct().scalar()      
            id_item=db.query(model.ItemMetaData.iditemmetadata).filter(model.ItemMetaData.description==poitemdesc2).distinct().scalar()
            db.query(model.ItemUserMap).filter_by(documentID=inv_id, mappedinvoiceitemcode=inv_itemcode).delete()
            db.query(model.ItemUserMap).filter_by(itemmetadataid=id_item).delete()
            db.query(model.ItemMetaData).filter(model.ItemMetaData.iditemmetadata==id_item).delete()
            db.query(model.ItemMetaData).filter(model.ItemMetaData.itemcode==itemcode_generated).delete()
            # db.query(model.ItemMetaData).filter(model.ItemMetaData.description==poitemdesc2).delete()
            db.commit()
            c_item = model.ItemMetaData(itemcode=itemcode_generated, description=poitemdesc2,createdOn=datetime.now(tz_region).strftime("%Y-%m-%d %H:%M:%S"))
            db.add(c_item)
            db.commit()
            item_metadata_id = db.query(model.ItemMetaData.iditemmetadata).filter_by(itemcode=itemcode_generated).distinct().scalar()
        # END
        if po_itemcode1 in present_itemcode:
            item_code1 = db.query(model.DocumentLineItems.itemCode).filter_by(documentID=inv_id,
                                                                              invoice_itemcode=po_itemcode).distinct().one()
            inv_item_code1 = db.query(model.DocumentLineItems.invoice_itemcode).filter_by(documentID=inv_id,
                                                                                          itemCode=inv_itemcode).distinct().one()
            db.query(model.DocumentLineItems).filter_by(documentID=inv_id, itemCode=inv_itemcode).update(
                {"invoice_itemcode": po_itemcode, "Fuzzy_scr": 0})

            db.query(model.ItemUserMap).filter_by(documentID=inv_id, mappedinvoiceitemcode=inv_itemcode).delete()
            db.query(model.ItemUserMap).filter_by(documentID=inv_id, itemmetadataid=item_metadata_id).delete()

            # db.query(model.ItemUserMap).filter_by(documentID=inv_id,mappedinvoiceitemcode=inv_itemcode).update(
            #     {"itemmetadataid": item_metadata_id[0],"mappedinvoiceitemcode":inv_itemcode,"mappedinvoitemdescription":mapped_invoitem_description[0],"batcherrortype":errotypeid,"previousitemmetadataid":prev_itemmeta_id[0],"UserID":uid})
            # db.query(model.ItemUserMap).filter_by(documentID=inv_id,itemmetadataid=item_metadata_id[0]).update(
            #     {"itemmetadataid": item_metadata_id[0],"mappedinvoiceitemcode":inv_itemcode,"mappedinvoitemdescription":mapped_invoitem_description[0],"batcherrortype":errotypeid,"previousitemmetadataid":prev_itemmeta_id[0],"UserID":uid})
            # db.query(model.ItemUserMap).filter_by(documentID=inv_id,itemmetadataid=item_metadata_id[0]).delete()
            db.commit()
            # else:
            c4 = model.ItemUserMap(previousitemmetadataid=prev_itemmeta_id, itemmetadataid=item_metadata_id,
                                   documentID=inv_id, vendoraccountID=vendoraccountID,
                                   mappedinvoiceitemcode=inv_itemcode,
                                   mappedinvoitemdescription=mapped_invoitem_description[0], batcherrortype=errotypeid,
                                   UserID=uid, createdOn=datetime.now(tz_region).strftime("%Y-%m-%d %H:%M:%S"))
            db.add(c4)
            db.query(model.DocumentLineItems).filter_by(documentID=inv_id, itemCode=item_code1[0]).update(
                {"invoice_itemcode": inv_item_code1[0]})


        else:

            db.query(model.DocumentLineItems).filter_by(documentID=inv_id, itemCode=inv_itemcode).update(
                {"invoice_itemcode": po_itemcode, "Fuzzy_scr": 0})
            db.query(model.ItemUserMap).filter_by(documentID=inv_id, mappedinvoiceitemcode=inv_itemcode).delete()
            db.query(model.ItemUserMap).filter_by(documentID=inv_id, itemmetadataid=item_metadata_id).delete()

            # db.query(model.ItemUserMap).filter_by(documentID=inv_id,itemmetadataid=item_metadata_id[0]).delete()
            db.commit()

            # already_present=db.query(model.ItemUserMap.iditemusermap).filter_by(documentID=inv_id,mappedinvoiceitemcode=inv_itemcode).all()     
            # if len(already_present)>0:
            #     db.query(model.ItemUserMap).filter_by(documentID=inv_id,mappedinvoiceitemcode=inv_itemcode).update(
            #         {"itemmetadataid": item_metadata_id[0],"mappedinvoitemdescription":mapped_invoitem_description[0],"batcherrortype":errotypeid,"previousitemmetadataid":prev_itemmeta_id[0],"UserID":uid})
            # else:
            c4 = model.ItemUserMap(previousitemmetadataid=prev_itemmeta_id, itemmetadataid=item_metadata_id,
                                   documentID=inv_id, vendoraccountID=vendoraccountID,
                                   mappedinvoiceitemcode=inv_itemcode,
                                   mappedinvoitemdescription=mapped_invoitem_description[0], batcherrortype=errotypeid,
                                   UserID=uid, createdOn=datetime.now(tz_region).strftime("%Y-%m-%d %H:%M:%S"))
            db.add(c4)
            print("not present")

        db.commit()
        return {"result": "Updated"}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV", "BatchexceptionCrud.py update_line_mapping", str(e))
        return Response(status_code=500, headers={"Error": "Server error", "Desc": "Invalid result"})


async def get_current_itemmapped(inv_id: int, db: Session):
    try:

        item_desc1 = db.query(model.ItemMetaData, model.ItemUserMap).options(
            Load(model.ItemMetaData).load_only("description", "itemcode"),
            Load(model.ItemUserMap).load_only("mappedinvoiceitemcode")).filter(
            model.ItemMetaData.iditemmetadata == model.ItemUserMap.itemmetadataid).filter(
            model.ItemUserMap.documentID == inv_id).all()

        return {"description": item_desc1}
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV", "BatchexceptionCrud.py get_current_itemmapped", str(e))
        return Response(status_code=500, headers={"Error": "Server error", "Desc": "Invalid result"})
