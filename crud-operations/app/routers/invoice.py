from fastapi import Depends, FastAPI, HTTPException, status, APIRouter, BackgroundTasks
from sqlalchemy.orm import Session, session
from typing import Optional, List
from fastapi import File, UploadFile
from fastapi.responses import FileResponse
import sys,os

sys.path.append("..")
from Utilities import pdfcreator,uploadtoblob
from crud import InvoiceCrud as crud
from schemas import InvoiceSchema as schema
import model
from dependency import dependencies
from session import Session as SessionLocal
from session import engine
from auth import AuthHandler

# model.Base.metadata.create_all(bind=engine)
auth_handler = AuthHandler()

router = APIRouter(
    prefix="/apiv1.1/Invoice",
    tags=["invoice"],
    dependencies=[Depends(auth_handler.auth_wrapper)],
    responses={404: {"description": "Not found"}},
)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

    # Delete if not used


# @router.get("/getInvoiceType/{userID}", status_code=status.HTTP_200_OK)
# async def get_invoice_types(userID: int, invoiceTypeID: Optional[int] = None,
#                             skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     """
#     ### API route to get Invoice Types. It contains following parameters.
#     - userID : Unique indetifier used to indentify a user
#     - invoiceTypeID: It is an optional query parameters that is of integer type, it provides unique ID for invoice type. If provided it will fetch details of the given type.
#     - skip: to set an offset value
#     - limit: limits the number of records pulled from the db
#     - db: It provides a session to interact with the backend Database,that is of Session Object Type.
#     - return: It returns the result status.
#     """
#     return await crud.getInvoiceTypes(userID, invoiceTypeID, skip, limit, db)


@router.post("/createInvoiceModel/{u_id}", status_code=status.HTTP_201_CREATED)
async def create_invoice_model(u_id: int, bg_task: BackgroundTasks, invoiceModel: schema.InvoiceModel,
                               tags: schema.tagDefList, db: Session = Depends(get_db)):
    """
    ### API route to create a new Invoice model with associated tag definitions. It contains following parameters.
    - u_id : Unique identifier used to identify a user
    - invoiceModel: It is Body parameter that is of a Pydantic class object, creates member data for creating a new Invoice Model
    - tags: It is Body parameter that is of a Pydantic class object, creates member data for creating a set of tag definitions
    - db: It provides a session to interact with the backend Database,that is of Session Object Type.
    - return: It returns the result status.
    """
    # 2 CRUD operations : create new InvoiceModel ---> add tag definitions
    rsp_create_newModel = crud.createInvoiceModel(u_id, invoiceModel, db)
    if type(rsp_create_newModel) != dict:
        return rsp_create_newModel
    rsp_add_tagDef = crud.addTagDefinition(u_id, tags, db)
    if type(rsp_add_tagDef) != dict:
        return rsp_create_newModel
    return {"result": "created", "records": [rsp_create_newModel, rsp_add_tagDef]}


@router.post("/createInvoice/{u_id}", status_code=status.HTTP_200_OK)
async def create_invoice(u_id: int, bg_task: BackgroundTasks, invoice: schema.NewInvoice,
                         invoiceData: schema.NewInvoiceDataList,
                         invoiceTableDef: schema.TableDef, invoiceLineItems: schema.InvoiceLineItemsList,
                         db: Session = Depends(get_db)):
    """
    ### API route to create a new Invoice with Invoice data. It contains following parameters.
    - u_id : Unique Unique identifier used to identify a user
    - invoice: It is Body parameter that is of a Pydantic class object, creates member data for creating a new Invoice 
    - invoiceData: It is Body parameter that is of a Pydantic class object, creates member data for creating a set of records of Invoice Data
    - invoiceTableDef: It is Body parameter that is of a Pydantic class object, creates member data for creating a table definition
    - invoiceLineItems: It is Body parameter that is of a Pydantic class object, creates member data for creating a set of line items
    - db: It provides a session to interact with the backend Database,that is of Session Object Type.
    - return: It returns the result status.
    ### CRUD Ops:
    1. Creates a New Invoice
    2. Creates and add Invoice Data
    3. Creates table defintion in the invoice
    4. Creates and add table line items
    """
    rsp_create_invoice = crud.createInvoice(u_id, invoice, db)
    invoiceID = dict(rsp_create_invoice)["invoiceID"]
    rsp_create_invoice_data = crud.createInvoiceData(u_id, invoiceID, invoiceData, db)
    rsp_create_invoice_tableDef = crud.createInvoiceTableDef(u_id, invoiceID, invoiceTableDef, db)
    rsp_create_invoice_lineItems = crud.createInvoiceLineItems(u_id, invoiceID, invoiceLineItems, db)

    return await {"result": "created", "records": [rsp_create_invoice, rsp_create_invoice_data,
                                                   rsp_create_invoice_tableDef, rsp_create_invoice_lineItems]}


# uncomment if required or remove it
# @router.put("/updateInvoice/{userID}/Invoices/{invoiceID}",
#             status_code=status.HTTP_200_OK, response_model=schema.ResponseList)
# async def update_invoice_data(userID: int, invoiceID: int, invoiceUpdate: schema.InvoiceUpdate,
#                               invoiceStage: Optional[schema.UpdateInvoiceStage] = None,
#                               invoiceTableDef: Optional[schema.TableDef] = None,
#                               invoiceStatus: Optional[schema.UpdateInvoiceStatus] = None,
#                               lineitem: Optional[schema.InvoiceLineItems] = None,
#                               invoiceDataID: Optional[int] = None, invoiceLineItemID: Optional[int] = None,
#                               db: Session = Depends(get_db)):
#     """
#     <b> API route to update invoice data. It contains following parameters.</b>
#     - userID : Unique indetifier used to indentify a user
#     - invoiceID : Unique indetifier used to indentify a particular invoice in database
#     - invoiceDataID : Unique indetifier used to indentify a particular data field value in an invoice
#     - invoiceLineItemID : Unique indetifier used to indentify a particular line item field value in an invoice
#     - invoiceUpdate : It is Body parameter that is of a Pydantic class object, creates member data for updating invoice data
#     - invoiceStage :  It is Body parameter that is of a Pydantic class object, creates member data for updating invoice stage
#     - invoiceStatus: It is Body parameter that is of a Pydantic class object, creates member data for updating invoice status
#     - db: It provides a session to interact with the backend Database,that is of Session Object Type.
#     - return: It returns the result status.
#     ### CRUD Ops:
#     1. Creates an invoice update
#     2. Update Invoice Stage
#     3. Update Invoice status
#     4. Update invoice table defintion
#     5. Update Invoice line items
#     """
#     rsp_list = []
#     rsp_create_invoiceupdate = crud.createInvoiceUpdate(userID, invoiceDataID, invoiceLineItemID, invoiceUpdate, db)
#     rsp_list.append(rsp_create_invoiceupdate)
#     if invoiceStage:
#         rsp_update_stage = crud.updateInvoiceStage(userID, invoiceDataID, invoiceStage, db)
#         rsp_list.append(rsp_update_stage)
#     if invoiceStatus:
#         rsp_update_status = crud.updateInvoiceStatus(userID, invoiceID, invoiceStatus, db)
#         rsp_list.append(rsp_update_status)
#     if invoiceTableDef:
#         rsp_update_tabledef = crud.updateInvoiceTableDef(userID, invoiceID, invoiceTableDef, db)
#         rsp_list.append(rsp_update_tabledef)
#     if lineitem:
#         rsp_update_lineitem = crud.updateInvoiceLineItemTags(userID, invoiceID, lineitem, db)
#         rsp_list.append(rsp_update_lineitem)
#     return await {"result": "created", "records": rsp_list}


##########################################################################################################
#Code to be Written by Misbah Khanum
@router.get("/readDocumentPOList/{u_id}")
async def read_doc_po_list_item(u_id: int,
                                db: Session = Depends(get_db)):
    """
    ### API route to read the PO Documents. It contains following parameters.
    :param u_id : Unique Unique identifier used to identify a user.
    :param sp_id: It is an optional parameter for filtering doc based on service provider id, of int type.
    :param ven_id: It is an optional parameter for filtering doc based on vendor id, of int type.
    :param usertype: It is a dependent function which returns type of the user.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns PO document list.
    """
    return "success"
    
#Code to be Written by Harshitha
@router.get("/readDocumentINVList/{u_id}")
async def read_doc_inv_list_item(u_id: int,
                                 db: Session = Depends(get_db)):
    """
    ### API route to read the Invoice Documents. It contains following parameters.
    :param u_id: Unique Unique identifier used to identify a user.
    :param sp_id: It is an optional parameter for filtering doc based on service provider id, of int type.
    :param ven_id: It is an optional parameter for filtering doc based on vendor id, of int type.
    :param usertype: It is a dependent function which returns type of the user.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns Invoice document list.
    """
    return "success"

@router.get("/readDocumentARCList/{u_id}")
async def read_doc_inv_list_item(u_id: int, ven_id: Optional[int] = None,
                                 usertype: int = Depends(dependencies.check_usertype),
                                 db: Session = Depends(get_db)):
    """
    ### API route to read the Invoice Documents. It contains following parameters.
    :param u_id: Unique Unique identifier used to identify a user.
    :param sp_id: It is an optional parameter for filtering doc based on service provider id, of int type.
    :param ven_id: It is an optional parameter for filtering doc based on vendor id, of int type.
    :param usertype: It is a dependent function which returns type of the user.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns Invoice document list.
    """
    data = {}
    if usertype == 1:
        data["ser"] = await crud.read_doc_inv_arc_list(u_id, None, ven_id, usertype, "ser", db)
    data["ven"] =await crud.read_doc_inv_arc_list(u_id, None, ven_id, usertype, "ven", db)
    return {"result": data}

#Code to be Written by Nandini T
@router.get("/readDocumentRejectList/{u_id}")
async def read_doc_inv_list_item(u_id: int,
                                 db: Session = Depends(get_db)):
    """
    ### API route to read the Invoice Documents. It contains following parameters.
    :param u_id: Unique Unique identifier used to identify a user.
    :param sp_id: It is an optional parameter for filtering doc based on service provider id, of int type.
    :param ven_id: It is an optional parameter for filtering doc based on vendor id, of int type.
    :param usertype: It is a dependent function which returns type of the user.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns Invoice document list.
    """
    return "success"


@router.get("/readDocumentGRNException/{u_id}")
async def read_doc_grn_exception_list_item(u_id: int,
                                 usertype: int = Depends(dependencies.check_usertype),
                                 db: Session = Depends(get_db)):
    """
    ### API route to read the Invoice Documents. It contains following parameters.
    :param u_id: Unique Unique identifier used to identify a user.
    :param sp_id: It is an optional parameter for filtering doc based on service provider id, of int type.
    :param ven_id: It is an optional parameter for filtering doc based on vendor id, of int type.
    :param usertype: It is a dependent function which returns type of the user.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns Invoice document list.
    """
    data = await crud.read_doc_grn_exception_list(u_id, usertype, db)
    return {"result": data}


@router.get("/readDocumentINVListService/{u_id}")
async def read_doc_inv_list_item(u_id: int, sp_id: Optional[int] = None,
                                 usertype: int = Depends(dependencies.check_usertype),
                                 db: Session = Depends(get_db)):
    """
    ### API route to read the Invoice Documents. It contains following parameters.
    :param u_id: Unique Unique identifier used to identify a user.
    :param sp_id: It is an optional parameter for filtering doc based on service provider id, of int type.
    :param ven_id: It is an optional parameter for filtering doc based on vendor id, of int type.
    :param usertype: It is a dependent function which returns type of the user.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns Invoice document list.
    """
    return await crud.read_doc_inv_list(u_id, sp_id, None, usertype, "ser", db)

#Code to be Written by Neha Kouser
@router.get("/readDocumentGRNList/{u_id}")
async def read_doc_grn_list_item(u_id: int,
                                 db: Session = Depends(get_db)):
    """
    ### API route to read the GRN Documents. It contains following parameters.
    :param u_id: Unique Unique identifier used to identify a user.
    :param sp_id: It is an optional parameter for filtering doc based on service provider id, of int type.
    :param ven_id: It is an optional parameter for filtering doc based on vendor id, of int type.
    :param usertype: It is a dependent function which returns type of the user.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns GRN document list.
    """
    return "success"

@router.get("/readInvoiceData/{u_id}/idInvoice/{inv_id}")
async def read_invoice_data_item(u_id: int, inv_id: int, db: Session = Depends(get_db)):
    """
    ### API route to read Document data. It contains following parameters.
    :param u_id: Unique Unique identifier used to identify a user.
    :param inv_id: It is an path parameter for selecting document id to return its data, it is of int type.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns the Document data [header details, line details, base64pdf string].
    """
    return await crud.read_invoice_data(u_id, inv_id, db)


@router.get("/readInvoiceFile/{u_id}/idInvoice/{inv_id}")
async def read_invoice_file_item(u_id: int, inv_id: int, db: Session = Depends(get_db)):
    """
    ### API route to read Document data. It contains following parameters.
    :param u_id: Unique Unique identifier used to identify a user.
    :param inv_id: It is an path parameter for selecting document id to return its data, it is of int type.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns the Document data [header details, line details, base64pdf string].
    """
    return await crud.read_invoice_file(u_id, inv_id, db)


@router.get("/readPOData/{u_id}/idInvoice/{inv_id}")
async def read_po_data_item(u_id: int, inv_id: int, db: Session = Depends(get_db)):
    """
    ### API route to read PO data for invoice upload. It contains following parameters.
    :param u_id: Unique Unique identifier used to identify a user.
    :param inv_id: It is an path parameter for selecting document id to return its data, it is of int type.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns the Document data [header details, line details, base64pdf string].
    """
    return await crud.read_po_data(u_id, inv_id, db)


@router.post("/updateInvoiceData/{u_id}/idInvoice/{inv_id}")
async def update_invoice_data_item(u_id: int, inv_id: int, inv_data: List[schema.UpdateServiceAccountInvoiceData],
                                   db: Session = Depends(get_db)):
    """
    ### API route to update Document data. It contains following parameters.
    :param u_id: Unique Unique identifier used to identify a user.
    :param inv_id: It is an path parameter for selecting document id to return its data, it is of int type.
    :param inv_data: It is Body parameter that is of a Pydantic class object, holds list of updated invoice data for
    updating.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It return flag result [success or failed]
    """
    return await crud.update_invoice_data(u_id, inv_id, inv_data, db)


@router.post("/updateColumnPos/{u_id}/tabname/{tabtype}")
async def update_column_pos_item(u_id: int, bg_task: BackgroundTasks, tabtype: str, col_data: List[schema.columnpos],
                                 db: Session = Depends(get_db)):
    """
    ### API route to update column position of a user. It contains following parameters.
    :param u_id: Unique Unique identifier used to identify a user.
    :param tabtype: It is an path parameter for selecting the tab, it is of string type.
    :param col_data: It is Body parameter that is of a Pydantic class object, hold list of column position for updating
    the tab.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It return flag result [success or failed]
    """
    return await crud.update_column_pos(u_id, tabtype, col_data, bg_task, db)


@router.get("/resetColumnPos/{u_id}/tabname/{tabtype}")
async def reset_column_pos_item(u_id: int, bg_task: BackgroundTasks, tabtype: str, db: Session = Depends(get_db)):
    """
    ### API route to reset column position of a user. It contains following parameters.
    :param u_id: Unique Unique identifier used to identify a user.
    :param tabtype: It is an path parameter for selecting the tab, it is of string type.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It return flag result [success or failed]
    """
    return await crud.reset_column_pos(u_id, tabtype, bg_task, db)


@router.get("/readColumnPos/{u_id}/tabname/{tabtype}")
async def read_column_pos_item(u_id: int, tabtype: str, db: Session = Depends(get_db)):
    """
    ### API route to read column position of a user. It contains following parameters.
    :param u_id: Unique Unique identifier used to identify a user.
    :param tabtype: It is an path parameter for selecting the tab, it is of string type.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It return the column position data for a tab.
    """
    return await crud.read_column_pos(u_id, tabtype, db)


@router.get("/readInvoiceList/{u_id}/edited", dependencies=[Depends(dependencies.check_user_access_customer)])
async def read_invoice_list_edited_item(u_id: int, db: Session = Depends(get_db)):
    """
    ### API route to read Invoice documents for edited tab of a user. It contains following parameters.
    :param u_id: Unique Unique identifier used to identify a user.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns the Edited Tab Invoice documents for a user.
    """
    return await crud.read_vendor_invoice_list_edited(u_id, db)


@router.get("/readInvoiceListService/{u_id}/edited", dependencies=[Depends(dependencies.check_user_access_customer)])
async def read_invoice_list_edited_item(u_id: int, db: Session = Depends(get_db)):
    """
    ### API route to read Invoice documents for edited tab of a user. It contains following parameters.
    :param u_id: Unique Unique identifier used to identify a user.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns the Edited Tab Invoice documents for a user.
    """
    return await crud.read_service_invoice_list_edited(u_id, db)


@router.get("/readInvoiceList/{u_id}/approved")
async def read_invoice_list_approved_item(u_id: int, usertype: int = Depends(dependencies.check_usertype),
                                          db: Session = Depends(get_db)):
    """
    ### API route to read Invoice documents for approved tab of a user. It contains following parameters.
    :param u_id: Unique Unique identifier used to identify a user.
    :param usertype: It is a dependent function which returns type of the user.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns the approved Tab Invoice documents for a user.
    """
    return await crud.read_invoice_list_approved(u_id, usertype, "ven", db)


@router.get("/readInvoiceListService/{u_id}/approved")
async def read_invoice_list_approved_item(u_id: int, usertype: int = Depends(dependencies.check_usertype),
                                          db: Session = Depends(get_db)):
    """
    ### API route to read Invoice documents for approved tab of a user. It contains following parameters.
    :param u_id: Unique Unique identifier used to identify a user.
    :param usertype: It is a dependent function which returns type of the user.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns the approved Tab Invoice documents for a user.
    """
    return await crud.read_invoice_list_approved(u_id, usertype, "ser", db)


@router.get("/readInvoiceList/{u_id}/vendor/{ven_id}")
async def read_invoice_list_vendor_item(u_id: int, ven_id: int, db: Session = Depends(get_db)):
    """
    ### API route to read Invoice documents for vendor tab of a user. It contains following parameters.
    :param u_id: u_id: Unique Unique identifier used to identify a user.
    :param ven_id: It is an optional parameter for filtering doc based on vendor id, of int type.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return:
    """
    return await crud.read_invoice_list_vendor(u_id, ven_id, db)


@router.get("/readInvoiceList/{u_id}/serviceprovider/{sp_id}")
async def read_invoice_list_serviceprovider_item(u_id: int, sp_id: int, db: Session = Depends(get_db)):
    """
    ### API route to read Invoice documents for service provider tab of a user. It contains following parameters.
    :param u_id: u_id: Unique Unique identifier used to identify a user.
    :param sp_id: It is an optional parameter for filtering doc based on service provider id, of int type.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return:
    """
    return await crud.read_invoice_list_serviceprovider(u_id, sp_id, db)


@router.get("/readGRNReadyInvoiceList/{u_id}")
async def read_invoice_grn_ready_item(u_id: int, db: Session = Depends(get_db)):
    """
    ### API route to rea Invoice documents for service provider tab of a user. It contains following parameters.
    :param u_id: u_id: Unique Unique identifier used to identify a user.
    :param sp_id: It is an optional parameter for filtering doc based on service provider id, of int type.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return:
    """
    return await crud.read_invoice_grn_ready(u_id, db)


@router.get("/readGRNReadyInvoiceData/{u_id}")
async def read_invoice_grn_ready_data_item(u_id: int, inv_id: int, db: Session = Depends(get_db)):
    """
    ### API route to rea Invoice documents for service provider tab of a user. It contains following parameters.
    :param u_id: u_id: Unique Unique identifier used to identify a user.
    :param sp_id: It is an optional parameter for filtering doc based on service provider id, of int type.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return:
    """
    return await crud.read_invoice_grn_ready_data(u_id, inv_id, db)


@router.post("/saveCustomGRNData/{u_id}")
async def save_invoice_grn_data_item(u_id: int, inv_id: int, submit_type: bool, grn_data: List[schema.GrnData],
                                     bg_task: BackgroundTasks, db: Session = Depends(get_db)):
    """
    ### API route to rea Invoice documents for service provider tab of a user. It contains following parameters.
    :param u_id: u_id: Unique Unique identifier used to identify a user.
    :param sp_id: It is an optional parameter for filtering doc based on service provider id, of int type.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return:
    """
    return await crud.save_invoice_grn_data(u_id, inv_id, submit_type, grn_data, bg_task, db)


@router.get("/assignInvoice/{u_id}/idInvoice/{inv_id}",
            dependencies=[Depends(dependencies.check_invoice_entity_user)])
async def assign_invoice_to_user_item(u_id: int, bg_task: BackgroundTasks, inv_id: int,
                                      db: Session = Depends(get_db)):
    """
    ### API route to assign Invoice document to a user. It contains following parameters.
    :param u_id: u_id: Unique Unique identifier used to identify a user.
    :param inv_id: It is an path parameter for selecting document id to return its data, it is of int type.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return:
    """
    return await crud.assign_invoice_to_user(u_id, inv_id, bg_task, db)


@router.post("/submitInvoice/{u_id}/idInvoice/{inv_id}",
             dependencies=[Depends(dependencies.check_eidt_invoice_permission)])
async def update_invoice_item(u_id: int, bg_task: BackgroundTasks, inv_id: int, dochist: schema.DocHistoryLog,
                              db: Session = Depends(get_db)):
    """
    ### API route to submit edited  Invoice document for Review. It contains following parameters.
    :param u_id: u_id: Unique Unique identifier used to identify a user.
    :param inv_id: It is an path parameter for selecting document id to return its data, it is of int type.
    :param dochist: It is Body parameter that is of a Pydantic class object, holds description for the update.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return:
    """
    return await crud.submit_invoice(u_id, inv_id, dict(dochist), bg_task, db)


@router.post("/approveEditInvoice/{u_id}/idInvoice/{inv_id}",
             dependencies=[Depends(dependencies.check_eidt_invoice_approve_permission)])
async def approve_invoice_item(u_id: int, bg_task: BackgroundTasks, inv_id: int, dochist: schema.DocHistoryLog,
                               db: Session = Depends(get_db)):
    """
    ### API route to approve edited Invoice document for Review. It contains following parameters.
    :param u_id: u_id: Unique Unique identifier used to identify a user.
    :param inv_id: It is an path parameter for selecting document id to return its data, it is of int type.
    :param dochist: It is Body parameter that is of a Pydantic class object, holds description for the update.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It return flag result [success or failed]
    """
    return await crud.approve_invoice(u_id, inv_id, dict(dochist), bg_task, db)


@router.post("/rejectIT/{u_id}/idInvoice/{inv_id}",
             dependencies=[Depends(dependencies.check_eidt_invoice_permission)])
async def reject_invoice_it_item(u_id: int, bg_task: BackgroundTasks, inv_id: int, dochist: schema.DocHistoryLog,
                                 db: Session = Depends(get_db)):
    """
    ### API route to reject Invoice document to it or vendor. It contains following parameters.
    :param u_id: u_id: Unique Unique identifier used to identify a user.
    :param inv_id: It is an path parameter for selecting document id to return its data, it is of int type.
    :param dochist: It is Body parameter that is of a Pydantic class object, holds description for the update.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It return flag result [success or failed]
    """
    return await crud.reject_invoice_it(u_id, inv_id, dict(dochist), bg_task, db)


@router.post("/rejectVendor/{u_id}/idInvoice/{inv_id}",
             dependencies=[Depends(dependencies.check_eidt_invoice_permission)])
async def reject_invoice_ven_item(u_id: int, bg_task: BackgroundTasks, inv_id: int, dochist: schema.DocHistoryLog,
                                  db: Session = Depends(get_db)):
    """
    ### API route to reject Invoice document to it or vendor. It contains following parameters.
    :param u_id: u_id: Unique Unique identifier used to identify a user.
    :param inv_id: It is an path parameter for selecting document id to return its data, it is of int type.
    :param dochist: It is Body parameter that is of a Pydantic class object, holds description for the update.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It return flag result [success or failed]
    """
    return await crud.reject_invoice_ven(u_id, inv_id, dict(dochist), bg_task, db)


@router.get("/readInvoicePaymentStatus/{u_id}")
async def read_invoice_payment_status_item(u_id: int, usertype: int = Depends(dependencies.check_usertype),
                                           db: Session = Depends(get_db)):
    """
    ### API route to read Invoice document payment status. It contains following parameters.
    :param u_id: u_id: Unique Unique identifier used to identify a user.
    :param usertype: It is a dependent function which returns type of the user.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns Invoice document payment status [not payed, partially payed, completely payed].
    """
    return await crud.read_invoice_payment_status(u_id, usertype, db)


@router.get("/readVendorRejectedInvoice/{u_id}")
async def read_vendor_rejected_invoices_item(u_id: int, usertype: int = Depends(dependencies.check_usertype),
                                             db: Session = Depends(get_db)):
    """
    ### API route to read rejected Invoice document for Vendor Queue. It contains following parameters.
    :param u_id: u_id: Unique Unique identifier used to identify a user.
    :param usertype: It is a dependent function which returns type of the user.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns Invoice document rejected by customer to vendor.
    """
    return await crud.read_vendor_rejected_invoices(u_id, usertype, db)


@router.get("/readVendorPendingInvoice/{u_id}")
async def read_status_pending_invoices_item(u_id: int, usertype: int = Depends(dependencies.check_usertype),
                                            db: Session = Depends(get_db)):
    """
    ### API route to read Invoice document pending by customer cycle to be approved, vendor related. It contains following
    parameters.
    :param u_id: u_id: Unique Unique identifier used to identify a user.
    :param usertype: It is a dependent function which returns type of the user.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns Invoice document yet to be approved by customer.
    """
    return await crud.read_pending_invoices(u_id, usertype, db)


@router.get("/readVendorApprovedInvoice/{u_id}")
async def read_vendor_approved_invoices_item(u_id: int, usertype: int = Depends(dependencies.check_usertype),
                                             db: Session = Depends(get_db)):
    """
    ### API route to read Invoice document approved by customer, vendor related. It contains following
    parameters.
    :param u_id: u_id: Unique Unique identifier used to identify a user.
    :param usertype: It is a dependent function which returns type of the user.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns Invoice document approved by customer.
    """
    return await crud.read_vendor_approved_invoices(u_id, usertype, db)


@router.get("/readInvoiceStatusHistory/{u_id}/idInvoice/{inv_id}")
async def read_invoice_status_history_item(u_id: int, inv_id: int,
                                           db: Session = Depends(get_db)):
    """
    ### API route to read Invoice document Status History. It contains following parameters.
    :param u_id: u_id: Unique Unique identifier used to identify a user.
    :param inv_id: It is an path parameter for selecting document id to return its data, it is of int type.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns Invoice document status history.
    """
    return await crud.read_invoice_status_history(u_id, inv_id, db)


@router.post("/uploadMasterItemMapping/{u_id}")
async def upload_mater_item_mapping(u_id: int, bg_task: BackgroundTasks, file: UploadFile = File(...),
                                    db: Session = Depends(get_db)):
    """
    ### API route to read Invoice document Status History. It contains following parameters.
    :param u_id: u_id: Unique Unique identifier used to identify a user.
    :param inv_id: It is an path parameter for selecting document id to return its data, it is of int type.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns Invoice document status history.
    """
    return await crud.upload_mater_item_mapping(u_id, file, bg_task, db)


@router.get("/readItemMetaStatus/{u_id}")
async def read_item_master_status(u_id: int,
                                  db: Session = Depends(get_db)):
    """
    ### API route to read Invoice document Status History. It contains following parameters.
    :param u_id: u_id: Unique Unique identifier used to identify a user.
    :param inv_id: It is an path parameter for selecting document id to return its data, it is of int type.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns Invoice document status history.
    """
    return await crud.read_item_master_status(u_id, db)


@router.get("/downloadItemMasterErrorRecords/{u_id}")
async def download_item_master_error(u_id: int, item_history_id: int,
                                     db: Session = Depends(get_db)):
    """
    ### API route to read Invoice document Status History. It contains following parameters.
    :param u_id: u_id: Unique Unique identifier used to identify a user.
    :param inv_id: It is an path parameter for selecting document id to return its data, it is of int type.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns Invoice document status history.
    """
    return await crud.download_item_master_error(u_id, item_history_id, db)


@router.get("/getDocumentLockInfo/{u_id}/idDocument/{inv_id}")
async def read_document_lock_status(u_id: int, inv_id: int,
                                     db: Session = Depends(get_db)):
    """
    ### API route to read Invoice document Status History. It contains following parameters.
    :param u_id: u_id: Unique Unique identifier used to identify a user.
    :param inv_id: It is an path parameter for selecting document id to return its data, it is of int type.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns Invoice document status history.
    """
    return await crud.read_document_lock_statu(u_id, inv_id, db)


@router.post("/updateDocumentLockInfo/{u_id}/idDocument/{inv_id}")
async def update_document_lock_status(u_id: int, inv_id: int, session_datetime:schema.SessionTime,
                                     db: Session = Depends(get_db)):
    """
    ### API route to read Invoice document Status History. It contains following parameters.
    :param u_id: u_id: Unique Unique identifier used to identify a user.
    :param inv_id: It is an path parameter for selecting document id to return its data, it is of int type.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns Invoice document status history.
    """
    return await crud.update_document_lock_statu(u_id, inv_id, session_datetime, db)


@router.get("/readItemMetaData/{u_id}")
async def read_item_master_items(u_id: int, ven_acc_id: int,
                                  db: Session = Depends(get_db)):
    """
    ### API route to read Invoice document Status History. It contains following parameters.
    :param u_id: u_id: Unique Unique identifier used to identify a user.
    :param inv_id: It is an path parameter for selecting document id to return its data, it is of int type.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns Invoice document status history.
    """
    return await crud.read_item_master_items(u_id, ven_acc_id, db)

@router.delete("/deleteLineItem/{docid}/{item_code}")
async def deletelineitem(docid: int, item_code: int,db: Session = Depends(get_db)):
    """
    ### API route to delete junk line items. It contains following parameters.
    :param docid: It is an path parameter for selecting document id to return its data, it is of int type.
    :param item_code: Line item number, it is of int type.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns deleted info.
    """
    return await crud.deletelineitem(docid,item_code,db)  

@router.post("/createLineItem")
async def createLineItem(docinput: schema.DocLineItems,db: Session = Depends(get_db)):
    """
    ### API route to add new line items. It contains following parameters.
    :body documentID: It document id to add line item to, it is of int type.
    :body itemCode: Line item number, it is of int type.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns added info.
    """
    return await crud.addLineItem(docinput,db)

@router.get("/checkLineItemExists/{docid}/{item_code}")
async def checklineitemcode(docid: int, item_code: int,db: Session = Depends(get_db)):
    """
    ### API route to check line item code before adding. It contains following parameters.
    :param docid: It is an path parameter for selecting document id to return its data, it is of int type.
    :param item_code: Line item number, it is of int type.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns exists or not exists.
    """
    return await crud.checklineitemcode(docid,item_code,db)    

@router.get("/journeydoc/docid/{inv_id}")
async def download_journeydoc(inv_id: int,db: Session = Depends(get_db)):
    """
    ### API route to download journey document. It contains following parameters.
    :param inv_id: It is an path parameter for selecting document id to return its data, it is of int type.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: journey doc as pdf.
    """
    for f in os.listdir():
        if os.path.isfile(f) and f.endswith(".pdf"):
            os.unlink(f)
    all_status = await crud.read_doc_history(inv_id,db)
    doc_data = await crud.read_doc_data(inv_id,db)
    filename = pdfcreator.createdoc(all_status,doc_data,inv_id)
    with open(filename,'rb') as file:
        file_content = file.read()
        uploadtoblob.upload_to_blob(filename,file_content,db)
    return FileResponse(path=filename, filename=filename, media_type='application/pdf')