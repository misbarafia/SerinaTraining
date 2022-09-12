import traceback
from fastapi import Depends, APIRouter, FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import json
import random
from datetime import datetime, timedelta
import pytz as tz
from sqlalchemy.orm import load_only, Load
import jwt
from fastapi.responses import Response
import sys
import os

endpoint_site = os.getenv('Endpoint_Site', default="https://rovedev.serinaplus.com/")
sys.path.append("..")
from auth import AuthHandler
from schemas.authSchema import AuthDetails, Token, ActivationBody
from session import Session as SessionLocal
import model
from session.notificationsession import client as mqtt

router = APIRouter(
    prefix="/apiv1.1",
    tags=["Login"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


auth_handler = AuthHandler()
tz_region_name = os.getenv("serina_tz", "Asia/Dubai")
tz_region = tz.timezone(tz_region_name)


def getuserdetails(username, db):
    """
    ### Function to fetch the details of the user performing log in
    :param username: It is a string parameter for providing username
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns the user data
    """
    try:
        data = db.query(model.User, model.Credentials, model.AccessPermission.idAccessPermission,
                        model.AccessPermissionDef, model.AmountApproveLevel).options(
            Load(model.User).load_only("firstName", "lastName", "isActive", "email"),
            Load(model.AccessPermissionDef).load_only("NameOfRole", "Priority", "User", "Permissions", "isUserRole",
                                                      "AccessPermissionTypeId", "allowBatchTrigger", "is_epa",
                                                      "allowServiceTrigger", "isDashboard", "NewInvoice",
                                                      "isConfigPortal", "is_gpa", "is_vspa", "is_spa"),
            Load(model.Credentials).load_only("LogSecret", "crentialTypeId")).filter(
            model.User.idUser == model.Credentials.userID).filter(
            model.Credentials.crentialTypeId.in_((1, 2))).filter(model.Credentials.LogName == username).join(
            model.AccessPermission, model.AccessPermission.userID == model.User.idUser, isouter=True).join(
            model.AccessPermissionDef,
            model.AccessPermissionDef.idAccessPermissionDef == model.AccessPermission.permissionDefID).join(
            model.AmountApproveLevel,
            model.AmountApproveLevel.idAmountApproveLevel == model.AccessPermissionDef.amountApprovalID, isouter=True)
        return data.all()
    except:
        print(traceback.print_exc())
    finally:
        db.close()


@router.post('/login')
def login(auth_details: AuthDetails, db: Session = Depends(get_db)):
    """
    ### API route to login and get access token. It contains following parameters.
    :param auth_details: It is a Form object, that provides user details [username, password].
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns the token and user details if login successful.
    """
    try:
        userdetails = getuserdetails(auth_details.username, db)
        # Authenticating
        if not userdetails or (not auth_handler.verify_password(auth_details.password, userdetails[0][1].LogSecret)):
            return Response(status_code=401, headers={"Error": f"Invalid username and/or password"})
        token = auth_handler.encode_token(auth_details.username)
        # check the user type and provide a key pair for diverting to respective portals
        if userdetails[0][1].crentialTypeId == 1:
            user_type = "customer_portal"
        else:
            user_type = "vendor_portal"
        # if isActive 0 then request user to active account.
        if userdetails[0][0].isActive == 0:
            return Response(status_code=401, headers={"Error": "Please activate your user account"})
        # get last login
        lastlogin = db.query(model.Credentials.lastloginDate).filter_by(userID=userdetails[0][0].idUser).filter(
            model.Credentials.crentialTypeId.in_((1, 2))).scalar()
        # logging info
        data = {"lastloginDate": datetime.now(tz_region).strftime("%Y-%m-%d %H:%M:%S")}
        db.query(model.Credentials).filter_by(userID=userdetails[0][0].idUser).update(data)
        db.commit()
        try:
            mqtt.publish("notification_re_sender", json.dumps({"user_id": userdetails[0][0].idUser}), qos=0)
        except Exception as e:
            print("notification exception", e)
        return {"token": token, "userdetails": userdetails[0][0], "permissioninfo": userdetails[0][3],
                "amountapproval": userdetails[0][4], "user_type": user_type, "last_login": lastlogin}
    except:
        return Response(status_code=401, headers={"Error": "Invalid username and/or password"})


@router.post("/newUserActivation")
async def activateuser(activatebody: ActivationBody, db: Session = Depends(get_db)):
    """
    ### API route to perform user activation. It contains following parameters.
    :param activatebody: It is a Object encoded by JWT, that provides user details.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It return Flag [Account Activated]
    """
    try:
        activatebody = dict(activatebody)
        data = jwt.decode(activatebody["activation_code"], "9joxN0XD3jyowKdMALUO1ayOWve9bdS1", algorithms=["HS256"])
        # d1 encoded date, d2 utc now date
        d1 = datetime.strptime(data["exp_date"], "%Y-%m-%d")
        d2 = datetime.strptime(datetime.now(tz_region).strftime("%Y-%m-%d"), "%Y-%m-%d")
        if d2 <= d1:
            # check if the code was already used to activate account
            state = db.query(model.User.isActive).filter_by(idUser=data["idUser"]).scalar()
            if state:
                return Response(status_code=400, headers={"error": "Code Already used"})
            auth_handler = AuthHandler()
            db.query(model.User).filter_by(idUser=data["idUser"]).update({"isActive": 1})
            db.query(model.Credentials).filter_by(userID=data["idUser"]).update(
                {"LogSecret": auth_handler.get_password_hash(activatebody["password"])})
            # check if the user column config is already present
            uid = db.query(model.DocumentColumnPos.userID).filter_by(userID=data["idUser"]).distinct().scalar()
            if not uid:
                db.execute(f"CALL userdefaultdoccol({data['idUser']}, @docresult)")
            db.commit()
        # mqtt.publish("notification_processor", "")
        return {"result": "Account Activated"}
    except Exception as e:
        print(traceback.print_exc())
        return Response(status_code=500, headers={"Error": "Server error"})
    finally:
        db.close()


@router.get("/resetPassword/")
async def passwordreset(email: str, db: Session = Depends(get_db)):
    """
    ### API route to start password reset. It contains following parameters.
    :param email: It is a string parameter against which the account reset mail is sent.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: it returns a flag [sent mail].
    """
    try:
        userdetails = db.query(model.User).options(load_only("isActive")).filter_by(
            email=email).distinct().one()
        if userdetails.isActive == 0:
            return Response(status_code=401, headers={"Error": f"Please activate your user account"})
        userdetails.username = db.query(model.Credentials.LogName).filter_by(
            userID=userdetails.idUser).filter(model.Credentials.crentialTypeId.in_((1, 2))).scalar()
        userdetails = userdetails.__dict__
        userdetails.pop("_sa_instance_state")
        otp_code = random.randrange(111111, 999999)
        userdetails["otp_code"] = otp_code
        exp_date = datetime.now(tz_region) + timedelta(days=1)
        exp_date = exp_date.strftime("%Y-%m-%d")
        data = model.Otp_Code(password_otpcolcode=otp_code, password_otp_userid=userdetails["idUser"], expDate=exp_date)
        db.add(data)
        db.commit()
        cust_id = db.query(model.User.customerID).filter_by(email=email).scalar()
        details = {"user_id": None, "trigger_code": 8017, "cust_id": cust_id, "inv_id": None,
                   "additional_details": {"recipients": email, "otp_code": otp_code, "subject": "Password Reset OTP",
                                          "user_details": userdetails}}
        mqtt.publish("notification_processor", json.dumps(details))
        return {"result": "successful"}
    except Exception as e:
        print(traceback.print_exc())
        return Response(status_code=500, headers={"Error": "Server error"})
    finally:
        db.close()


@router.post("/setPassword/")
async def setpassword(activatebody: ActivationBody, db: Session = Depends(get_db)):
    """
    ### API route to set new password. It contains following parameters.
    :param activatebody:It is a object encoded by jWT.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It returns a flag [successful].
    """
    try:
        activatebody = activatebody.__dict__
        data = db.query(model.Otp_Code).filter_by(password_otpcolcode=activatebody["activation_code"]).scalar()
        # d1 encoded date, d2 utc now date
        data = data.__dict__
        d1 = data["expDate"]
        d2 = datetime.strptime(datetime.now(tz_region).strftime("%Y-%m-%d"), "%Y-%m-%d")
        if d2 <= d1:
            auth_handler = AuthHandler()
            db.query(model.Credentials).filter_by(userID=data["password_otp_userid"]).update(
                {"LogSecret": auth_handler.get_password_hash(activatebody["password"])})
            db.query(model.Otp_Code).filter_by(idpassword_otp=data["idpassword_otp"]).delete()
            db.commit()
            return {"result": "successful"}
        else:
            db.query(model.Otp_Code).filter_by(idpassword_otp=data["idpassword_otp"]).delete()
            db.commit()
            return Response(status_code=400, headers={"clientError": "Invalid Code"})
    except Exception as e:
        print(e)
        return Response(status_code=500, headers={"Error": "Server error"})
    finally:
        db.close()


@router.get("/resetExpiredActivationLink/")
async def accountreset(activation_code: str, email: str, db: Session = Depends(get_db)):
    """
    ### API route to get new link for the expired link, account activation. It contains following parameters.
    :param activation_code: It is a object encoded by jWT.
    :param email: It is a string parameter against which the account reset mail is sent.
    :param db: It provides a session to interact with the backend Database,that is of Session Object Type.
    :return: It resturns a flag [Password reset successful].
    """
    try:
        # decode the token
        data = jwt.decode(activation_code, "9joxN0XD3jyowKdMALUO1ayOWve9bdS1", algorithms=["HS256"])
        # use the userid to compare if the email provided exists
        email2 = db.query(model.User.email).filter_by(idUser=data["idUser"]).scalar()
        users = db.query(model.User.firstName, model.User.lastName).filter_by(idUser=data["idUser"]).one()
        if email2 and str(email2).lower() == str(email).lower():
            # pop the exp date which will be reset in sendmail
            data.pop("exp_date")
            cust_id = db.query(model.User.customerID).filter_by(email=email).scalar()
            details = {"user_id": None, "trigger_code": 8011, "cust_id": cust_id, "inv_id": None,
                       "additional_details": {"recipients": [(email, users.firstName, users.lastName)],
                                              "subject": "Verification mail",
                                              "endpoint_url": f"{endpoint_site}/#/registration-page/activationLink/",
                                              "user_details": data}}
            mqtt.publish("notification_processor", json.dumps(details))
            return {"result": "Account reset successful"}
        else:
            return Response(status_code=400, headers={"clientError": "Invalid Email id"})
    except Exception as e:
        print(traceback.print_exc())
        return Response(status_code=500, headers={"Error": "Server error", "Desc": "Invalid result"})
    finally:
        db.close()
