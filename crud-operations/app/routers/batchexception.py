from fastapi import Depends, FastAPI
from fastapi import APIRouter, Depends, Body, status,HTTPException,File, UploadFile
from auth import AuthHandler
from sqlalchemy.orm import Session
from session import Session as SessionLocal
from crud import BatchexceptionCrud as crud
auth_handler = AuthHandler()

router = APIRouter(
    prefix="/apiv1.1/Exception",
    tags=["Exception"],
    dependencies=[Depends(auth_handler.auth_wrapper)],
    responses={404: {"description": "Not found"}},
)
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()



@router.get("/batchprocesssummary/{u_id}")
async def read_batchprocesssummary(u_id: int, db: Session = Depends(get_db)):
    return await crud.readbatchprocessdetails(u_id,db)




@router.get("/Send_to_batch_approval/{u_id}/invoiceid/{inv_id}")
async def send_to_batch_approval(u_id:int,rule_id:int,inv_id:int, db: Session = Depends(get_db)):
    return await crud.send_to_batch_approval(u_id,rule_id,inv_id,db)


@router.get("/Send_to_manual_approval/{u_id}/invoiceid/{inv_id}")
async def send_to_manual_approval(u_id:int,inv_id:int, db: Session = Depends(get_db)):
    return await crud.send_to_manual_approval(u_id,inv_id,db)

    

@router.get("/batchprocesssummaryAdmin/{u_id}")
async def read_batchprocesssummaryAdmin(u_id: int, db: Session = Depends(get_db)):
    return await crud.readbatchprocessdetailsAdmin(u_id,db)


@router.get("/Send_to_batch_approval_Admin/{u_id}/invoiceid/{inv_id}")
async def send_to_batch_approval_Admin(u_id:int,inv_id:int, db: Session = Depends(get_db)):
    return await crud.send_to_batch_approval_Admin(u_id,inv_id,db)

@router.get("/Send_to_manual_approval_Admin/{u_id}/invoiceid/{inv_id}")
async def send_to_manual_approval_Admin(u_id:int,inv_id:int, db: Session = Depends(get_db)):
    return await crud.send_to_manual_approval_Admin(u_id,inv_id,db)

@router.get("/Invokebatchprocesssummary/{u_id}")
async def read_invokebatchummary(u_id: int, db: Session = Depends(get_db)):
    return await crud.readInvokebatchsummary(u_id,db)
    


@router.get("/FinancialApprovalSummary/{u_id}")
async def read_Financialapprovalummary(u_id: int, db: Session = Depends(get_db)):
    return await crud.readfinancialapprovalsummary(u_id,db)


####################################33
@router.get("/testbatchdata/{u_id}")
async def test_batch_data(u_id:int, db: Session = Depends(get_db)):
    return await crud.test_batchdata(u_id,db)


#main api to read line data
@router.get("/testlinedata/{u_id}/invoiceid/{inv_id}")
async def testlinedata(u_id:int,inv_id:int, db: Session = Depends(get_db)):
    return await crud.readlinedatatest(u_id,inv_id,db)


#to read file path
@router.get("/readfilepath/{u_id}/invoiceid/{inv_id}")
async def read_filepath(u_id:int,inv_id:int, db: Session = Depends(get_db)):
    return await crud.readinvoicefilepath(u_id,inv_id,db)

@router.get("/Update_po_number/{inv_id}/po_num/{po_num}")
async def update_PO_number(inv_id:int, po_num:str,db: Session = Depends(get_db)):
    return await crud.update_po_number(inv_id,po_num,db)



#for changing line mapping
@router.get("/get_items/{inv_id}")
async def get_lineitems(inv_id:int,db: Session = Depends(get_db)):
    return await crud.get_all_itemcode(inv_id,db)

@router.get("/get_errortypes")
async def get_ErrorTypes(db: Session = Depends(get_db)):
    return await crud.get_all_errortypes(db)

@router.get("/update_line_mapping/{inv_id}/{inv_itemcode}/{po_item_code}/{errotypeid}/{vendoraccountID}/{uid}")
async def update_lineMapping(inv_id:int,inv_itemcode:str,po_item_code:str,errotypeid:int,vendoraccountID:int,uid:int,db: Session = Depends(get_db)):
    return await crud.update_line_mapping(inv_id,inv_itemcode,po_item_code,errotypeid,vendoraccountID,uid,db)


@router.get("/get_mappeditem/{inv_id}")
async def get_mappeditem(inv_id:int,db: Session = Depends(get_db)):
    return await crud.get_current_itemmapped(inv_id,db)