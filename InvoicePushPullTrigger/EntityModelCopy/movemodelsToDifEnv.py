from session import Session
from uatsession import UATSession
import model,modeluat
db = Session()
uatdb = UATSession()
models = db.query(model.DocumentModel).all()

for m in models:
    uatmodel = uatdb.query(modeluat.DocumentModel).filter(modeluat.DocumentModel.modelName == m.modelName).first()
    if uatmodel is None:
        modeltoinsert = m.__dict__
        del modeltoinsert["_sa_instance_state"]
        invoiceid = modeltoinsert["idDocumentModel"]
        del modeltoinsert["idDocumentModel"]
        checkvendorid = uatdb.query(modeluat.VendorAccount).filter(modeluat.VendorAccount.idVendorAccount == modeltoinsert["idVendorAccount"]).first()
        if checkvendorid is not None:
            frmetadata = uatdb.query(model.FRMetaData).filter(model.FRMetaData.idInvoiceModel == invoiceid).first()
            print(invoiceid)
            if frmetadata is not None:
                print(frmetadata.__dict__)
    print(m.modelName)
    
