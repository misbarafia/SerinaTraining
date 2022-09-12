import pandas as pd
import os
from datetime import date,datetime
today = date.today()
import pytz as tz
import model
from session import engine,Session
tz_region_name = os.getenv("serina_tz", "Asia/Dubai")
tz_region = tz.timezone(tz_region_name)

db = Session()
connection = engine.connect()
print("connected")
#get all distinct vendor code
df = pd.read_sql(f"select distinct(Account) from vendoraccount",connection)
print("got data")
if len(df) > 0:
    for i in range(len(df)):
        #for each vendor code get the vendor account id
        vendors = pd.read_sql(f"select idVendorAccount from vendoraccount where Account = '{df['Account'][i]}'",connection)
        vendoraccounts = []
        for j in range(len(vendors)):
           vendoraccounts.append(vendors['idVendorAccount'][j])
        models = pd.read_sql(f"select * from documentmodel where idVendorAccount in {tuple(vendoraccounts)}",connection)
        if len(models) > 0:
            templates = list(set([models['modelName'][fy] for fy in range(len(models))]))
            missing_models = []
            for t in templates:
                inputmodel = {}
                for v in vendoraccounts:
                    docmodelqr = "SELECT * FROM documentmodel WHERE idVendorAccount="+str(v)+" and modelName = '"+t+"';"
                    docmodel = pd.read_sql(docmodelqr, connection)
                    if docmodel is None or len(docmodel) == 0:
                        missing_models.append({"idVendorAccount":v,"modelName":t})
                    else:
                        if len(inputmodel.keys()) == 0:
                            for d in docmodel.head():
                                inputmodel[d] = docmodel[d][0]
                model_id = inputmodel['idDocumentModel']
                frmetadataqr = "SELECT * FROM frmetadata WHERE idInvoiceModel="+str(model_id)+""
                frmetadatares = pd.read_sql(frmetadataqr, connection)
                frmetadata = {}
                for f in frmetadatares.head():
                    frmetadata[f] = frmetadatares[f][0]
                del frmetadata['idFrMetaData']
                del inputmodel['idDocumentModel']
                for m in missing_models:
                    inputmodel['idVendorAccount'] = m['idVendorAccount']
                    inputmodel["CreatedOn"] = datetime.now(tz_region).strftime("%Y-%m-%d %H:%M:%S")
                    inputmodel["UpdatedOn"] = inputmodel["CreatedOn"]
                    invoiceModelDB = model.DocumentModel(**inputmodel)
                    db.add(invoiceModelDB)
                    db.commit()
                    iddocqr = db.query(model.DocumentModel.idDocumentModel).filter(model.DocumentModel.idVendorAccount == m['idVendorAccount'],model.DocumentModel.modelName == t).first()    
                    print(iddocqr[0])
                    checktmeta = db.query(model.FRMetaData).filter(model.FRMetaData.idInvoiceModel == iddocqr[0]).first()
                    if checktmeta is None:
                        frmetadata['idInvoiceModel'] = iddocqr[0]
                        frmetaDataDB = model.FRMetaData(**frmetadata)
                        db.add(frmetaDataDB)
                        db.commit()
                    documenttagdefqr = "SELECT * FROM documenttagdef WHERE idDocumentModel="+str(model_id)+""
                    documenttagdefres = pd.read_sql(documenttagdefqr, connection)
                    documenttagdef = []
                    for i in range(len(documenttagdefres)):
                        obj = {}
                        for f in documenttagdefres.head():
                            if f != "idDocumentTagDef":
                                obj[f] = documenttagdefres[f][i]
                        documenttagdef.append(obj)
                    checktag = db.query(model.DocumentTagDef).filter(model.DocumentTagDef.idDocumentModel == iddocqr[0]).first()
                    if checktag is None:
                        for d in documenttagdef:
                            d['idDocumentModel'] = iddocqr[0]
                            documenttagdefDB = model.DocumentTagDef(**d)
                            db.add(documenttagdefDB)
                            db.commit()
                    documentlinedefqr = "SELECT * FROM documentlineitemtags WHERE idDocumentModel="+str(model_id)+""
                    documentlinedefres = pd.read_sql(documentlinedefqr, connection)
                    documentlinedef = []
                    for i in range(len(documentlinedefres)):
                        obj = {}
                        for f in documentlinedefres.head():
                            if f != "idDocumentLineItemTags":
                                obj[f] = documentlinedefres[f][i]
                        documentlinedef.append(obj)
                    checktag = db.query(model.DocumentLineItemTags).filter(model.DocumentLineItemTags.idDocumentModel == iddocqr[0]).first()
                    if checktag is None:
                        for d in documentlinedef:
                            d['idDocumentModel'] = iddocqr[0]
                            documentlinedefDB = model.DocumentLineItemTags(**d)
                            db.add(documentlinedefDB)
                            db.commit()
                break
        break          
        