# convert into bytes:
# check type
# application/pdf, image/jpeg, image/png, or image/tiff
import os
import traceback
from os import walk
import math
import sys
import json, requests
from io import BytesIO
import model
from PyPDF2 import PdfFileReader, PdfFileWriter
sys.path.append("..")
from session.notificationsession import client as mqtt


# Background task publisher
def meta_data_publisher(msg):
    try:
        mqtt.publish("notification_processor", json.dumps(msg), qos=2, retain=True)
    except Exception as e:
        pass


def check_file_exist(vendorAccountID, entityID, filename, file_path, bg_task, db):
    """
    Check if the file exist, return==0 => file missing, return==1 => file found
    :param file_path:str, File path
    :return:int
    """
    # print(file_path)
    resp = requests.get(file_path)

    if resp.status_code == 200:
        file_exists_status = 1
        file_exists_msg = "File Found"
    else:
        file_exists_status = 0
        file_exists_msg = "File Not Found"
        try:
            ############ start of notification trigger #############
            vendor = db.query(model.Vendor.VendorName).filter(
                model.Vendor.idVendor == model.VendorAccount.vendorID).filter(
                model.VendorAccount.idVendorAccount == vendorAccountID).scalar()
            # filter based on role if added
            role_id = db.query(model.NotificationCategoryRecipient.roles).filter_by(entityID=entityID,
                                                                                    notificationTypeID=2).scalar()
            # getting recipients for sending notification
            recepients1 = db.query(model.AccessPermission.userID).filter(
                model.AccessPermission.permissionDefID.in_(role_id["roles"])).distinct()
            recepients2 = db.query(model.VendorUserAccess.vendorUserID).filter_by(
                vendorAccountID=vendorAccountID, isActive=1).distinct()
            recepients = db.query(model.User.idUser, model.User.email, model.User.firstName,
                                  model.User.lastName).filter((model.User.idUser.in_(recepients1) |
                                                                  model.User.idUser.in_(recepients2))).filter(
                model.User.isActive == 1).filter(model.UserAccess.UserID == model.User.idUser).filter(
                            model.UserAccess.EntityID == entityID, model.UserAccess.isActive == 1).all()
            user_ids, *email = zip(*list(recepients))
            # just format update
            email_ids = list(zip(email[0], email[1], email[2]))
            try:
                isdefaultrep = db.query(model.NotificationCategoryRecipient.isDefaultRecepients,
                                        model.NotificationCategoryRecipient.notificationrecipient).filter(
                    model.NotificationCategoryRecipient.entityID == entityID,
                    model.NotificationCategoryRecipient.notificationTypeID == 2).one()
            except Exception as e:
                pass
            if isdefaultrep and isdefaultrep.isDefaultRecepients and len(
                    isdefaultrep.notificationrecipient["to_addr"]) > 0:
                email_ids.extend([(x, "Serina", "User") for x in isdefaultrep.notificationrecipient["to_addr"]])
                cc_email_ids = isdefaultrep.notificationrecipient["cc_addr"]
            cust_id = db.query(model.Entity.customerID).filter_by(idEntity=entityID).scalar()
            details = {"user_id": user_ids, "trigger_code": 8030, "cust_id": cust_id, "inv_id": None,
                       "additional_details": {"subject": "Invoice Upload Issue", "recipients": email_ids, "cc": cc_email_ids,
                                              "Vendor_Name": vendor,
                                              "filename": filename, "desc": file_exists_msg}}
            bg_task.add_task(meta_data_publisher, details)
            ############ End of notification trigger #############
        except Exception as e:
            print(e)

    # if os.path.exists(file_path):
    #     file_exists_status = 1
    #     file_exists_msg = "File Found"
    # else:
    #     file_exists_status = 0
    #     file_exists_msg = "File Not Found"
    return file_exists_status, file_exists_msg


def check_single_filetype(vendorAccountID, entityID, filename, accepted_file_type, bg_task, db):
    try:

        extn = [(filename.split(".")[-1])]
        present_file_type = list(set(extn))
        not_accepted = set(present_file_type) - set(accepted_file_type)
        if len(not_accepted) == 0:
            check_filetype_status = 1
            check_filetype_msg = "Good to go"
        else:
            check_filetype_status = 0
            check_filetype_msg = "Please check the uploaded file type, Accepted types: " + \
                                 str(accepted_file_type)
            try:
                ############ start of notification trigger #############
                vendor = db.query(model.Vendor.VendorName).filter(
                    model.Vendor.idVendor == model.VendorAccount.vendorID).filter(
                    model.VendorAccount.idVendorAccount == vendorAccountID).scalar()
                # filter based on role if added
                role_id = db.query(model.NotificationCategoryRecipient.roles).filter_by(entityID=entityID,
                                                                                        notificationTypeID=2).scalar()
                # getting recipients for sending notification
                recepients1 = db.query(model.AccessPermission.userID).filter(
                    model.AccessPermission.permissionDefID.in_(role_id["roles"])).distinct()
                recepients2 = db.query(model.VendorUserAccess.vendorUserID).filter_by(
                    vendorAccountID=vendorAccountID, isActive=1).distinct()
                recepients = db.query(model.User.idUser, model.User.email, model.User.firstName,
                                      model.User.lastName).filter((model.User.idUser.in_(recepients1) |
                                                                  model.User.idUser.in_(recepients2))).filter(
                    model.User.isActive == 1).all()
                user_ids, *email = zip(*list(recepients))
                # just format update
                email_ids = list(zip(email[0], email[1], email[2]))
                # getting recipients for sending notification
                try:
                    isdefaultrep = db.query(model.NotificationCategoryRecipient.isDefaultRecepients,
                                            model.NotificationCategoryRecipient.notificationrecipient).filter(
                        model.NotificationCategoryRecipient.entityID == entityID,
                        model.NotificationCategoryRecipient.notificationTypeID == 2).one()
                except Exception as e:
                    pass
                if isdefaultrep and isdefaultrep.isDefaultRecepients and len(
                        isdefaultrep.notificationrecipient["to_addr"]) > 0:
                    email_ids.extend([(x, "Serina", "User") for x in isdefaultrep.notificationrecipient["to_addr"]])
                    cc_email_ids = isdefaultrep.notificationrecipient["cc_addr"]
                cust_id = db.query(model.Entity.customerID).filter_by(idEntity=entityID).scalar()
                details = {"user_id": user_ids, "trigger_code": 8030, "cust_id": cust_id, "inv_id": None,
                           "additional_details": {"subject": "Invoice Upload Issue", "recipients": email_ids, "cc": cc_email_ids,
                                                  "Vendor_Name": vendor,
                                                  "filename": filename, "desc": check_filetype_msg}}
                bg_task.add_task(meta_data_publisher, details)
                ############ End of notification trigger #############
            except Exception as e:
                print(e)
        print(check_filetype_msg)
    except Exception as e:
        check_filetype_status = 0
        check_filetype_msg = str(e)
    return check_filetype_status, check_filetype_msg


# 3. check file size:

def ck_size_limit(vendorAccountID, entityID, filename, file_path, file_size_accepted, bg_task, db):
    # print(file_path)
    fl_status = 1
    try:

        # skip if it is symbolic link
        resp = requests.get(file_path)
        if resp.status_code == 200:
            # print(fp)
            # print(f,'--------------',os.path.getsize(fp))
            size_bytes = len(resp.content)

            if size_bytes == 0:
                # fl_sts_msg = "0 byte file found, Please upload valid files"
                # print("0000000")
                fl_status = fl_status * 0
            elif size_bytes > 0:  # min os ok
                # size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
                i = int(math.floor(math.log(size_bytes, 1024)))
                # print(i)
                if i == 2:
                    p = math.pow(1024, i)
                    s = round(size_bytes / p, 2)
                    # print(s)
                    if s >= file_size_accepted:
                        fl_status = fl_status * 0
                    else:
                        fl_status = fl_status * 2
                elif i < 2:
                    fl_status = fl_status * 2
            else:
                fl_status = fl_status * 0
        else:
            fl_status == 0
            fl_sts_msg = "File not found!: ck_size_limit"
        if fl_status == 0:
            fl_sts_msg = "Please check the file size. Uploaded flies should be grater than 0 Bytes and be less than 50 MB"
            try:
                ############ start of notification trigger #############
                vendor = db.query(model.Vendor.VendorName).filter(
                    model.Vendor.idVendor == model.VendorAccount.vendorID).filter(
                    model.VendorAccount.idVendorAccount == vendorAccountID).scalar()
                # filter based on role if added
                role_id = db.query(model.NotificationCategoryRecipient.roles).filter_by(entityID=entityID,
                                                                                        notificationTypeID=2).scalar()
                # getting recipients for sending notification
                recepients1 = db.query(model.AccessPermission.userID).filter(
                    model.AccessPermission.permissionDefID.in_(role_id["roles"])).distinct()
                recepients2 = db.query(model.VendorUserAccess.vendorUserID).filter_by(
                    vendorAccountID=vendorAccountID, isActive=1).distinct()
                recepients = db.query(model.User.idUser, model.User.email, model.User.firstName,
                                      model.User.lastName).filter((model.User.idUser.in_(recepients1) |
                                                                  model.User.idUser.in_(recepients2))).filter(
                    model.User.isActive == 1).all()
                user_ids, *email = zip(*list(recepients))
                # just format update
                email_ids = list(zip(email[0], email[1], email[2]))
                # getting recipients for sending notification
                try:
                    isdefaultrep = db.query(model.NotificationCategoryRecipient.isDefaultRecepients,
                                            model.NotificationCategoryRecipient.notificationrecipient).filter(
                        model.NotificationCategoryRecipient.entityID == entityID,
                        model.NotificationCategoryRecipient.notificationTypeID == 2).one()
                except Exception as e:
                    pass
                if isdefaultrep and isdefaultrep.isDefaultRecepients and len(
                        isdefaultrep.notificationrecipient["to_addr"]) > 0:
                    email_ids.extend([(x, "Serina", "User") for x in isdefaultrep.notificationrecipient["to_addr"]])
                    cc_email_ids = isdefaultrep.notificationrecipient["cc_addr"]
                cust_id = db.query(model.Entity.customerID).filter_by(idEntity=entityID).scalar()
                details = {"user_id": user_ids, "trigger_code": 8030, "cust_id": cust_id, "inv_id": None,
                           "additional_details": {"subject": "Invoice Upload Issue", "recipients": email_ids, "cc": cc_email_ids,
                                                  "Vendor_Name": vendor,
                                                  "filename": filename, "desc": fl_sts_msg}}
                bg_task.add_task(meta_data_publisher, details)
                ############ End of notification trigger #############
            except Exception as e:
                print(e)
        elif fl_status > 1:
            fl_sts_msg = "Good to upload"
            fl_status = 1
        else:
            fl_sts_msg = "Please check the file size"
            try:
                ############ start of notification trigger #############
                vendor = db.query(model.Vendor.VendorName).filter(
                    model.Vendor.idVendor == model.VendorAccount.vendorID).filter(
                    model.VendorAccount.idVendorAccount == vendorAccountID).scalar()
                # filter based on role if added
                role_id = db.query(model.NotificationCategoryRecipient.roles).filter_by(entityID=entityID,
                                                                                        notificationTypeID=2).scalar()
                # getting recipients for sending notification
                recepients1 = db.query(model.AccessPermission.userID).filter(
                    model.AccessPermission.permissionDefID.in_(role_id["roles"])).distinct()
                recepients2 = db.query(model.VendorUserAccess.vendorUserID).filter_by(
                    vendorAccountID=vendorAccountID, isActive=1).distinct()
                recepients = db.query(model.User.idUser, model.User.email, model.User.firstName,
                                      model.User.lastName).filter(model.User.idUser.in_(recepients1) |
                                                                  model.User.idUser.in_(recepients2)).filter(
                    model.User.isActive == 1).all()
                user_ids, *email = zip(*list(recepients))
                # just format update
                email_ids = list(zip(email[0], email[1], email[2]))
                # getting recipients for sending notification
                try:
                    isdefaultrep = db.query(model.NotificationCategoryRecipient.isDefaultRecepients,
                                            model.NotificationCategoryRecipient.notificationrecipient).filter(
                        model.NotificationCategoryRecipient.entityID == entityID,
                        model.NotificationCategoryRecipient.notificationTypeID == 2).one()
                except Exception as e:
                    pass
                if isdefaultrep and isdefaultrep.isDefaultRecepients and len(
                        isdefaultrep.notificationrecipient["to_addr"]) > 0:
                    email_ids.extend([(x, "Serina", "User") for x in isdefaultrep.notificationrecipient["to_addr"]])
                    cc_email_ids = isdefaultrep.notificationrecipient["cc_addr"]
                cust_id = db.query(model.Entity.customerID).filter_by(idEntity=entityID).scalar()
                details = {"user_id": user_ids, "trigger_code": 8030, "cust_id": cust_id, "inv_id": None,
                           "additional_details": {"subject": "Invoice Upload Issue", "recipients": email_ids, "cc": cc_email_ids,
                                                  "Vendor_Name": vendor,
                                                  "filename": filename, "desc": fl_sts_msg}}
                bg_task.add_task(meta_data_publisher, details)
                ############ End of notification trigger #############
            except Exception as e:
                print(e)
            fl_status = 0
    except Exception as e:
        fl_sts_msg = str(e)
        fl_status = 0
    return fl_status, fl_sts_msg


def get_binary_data(file_path):
    try:
        print("preprocessing: line(265)",str(file_path))
        resp = requests.get(file_path)
        print("resp.status_code:",resp.status_code)
        print("line 267")
        inputdata = BytesIO(resp.content)
        print("type(inputdata),len(inputdata): ",type(inputdata))
        input_data = BytesIO(resp.content)
        #inputdata = BytesIO(resp.content).getvalue()
        inputdata_list = []
        input_pdf = PdfFileReader(input_data, strict=False)
        pdf_len = input_pdf.getNumPages()
        for pdf_pg in range(0,pdf_len):
            print(pdf_pg)
            #pdf = PdfFileReader(input_pdf)
            writer = PdfFileWriter()
            page = input_pdf.getPage(pdf_pg)
            writer.addPage(page)
            tmp = BytesIO()
            writer.write(tmp)
            pg_data = tmp.getvalue()    
            inputdata_list.append(pg_data)

        get_binary_status = 1
        get_binary_msg = " PDF pg cnt : " + str(pdf_len)
        # print("inputdata_list",len(inputdata_list))
        if len(inputdata_list)>0:
            print(type(inputdata_list[0]),' frm preprocessing')

    except Exception as e:
        get_binary_status = 0
        get_binary_msg = str(e)
        print("in binary exception:",str(e))
        inputdata_list = []
    return inputdata_list, get_binary_status, get_binary_msg


def fr_preprocessing(vendorAccountID, entityID, file_path, accepted_file_type, file_size_accepted, filename, bg_task,
                     db):
    print("In preprocessing : -------------------- ", file_path, accepted_file_type, file_size_accepted)
    fr_preprocessing_status_msg = ""
    print('file_path: ', file_path)
    fr_preprocessing_data = []
    fr_preprocessing_status = 0
    try:
        file_exists_status, file_exists_msg = check_file_exist(vendorAccountID, entityID, filename, file_path, bg_task,
                                                               db)
        if file_exists_status == 1:
            check_filetype_status, check_filetype_msg = check_single_filetype(vendorAccountID, entityID,
                                                                              filename, accepted_file_type, bg_task, db)
            if check_filetype_status == 1:
                fl_status, fl_sts_msg = ck_size_limit(vendorAccountID, entityID, filename,
                                                      file_path, file_size_accepted, bg_task, db)
                if fl_status == 1:
                    input_data, get_binary_status, get_binary_msg = get_binary_data(
                        file_path)
                    if get_binary_status == 1:
                        #if type(input_data) == bytes:
                        if len(input_data) > 0:
                            fr_preprocessing_data = input_data
                            fr_preprocessing_status = 1
                            fr_preprocessing_msg = "Loaded Binary data"
                            fr_preprocessing_status_msg = json.dumps(
                                {"percentage": 25, "status": "Pre-Processing ⏳"})
                        else:
                            fr_preprocessing_msg = "Binary data issue"
                            fr_preprocessing_status = 0
                    else:
                        fr_preprocessing_msg = get_binary_msg
                        fr_preprocessing_status = get_binary_status

                else:
                    fr_preprocessing_status = fl_status
                    fr_preprocessing_msg = fl_sts_msg
            else:
                fr_preprocessing_status = check_filetype_status
                fr_preprocessing_msg = check_filetype_msg
        else:
            fr_preprocessing_status = file_exists_status
            fr_preprocessing_msg = file_exists_msg
    except Exception as r:
        fr_preprocessing_status = 0
        fr_preprocessing_msg = "Error in preprocessing: " + str(r)
    print("preprocessing status: ", fr_preprocessing_msg, fr_preprocessing_status)
    return fr_preprocessing_status, fr_preprocessing_msg, fr_preprocessing_data, fr_preprocessing_status_msg
