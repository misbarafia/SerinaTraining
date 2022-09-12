from csv import unix_dialect
from fastapi import Depends, FastAPI, HTTPException, status, APIRouter
from sqlalchemy.orm import Session, session
from typing import Optional, List
import sys
sys.path.append("..")

from crud import notificationCrud as crud
from schemas import notificationsm as schema
import model
from dependency import dependencies
from session import Session as SessionLocal
from session import engine
from auth import AuthHandler

# model.Base.metadata.create_all(bind=engine)
auth_handler = AuthHandler()

router = APIRouter(
    prefix="/apiv1.1/Notification",
    tags=["Notification"],
    dependencies=[Depends(auth_handler.auth_wrapper)],
    responses={404: {"description": "Not found"}},
)

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@router.get("/getNotificationsRecepients/{u_id}/notificationTypeID/{nty_id}/entityID/{ent_id}", status_code=status.HTTP_200_OK)
async def get_notifications_recipients_items(u_id: int, nty_id: int, ent_id: int, db: Session = Depends(get_db)):
    """
    ### API route toget notification templates. It contains the following parameters.
    - u_id: Unique indetifier used to indentify a user
    - db: It provides a session to interact with the backend Database,that is of Session Object Type.
    - return: It returns the result status.
    :return: It returns a json object of notification templates.
    """
    return await crud.get_notifications_recipients(u_id, nty_id, ent_id, db)


@router.get("/markNotification/{u_id}", status_code=status.HTTP_200_OK)
async def mark_notification_items(u_id: int, nt_id: Optional[int]=None, db: Session = Depends(get_db)):
    """
    ### API route to mark a notification as read and removed from notification tab. It contains the following parameters.
    - u_id: Unique indetifier used to indentify a user
    - nt_id:  Unique indetifier used to indentify a notification.
    - db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns a status result.
    """
    return await crud.mark_notifications(u_id, nt_id, db)


@router.post("/resetNotificationTemplate/{u_id}/idPullNotificationTemplate{ntt_id}", status_code=status.HTTP_200_OK)
async def reset_notification_template_item(u_id: int, ntt_id: int, db: Session = Depends(get_db)):
    """
    ### API route to reset the notification template for a user, if default has been replaced with custom template.
    It contains the following parameters.
    - u_id: Unique indetifier used to indentify a user
    - ntt_id: Unique indetifier used to indentify a notification template.
    - db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns a status result.
    """
    return await crud.reset_notification_template(u_id, ntt_id, db)


@router.post("/updateNotificationRecipients/{u_id}/notificationTypeID/{nty_id}/entityID/{ent_id}", status_code=status.HTTP_200_OK)
async def update_notification_recipients_item(u_id: int, nty_id: int, ent_id: int, ntr_bdy: schema.NotificationTemplateRecipients, db: Session = Depends(get_db)):
    """
    ### API route to update an existing custom notification template or to create a custom template for a event.
    It contains the following parameters.
    - u_id: Unique indetifier used to indentify a user
    - ntt_id: Unique indetifier used to indentify a notification template.
    - ntt_bdy: Json body to hold notification template body items.
    - db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns a status result.
    """
    return await crud.update_notification_recipients(u_id, nty_id, ent_id, ntr_bdy, db)


# @router.get("/readTemplateTags/{u_id}", status_code=status.HTTP_200_OK)
# async def get_template_tags_items(u_id: int, db: Session = Depends(get_db)):
#     """
#     ### API route toget notification templates. It contains the following parameters.
#     - u_id: Unique indetifier used to indentify a user
#     - db: It provides a session to interact with the backend Database,that is of Session Object Type.
#     - return: It returns the result status.
#     :return: It returns a json object of notification templates.
#     """
#     return await crud.get_template_tags(u_id, db)


@router.get("/ReadRecipients/{u_id}/entityID/{ent_id}")
async def recipients_items(u_id: int, ent_id: int, db: Session = Depends(get_db)):
    """
    ### API route to get all the recepients for logged in user. It contains the following paramenters.
    - u_id: Unique identifier used to identify a user
    - db: It provides a session to interact with the backend Database, that is of Session Object Type.
    - return: It returns the result status.
    :return: It returns a json object of user id's.
    """
    return await crud.getrecepients(u_id, ent_id, db)


