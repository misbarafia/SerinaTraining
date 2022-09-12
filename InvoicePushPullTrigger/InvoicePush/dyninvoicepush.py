import pandas as pd
from sqlalchemy import create_engine,select,MetaData, Table, and_,select
import pymysql
import requests
from sqlalchemy.sql import text as sa_text
import json
from datetime import datetime

SQL_USER = 'serina'
SQL_PASS = 'dsserina'
SQL_DB = 'EBSDB'
SQL_PORT = '3306'
localhost = 'serina-qa-server1.mysql.database.azure.com'
engine = create_engine(f'mysql+pymysql://{SQL_USER}:{SQL_PASS}@{localhost}:{SQL_PORT}/{SQL_DB}')
connection = engine.connect()
SQL_USER1 = 'serina'
SQL_PASS1 = 'dsserina'
SQL_DB1 = 'serina_agi'
SQL_PORT1 = '3306'
localhost1 = 'serina-qa-server1.mysql.database.azure.com'
engine1 = create_engine(f'mysql+pymysql://{SQL_USER1}:{SQL_PASS1}@{localhost1}:{SQL_PORT1}/{SQL_DB1}')
connection1 = engine1.connect()

client_id = "6cdcfa6f-bb0e-43f3-9063-765ebddadc25"
client_secret = "XOa7Q~wRQhQPZ1wgnklLsf_uFazwpbEeJZ_52"
res='https://agifd-apinvoiceauto793982e5b48be771devaos.cloudax.uae.dynamics.com/'
# scope = "appstore::apps:readwrite"
grant_type = "client_credentials"
data = {
    "grant_type": grant_type,
    "client_id": client_id,
    "client_secret": client_secret,
    "resource": res
}
amazon_auth_url = "https://login.microsoftonline.com/38a3f678-5fe7-4dbb-8eb9-eee7a0c6fd57/oauth2/token"
auth_response = requests.post(amazon_auth_url, data=data)

# Read token from auth response
auth_response_json = auth_response.json()
auth_token = auth_response_json["access_token"]
auth_token_header_value = "Bearer %s" % auth_token
headers = {"Authorization": auth_token_header_value}

#PO base
df = pd.read_sql("SELECT * FROM d3agi_poinvoice",connection)

j = (df.groupby(['purchid','dataAreaId','invoiceNumber','invoiceDate','invoiceTotal','DocName','URL'])
       .apply(lambda x: x[['linenumber','ItemId','Qty','lineAmount','lineUnitPrice','lineDescription']].to_dict('records'))
       .reset_index()
       .rename(columns={0:'ItemDetails'})
       .to_json(orient='records'))

a1=json.loads(j)

inv_posturl = "https://agifd-apinvoiceauto793982e5b48be771devaos.cloudax.uae.dynamics.com//api/services/SER_POInvoiceServiceGroup/SER_POPartialInvoiceService/POInvoice"
check_statusurl="https://agifd-apinvoiceauto793982e5b48be771devaos.cloudax.uae.dynamics.com//api/services/SER_POInvoiceServiceGroup/SER_POPartialInvoiceService/checkInvoice"
docStatus=4
created_date=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
for i in range(len(a1)):
    data_inv={"jsondata":a1[i]}
    vend_code=df[df['invoiceNumber']==a1[i]['invoiceNumber']].supplierName.unique()[0]
    status_checkdata={"dataArea":a1[i]['dataAreaId'],"vendAccount":vend_code,"invoicenum":a1[i]['invoiceNumber']}
    status_response = requests.post(check_statusurl, json=status_checkdata,headers=headers)
    status_response_json = status_response.json()
    status_response_json = json.loads(status_response_json)
    inv_id=df[df['invoiceNumber']==a1[i]['invoiceNumber']].documentid.unique()[0]
    if status_response_json['IsPosted'] == 'No' and status_response_json['Message'] == 'Invoice Not Exists':
        auth_response1 = requests.post(inv_posturl, json=data_inv,headers=headers)
        auth_response_json1 = auth_response1.json()
        auth_response_json1 = json.loads(auth_response_json1)
        print(data_inv)
        docDesc=auth_response_json1['Message']
        if 'Value' in auth_response_json1:
            if auth_response_json1['Value'] == 'Success':
                his_qry1 = " UPDATE document SET documentStatusID='" + str(7) + "' WHERE iddocument=" + str(inv_id) + ""
                with engine1.begin() as conn:
                    conn.execute(his_qry1)
                his_qry = 'INSERT INTO '+str(SQL_DB1)+'.documenthistorylog (documentID, documentdescription, documentStatusID,documentSubStatusID,CreatedOn) values (' + str(
                        inv_id) + ', "' + docDesc + '",' + str(7) +',' + str(31) +',"'+str(created_date)+ '")'
                with engine1.begin() as conn:
                    conn.execute(his_qry)
            elif auth_response_json1['Value'] == 'Fail':
                his_qry = 'INSERT INTO '+str(SQL_DB1)+'.documenthistorylog (documentID, documentdescription, documentStatusID,documentSubStatusID,CreatedOn) values (' + str(
                        inv_id) + ', "' + docDesc + '",' + str(docStatus) +',' + str(32) +',"'+str(created_date)+ '")'
                with engine1.begin() as conn:
                    conn.execute(his_qry)
                print(inv_id)
                doc_Status = " UPDATE document SET documentStatusID='" + str(4) + "', documentsubstatusID = " + str(32) + " WHERE iddocument=" + str(inv_id) + ""
                with engine1.begin() as conn:
                    conn.execute(doc_Status)
#     if 'ExceptionType' in auth_response_json1:
#     if auth_response_json1['Value'] != 'Success':
        elif 'ExceptionType' in auth_response_json1:
            his_qry = 'INSERT INTO '+str(SQL_DB1)+'.documenthistorylog (documentID, documentdescription, documentStatusID,documentSubStatusID,CreatedOn) values (' + str(
                    inv_id) + ', "' + docDesc + '",' + str(docStatus) +',' + str(32) +',"'+str(created_date)+ '")'
            with engine1.begin() as conn:
                conn.execute(his_qry)
            print(inv_id)
            doc_Status = " UPDATE document SET documentStatusID='" + str(4) + "', documentsubstatusID = " + str(32) + " WHERE iddocument=" + str(inv_id) + ""
            with engine1.begin() as conn:
                conn.execute(doc_Status)
    else:
        docDesc=status_response_json['Message']
        his_qry = 'INSERT INTO '+str(SQL_DB1)+'.documenthistorylog (documentID, documentdescription, documentStatusID,documentSubStatusID,CreatedOn) values (' + str(
                inv_id) + ', "' + docDesc + '",' + str(docStatus) +',' + str(32) +',"'+str(created_date)+ '")'
        with engine1.begin() as conn:
            conn.execute(his_qry)
        print(inv_id)
        doc_Status = " UPDATE document SET documentStatusID='" + str(4) + "', documentsubstatusID = " + str(32) + " WHERE iddocument=" + str(inv_id) + ""
        with engine1.begin() as conn:
            conn.execute(doc_Status)

del_rec1 = "delete from d3agi_poinvoice"
with engine.begin() as conn:
    conn.execute(del_rec1)

#SErvice based
df_service = pd.read_sql("SELECT * FROM d3agi_service_invoice where type='service'",connection)

serv = (df_service.groupby(['dataArea','InvoiceNumber'])
       .apply(lambda x: x[['VendorAccount','InvoiceDate','InvoiceNumber','Description','Credit','CurrencyCode','Company','CostCenter','MainAccount','Product','Interco','Location','Project','DocName','URL']].to_dict('records'))
       .reset_index()
       .rename(columns={0:'InvoiceDetails'})
       .to_json(orient='records'))

serv=json.loads(serv)

inv_posturl_service = "https://agifd-apinvoiceauto793982e5b48be771devaos.cloudax.uae.dynamics.com//api/services/SER_POInvoiceServiceGroup/SER_POPartialInvoiceService/doPOInvoiceJournal"
check_statusurl="https://agifd-apinvoiceauto793982e5b48be771devaos.cloudax.uae.dynamics.com//api/services/SER_POInvoiceServiceGroup/SER_POPartialInvoiceService/checkInvoice"
docStatus=4
created_date=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
for i in range(len(serv)):
    inv_id=df_service[df_service['InvoiceNumber']==serv[i]['InvoiceNumber']].documentid.unique()[0]
    vend_code=df_service[df_service['InvoiceNumber']==serv[i]['InvoiceNumber']].VendorAccount.unique()[0]
    status_checkdata={"dataArea":serv[i]['dataArea'],"vendAccount":vend_code,"invoicenum":serv[i]['InvoiceNumber']}
    del serv[i]['InvoiceNumber']
    data_invserv={"jsondata":serv[i]}

    status_response = requests.post(check_statusurl, json=status_checkdata,headers=headers)
    status_response_json = status_response.json()
    status_response_json = json.loads(status_response_json)
    if status_response_json['IsPosted'] == 'No' and status_response_json['Message'] == 'Invoice Not Exists':
        auth_response_serv = requests.post(inv_posturl_service, json=data_invserv,headers=headers)
        auth_response_json_serv = auth_response_serv.json()
        auth_response_json_serv = json.loads(auth_response_json_serv)
        print(auth_response_json_serv,inv_id)

        docDesc=auth_response_json_serv['Message']
        if 'Value' in auth_response_json_serv:
            if auth_response_json_serv['Value'] == 'Success':
                his_qry1 = " UPDATE document SET documentStatusID='" + str(7) + "' WHERE iddocument=" + str(inv_id) + ""
                with engine1.begin() as conn:
                    conn.execute(his_qry1)
                his_qry = 'INSERT INTO '+str(SQL_DB1)+'.documenthistorylog (documentID, documentdescription, documentStatusID,documentSubStatusID,CreatedOn) values (' + str(
                        inv_id) + ', "' + docDesc + '",' + str(7) +',' + str(1) +',"'+str(created_date)+ '")'
                with engine1.begin() as conn:
                    conn.execute(his_qry)
            elif auth_response_json_serv['Value'] == 'Fail':
                his_qry = 'INSERT INTO '+str(SQL_DB1)+'.documenthistorylog (documentID, documentdescription, documentStatusID,documentSubStatusID,CreatedOn) values (' + str(
                        inv_id) + ', "' + docDesc + '",' + str(docStatus) +',' + str(32) +',"'+str(created_date)+ '")'
                with engine1.begin() as conn:
                    conn.execute(his_qry)
                print(inv_id)
                doc_Status = " UPDATE document SET documentStatusID='" + str(4) + "', documentsubstatusID = " + str(32) + " WHERE iddocument=" + str(inv_id) + ""
                with engine1.begin() as conn:
                    conn.execute(doc_Status)
        elif 'ExceptionType' in auth_response_json_serv:
            his_qry = 'INSERT INTO '+str(SQL_DB1)+'.documenthistorylog (documentID, documentdescription, documentStatusID,documentSubStatusID,CreatedOn) values (' + str(
                    inv_id) + ', "' + docDesc + '",' + str(docStatus) +',' + str(32) +',"'+str(created_date)+ '")'
            with engine1.begin() as conn:
                conn.execute(his_qry)
            print(inv_id)
            doc_Status = " UPDATE document SET documentStatusID='" + str(4) + "', documentsubstatusID = " + str(32) + " WHERE iddocument=" + str(inv_id) + ""
            with engine1.begin() as conn:
                conn.execute(doc_Status)
    else:
        docDesc=status_response_json['Message']
        his_qry = 'INSERT INTO '+str(SQL_DB1)+'.documenthistorylog (documentID, documentdescription, documentStatusID,documentSubStatusID,CreatedOn) values (' + str(
                inv_id) + ', "' + docDesc + '",' + str(docStatus) +',' + str(32) +',"'+str(created_date)+ '")'
        with engine1.begin() as conn:
            conn.execute(his_qry)
        print(inv_id)
        doc_Status = " UPDATE document SET documentStatusID='" + str(4) + "', documentsubstatusID = " + str(32) + " WHERE iddocument=" + str(inv_id) + ""
        with engine1.begin() as conn:
            conn.execute(doc_Status)

del_rec = "delete from d3agi_service_invoice where type='service'"
with engine.begin() as conn:
    conn.execute(del_rec)
#Non PO
df_nonpo = pd.read_sql("SELECT * FROM d3agi_service_invoice where type='nonpo'",connection)
nonpo = (df_nonpo.groupby(['dataArea','InvoiceNumber'])
       .apply(lambda x: x[['VendorAccount','InvoiceDate','InvoiceNumber','Description','Credit','CurrencyCode','Company','CostCenter','MainAccount','Product','Interco','Location','Project','DocName','URL']].to_dict('records'))
       .reset_index()
       .rename(columns={0:'InvoiceDetails'})
       .to_json(orient='records'))

nonpo=json.loads(nonpo)
inv_posturl_nonpo = "https://agifd-apinvoiceauto793982e5b48be771devaos.cloudax.uae.dynamics.com//api/services/SER_POInvoiceServiceGroup/SER_POPartialInvoiceService/doPOInvoiceJournal"
check_statusurl="https://agifd-apinvoiceauto793982e5b48be771devaos.cloudax.uae.dynamics.com//api/services/SER_POInvoiceServiceGroup/SER_POPartialInvoiceService/checkInvoice"
docStatus=4
created_date=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
for i in range(len(nonpo)):
    inv_id=df_nonpo[df_nonpo['InvoiceNumber']==nonpo[i]['InvoiceNumber']].documentid.unique()[0]  
    vend_code=df_nonpo[df_nonpo['InvoiceNumber']==nonpo[i]['InvoiceNumber']].VendorAccount.unique()[0]
    status_checkdata={"dataArea":nonpo[i]['dataArea'],"vendAccount":vend_code,"invoicenum":nonpo[i]['InvoiceNumber']}
    del nonpo[i]['InvoiceNumber']
    data_invnonpo={"jsondata":nonpo[i]}
    status_response = requests.post(check_statusurl, json=status_checkdata,headers=headers)
    status_response_json = status_response.json()
    status_response_json = json.loads(status_response_json)
    if status_response_json['IsPosted'] == 'No' and status_response_json['Message'] == 'Invoice Not Exists':
        auth_response_nonpo = requests.post(inv_posturl_nonpo, json=data_invnonpo,headers=headers)
        auth_response_json_nonpo = auth_response_nonpo.json()
        auth_response_json_nonpo = json.loads(auth_response_json_nonpo)
        print(auth_response_json_nonpo,inv_id)

        docDesc=auth_response_json_nonpo['Message']
        if 'Value' in auth_response_json_nonpo:
            if auth_response_json_nonpo['Value'] == 'Success':
                his_qry1 = " UPDATE document SET documentStatusID='" + str(7) + "' WHERE iddocument=" + str(inv_id) + ""
                with engine1.begin() as conn:
                    conn.execute(his_qry1)
                his_qry = 'INSERT INTO '+str(SQL_DB1)+'.documenthistorylog (documentID, documentdescription, documentStatusID,documentSubStatusID,CreatedOn) values (' + str(
                        inv_id) + ', "' + docDesc + '",' + str(7) +',' + str(31) +',"'+str(created_date)+ '")'
                with engine1.begin() as conn:
                    conn.execute(his_qry)
            elif auth_response_json_nonpo['Value'] == 'Fail':
                his_qry = 'INSERT INTO '+str(SQL_DB1)+'.documenthistorylog (documentID, documentdescription, documentStatusID,documentSubStatusID,CreatedOn) values (' + str(
                        inv_id) + ', "' + docDesc + '",' + str(docStatus) +',' + str(32) +',"'+str(created_date)+ '")'
                with engine1.begin() as conn:
                    conn.execute(his_qry)
                print(inv_id)
                doc_Status = " UPDATE document SET documentStatusID='" + str(4) + "', documentsubstatusID = " + str(32) + " WHERE iddocument=" + str(inv_id) + ""
                with engine1.begin() as conn:
                    conn.execute(doc_Status)
        elif 'ExceptionType' in auth_response_json_nonpo:
            his_qry = 'INSERT INTO '+str(SQL_DB1)+'.documenthistorylog (documentID, documentdescription, documentStatusID,documentSubStatusID,CreatedOn) values (' + str(
                    inv_id) + ', "' + docDesc + '",' + str(docStatus) +',' + str(32) +',"'+str(created_date)+ '")'
            with engine1.begin() as conn:
                conn.execute(his_qry)
            print(inv_id)
            doc_Status = " UPDATE document SET documentStatusID='" + str(4) + "', documentsubstatusID = " + str(32) + " WHERE iddocument=" + str(inv_id) + ""
            with engine1.begin() as conn:
                conn.execute(doc_Status)
    else:
        docDesc=status_response_json['Message']
        his_qry = 'INSERT INTO '+str(SQL_DB1)+'.documenthistorylog (documentID, documentdescription, documentStatusID,documentSubStatusID,CreatedOn) values (' + str(
                inv_id) + ', "' + docDesc + '",' + str(docStatus) +',' + str(32) +',"'+str(created_date)+ '")'
        with engine1.begin() as conn:
            conn.execute(his_qry)
        print(inv_id)
        doc_Status = " UPDATE document SET documentStatusID='" + str(4) + "', documentsubstatusID = " + str(32) + " WHERE iddocument=" + str(inv_id) + ""
        with engine1.begin() as conn:
            conn.execute(doc_Status)

del_rec = "delete from d3agi_service_invoice where type='nonpo'"
with engine.begin() as conn:
    conn.execute(del_rec)
