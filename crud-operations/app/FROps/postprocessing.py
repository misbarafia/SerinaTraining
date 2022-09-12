import json,os
import re
from collections import Counter
import pandas as pd
import sys
import traceback
import datetime
sys.path.append("..")
import model
from session.session import DB
from dateutil import parser
from logModule import applicationlogging, email_sender
from session import SQLALCHEMY_DATABASE_URL, DB, engine
from session import Session as SessionLocal
from session.notificationsession import client as mqtt
from fuzzywuzzy import fuzz
import time
SQL_DB = DB
import pytz as tz
tz_region_name = os.getenv("serina_tz", "Asia/Dubai")
tz_region = tz.timezone(tz_region_name)

# Background task publisher
def meta_data_publisher(msg):
    try:
        mqtt.publish("notification_processor", json.dumps(msg), qos=2, retain=True)
    except Exception as e:
        pass


def date_cnv(doc_date, date_format):
    correctDate = None
    get_date = {'jan': '01',
                'feb': '02', 'mar': '03', 'apr': '04', 'may': '05', 'jun': '06', 'jul': '07', 'aug': '08',
                'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12'}

    date_status = 0
    req_date = doc_date

    try:

        if date_format in ["mm.dd.yyyy", "mm-dd-yyyy", "mm/dd/yyyy", "mm dd yyyy", "mm.dd.yy", "mm/dd/yy","mm dd yy","mm/dd/yyyy","mm/dd/yy","mm.dd.yyyy"]:
            doc_dt_slt = re.findall(r'\d+', doc_date)
            if len(doc_dt_slt) == 3:
                mm = doc_dt_slt[0]
                dd = doc_dt_slt[1]
                yy = doc_dt_slt[2]
                if len(dd) == 1:
                    dd = "0" + str(dd)
                if len(yy) == 2:
                    yy = '20' + str(yy)
                if len(mm) == 1:
                    mm = "0" + str(mm)
                req_date = yy + "-" + mm + "-" + dd
                date_status = 1

            elif len(doc_dt_slt) == 2:
                if doc_date[:3].lower() in list(get_date.keys()):
                    dd = doc_dt_slt[0]
                    yy = doc_dt_slt[1]
                    mm = get_date[doc_date[:3].lower()]
                    if len(dd) == 1:
                        dd = "0" + str(dd)
                    if len(yy) == 2:
                        yy = '20' + str(yy)
                    if len(mm) == 1:
                        mm = "0" + str(mm)
                    req_date = yy + "-" + mm + "-" + dd
                    date_status = 1
                else:
                    date_status = 0
                    req_date = doc_date
            else:
                date_status = 0
                req_date = doc_date
        elif date_format in ["dd-mm-yy", "dd mm yy", "dd.mm.yy", "dd.mm.yyyy", "dd-mm-yyyy", "dd mm yyyy", "dd/mm/yy",
                             "dd mm yy", "dd mm yyyy","dd.mm.yyyy","dd/mm/yy","dd-mmm-yy","dd-mm-yyyy","dd-mm-yy"]:
            doc_dt_slt = re.findall(r'\d+', doc_date)
            if len(doc_dt_slt) == 3:
                dd = doc_dt_slt[0]
                mm = doc_dt_slt[1]
                yy = doc_dt_slt[2]
                if len(dd) == 1:
                    dd = "0" + str(dd)
                if len(yy) == 2:
                    yy = '20' + str(yy)
                if len(mm) == 1:
                    mm = "0" + str(mm)
                req_date = yy + "-" + mm + "-" + dd
                date_status = 1
            elif len(doc_dt_slt) == 2:
                date_res = re.split('([-+]?\d+\.\d+)|([-+]?\d+)', doc_date.strip())
                res_f = [r.strip() for r in date_res if r is not None and r.strip() != '']
                while 'th' in res_f:
                    res_f.remove('th')
                for mnt_ck in range(len(res_f)):
                    while res_f[mnt_ck][0].isalnum() == 0:
                        res_f[mnt_ck] = res_f[mnt_ck][1:]
                    while res_f[mnt_ck][-1].isalnum() == 0:
                        res_f[mnt_ck] = res_f[mnt_ck][:-1]
                if ' ' in res_f[1]:
                    sp_ck_mnt = res_f[1].split(' ')
                    for cr_mth in sp_ck_mnt:
                        if cr_mth[:3].lower() in list(get_date.keys()):
                            mm = get_date[cr_mth[:3].lower()]
                            dd = doc_dt_slt[0]
                            yy = doc_dt_slt[1]
                            if len(dd) == 1:
                                dd = "0" + str(dd)
                            if len(mm) == 1:
                                mm = "0" + str(mm)
                            if len(yy) == 2:
                                yy = '20' + str(yy)
                            req_date = yy + "-" + mm + "-" + dd
                            date_status = 1
                            break;
                elif res_f[1][:3].lower() in list(get_date.keys()):
                    mm = get_date[res_f[1][:3].lower()]
                    dd = doc_dt_slt[0]
                    yy = doc_dt_slt[1]
                    if len(dd) == 1:
                        dd = "0" + str(dd)
                    if len(yy) == 2:
                        yy = '20' + str(yy)
                    if len(mm) == 1:
                        mm = "0" + str(mm)
                    req_date = yy + "-" + mm + "-" + dd
                    date_status = 1
                else:
                    date_status = 0
                    req_date = doc_date
            else:
                date_status = 0
                req_date = doc_date
        elif date_format in ["yyyy mm dd", "yyyy.mm.dd"]:
            doc_dt_slt = re.findall(r'\d+', doc_date)
            if len(doc_dt_slt) == 3:
                yy = doc_dt_slt[0]
                mm = doc_dt_slt[1]
                dd = doc_dt_slt[2]
                if len(dd) == 1:
                    dd = "0" + str(dd)
                if len(yy) == 2:
                    yy = '20' + str(yy)
                if len(mm) == 1:
                    mm = "0" + str(mm)
                req_date = yy + "-" + mm + "-" + dd
                date_status = 1
            elif len(doc_dt_slt) == 2:
                date_res = re.split('([-+/]?!S)|([-+]?\d+\.\d+)|([-+/]?\d+)', doc_date.strip())
                res_f = [r.strip() for r in date_res if r is not None and r.strip() != '']
                while 'th' in res_f:
                    res_f.remove('th')
                for mnt_ck in range(len(res_f)):
                    while res_f[mnt_ck][0].isalnum() == 0:
                        res_f[mnt_ck] = res_f[mnt_ck][1:]
                    while res_f[mnt_ck][-1].isalnum() == 0:
                        res_f[mnt_ck] = res_f[mnt_ck][:-1]
                if ' ' in res_f[1]:
                    sp_ck_mnt = res_f[1].split(' ')
                    for cr_mth in sp_ck_mnt:
                        if cr_mth[:3].lower() in list(get_date.keys()):
                            mm = get_date[cr_mth[:3].lower()]
                            dd = doc_dt_slt[0]
                            yy = doc_dt_slt[1]
                            if len(dd) == 1:
                                dd = "0" + str(dd)
                            if len(mm) == 1:
                                mm = "0" + str(mm)
                            if len(yy) == 2:
                                yy = '20' + str(yy)
                            req_date = yy + "-" + mm + "-" + dd
                            date_status = 1
                elif res_f[1][:3].lower() in list(get_date.keys()):
                    mm = get_date[res_f[1][:3].lower()]
                    yy = doc_dt_slt[0]
                    dd = doc_dt_slt[1]
                    if len(dd) == 1:
                        dd = "0" + str(dd)
                    if len(yy) == 2:
                        yy = '20' + str(yy)
                    if len(mm) == 1:
                        mm = "0" + str(mm)
                    req_date = yy + "-" + mm + "-" + dd
                    date_status = 1
                else:
                    date_status = 0
                    req_date = doc_date
            else:
                date_status = 0
                req_date = doc_date
    except Exception as dt_ck_:
        print(str(dt_ck_))
        date_status = 0
        req_date = doc_date
    if date_status == 1:
        try:
            newDate = datetime.datetime(int(yy), int(mm), int(dd))
            correctDate = True
        except ValueError:
            correctDate = False
        print(str(correctDate))
        if correctDate == False:
            date_status = 0

    return req_date, date_status


def tb_cln_amt(amt):
    cln_amt_sts = 0
    amt_cpy = amt
    # amt = amt.replace(',','.')
    try:
        if ',' in amt:
            if amt[-3] == ',':
                print('yes')
                amt = amt[:-3] + "." + amt[-2:]
    except Exception as at:
        print(at)
        amt = amt_cpy
    try:
        inl = 1
        fn = 0
        sb_amt = ''
        for amt_sp in amt:
            # print(amt_sp)
            if amt_sp.isdigit():
                sb_amt = sb_amt + amt_sp
                inl = inl * 1
                fn = 1
            elif (inl == 1) and (amt_sp == '.') and fn == 1:
                # print('------')
                sb_amt = sb_amt + amt_sp
                inl = 2
        sb_amt = float(sb_amt)
        # cln_amt_sts = 1

    except Exception as e:
        sb_amt = amt
        print(str(e))
        sb_amt = str(sb_amt)

    return sb_amt


def cln_amt(amt):
    amt_cpy = amt
    # amt = str(amt).replace(',','.')
    try:
        if ',' in amt:
            if amt[-3] == ',':
                print('yes')
                amt = amt[:-3] + "." + amt[-2:]
    except Exception as er:
        amt = amt_cpy

    if len(amt) > 0:
        if len(re.findall("\d+\,\d+\d+\.\d+", amt)) > 0:
            cl_amt = re.findall("\d+\,\d+\d+\.\d+", amt)[0]
            cl_amt = float(cl_amt.replace(",", ""))
        elif len(re.findall("\d+\.\d+", amt)) > 0:
            cl_amt = re.findall("\d+\.\d+", amt)[0]
            cl_amt = float(cl_amt)
        elif len(re.findall("\d+", amt)) > 0:
            cl_amt = re.findall("\d+", amt)[0]
            cl_amt = float(cl_amt)
        else:
            cl_amt = amt
    else:
        cl_amt = amt
    return cl_amt


def dataPrep_postprocess_prebuilt(input_data):
    all_pg_data = {}
    # def dataPrep_postprocess(input_data):
    getData_headerPg = {}  # replace with pg_1['analyzeResult']['documentResults'][0]['fields']

    for pg_data in input_data:
        # print(pg_data['analyzeResult']['documentResults'][0]['fields'].keys())
        pre_pg_data = pg_data['analyzeResult']['documentResults'][0]['fields'].copy()

        for tgs in pre_pg_data:
            # print(tgs)

            if tgs not in ('Items'):
                if tgs in getData_headerPg:
                    if (getData_headerPg[tgs]['confidence']) < (pre_pg_data[tgs]['confidence']):
                        getData_headerPg.update({tgs: pre_pg_data[tgs]})
                else:
                    getData_headerPg[tgs] = pre_pg_data[tgs]

    all_pg_data = input_data[0].copy()
    all_pg_data['analyzeResult']['documentResults'][0]['fields'] = getData_headerPg

    return all_pg_data

def tab_to_dict(new_invoLineData_df,itemCode,typ = ''):
    invo_NW_itemDict = {}
    des = ''
    for itmId in list(new_invoLineData_df[itemCode].unique()):
        tmpdf = new_invoLineData_df[new_invoLineData_df[itemCode]==itmId].reset_index(drop=True)
        tmpdict = {}
        for ch in range(0,len(tmpdf)):
            val = tmpdf['Value'][ch]
            tg_nm = tmpdf['TagName'][ch]
            if tg_nm in ['Description','Quantity']:
                if tg_nm=='Description':
                    des = val
                tmpdict[tg_nm] =val
        if typ =='grn':
            invo_NW_itemDict[itmId] = tmpdict
        else:
            invo_NW_itemDict[itmId+"__"+des] = tmpdict
    return invo_NW_itemDict


def dataPrep_postprocess_cust(input_data):
    # print("input_data len: ",len(input_data))
    all_pg_data = {}
    # def dataPrep_postprocess(input_data):
    getData_headerPg = {}  # replace with pg_1['analyzeResult']['documentResults'][0]['fields']
    getData_TabPg = []  # pg_1['analyzeResult']['documentResults'][0]['fields']['tab_1']['valueArray']
    cnt = 0
    for pg_data in input_data:
        # print(pg_data['analyzeResult']['documentResults'][0]['fields'].keys())
        cust_pg_data = pg_data['analyzeResult']['documentResults'][0]['fields'].copy()
        cust_tab_pg_data = pg_data['analyzeResult']['documentResults'][0]['fields']['tab_1'][
            'valueArray'].copy() if 'valueArray' in pg_data['analyzeResult']['documentResults'][0]['fields'][
            'tab_1'] else []
        # print("cust_tab_pg_data: ",len(cust_tab_pg_data))
        for pg_rw in cust_tab_pg_data:
            cnt = cnt + 1
            print("rw cnt: ", cnt)
            getData_TabPg.append(pg_rw)

        for tgs in cust_pg_data:
            if tgs not in ('tab_1', 'tab_2', 'tab_3', 'tab_3'):
                if tgs in getData_headerPg.keys():
                    if 'text' in cust_pg_data[tgs]:
                        if (getData_headerPg[tgs]['confidence']) < (cust_pg_data[tgs]['confidence']):
                            getData_headerPg.update({tgs: cust_pg_data[tgs]})
                else:
                    getData_headerPg[tgs] = cust_pg_data[tgs]
    # print("tab len: ",len(getData_TabPg))
    all_pg_data = input_data[0].copy()
    all_pg_data['analyzeResult']['documentResults'][0]['fields'] = getData_headerPg
    print(getData_headerPg)
    # tb_dict = {'tab_1': {'type': 'array', 'valueArray': getData_TabPg}}
    # all_pg_data['analyzeResult']['documentResults'][0]['fields']['tab_1'] =}
    # all_pg_data['analyzeResult']['documentResults'][0]['fields']
    all_pg_data['analyzeResult']['documentResults'][0]['fields']['tab_1'] = {'type': 'array',
                                                                             'valueArray': getData_TabPg}
    # ['tab_1']['valueArray']
    return all_pg_data


def postpro(cst_data_, pre_data_, date_format, invo_model_id, SQLALCHEMY_DATABASE_URL, entityID, vendorAccountID,
            bg_task, filename,
            db, sender):
    # SQLALCHEMY_DATABASE_URL = f'mysql+pymysql://{SQL_USER}:{SQL_PASS}@{localhost}:{SQL_PORT}/{SQL_DB}'

    #     with open('/datadrive/SERINA/API/V1.2/app/train_docs/cst_data_new.txt', 'w') as fl:
    #         fl.write(json.dumps(cst_data))
    #         fl.close()
    #     with open('/datadrive/SERINA/API/V1.2/app/train_docs/pre_data_new.txt', 'w') as fl:
    #         fl.write(json.dumps(pre_data))
    #         fl.close()

    # print(cst_data)
    # print()
    # print(pre_data)
    global qty_rw_status, amt_withTax_rw_status, vatAmt_rw_status, utprice_rw_status, vatAmt_rw, amt_withTax_rw, discount_rw_status
    duplicate_status = 1
    print("cst_data_: ", len(cst_data_), " pre_data_:", len(pre_data_))
    default_qty_ut = 0
    tab_cal_unitprice = 0
    subtotal_Cal = 0
    tab_cal_unitprice_AmtExcTax = 0
    cust_oly = 0
    missing_rw_tab = []
    subtotal_rw = ''
    totaldiscount_rw = ''
    totalTax_rw = ''
    invoiceTotal_rw = ''
    skp_tab_mand_ck = 0

    try:

        print("in posrprocessing: below try")
        cst_data = dataPrep_postprocess_cust(cst_data_)
        pre_data = dataPrep_postprocess_prebuilt(pre_data_)
        with open('cust_data.json', 'w') as f1:
            f1.write(json.dumps(cst_data))

        with open('prebuilt_data.json', 'w') as f2:
            f2.write(json.dumps(pre_data))
        print("Both cust n prebuilt ready !!")
        fr_lab_String = "SELECT mandatoryheadertags,mandatorylinetags,erprule,idInvoiceModel FROM " + DB + ".frmetadata WHERE idInvoiceModel=" + str(
            invo_model_id) + ";"
        fr_lab_df = pd.read_sql(fr_lab_String, SQLALCHEMY_DATABASE_URL)
        mandatory_header = list(fr_lab_df['mandatoryheadertags'])[0].split(",")
        mandatory_tab_col = list(fr_lab_df['mandatorylinetags'])[0].split(",")

        try:
            erprule = int(list(fr_lab_df['erprule'])[0])
            print("erprule: ", erprule)
            if erprule == 5:
                default_qty_ut = 1
            else:
                default_qty_ut = 0
            if erprule == 6:
                tab_cal_unitprice = 1
            else:
                tab_cal_unitprice = 0
            if erprule == 7:
                tab_cal_unitprice_AmtExcTax = 1
                subtotal_Cal = 1
            else:
                tab_cal_unitprice_AmtExcTax = 0
                subtotal_Cal = 0
            if erprule == 2:
                skp_tab_mand_ck = 1
            else:
                skp_tab_mand_ck = 0





        except Exception as ep:
            print("postprocessing Exception: ", str(ep))
        try:
            et_idInvoiceModel = int(list(fr_lab_df['idInvoiceModel'])[0])
            print("et_idInvoiceModel: ", et_idInvoiceModel)
            if et_idInvoiceModel == 312:
                cust_oly = 1
            else:
                cust_oly = 0


        except Exception as ep:
            print("postprocessing Exception: ", str(ep))

        cst_tmp_dict = {}
        print(cst_data['analyzeResult']['documentResults'][0]['fields'])
        for cst_hd in cst_data['analyzeResult']['documentResults'][0]['fields']:
            if 'text' in cst_data['analyzeResult']['documentResults'][0]['fields'][cst_hd]:
                if 'boundingBox' in cst_data['analyzeResult']['documentResults'][0]['fields'][cst_hd].keys():
                    cst_tmp_dict[cst_hd] = {
                        'text': cst_data['analyzeResult']['documentResults'][0]['fields'][cst_hd]['text'],
                        'confidence': cst_data['analyzeResult']['documentResults'][0]['fields'][cst_hd][
                            'confidence'],
                        'boundingBox': cst_data['analyzeResult']['documentResults'][0]['fields'][cst_hd]['boundingBox']}
                else:
                    cst_tmp_dict[cst_hd] = {
                        'text': cst_data['analyzeResult']['documentResults'][0]['fields'][cst_hd]['text'],
                        'confidence': 0,
                        'boundingBox': ''}
        pre_tmp_dict = {}
        for pre_hd in pre_data['analyzeResult']['documentResults'][0]['fields']:

            if 'text' in pre_data['analyzeResult']['documentResults'][0]['fields'][pre_hd]:
                pre_tmp_dict[pre_hd] = {
                    'text': pre_data['analyzeResult']['documentResults'][0]['fields'][pre_hd]['text'],
                    'confidence': pre_data['analyzeResult']['documentResults'][0]['fields'][pre_hd][
                        'confidence'] if 'confidence' in pre_data['analyzeResult']['documentResults'][0]['fields'][
                        pre_hd] else "0",
                    'boundingBox': pre_data['analyzeResult']['documentResults'][0]['fields'][pre_hd][
                        'boundingBox'] if 'boundingBox' in pre_data['analyzeResult']['documentResults'][0]['fields'][
                        pre_hd] else [0, 0, 0, 0, 0, 0]}

                # print(pre_hd)
        pre_dict = pre_tmp_dict
        cst_dict = cst_tmp_dict
        # print('PRE: ', pre_dict.keys())
        # print(cst_dict.keys())
        '''# cmt later -----------------***************************************
        cst_dict['InvoiceId'] = cst_tmp_dict['invoice_number']
        cst_dict['InvoiceDate'] = cst_tmp_dict['invoice_date']
        cst_dict['PurchaseOrder'] = cst_tmp_dict['po_number']'''

        sm_tag = set(cst_dict.keys()).intersection(set(pre_dict.keys()))
        cst_tag = set(cst_dict.keys()).difference(sm_tag)
        fr_headers = []
        ovrll_conf_ck = 1
        field_threshold = 0.7
        status_message = ""
        for hd_tags in sm_tag:
            tmp_fr_headers = {}
            # print(cst_dict[hd_tags]['confidence'])
            pre_conf = float(pre_dict[hd_tags]['confidence'])
            cst_conf = float(cst_dict[hd_tags]['confidence'])
            print("diff cust n pre-------", abs(pre_conf - cst_conf))
            # tmp_fr_headers[hd_tags] = {'value':val,'prebuilt_confidence':,'custom_confidence'}
            if max(cst_conf, pre_conf) >= field_threshold:
                tag_status = 1

            else:
                tag_status = 0
                ovrll_conf_ck = ovrll_conf_ck * 0

                try:
                    status_message = "Low confidence: " + str(max(cst_conf, pre_conf) * 100) + "%."
                except Exception as et:
                    status_message = "Low confidence,Please review."

            '''print('cst_conf < pre_conf', cst_conf < pre_conf)
            print('pre_conf < cst_conf', pre_conf < cst_conf)
            print('pre_conf == cst_conf', pre_conf == cst_conf)
            print(" cst_conf[hd_tags]['text']", cst_dict[hd_tags]['text'])'''
            if cust_oly == 1:
                if 'text' in cst_dict[hd_tags]:
                    tag_val = cst_dict[hd_tags]['text']
                if 'boundingBox' in cst_dict[hd_tags]:
                    bounding_bx = cst_dict[hd_tags]['boundingBox']
            else:

                if cst_conf < pre_conf:
                    if hd_tags == 'VendorName':
                        if 'text' in cst_dict[hd_tags]:
                            tag_val = cst_dict[hd_tags]['text']
                        if 'boundingBox' in cst_dict[hd_tags]:
                            bounding_bx = cst_dict[hd_tags]['boundingBox']
                    if (cst_conf + 0.2) > pre_conf:
                        if 'text' in cst_dict[hd_tags]:
                            tag_val = cst_dict[hd_tags]['text']
                        if 'boundingBox' in cst_dict[hd_tags]:
                            bounding_bx = cst_dict[hd_tags]['boundingBox']
                    else:
                        if 'text' in pre_dict[hd_tags]:
                            tag_val = pre_dict[hd_tags]['text']
                        if 'boundingBox' in pre_dict[hd_tags]:
                            bounding_bx = pre_dict[hd_tags]['boundingBox']
                elif pre_conf < cst_conf:
                    if 'text' in cst_dict[hd_tags]:
                        tag_val = cst_dict[hd_tags]['text']
                    if 'boundingBox' in cst_dict[hd_tags]:
                        bounding_bx = cst_dict[hd_tags]['boundingBox']
                elif (pre_conf == cst_conf):
                    if 'text' in cst_dict[hd_tags]:
                        tag_val = cst_dict[hd_tags]['text']
                    if 'boundingBox' in cst_dict[hd_tags]:
                        bounding_bx = cst_dict[hd_tags]['boundingBox']
                if (pre_conf < cst_conf) and (abs(pre_conf - cst_conf) > 0.3):
                    print("diff cust n pre-------", abs(pre_conf - cst_conf))

                    if (pre_conf == '' and cst_conf < field_threshold) or cst_conf < field_threshold:
                        tag_status = 0
                        ovrll_conf_ck = ovrll_conf_ck * 0
                        status_message = "Low confidence: " + str(cst_conf * 100) + "%."
                    else:
                        print("prebuilt conf empty")
                        status_message = "Low prebuilt Confidence"

            tmp_fr_headers['tag'] = hd_tags
            tmp_fr_headers['data'] = {'value': tag_val, 'prebuilt_confidence': str(pre_conf),
                                      'custom_confidence': str(cst_conf)}
            bx = {}
            bo_bx = bounding_bx
            x = str(bo_bx[0])
            y = str(bo_bx[1])
            w = str(bo_bx[2] - bo_bx[0])
            h = str(bo_bx[5] - bo_bx[1])
            bx['x'] = x
            bx['y'] = y
            bx['w'] = w
            bx['h'] = h
            tmp_fr_headers['boundingBox'] = bx

            '''tmp_fr_headers[hd_tags] = {'value': tag_val, 'prebuilt_confidence': str(pre_conf),
                                    'custom_confidence': str(cst_conf)}'''

            tmp_fr_headers['status'] = tag_status
            tmp_fr_headers['status_message'] = status_message
            fr_headers.append(tmp_fr_headers)
        for ct_tag in cst_tag:
            tmp_fr_headers = {}
            if 'text' in cst_dict[ct_tag]:
                if 'confidence' in cst_dict[ct_tag]:
                    cst_conf = float(cst_dict[ct_tag]['confidence'])
                tag_val = cst_dict[ct_tag]['text']
                if 'boundingBox' in cst_dict[ct_tag]:
                    bounding_bx = cst_dict[ct_tag]['boundingBox']
                if cst_conf >= field_threshold:
                    tag_status = 1
                    status_message = "NO OCR issue"
                else:
                    tag_status = 0
                    status_message = "Low confidence: " + str(cst_conf * 100) + "%."
                    ovrll_conf_ck = ovrll_conf_ck * 0
                tmp_fr_headers['tag'] = ct_tag
                tmp_fr_headers['data'] = {'value': tag_val, 'prebuilt_confidence': '',
                                          'custom_confidence': str(cst_conf)}
                bx = {}
                if bounding_bx != '':
                    bo_bx = bounding_bx
                    x = str(bo_bx[0])
                    y = str(bo_bx[1])
                    w = str(bo_bx[2] - bo_bx[0])
                    h = str(bo_bx[5] - bo_bx[1])
                    bx['x'] = x
                    bx['y'] = y
                    bx['w'] = w
                    bx['h'] = h
                    tmp_fr_headers['boundingBox'] = bx
                    tmp_fr_headers['status'] = tag_status
                    tmp_fr_headers['status_message'] = status_message
                else:
                    tag_status = 0
                    tmp_fr_headers['boundingBox'] = bx
                    tmp_fr_headers['status'] = tag_status
                    tmp_fr_headers['status_message'] = status_message
            fr_headers.append(tmp_fr_headers)
        overall_status = ovrll_conf_ck

        # pageRange = cst_data['analyzeResult']['documentResults'][0]['pageRange']

        cst_data['analyzeResult']['documentResults'][0]
        fields = cst_data['analyzeResult']['documentResults'][0]['fields']
        # tab data:
        tabs = [tb for tb in list(cst_data['analyzeResult']['documentResults'][0]['fields'].keys()) if
                tb.startswith('tab_')]
        # print("tabs: ", tabs)
        itm_list = []
        # fields = cst_data['analyzeResult']['documentResults'][0]['fields']
        ignore_tags = ['SerialNo', 'VAT Amount', 'Item']
        for tbs in tabs:
            if 'valueArray' in fields[tbs]:
                # print(fields[tbs]['valueArray'])
                # print("In post processing: line 433",len(fields[tbs]['valueArray']))
                print("len tab: ", len(fields[tbs]['valueArray']))
                print("fields[tbs]['valueArray']: ", fields[tbs]['valueArray'])
                for itm_no in range(len(fields[tbs]['valueArray'])):
                    tmp_dict = {}
                    tmp_list = []
                    page_no = 1
                    # if 'page' in fields[tbs]['valueArray'][0]['valueObject']['Description']:
                    #     page_no = fields[tbs]['valueArray'][0]['valueObject']['Description']['page']
                    # else:
                    #     page_no = 1
                    ''' tmp_dict['data'] = page_no
                    tmp_dict['tag'] = 'page'
                    tmp_list.append(tmp_dict)'''
                    # tmp_dict = {}
                    print("TABLE Postprocessing start: ----------------------")
                    present_tab_header = []
                    for ky in fields[tbs]['valueArray'][itm_no]['valueObject']:

                        # print(ky)
                        if ky not in ignore_tags:

                            if fields[tbs]['valueArray'][itm_no]['valueObject'][ky] == None:
                                tmp_dict['tag'] = ky
                                print(ky)

                                if fields[tbs]['valueArray'][itm_no]['valueObject'][ky] != "":
                                    tmp_dict['data'] = ""
                                    bx = {}
                                    if 'boundingBox' in fields[tbs]['valueArray'][itm_no]['valueObject'][ky]:
                                        bo_bx = fields[tbs]['valueArray'][itm_no]['valueObject'][ky][
                                            'boundingBox']
                                    else:
                                        bo_bx = [0, 0, 0, 0, 0, 0]
                                    x = str(bo_bx[0])
                                    y = str(bo_bx[1])
                                    w = str(bo_bx[2] - bo_bx[0])
                                    h = str(bo_bx[5] - bo_bx[1])
                                    bx['x'] = x
                                    bx['y'] = y
                                    bx['w'] = w
                                    bx['h'] = h
                                    tmp_dict['boundingBox'] = bx
                                    tmp_list.append(tmp_dict)
                                    tmp_dict = {}
                                else:
                                    tmp_dict['data'] = ''
                                    tmp_dict['boundingBox'] = None

                            else:
                                tmp_dict['tag'] = ky
                                if fields[tbs]['valueArray'][itm_no]['valueObject'][ky] != "":
                                    tmp_dict['data'] = fields[tbs]['valueArray'][itm_no]['valueObject'][ky][
                                        'text'] if 'text' in fields[tbs]['valueArray'][itm_no]['valueObject'][
                                        ky] else ""
                                    bx = {}
                                    bo_bx = fields[tbs]['valueArray'][itm_no]['valueObject'][ky][
                                        'boundingBox'] if 'boundingBox' in \
                                                          fields[tbs]['valueArray'][itm_no]['valueObject'][ky] else [0,
                                                                                                                     0,
                                                                                                                     0,
                                                                                                                     0,
                                                                                                                     0,
                                                                                                                     0]
                                    x = str(bo_bx[0])
                                    y = str(bo_bx[1])
                                    w = str(bo_bx[2] - bo_bx[0])
                                    h = str(bo_bx[5] - bo_bx[1])
                                    bx['x'] = x
                                    bx['y'] = y
                                    bx['w'] = w
                                    bx['h'] = h

                                    tmp_dict['boundingBox'] = bx

                                    if tmp_dict['tag'] in ['AmountExcTax', 'UnitPrice', 'Amount', 'Quantity']:
                                        # call
                                        cl_dt = tb_cln_amt(tmp_dict['data'])
                                        tmp_dict['data'] = str(cl_dt)
                                        if type(cl_dt) == str:
                                            tmp_dict['status'] = 0
                                            tmp_dict['status_message'] = "Low confidence/Missing Value"

                                    if default_qty_ut == 1:
                                        if tmp_dict['tag'] in ['Quantity', 'UnitPrice']:
                                            tmp_dict['data'] = 1
                                            bx['x'] = '0'
                                            bx['y'] = '0'
                                            bx['w'] = '0'
                                            bx['h'] = '0'
                                            tmp_dict['boundingBox'] = bx
                                            # tmp_list.append(tmp_dict)
                                            # tmp_dict = {}
                                    present_tab_header.append(tmp_dict['tag'])
                                    tmp_list.append(tmp_dict)
                                    tmp_dict = {}

                                else:
                                    tmp_dict['data'] = ''
                                    tmp_dict['boundingBox'] = None
                                # tmp_dict[ky] = fields[tbs]['valueArray'][itm_no]['valueObject'][ky]['text']

                    if tab_cal_unitprice_AmtExcTax == 1:
                        if 'AmountExcTax' not in present_tab_header:
                            tmp_dict['tag'] = 'AmountExcTax'

                            tmp_dict['data'] = ''
                            bx['x'] = '0'
                            bx['y'] = '0'
                            bx['w'] = '0'
                            bx['h'] = '0'
                            tmp_dict['boundingBox'] = bx
                            tmp_dict['status'] = 0
                            tmp_dict['status_message'] = "Mandatory value missing"

                            tmp_list.append(tmp_dict)
                            present_tab_header.append('Quantity')
                            tmp_dict = {}

                    if default_qty_ut == 1:
                        if 'Quantity' not in present_tab_header:
                            tmp_dict['tag'] = 'Quantity'

                            # if ky in ['Quantity', 'UnitPrice']:
                            #     if default_qty_ut == 1:
                            tmp_dict['data'] = 1
                            bx['x'] = '0'
                            bx['y'] = '0'
                            bx['w'] = '0'
                            bx['h'] = '0'
                            tmp_dict['boundingBox'] = bx
                            tmp_list.append(tmp_dict)
                            present_tab_header.append('Quantity')
                            tmp_dict = {}
                        if 'UnitPrice' not in present_tab_header:
                            print("UnitPrice line 571")
                            tmp_dict['tag'] = 'UnitPrice'
                            # if ky in ['Quantity', 'UnitPrice']:
                            #     if default_qty_ut == 1:
                            tmp_dict['data'] = 1
                            bx['x'] = '0'
                            bx['y'] = '0'
                            bx['w'] = '0'
                            bx['h'] = '0'
                            tmp_dict['boundingBox'] = bx
                            tmp_list.append(tmp_dict)
                            tmp_dict = {}
                            present_tab_header.append('UnitPrice')

                    itm_list.append(tmp_list)
                    print("present_tab_header------------", present_tab_header)
        try:
            for rw_ck_1 in range(0, len(itm_list)):
                missing_tab_val = []
                prst_rw_val = []
                # rw_ck_1 = 0
                utprice_rw = ''
                amxExtx_rw = ''
                discount_rw = ''
                qty_rw = ''
                for ech_tg in range(0, len(itm_list[rw_ck_1])):
                    # print(itm_list[rw_ck_1][ech_tg]['tag'])
                    if itm_list[rw_ck_1][ech_tg]['tag'] in ('Quantity', 'Discount', 'UnitPrice', 'AmountExcTax'):
                        try:
                            qty_ck_cl = cln_amt(itm_list[rw_ck_1][ech_tg]['data'])
                            if type(qty_ck_cl) == str:
                                itm_list[rw_ck_1][ech_tg]['status'] = 0
                                itm_list[rw_ck_1][ech_tg]['status_message'] = "Low confidence"
                            elif type(qty_ck_cl) == float:
                                itm_list[rw_ck_1][ech_tg]['data'] = str(qty_ck_cl)
                            else:
                                itm_list[rw_ck_1][ech_tg]['status'] = 0
                                itm_list[rw_ck_1][ech_tg]['status_message'] = "Low confidence"



                        except Exception as qt:
                            itm_list[rw_ck_1][ech_tg]['status'] = 0
                            itm_list[rw_ck_1][ech_tg]['status_message'] = "Low confidence"
                            print("exception in postprocess cln: ", str(qt))

                    if itm_list[rw_ck_1][ech_tg]['tag'] in mandatory_tab_col:
                        if itm_list[rw_ck_1][ech_tg]['data'] == '':
                            itm_list[rw_ck_1][ech_tg]['status'] = 0
                            itm_list[rw_ck_1][ech_tg]['status_message'] = "Mandatory value missing"
                for ech_tg_1 in itm_list[rw_ck_1]:
                    prst_rw_val.append(ech_tg_1['tag'])
                    if tab_cal_unitprice == 1:
                        print("tab_cal_unitprice  = 1 ", ech_tg_1['tag'])
                        if ech_tg_1['tag'] == 'Quantity':
                            qty_rw = ech_tg_1['data']
                        if ech_tg_1['tag'] == 'Discount':
                            discount_rw = ech_tg_1['data']
                        if ech_tg_1['tag'] == 'UnitPrice':
                            utprice_rw = ech_tg_1['data']
                        if ech_tg_1['tag'] == 'AmountExcTax':
                            amxExtx_rw = ech_tg_1['data']
                    if tab_cal_unitprice_AmtExcTax == 1:
                        print("tab_cal_unitprice_AmtExcTax  = 1 ", ech_tg_1['tag'])

                        if ech_tg_1['tag'] == 'Quantity':
                            qty_rw = ech_tg_1['data']
                            if 'status' in ech_tg_1:
                                qty_rw_status = ech_tg_1['status']
                            else:
                                cln_qty_ck = tb_cln_amt(qty_rw)
                                if type(cln_qty_ck) == float:
                                    qty_rw_status = 1
                                else:
                                    qty_rw_status = 0

                        if ech_tg_1['tag'] == 'Discount':
                            discount_rw = ech_tg_1['data']
                            if 'status' in ech_tg_1:
                                discount_rw_status = ech_tg_1['status']
                            else:
                                cln_dis_cmt = tb_cln_amt(discount_rw)
                                if type(cln_dis_cmt) == float:
                                    discount_rw_status = 1
                                else:
                                    discount_rw_status = 0

                        if ech_tg_1['tag'] == 'UnitPrice':
                            utprice_rw = ech_tg_1['data']
                            if 'status' in ech_tg_1:
                                utprice_rw_status = ech_tg_1['status']
                            else:
                                qt_cln_val = tb_cln_amt(utprice_rw)
                                if type(qt_cln_val) == float:
                                    utprice_rw_status = 1
                                else:
                                    utprice_rw_status = 0

                        if ech_tg_1['tag'] == 'Amount':
                            amt_withTax_rw = ech_tg_1['data']
                            if 'status' in ech_tg_1:
                                amt_withTax_rw_status = ech_tg_1['status']
                            else:
                                cl_val = tb_cln_amt(amt_withTax_rw)
                                if type(cl_val) == float:
                                    amt_withTax_rw_status = 1
                                else:
                                    amt_withTax_rw_status = 0
                        if ech_tg_1['tag'] == 'Tax':
                            vatAmt_rw = ech_tg_1['data']
                            if 'status' in ech_tg_1:
                                amt_withTax_rw_status = ech_tg_1['status']
                            else:
                                vtcln_amt = tb_cln_amt(vatAmt_rw)
                                if type(vtcln_amt) == float:
                                    vatAmt_rw_status = 1
                                else:
                                    vatAmt_rw_status = 0

                print("qty_rw: ", qty_rw, " discount_rw: ", discount_rw, " utprice_rw: ", utprice_rw, " amxExtx_rw: ",
                      amxExtx_rw)

                if tab_cal_unitprice_AmtExcTax == 1:
                    if (qty_rw != '') and (discount_rw != '') and (utprice_rw != '') and (amt_withTax_rw != '') and (
                            vatAmt_rw != ''):
                        if (qty_rw_status == 1) and (discount_rw_status == 1) and (utprice_rw_status == 1) and (
                                amt_withTax_rw_status == 1) and (vatAmt_rw_status == 1):
                            qty_rw = cln_amt(qty_rw)
                            utprice_rw = cln_amt(utprice_rw)
                            amt_withTax_rw = cln_amt(amt_withTax_rw)
                            discount_rw = cln_amt(discount_rw)
                            vatAmt_rw = cln_amt(vatAmt_rw)
                            amt_excTax_cal = amt_withTax_rw - vatAmt_rw
                            try:
                                cal_utprice_rw = utprice_rw - (discount_rw / qty_rw)
                            except Exception as cl:
                                print(str(cl))
                                cal_utprice_rw = ''

                            print("cal_utprice_rw: ", cal_utprice_rw, ' utprice_rw: ', utprice_rw, ' discount_rw:',
                                  discount_rw, ' qty_rw:', qty_rw, "amt_excTax_cal: ", amt_excTax_cal)
                            try:
                                cal_amtExTx_PE = amt_excTax_cal / qty_rw
                            except Exception as cl:
                                cal_amtExTx_PE = ''

                            if cal_utprice_rw == (cal_amtExTx_PE):
                                for ech_tg_4 in range(0, len(itm_list[rw_ck_1])):
                                    if itm_list[rw_ck_1][ech_tg_4]['tag'] == 'UnitPrice':
                                        itm_list[rw_ck_1][ech_tg_4]['data'] = cal_utprice_rw
                                    if itm_list[rw_ck_1][ech_tg_4]['tag'] == 'AmountExcTax':
                                        itm_list[rw_ck_1][ech_tg_4]['status'] = 1
                                        itm_list[rw_ck_1][ech_tg_4]['data'] = amt_excTax_cal
                                        itm_list[rw_ck_1][ech_tg_4][
                                            'status_message'] = "Calculated value"

                            else:
                                for ech_tg_2 in range(0, len(itm_list[rw_ck_1])):
                                    if itm_list[rw_ck_1][ech_tg_2]['tag'] == 'UnitPrice':
                                        itm_list[rw_ck_1][ech_tg_2]['status'] = 0
                                        itm_list[rw_ck_1][ech_tg_2][
                                            'status_message'] = "Unitprice calculation with discount failed"
                                    if itm_list[rw_ck_1][ech_tg_2]['tag'] == 'AmountExcTax':
                                        itm_list[rw_ck_1][ech_tg_2]['data'] = ''
                                        itm_list[rw_ck_1][ech_tg_2]['status'] = 0
                                        itm_list[rw_ck_1][ech_tg_2][
                                            'status_message'] = "AmountExcTax calculation with discount failed"
                                # itm_list[rw_ck_1][ech_tg_2].append({'tag': 'AmountExcTax','data': '','status': 0,'status_message': 'AmountExcTax calculation with discount failed'})
                        else:

                            for ech_tg_2 in range(0, len(itm_list[rw_ck_1])):
                                if itm_list[rw_ck_1][ech_tg_2]['tag'] == 'UnitPrice':
                                    itm_list[rw_ck_1][ech_tg_2]['status'] = 0
                                    itm_list[rw_ck_1][ech_tg_2][
                                        'status_message'] = "Unitprice calculation with discount failed"
                                if itm_list[rw_ck_1][ech_tg_2]['tag'] == 'AmountExcTax':
                                    itm_list[rw_ck_1][ech_tg_2]['data'] = ''
                                    itm_list[rw_ck_1][ech_tg_2]['status'] = 0
                                    itm_list[rw_ck_1][ech_tg_2][
                                        'status_message'] = "AmountExcTax calculation with discount failed"
                            # itm_list[rw_ck_1][ech_tg_2].append({'tag': 'AmountExcTax','data': '','status': 0,'status_message': 'AmountExcTax calculation with discount failed'})
                    else:
                        for ech_tg_2 in range(0, len(itm_list[rw_ck_1])):
                            if itm_list[rw_ck_1][ech_tg_2]['tag'] == 'UnitPrice':
                                itm_list[rw_ck_1][ech_tg_2]['status'] = 0
                                itm_list[rw_ck_1][ech_tg_2][
                                    'status_message'] = "Unitprice calculation with discount failed"
                            if itm_list[rw_ck_1][ech_tg_2]['tag'] == 'AmountExcTax':
                                itm_list[rw_ck_1][ech_tg_2]['status'] = 0
                                itm_list[rw_ck_1][ech_tg_2][
                                    'status_message'] = "AmountExcTax calculation with discount failed"
                        # itm_list[rw_ck_1][ech_tg_2].append({'tag': 'AmountExcTax', 'data': '', 'status': 0,
                        #                                     'status_message': 'AmountExcTax calculation with discount failed'})

                if tab_cal_unitprice == 1:
                    if (qty_rw != '') and (discount_rw != '') and (utprice_rw != '') and (amxExtx_rw != ''):
                        qty_rw = cln_amt(qty_rw)
                        utprice_rw = cln_amt(utprice_rw)
                        amxExtx_rw = cln_amt(amxExtx_rw)
                        discount_rw = cln_amt(discount_rw)
                        try:
                            cal_utprice_rw = utprice_rw - (discount_rw / qty_rw)
                        except Exception as cl_vl:
                            print(str(cl_vl))
                            cal_utprice_rw = ''

                        try:
                            cal_amtExTx_PE = amxExtx_rw / qty_rw
                        except Exception as cl_vl:
                            print(str(cl_vl))
                            cal_amtExTx_PE = ''

                        if cal_utprice_rw == (cal_amtExTx_PE) and (cal_amtExTx_PE != '') and (cal_utprice_rw != ''):
                            for ech_tg_4 in range(0, len(itm_list[rw_ck_1])):
                                if itm_list[rw_ck_1][ech_tg_4]['tag'] == 'UnitPrice':
                                    itm_list[rw_ck_1][ech_tg_4]['data'] = cal_utprice_rw
                        else:
                            for ech_tg_2 in range(0, len(itm_list[rw_ck_1])):
                                if itm_list[rw_ck_1][ech_tg_2]['tag'] == 'UnitPrice':
                                    itm_list[rw_ck_1][ech_tg_2]['status'] = 0
                                    itm_list[rw_ck_1][ech_tg_2][
                                        'status_message'] = "Unitprice calculation with discount failed"
                    else:
                        for ech_tg_3 in range(0, len(itm_list[rw_ck_1])):
                            if itm_list[rw_ck_1][ech_tg_3]['tag'] == 'UnitPrice':
                                itm_list[rw_ck_1][ech_tg_3]['status'] = 0
                                itm_list[rw_ck_1][ech_tg_3][
                                    'status_message'] = "Unitprice calculation with discount failed"
                if skp_tab_mand_ck == 1:
                    missing_rw_tab = []
                else:
                    if set(mandatory_tab_col).issubset(set(prst_rw_val)) == False:
                        missing_rw_tab = list(set(mandatory_tab_col) - set(prst_rw_val))

                    for mis_rw_val in missing_rw_tab:
                        itm_list[rw_ck_1][ech_tg]['tag'] = mis_rw_val
                        itm_list[rw_ck_1][ech_tg]['data'] = ''
                        itm_list[rw_ck_1][ech_tg]['status'] = 0
                        itm_list[rw_ck_1][ech_tg]['status_message'] = "Mandatory value not detected"
                        itm_list[rw_ck_1][ech_tg]['boundingBox'] = {'x': '', 'y': '', 'w': '', 'h': ''}
        except Exception as E:
            print("exception frm new upate on postprocessing: ", str(E))

        fr_data = {'header': fr_headers, 'tab': itm_list,
                   'overall_status': overall_status}
        # print("fr_data", fr_data)
        postprocess_status = 1
        postprocess_msg = 'success'

        dt = fr_data

        # print("dt header: ", dt.keys())
        # print('line 379 post process: ', (len(dt['header'])))
        # print(dt['header'])
        get_nm_trn_qry = "SELECT TRNNumber,VendorName FROM " + DB + ".vendor where idVendor in(SELECT vendorID FROM " + DB + ".vendoraccount where idVendorAccount in (SELECT idVendorAccount FROM " + DB + ".documentmodel WHERE idDocumentModel=" + str(
            invo_model_id) + "));"
        vdr_nm_trn_df = pd.read_sql(get_nm_trn_qry, SQLALCHEMY_DATABASE_URL)
        vdr_trn_df = pd.DataFrame(vdr_nm_trn_df['TRNNumber'])
        vdr_name_df = pd.DataFrame(vdr_nm_trn_df['VendorName'])
        trn_val = list(vdr_trn_df['TRNNumber'])[0] if 'TRNNumber' in vdr_trn_df and len(
            list(vdr_trn_df['TRNNumber'])) > 0 else ""
        name_val = list(vdr_name_df['VendorName'])[0] if 'VendorName' in vdr_name_df and len(
            list(vdr_name_df['VendorName'])) > 0 else ""
        trn_match_metadata = 0
        for tg in range(len(dt['header'])):
            if dt['header'][tg]['tag'] == 'InvoiceId':

                # print(dt['header'][tg]['data']['value'])
                doc_invID = dt['header'][tg]['data']['value']
                while doc_invID[0].isalnum() == 0:
                    doc_invID = doc_invID[1:]
                    # if doc_invID[0].isalnum() == 0:
                    #     doc_invID = doc_invID[1:]

                while doc_invID[-1].isalnum() == 0:
                    doc_invID = doc_invID[:-1]
                    # if doc_invID[-1].isalnum() == 0:
                    #     doc_invID = doc_invID[:-1]
                dt['header'][tg]['data']['value'] = doc_invID
                duplicate_ck_str = "SELECT * FROM " + DB + ".document where docheaderID = '" + str(
                    doc_invID) + "' and VendorAccountId = " + str(vendorAccountID) + " and idDocumentType=3;"

                duplicate_ck_df = pd.read_sql(duplicate_ck_str, SQLALCHEMY_DATABASE_URL)
                if len(duplicate_ck_df) > 0:
                    latest_docId = duplicate_ck_df['idDocument'].max()
                    print('latest_docId: ', latest_docId, ' vendorAccountID: ', vendorAccountID)
                    dplk_doc_sts = \
                        duplicate_ck_df[duplicate_ck_df['idDocument'] == latest_docId].reset_index(drop=True)[
                            'documentStatusID'][0]
                    if dplk_doc_sts == 10 or dplk_doc_sts == 0:
                        duplicate_status = 1
                        # break;
                    else:
                        duplicate_status = 0

            print("dt['header'][tg]['tag']: ", dt['header'][tg]['tag'])
            if dt['header'][tg]['tag'] == 'InvoiceDate':
                doc_date = dt['header'][tg]['data']['value']
                while doc_date[0].isalnum() == 0:
                    doc_date = doc_date[1:]
                while doc_date[-1].isalnum() == 0:
                    doc_date = doc_date[:-1]
                req_date, date_status = date_cnv(doc_date, date_format)
                if date_status == 0:
                    dt['header'][tg]['status_message'] = "Invalid Date, Please enter YYYY-MM-DD"
                    dt['header'][tg]['status'] = 0

                dt['header'][tg]['data']['value'] = req_date
            if dt['header'][tg]['tag'] == 'TRN':
                doc_trn = dt['header'][tg]['data']['value']
                try:
                    doc_trn_nw = ''
                    for trn_sp in doc_trn.split(' '):
                        # print(trn_sp)
                        sb_tn = ''
                        for i_ in trn_sp:
                            if i_.isdigit():
                                sb_tn = sb_tn + i_
                        if len(sb_tn) > 0:
                            doc_trn_nw = doc_trn_nw + " " + sb_tn

                    ocr_trn = max((re.findall(r'\b\d+\b', doc_trn_nw)), default=0, key=len)
                    dt['header'][tg]['data']['value'] = ocr_trn
                    # TRN Match:
                    get_trn_qry = "SELECT TRNNumber FROM " + DB + ".vendor where idVendor in(SELECT vendorID FROM " + DB + ".vendoraccount where idVendorAccount in (SELECT idVendorAccount FROM " + DB + ".documentmodel WHERE idDocumentModel=" + str(
                        invo_model_id) + "));"
                    vdr_trn_df = pd.read_sql(get_trn_qry, SQLALCHEMY_DATABASE_URL)
                    trn_val = list(vdr_trn_df['TRNNumber'])[0] if 'TRNNumber' in vdr_trn_df and len(
                        list(vdr_trn_df['TRNNumber'])) > 0 else ""
                    if trn_val == "":
                        dt['header'][tg]['status_message'] = "TRN is missing from Vendor metadata."
                        dt['header'][tg]['status'] = 0
                        trn_match_metadata = 0

                    vdr_trn = re.findall(r'\d+', trn_val)[0]
                    if len(vdr_trn) > 12:
                        print("YES")
                        trn_val = vdr_trn
                    else:
                        trn_val = ''
                        dt['header'][tg]['status_message'] = "TRN is missing from Vendor metadata."
                        dt['header'][tg]['status'] = 0
                    # else:
                    #     trn_match_metadata = 1
                    if trn_val != "" and trn_val != ocr_trn:
                        dt['header'][tg]['status_message'] = "TRN not matching with vendor metadata(" + str(
                            trn_val) + ")."
                        dt['header'][tg]['status'] = 0
                        trn_match_metadata = 0
                    elif trn_val == ocr_trn:
                        trn_match_metadata = 1

                    else:
                        trn_match_metadata = 0
                        dt['header'][tg]['status'] = 0
                        dt['header'][tg]['status_message'] = 'Low Confidence, Please Review.'

                except Exception as trn_exp:
                    print(trn_exp)
                    dt['header'][tg]['status_message'] = "Low Confidence, Meta data trn:" + str(
                        trn_val) + ")."
                    dt['header'][tg]['status'] = 0
                    trn_match_metadata = 0

            if dt['header'][tg]['tag'] == 'PurchaseOrder':
                doc_po = dt['header'][tg]['data']['value']
                digits = sum(c.isdigit() for c in doc_po)
                letters = sum(c.isalpha() for c in doc_po)
                spaces = sum(c.isspace() for c in doc_po)
                others = len(doc_po) - digits - letters - spaces
                if (digits < letters) or (digits < spaces) or (digits < others) or ('.' in doc_po):
                    dt['header'][tg]['status_message'] = "Invalid PO number, please insert valid PO number."
                    dt['header'][tg]['status'] = 0
            if subtotal_Cal == 1:
                if dt['header'][tg]['tag'] == 'InvoiceTotal':
                    invoiceTotal_rw = tb_cln_amt(dt['header'][tg]['data']['value'])
                    if type(invoiceTotal_rw) != float:
                        # dt['header'][tg]['data']['value']
                        dt['header'][tg]['status_message'] = "Invalid Value, Please review"
                        dt['header'][tg]['status'] = 0
                        invoiceTotal_rw = ''

                if dt['header'][tg]['tag'] == 'SubTotal':
                    subtotal_rw = tb_cln_amt(dt['header'][tg]['data']['value'])
                    if type(subtotal_rw) != float:
                        dt['header'][tg]['status_message'] = "Invalid Value, Please review"
                        dt['header'][tg]['status'] = 0
                        subtotal_rw = ''

                if dt['header'][tg]['tag'] == 'TotalDiscount':
                    totaldiscount_rw = tb_cln_amt(dt['header'][tg]['data']['value'])
                    if type(totaldiscount_rw) != float:
                        dt['header'][tg]['status_message'] = "Invalid Value, Please review"
                        dt['header'][tg]['status'] = 0
                        totaldiscount_rw = ''

                if dt['header'][tg]['tag'] == 'TotalTax':
                    totalTax_rw = tb_cln_amt(dt['header'][tg]['data']['value'])
                    if type(totalTax_rw) != float:
                        dt['header'][tg]['status_message'] = "Invalid Value, Please review"
                        dt['header'][tg]['status'] = 0
                        totalTax_rw = ''

        print("duplicate_status: ", duplicate_status)
        if duplicate_status == 0:
            subject = 'Duplicate Invoice Uploaded!'
            body = f"""
            <html>
                <body style="font-family: Segoe UI !important;height: 100% !important;margin: 0 !important;padding: 20px !important;color: #272727 !important;">
                    <strong>Error Summary</strong>: <i> Duplicate Invoice! </i>
                    <div style="margin-top: 2%;"></div>
                    <table border="1" cellpadding="0" cellspacing="0" width="100%">
                        <tr>
                            <th>Description</th>
                            <th>Sender</th>
                            <th>Date & Time</th>
                        </tr>
                        <tr>
                            <td>Invoice Id {str(doc_invID)} already uploaded once!</td>
                            <td>{sender}</td>
                            <td>{datetime.datetime.now(tz_region).strftime("%Y-%m-%d %H:%M:%S")}</td>
                        </tr>
                    </table>
                </body>
            </html>
            """
            email_sender.send_mail("serinaplus.dev@datasemantics.co", sender, subject, body)
            fr_data = {}
            postprocess_status = 0
            postprocess_msg = "Duplicate Invoice Uploaded!"
            # Rejection

        else:
            for row_cnt in range(len(dt['tab'])):
                for rw in range(len(dt['tab'][row_cnt])):
                    dt['tab'][row_cnt][rw]['row_count'] = row_cnt + 1
            SubTotal_data = ''
            InvoiceTotal_val = ''
            TotalTax = ''
            for tg in range(len(dt['header'])):
                if dt['header'][tg]['tag'] == 'InvoiceTotal':
                    dt['header'][tg]['data']['value'] = cln_amt(dt['header'][tg]['data']['value'])
                    InvoiceTotal_val = dt['header'][tg]['data']['value']
                    fr_data = dt
                if dt['header'][tg]['tag'] == 'SubTotal':
                    dt['header'][tg]['data']['value'] = cln_amt(dt['header'][tg]['data']['value'])
                    SubTotal_data = dt['header'][tg]['data']['value']
                    if subtotal_Cal == 1:
                        if (invoiceTotal_rw != '') and (totalTax_rw != '') and (totaldiscount_rw != '') and (
                                subtotal_rw != ''):
                            cal_subtotal_1 = invoiceTotal_rw - totalTax_rw
                            cal_subtotal_2 = subtotal_rw - totaldiscount_rw
                            if cal_subtotal_1 == cal_subtotal_2:
                                dt['header'][tg]['data']['value'] = cal_subtotal_2
                            else:
                                dt['header'][tg]['status_message'] = "Calculation failed, Please update with (Invoice " \
                                                                     "Total - Total Tax) "
                                dt['header'][tg]['status'] = 0
                        else:
                            dt['header'][tg]['status_message'] = "Calculation failed, Please update with (Invoice " \
                                                                 "Total - Total Tax) "
                            dt['header'][tg]['status'] = 0

                    fr_data = dt
                if dt['header'][tg]['tag'] == 'TotalTax':
                    dt['header'][tg]['data']['value'] = cln_amt(dt['header'][tg]['data']['value'])
                    TotalTax = dt['header'][tg]['data']['value']
                    fr_data = dt

                if dt['header'][tg]['tag'] == 'VendorName':
                    ocr_vdr_nm = dt['header'][tg]['data']['value']

                    if trn_match_metadata == 1:
                        dt['header'][tg]['data']['value'] = name_val
                        dt['header'][tg]['status'] = 1
                    elif trn_match_metadata == 0:
                        vendor_nm_list = name_val.lower().split(" ")
                        nm_scr = len(vendor_nm_list)
                        vdr_nm_mth = ''
                        for inm in vendor_nm_list:
                            if ocr_vdr_nm.find(inm) == -1:
                                nm_scr = nm_scr - 1
                            else:
                                vdr_nm_mth = vdr_nm_mth + inm + " "
                        if nm_scr >= (len(vendor_nm_list) - 1):
                            dt['header'][tg]['data']['value'] = vdr_nm_mth
                        else:
                            dt['header'][tg]['status'] = 0

            present_header = []
            missing_header = []

            # mandatory_header = ['PurchaseOrder', 'InvoiceId', 'VAT']
            for ck_hrd_tg in fr_data['header']:
                present_header.append(ck_hrd_tg['tag'])

            try:
                if 'InvoiceTotal' not in present_header:
                    if SubTotal_data != '':
                        tmp = {}
                        # tmp['tag'] = 'InvoiceTotal'
                        tmp = {'tag': 'InvoiceTotal',
                               'data': {'value': str(SubTotal_data),
                                        'prebuilt_confidence': '0.0',
                                        'custom_confidence': '0.0'},
                               'boundingBox': {'x': '',
                                               'y': '',
                                               'w': '',
                                               'h': ''},
                               'status': 1,
                               'status_message': 'Calculated Value'}
                        present_header.append('InvoiceTotal')
                        fr_data['header'].append(tmp)
            except Exception as e:
                print(str(e))

            # try:
            #     if 'SubTotal' not in present_header:
            #         if InvoiceTotal_val != '' and TotalTax != '':
            #             suntotal_vl = float(InvoiceTotal_val)-float(TotalTax)
            #             tp_tg = {'tag': 'SubTotal',
            #                      'data': {'value': str(suntotal_vl),
            #                               'prebuilt_confidence': '0.0',
            #                               'custom_confidence': '0.0'},
            #                      'boundingBox': {'x': '',
            #                                      'y': '',
            #                                      'w': '',
            #                                      'h': ''},
            #                      'status': 1,
            #                      'status_message': 'Calculated Value'}
            #             fr_data['header'].append(tp_tg)
            #             present_header.append('SubTotal')
            # except Exception as st:
            #     print(str(st))

            if set(mandatory_header).issubset(set(present_header)) == False:
                missing_header = list(set(mandatory_header) - set(present_header))
            # print("line 732: ", fr_data.keys())
            # print("_________________________________________")
            # print(fr_data['header'])
            # print("_________________________________________")
            for msg_itm_ck in missing_header:
                # notification missing header = msg_itm_ck
                tp_tg = {'tag': msg_itm_ck,
                         'data': {'value': '',
                                  'prebuilt_confidence': '0.0',
                                  'custom_confidence': '0.0'},
                         'boundingBox': {'x': '',
                                         'y': '',
                                         'w': '',
                                         'h': ''},
                         'status': 0,
                         'status_message': 'Mandatory Headers Missing'}
                fr_data['header'].append(tp_tg)

            if len(missing_header) >= (len(mandatory_header)):
                # reject invoice
                fr_data = {}
                postprocess_msg = "Please check the document uploaded! - Model not found."
                postprocess_status = 0

                try:
                    ############ start of notification trigger #############
                    details = {"user_id": None, "trigger_code": 8023, "cust_id": 1, "inv_id": None,
                               "additional_details": {
                                   "recipients": [(sender, "Serina", "User")],
                                   "subject": "Invoice Vendor Rejection", "ffirstName": "Serina",
                                   "llastName": "System"}}
                    bg_task.add_task(meta_data_publisher, details)
                    ############ End of notification trigger #############
                except Exception as rejection_:
                    print("Please check the document uploaded! - Model not found: " + str(rejection_))

            else:
                labels_not_present = []
                present_tab_itm = []
                for tbl_tg_ck in fr_data['tab']:
                    for rw_tbl_tg_ck in tbl_tg_ck:
                        present_tab_itm.append(rw_tbl_tg_ck['tag'])

                tb_pt_cnt = dict(Counter(present_tab_itm))
                # mandatory_tab_col = ['Description', 'Amount']
                for mtc in mandatory_tab_col:
                    if mtc in tb_pt_cnt:
                        if tb_pt_cnt[mtc] == len(fr_data['tab']):
                            print("all good with table")
                        else:
                            labels_not_present.append(mtc)
                            print("mandatory tab lable missing")
                            ############ End of notification trigger #############
                    else:
                        labels_not_present.append(mtc)
                        print("mandatory tab lable missing")
                missing_tab_val = missing_rw_tab
                if len(missing_tab_val) > 0 or len(missing_header) > 0:
                    try:
                        ############ start of notification trigger #############
                        vendor = db.query(model.Vendor.VendorName).filter(
                            model.Vendor.idVendor == model.VendorAccount.vendorID).filter(
                            model.VendorAccount.idVendorAccount == vendorAccountID).scalar()
                        # filter based on role if added
                        role_id = db.query(model.NotificationCategoryRecipient.roles).filter_by(entityID=entityID,
                                                                                                notificationTypeID=2).scalar()
                        # getting recipients for sending notification
                        recepients = db.query(model.AccessPermission.userID).filter(
                            model.AccessPermission.permissionDefID.in_(role_id["roles"])).distinct()
                        recepients = db.query(model.User.idUser, model.User.email, model.User.firstName,
                                              model.User.lastName).filter(model.User.idUser.in_(recepients)).filter(
                            model.User.isActive == 1).filter(model.UserAccess.UserID == model.User.idUser).filter(
                            model.UserAccess.EntityID == entityID, model.UserAccess.isActive == 1).all()
                        user_ids, *email = zip(*list(recepients))
                        # just format update
                        email_ids = list(zip(email[0], email[1], email[2]))
                        isdefaultrep = None
                    except Exception as e:
                        pass
                    try:
                        isdefaultrep = db.query(model.NotificationCategoryRecipient.isDefaultRecepients,
                                                model.NotificationCategoryRecipient.notificationrecipient).filter(
                            model.NotificationCategoryRecipient.entityID == entityID,
                            model.NotificationCategoryRecipient.notificationTypeID == 2).one()
                    except Exception as e:
                        pass
                    cc_email_ids = []
                    try:
                        if isdefaultrep and isdefaultrep.isDefaultRecepients and len(
                                isdefaultrep.notificationrecipient["to_addr"]) > 0:
                            email_ids.extend(
                                [(x, "Serina", "User") for x in isdefaultrep.notificationrecipient["to_addr"]])
                            cc_email_ids = isdefaultrep.notificationrecipient["cc_addr"]
                        cust_id = db.query(model.Entity.customerID).filter_by(idEntity=entityID).scalar()
                        details = {"user_id": user_ids, "trigger_code": 7001, "cust_id": cust_id, "inv_id": None,
                                   "additional_details": {"subject": "Missing Key Labels", "Vendor_Name": vendor,
                                                          "Labels": missing_tab_val + missing_header,
                                                          "filename": filename,
                                                          "recipients": email_ids, "cc": cc_email_ids}}
                        bg_task.add_task(meta_data_publisher, details)
                        ############ End of notification trigger #############
                    except Exception as e:
                        pass
    # print('dt----------------------',dt)
    # print('*****************************************************************')
    except Exception as e:
        applicationlogging.logException("DS Al Ghurair", "postprocessing.py postpro", str(e))
        fr_data = {}
        postprocess_status = 0
        postprocess_msg = str(e)
        print(traceback.format_exc())
        print("Excaption in postprocessing:", str(e))
    return fr_data, postprocess_msg, postprocess_status




'''fr_data, postprocess_msg, postprocess_status = postpro(cst_data, pre_data)
with open('fr_data.txt', 'w') as fl:
    fl.write(json.dumps(fr_data))
fl.close()
'''

# fr_data = postpro(cst_data, pre_data)

