from pandas import ExcelWriter
from typing import Optional
import pandas as pd
import os, time
from io import StringIO, BytesIO

import requests
from passlib.context import CryptContext
from fastapi.responses import FileResponse, Response
from azure.storage.blob import generate_blob_sas, BlobServiceClient, ContainerSasPermissions
import model
from datetime import datetime, timedelta
import pytz as tz
# from Crypto.Cipher import AES
from cryptography.fernet import Fernet
import traceback
# myctx = CryptContext(schemes=["sha256_crypt", "md5_crypt"])
# # myctx.update(default="md5_crypt")
# myctx.default_scheme()
import sys

sys.path.append("..")
from logModule import applicationlogging
tz_region_name = os.getenv("serina_tz", "Asia/Dubai")
tz_region = tz.timezone(tz_region_name)


async def downloadtemplate(temp):
    header_template = ['Sr #', 'ERP [EDP/EBS]', 'Bill Type', 'Company Name', 'Company Code',
                       'Address [Outlet/Office]', 'Location Code', 'Account Number', 'URL',
                       'UserName', 'Password', 'Admin Email for Exception',
                       'Sharepoint for Bill Storage', 'ERP URL', 'Login', 'Pswd',
                       'Responsibility ', 'FTP for BI Ingestion']

    GAL_cost_template = ['Sr #', 'ERP [EDP/EBS]', 'Bill Type',
                         'Company Name', 'Company Code', 'Location Code',
                         'Element', 'Division', 'Department',
                         'Element Factor', 'Natural Account', 'Account Number',
                         'SL Code', 'GL-SL']

    GICC_cost_template = ['Sr #', 'ERP [EDP/EBS]  ',
                          'Bill Type', 'Company Name',
                          'Company Code', 'Location Code',
                          'Element', 'Division',
                          'Department', 'Element Factor',
                          'Natural Account',
                          'Electricity Charges',
                          'Water& Sewerage Charges', 'Housing Fee',
                          'Account Number', 'Address[Outlet/Office]']

    header_template = pd.DataFrame(columns=header_template)
    GAL_cost_template = pd.DataFrame(columns=GAL_cost_template)
    GICC_cost_template = pd.DataFrame(columns=GICC_cost_template)
    file_location = 'templateexcel.xlsx'
    writer = ExcelWriter(file_location)
    header_template.to_excel(writer, 'Master Template')
    if temp == 'EDP':
        GAL_cost_template.to_excel(writer, 'Cost Category Template')
        file_name = 'GAL'
    elif temp == 'EBS':
        GICC_cost_template.to_excel(writer, 'Cost Category Template')
        file_name = 'GICC'
    writer.save()
    return FileResponse(file_location, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                        filename=file_name)


async def bulkuploaddata(file, db):
    try:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        filename = f'/datadrive/SERINA/API/V1.2/UploadedFiles/{time.time()}-{file.filename}'
        f = open(f'{filename}', 'wb')
        content = await file.read()
        f.write(content)
        f.close()
        df_master = pd.read_excel(filename, sheet_name='Master Template')
        df_costcateg = pd.read_excel(filename, sheet_name='Cost Category Template')
        os.remove(filename)

        # df_master.columns = df_master.iloc[2]

        # df_master = df_master.drop([0, 1, 2])
        df_master = df_master.reset_index(drop=True)
        # df_costcateg.columns = df_costcateg.iloc[2]
        # df_costcateg = df_costcateg.drop([0, 1, 2])
        df_costcateg = df_costcateg.reset_index(drop=True)
        df_costcateg = df_costcateg.fillna(0)
        df_master['Admin Email for Exception'] = df_master['Admin Email for Exception'].fillna(0)
        df_master['Location Code'] = df_master['Location Code'].fillna(0)
        df_master['URL'] = df_master['URL'].fillna(0)

        file_location = f'UploadedFiles/rejectedrecords.xlsx'

        with BytesIO() as buffer:
            writer = pd.ExcelWriter(buffer)
            header_template = pd.DataFrame(columns=['Reason'])
            GAL_cost_template = pd.DataFrame(columns=['Reason'])
            total = df_master.shape[0]
            inserted = 0
            for index, row in df_master.iterrows():
                idSP = db.query(model.ServiceProvider.idServiceProvider).filter(
                    model.ServiceProvider.ServiceProviderName == row['Bill Type']).all()
                #     for entityand entity body
                idEnt = db.query(model.Entity.idEntity).filter(model.Entity.EntityName == row['Company Name']).all()
                idEntBody = db.query(model.EntityBody.idEntityBody).filter(
                    model.EntityBody.EntityBodyName == row['Address [Outlet/Office]']).all()
                if idSP and idEnt and idEntBody:
                    l1 = []
                    df_costcateg_new = df_costcateg[df_costcateg['Account Number'] == row['Account Number']]
                    acc_id = db.query(model.ServiceAccount.idServiceAccount).filter(
                        model.ServiceAccount.Account == row['Account Number']).all()
                    for index1, row1 in df_costcateg_new.iterrows():
                        idDept = db.query(model.Department.idDepartment).filter(
                            model.Department.DepartmentName == row1['Department']).all()
                        l1.append(idDept)
                    l1 = list(filter(None, l1))
                    if len(l1) == df_costcateg_new.shape[0]:
                        element_factor_total = df_costcateg_new['Element Factor'].sum()
                        if element_factor_total == 1.0:
                            if not acc_id:
                                print(idSP[0][0], row['Location Code'], row['Admin Email for Exception'], idEnt[0][0],
                                      idEntBody[0][0])

                                c1 = model.ServiceAccount(serviceProviderID=idSP[0][0], Account=row['Account Number'],
                                                          LocationCode=row['Location Code'],
                                                          Email=row['Admin Email for Exception'], entityID=idEnt[0][0],
                                                          entityBodyID=idEntBody[0][0],
                                                          CreatedOn=datetime.now(tz_region).strftime("%Y-%m-%d %H:%M:%S"))

                                db.add(c1)
                                db.commit()

                                acc_id = db.query(model.ServiceAccount.idServiceAccount).filter(
                                    model.ServiceAccount.Account == row['Account Number']).all()
                                #         inserting in credentials
                                # passwrd=myctx.hash(row['Password'])
                                # obj = AES.new('This is a key123', AES.MODE_CFB, 'This is an IV456')
                                # passwrd = obj.encrypt(row['Password'])
                                # print(passwrd)
                                # passwrd=passwrd.decode('Windows-1251')
                                # print(passwrd)
                                if pd.isnull(row['UserName']):
                                    # row['UserName'].fillna(None)
                                    # passwrd==None

                                    c4 = model.Credentials(entityID=idEnt[0][0], entityBodyID=idEntBody[0][0],
                                                           URL=row['URL'], serviceProviderAccountID=acc_id[0][0],
                                                           crentialTypeId=4,
                                                           CreatedOn=datetime.now(tz_region).strftime("%Y-%m-%d %H:%M:%S"))
                                    db.add(c4)
                                    db.commit()
                                    inserted = inserted + 1
                                else:

                                    fernet = Fernet("g-FLG74U9o68MN4YOVTt-w8QuB6fgi2p2omd6qOZtUs=")
                                    encMessage = fernet.encrypt(row['Password'].encode())
                                    passwrd = encMessage.decode("utf-8")

                                    c4 = model.Credentials(UserName=row['UserName'], LogSecret=passwrd,
                                                           entityID=idEnt[0][0], entityBodyID=idEntBody[0][0],
                                                           URL=row['URL'], serviceProviderAccountID=acc_id[0][0],
                                                           crentialTypeId=4,
                                                           CreatedOn=datetime.now(tz_region).strftime("%Y-%m-%d %H:%M:%S"))
                                    db.add(c4)
                                    db.commit()
                                    inserted = inserted + 1
                            else:
                                header_template1 = df_master[df_master['Account Number'] == row['Account Number']]
                                header_template = header_template.append(header_template1, ignore_index=True)
                                header_template.loc[header_template['Account Number'] == row[
                                    'Account Number'], 'Reason'] = "Already Present in DB"

                            element_f = db.query(model.AccountCostAllocation.elementFactor).filter(
                                model.AccountCostAllocation.accountID == acc_id[0][0]).all()
                            if not element_f:
                                for index1, row1 in df_costcateg_new.iterrows():
                                    if 'Electricity Charges' in df_costcateg_new.columns:

                                        c2 = model.AccountCostAllocation(accountID=acc_id[0][0], entityID=idEnt[0][0],
                                                                         entityBodyID=idEntBody[0][0],
                                                                         division=row1['Division'],
                                                                         departmentID=idDept[0][0],
                                                                         naturalAccountElectricity_genric=row1[
                                                                             'Electricity Charges'],
                                                                         naturalAccountWater=row1[
                                                                             'Water& Sewerage Charges'],
                                                                         naturalAccountHousing=row1['Housing Fee'],
                                                                         elementFactor=row1['Element Factor'],
                                                                         CreatedOn=datetime.now(tz_region).strftime(
                                                                             "%Y-%m-%d %H:%M:%S"))
                                        db.add(c2)
                                    else:

                                        c3 = model.AccountCostAllocation(accountID=acc_id[0][0], entityID=idEnt[0][0],
                                                                         entityBodyID=idEntBody[0][0],
                                                                         division=row1['Division'],
                                                                         departmentID=idDept[0][0],
                                                                         naturalAccountElectricity_genric=row1[
                                                                             'Natural Account'], slCode=row1['SL Code'],
                                                                         gl_slCode=row1['GL-SL'],
                                                                         elementFactor=row1['Element Factor'],
                                                                         CreatedOn=datetime.now(tz_region).strftime(
                                                                             "%Y-%m-%d %H:%M:%S"))
                                        db.add(c3)
                            else:

                                GAL_cost_template = GAL_cost_template.append(df_costcateg_new, ignore_index=True)
                                GAL_cost_template.loc[GAL_cost_template['Account Number'] == row[
                                    'Account Number'], 'Reason'] = "Record is already present"
                        else:
                            header_template1 = df_master[df_master['Account Number'] == row['Account Number']]
                            header_template = header_template.append(header_template1, ignore_index=True)
                            header_template.loc[header_template['Account Number'] == row[
                                'Account Number'], 'Reason'] = "Element factor is not matching"

                            GAL_cost_template = GAL_cost_template.append(df_costcateg_new, ignore_index=True)
                            GAL_cost_template.loc[GAL_cost_template['Account Number'] == row[
                                'Account Number'], 'Reason'] = "Element factor is not matching"
                    else:
                        header_template1 = df_master[df_master['Account Number'] == row['Account Number']]
                        header_template = header_template.append(header_template1, ignore_index=True)
                        header_template.loc[header_template['Account Number'] == row[
                            'Account Number'], 'Reason'] = "Departmemt is not available"

                        GAL_cost_template = GAL_cost_template.append(df_costcateg_new, ignore_index=True)
                        GAL_cost_template.loc[GAL_cost_template['Account Number'] == row[
                            'Account Number'], 'Reason'] = "Departmemt is not available"

                else:
                    print("rejected1", row['Account Number'])

                    if idEnt and not idEntBody and not idSP:

                        reasoncode = "EntityBody and Service Provider are not present"
                        print("rejected", row['Account Number'], reasoncode)

                    elif idEnt and not idEntBody and idSP:
                        reasoncode = "EntityBody is not present"
                        print("rejected", row['Account Number'], reasoncode)
                    elif idEnt and idEntBody and not idSP:
                        reasoncode = "Service Provider is not present"
                        print("rejected", row['Account Number'], reasoncode)
                    elif not idEnt and idEntBody and not idSP:
                        reasoncode = "Entity and Service Provider are not present"
                        print("rejected", row['Account Number'], reasoncode)
                    elif not idEnt and not idEntBody and idSP:
                        reasoncode = "Entity and EntityBody are not present"
                        print("rejected", row['Account Number'], reasoncode)
                    elif not idEnt and idEntBody and idSP:
                        reasoncode = "Entity is not present"
                        print("rejected", row['Account Number'], reasoncode)
                    else:
                        reasoncode = "Service Provider/Entity/EntityBody not present"
                        print("rejected", row['Account Number'], reasoncode)
                    header_template1 = df_master[df_master['Account Number'] == row['Account Number']]
                    header_template = header_template.append(header_template1, ignore_index=True)
                    header_template.loc[
                        header_template['Account Number'] == row['Account Number'], 'Reason'] = reasoncode

                    GAL_cost_template1 = df_costcateg[df_costcateg['Account Number'] == row['Account Number']]
                    GAL_cost_template = GAL_cost_template.append(GAL_cost_template1, ignore_index=True)
                    GAL_cost_template.loc[
                        GAL_cost_template['Account Number'] == row['Account Number'], 'Reason'] = reasoncode
            header_template = header_template.drop(columns=['Unnamed: 0', 'Sr #'])
            GAL_cost_template = GAL_cost_template.drop(columns=['Unnamed: 0', 'Sr #'])
            header_template.to_excel(writer, 'Master Template', header=True)
            GAL_cost_template.to_excel(writer, 'Cost Category Template')
            writer.save()
            connection_str = "DefaultEndpointsProtocol=https;AccountName=serinablob;AccountKey=9eOFPkLlYKYHm+rm0RLZ0NuvQ/D01WVjDjDSFTGRmABeUZEYoZsMflRL7c3evwtDLCwXhKW3Fjo0Ps3feRdt/A==;EndpointSuffix=core.windows.net"
            blob_service_client = BlobServiceClient.from_connection_string(connection_str)
            container_client = blob_service_client.get_container_client("serinatest")
            container_client.upload_blob(name=file_location, data=buffer.getvalue(), overwrite=True)

            db.commit()
            a = str(inserted) + " Accounts inserted out of " + str(total)
            resp = {"result": a}
            return resp

    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV", "SPbulkuploadCrud.py bulkuploaddata", str(e))
        return Response(status_code=500, headers={"Error": "Server error", "Desc": "Invalid data"})

    finally:
        db.close()


async def BulkuploaddataRejectedRecords():
    try:
        file_location = f'UploadedFiles/rejectedrecords.xlsx'
        connection_str = "DefaultEndpointsProtocol=https;AccountName=serinablob;AccountKey=9eOFPkLlYKYHm+rm0RLZ0NuvQ/D01WVjDjDSFTGRmABeUZEYoZsMflRL7c3evwtDLCwXhKW3Fjo0Ps3feRdt/A==;EndpointSuffix=core.windows.net"
        account_key = connection_str.split("AccountKey=")[1].split(";EndpointSuffix")[0]
        blob_service_client = BlobServiceClient.from_connection_string(connection_str)
        sas_token = generate_blob_sas(
            account_name=blob_service_client.account_name,
            container_name="serinatest",
            blob_name=file_location,
            account_key=account_key,
            permission=ContainerSasPermissions(read=True),
            expiry=datetime.now(tz_region) + timedelta(hours=1),
        )
        resp = requests.get(
            f"https://{blob_service_client.account_name}.blob.core.windows.net/serinatest/UploadedFiles/rejectedrecords.xlsx?{sas_token}")
        data = BytesIO(resp.content).getvalue()
        with open('rejectedrecords.xlsx', 'wb+') as file1:
            file1.write(data)
            file1.close()
        file_name = 'Rejected_Records'
        return FileResponse('rejectedrecords.xlsx',
                            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            filename=file_name)
    except Exception as e:
        applicationlogging.logException("ROVE HOTEL DEV", "SPbulkuploadCrud.py BulkuploaddataRejectedRecords", str(e))
        return Response(status_code=500, headers={"Error": "Server error", "Desc": "Invalid data"})
