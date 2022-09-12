from fastapi import APIRouter, Depends, Body, status
from sqlalchemy.orm import scoped_session
# from database import SessionLocal, engine
from typing import Optional
from pydantic import BaseModel
import sys
sys.path.append("..")
from schemas import permissionssm
from crud import summaryCrud
from session import Session
from dependency import dependencies
from auth import AuthHandler

auth_handler = AuthHandler()

router = APIRouter(
    prefix="/apiv1.1/Summary",
    tags=["Summary"],
    dependencies=[Depends(auth_handler.auth_wrapper)],
    responses={404: {"description": "Not found"}},
)


def get_db():
    """
    This function yields a DB session object if the connection is established with the backend DB, takes
    in  no parameter.
    :return: It returns a DB session Object to the calling function.
    """
    db = Session()
    try:
        yield db
    finally:
        db.close()


@router.get("/apiv1.1/invoiceProcessSummary/{u_id}")
async def read_galadhari_summary_item(u_id: int, ftdate: Optional[str] = None, sp_id: Optional[int] =None, fentity: str = None,
                                      db: scoped_session = Depends(get_db)):
    return await summaryCrud.read_galadhari_summary(u_id, ftdate, sp_id, fentity, db)

@router.get("/apiv1.1/pages/{u_id}")
async def read_pages_summary(u_id: int, ftdate: Optional[str] = None, 
endate: Optional[str] = None, 
                                      db: scoped_session = Depends(get_db)):
    return await summaryCrud.read_pages_summary(u_id, ftdate,endate, db)


@router.get("/apiv1.1/EntityFilter/{u_id}")
async def read_entity_filter_item(u_id: int, db: scoped_session = Depends(get_db)):
    return await summaryCrud.read_entity_filter(u_id, db)

@router.get("/apiv1.1/ServiceFilter/{u_id}")
async def read_service_filter_item(u_id: int, db: scoped_session = Depends(get_db)):
    return await summaryCrud.read_service_filter(u_id, db)
