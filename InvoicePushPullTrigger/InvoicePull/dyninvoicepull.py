#!/usr/bin/env python
# coding: utf-8

# In[51]:


import pandas as pd
from sqlalchemy import create_engine,select,MetaData, Table, and_
import pymysql
import requests
from datetime import date
today = date.today()
from sqlalchemy.sql import text as sa_text
import json
from datetime import timedelta


# In[52]:


today=today-timedelta(days = 1)
date=today.strftime("%Y-%m-%d")


# In[53]:


SQL_USER = 'serina'
SQL_PASS = 'dsserina'
SQL_DB = 'ebsdb_rove'
SQL_PORT = '3306'
localhost = 'serina-qa-server1.mysql.database.azure.com'
engine = create_engine(f'mysql+pymysql://{SQL_USER}:{SQL_PASS}@{localhost}:{SQL_PORT}/{SQL_DB}')
connection = engine.connect()


# In[54]:


client_id = "9f75db6c-2c6e-4ac1-a26c-73d5799b3ca6"
client_secret = "r1IL.3~7wlbG1yaV3c4OoA_X~ly_h4.j2f"
res='https://ehgerpint.sandbox.operations.dynamics.com'
# scope = "appstore::apps:readwrite"
grant_type = "client_credentials"
data = {
    "grant_type": grant_type,
    "client_id": client_id,
    "client_secret": client_secret,
    "resource": res
}
amazon_auth_url = "https://login.microsoftonline.com/emaarproperties.onmicrosoft.com/oauth2/token"
auth_response = requests.post(amazon_auth_url, data=data)

# Read token from auth response
auth_response_json = auth_response.json()
auth_token = auth_response_json["access_token"]
auth_token_header_value = "Bearer %s" % auth_token
headers = {"Authorization": auth_token_header_value}


# In[5]:


#for organisation
org_url='https://ehgerpint.sandbox.operations.dynamics.com/data/SER_OrganizationDatas'
organisation_data = requests.get(org_url, headers=headers).json()
organisation_df=pd.DataFrame(organisation_data['value'])
organisation_df = organisation_df.iloc[: , 1:]


# In[24]:


#for vendor
vendor_url="https://ehgerpint.sandbox.operations.dynamics.com/data/SER_VendorDatas?cross-company=true&$filter=((dataAreaId eq 'RTP') or (dataAreaId eq 'RDD') or (dataAreaId eq 'RWH') or (dataAreaId eq 'REX') or (dataAreaId eq 'RCC') or (dataAreaId eq 'RTC') or (dataAreaId eq 'RHC') or (dataAreaId eq 'RDM') or (dataAreaId eq 'RLM') or (dataAreaId eq 'RCL') or (dataAreaId eq 'RHM') or (dataAreaId eq 'RHH')) and CreateDateTime ge "+date+"T00:00:00.000Z"
vendor_data = requests.get(vendor_url, headers=headers).json()
vendor_df=pd.DataFrame(vendor_data['value'])
vendor_df = vendor_df.iloc[: , 1:]


# In[59]:


#for po header
poheader_url="https://ehgerpint.sandbox.operations.dynamics.com/data/SER_PurchaseOrderHeaderDatas?cross-company=true&$filter=((dataAreaId eq 'RTP') or (dataAreaId eq 'RDD') or (dataAreaId eq 'RWH') or (dataAreaId eq 'REX') or (dataAreaId eq 'RCC') or (dataAreaId eq 'RTC') or (dataAreaId eq 'RHC') or (dataAreaId eq 'RDM') or (dataAreaId eq 'RLM') or (dataAreaId eq 'RCL') or (dataAreaId eq 'RHM') or (dataAreaId eq 'RHH')) and CreateDateTime ge "+date+"T00:00:00.000Z"
poheader_data = requests.get(poheader_url, headers=headers).json()
poheader_df=pd.DataFrame(poheader_data['value'])
poheader_df = poheader_df.iloc[: , 1:]


# In[45]:


#for po line
poline_url="https://ehgerpint.sandbox.operations.dynamics.com/data/SER_PurchaseOrderLinesDatas?cross-company=true&$filter=((dataAreaId eq 'RTP') or (dataAreaId eq 'RDD') or (dataAreaId eq 'RWH') or (dataAreaId eq 'REX') or (dataAreaId eq 'RCC') or (dataAreaId eq 'RTC') or (dataAreaId eq 'RHC') or (dataAreaId eq 'RDM') or (dataAreaId eq 'RLM') or (dataAreaId eq 'RCL') or (dataAreaId eq 'RHM') or (dataAreaId eq 'RHH')) and CreateDateTime ge "+date+"T00:00:00.000Z"
poline_data = requests.get(poline_url, headers=headers).json()
poline_df=pd.DataFrame(poline_data['value'])
poline_df = poline_df.iloc[: , 1:]


# In[34]:


#for slip header
pslipheader_url="https://ehgerpint.sandbox.operations.dynamics.com/data/SER_PackingSlipHeaderDatas?cross-company=true&$filter=((dataAreaId eq 'RTP') or (dataAreaId eq 'RDD') or (dataAreaId eq 'RWH') or (dataAreaId eq 'REX') or (dataAreaId eq 'RCC') or (dataAreaId eq 'RTC') or (dataAreaId eq 'RHC') or (dataAreaId eq 'RDM') or (dataAreaId eq 'RLM') or (dataAreaId eq 'RCL') or (dataAreaId eq 'RHM') or (dataAreaId eq 'RHH')) and DeliveryDate ge "+date+"T00:00:00Z"
pslipheader_data = requests.get(pslipheader_url, headers=headers).json()
pslipheader_df=pd.DataFrame(pslipheader_data['value'])
pslipheader_df = pslipheader_df.iloc[: , 1:]                                                                                                           


# In[35]:


#for slip line
pslipline_url="https://ehgerpint.sandbox.operations.dynamics.com/data/SER_PackingSlipLinesDatas?cross-company=true&$filter=((dataAreaId eq 'RTP') or (dataAreaId eq 'RDD') or (dataAreaId eq 'RWH') or (dataAreaId eq 'REX') or (dataAreaId eq 'RCC') or (dataAreaId eq 'RTC') or (dataAreaId eq 'RHC') or (dataAreaId eq 'RDM') or (dataAreaId eq 'RLM') or (dataAreaId eq 'RCL') or (dataAreaId eq 'RHM') or (dataAreaId eq 'RHH')) and DeliveryDate ge "+date+"T00:00:00Z"
pslipline_data = requests.get(pslipline_url, headers=headers).json()
pslipline_df=pd.DataFrame(pslipline_data['value'])
pslipline_df = pslipline_df.iloc[: , 1:]


# In[37]:


# #for COA
# coa_url="https://ehgerpint.sandbox.operations.dynamics.com/data/SER_ChartOfAccountDatas?cross-company=true&$filter=CreateDateTime ge "+date+"T00:00:00.000Z"
# coa_data = requests.get(coa_url, headers=headers).json()
# coa_df=pd.DataFrame(coa_data['value'])
# coa_df = coa_df.iloc[: , 1:]


# In[63]:


#for items
item_url="https://ehgerpint.sandbox.operations.dynamics.com/data/SER_ItemDatas?cross-company=true&$filter=((dataAreaId eq 'RTP') or (dataAreaId eq 'RDD') or (dataAreaId eq 'RWH') or (dataAreaId eq 'REX') or (dataAreaId eq 'RCC') or (dataAreaId eq 'RTC') or (dataAreaId eq 'RHC') or (dataAreaId eq 'RDM') or (dataAreaId eq 'RLM') or (dataAreaId eq 'RCL') or (dataAreaId eq 'RHM') or (dataAreaId eq 'RHH')) and CreateDateTime ge  cast("+date+"T00:00:00Z,Edm.DateTimeOffset)"
item_data = requests.get(item_url, headers=headers).json()
item_df=pd.DataFrame(item_data['value'])
item_df = item_df.iloc[: , 1:]
item_df.shape


# In[59]:


#for vendor
vendor_url_up="https://ehgerpint.sandbox.operations.dynamics.com/data/SER_ModifyVendorDatas?cross-company=true&$filter=((dataAreaId eq 'RTP') or (dataAreaId eq 'RDD') or (dataAreaId eq 'RWH') or (dataAreaId eq 'REX') or (dataAreaId eq 'RCC') or (dataAreaId eq 'RTC') or (dataAreaId eq 'RHC') or (dataAreaId eq 'RDM') or (dataAreaId eq 'RLM') or (dataAreaId eq 'RCL') or (dataAreaId eq 'RHM') or (dataAreaId eq 'RHH')) and ModifyDateTime ge "+date+"T00:00:00Z"
vendor_data_up = requests.get(vendor_url_up, headers=headers).json()
vendor_df_up=pd.DataFrame(vendor_data_up['value'])
vendor_df_up = vendor_df_up.iloc[: , 1:]


# In[34]:


#for po header
poheader_url_up="https://ehgerpint.sandbox.operations.dynamics.com/data/SER_ModifyPurchaseOrderDatas?cross-company=true&$filter=((dataAreaId eq 'RTP') or (dataAreaId eq 'RDD') or (dataAreaId eq 'RWH') or (dataAreaId eq 'REX') or (dataAreaId eq 'RCC') or (dataAreaId eq 'RTC') or (dataAreaId eq 'RHC') or (dataAreaId eq 'RDM') or (dataAreaId eq 'RLM') or (dataAreaId eq 'RCL') or (dataAreaId eq 'RHM') or (dataAreaId eq 'RHH')) and ModifyDateTime ge "+date+"T00:00:00.000Z"
poheader_data_up = requests.get(poheader_url_up, headers=headers).json()
poheader_df_up=pd.DataFrame(poheader_data_up['value'])
poheader_df_up = poheader_df_up.iloc[: , 1:]
poheader_df_up


# In[44]:


#for po line
poline_url_up="https://ehgerpint.sandbox.operations.dynamics.com/data/SER_ModifyPurchaseOrderLinesDatas?cross-company=true&$filter=((dataAreaId eq 'RTP') or (dataAreaId eq 'RDD') or (dataAreaId eq 'RWH') or (dataAreaId eq 'REX') or (dataAreaId eq 'RCC') or (dataAreaId eq 'RTC') or (dataAreaId eq 'RHC') or (dataAreaId eq 'RDM') or (dataAreaId eq 'RLM') or (dataAreaId eq 'RCL') or (dataAreaId eq 'RHM') or (dataAreaId eq 'RHH')) and ModifyDateTime ge "+date+"T00:00:00.000Z"
poline_data_up = requests.get(poline_url_up, headers=headers).json()
poline_df_up=pd.DataFrame(poline_data_up['value'])
poline_df_up = poline_df_up.iloc[: , 1:]


# In[ ]:


# engine.execute(sa_text('''TRUNCATE TABLE d3agi_organization''').execution_options(autocommit=True))
# organisation_df.to_sql('d3agi_organization', con = engine, if_exists = 'append', chunksize = 1000,index= False)


# In[ ]:


# engine.execute(sa_text('''TRUNCATE TABLE d3agi_vendor''').execution_options(autocommit=True))
# vendor_df.to_sql('d3agi_vendor', con = engine, if_exists = 'append', chunksize = 1000,index= False)


# In[ ]:


engine.execute(sa_text('''TRUNCATE TABLE d3agi_vendorupdate''').execution_options(autocommit=True))
vendor_df_up.to_sql('d3agi_vendorupdate', con = engine, if_exists = 'append', chunksize = 1000,index= False)


# In[72]:


engine.execute(sa_text('''TRUNCATE TABLE d3agi_poheader''').execution_options(autocommit=True))
poheader_df.to_sql('d3agi_poheader', con = engine, if_exists = 'append', chunksize = 1000,index= False)


# In[43]:


engine.execute(sa_text('''TRUNCATE TABLE d3agi_poheaderupdate''').execution_options(autocommit=True))
poheader_df_up.to_sql('d3agi_poheaderupdate', con = engine, if_exists = 'append', chunksize = 1000,index= False)


# In[73]:


engine.execute(sa_text('''TRUNCATE TABLE d3agi_poline''').execution_options(autocommit=True))
poline_df.to_sql('d3agi_poline', con = engine, if_exists = 'append', chunksize = 1000,index= False)


# In[53]:


engine.execute(sa_text('''TRUNCATE TABLE d3agi_polineupdate''').execution_options(autocommit=True))
poline_df_up.to_sql('d3agi_polineupdate', con = engine, if_exists = 'append', chunksize = 1000,index= False)


# In[ ]:


engine.execute(sa_text('''TRUNCATE TABLE d3agi_slipheader''').execution_options(autocommit=True))
pslipheader_df.to_sql('d3agi_slipheader', con = engine, if_exists = 'append', chunksize = 1000,index= False)


# In[ ]:


engine.execute(sa_text('''TRUNCATE TABLE d3agi_slipline''').execution_options(autocommit=True))
pslipline_df.to_sql('d3agi_slipline', con = engine, if_exists = 'append', chunksize = 1000,index= False)


# In[ ]:


# engine.execute(sa_text('''TRUNCATE TABLE d3agi_coa''').execution_options(autocommit=True))
# coa_df.to_sql('d3agi_coa', con = engine, if_exists = 'append', chunksize = 1000,index= False)


# In[ ]:


engine.execute(sa_text('''TRUNCATE TABLE d3agi_item''').execution_options(autocommit=True))
item_df.to_sql('d3agi_item', con = engine, if_exists = 'append', chunksize = 1000,index= False)

