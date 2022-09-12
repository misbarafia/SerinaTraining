from sqlalchemy import func
import sys
sys.path.append("..")
import model


def checkOCRError(invoiceID, db):

    try:
        # get modelID
        result = db.query(model.Document).filter(model.Document.idDocument ==
                                                 invoiceID).first()
        modelID = result.documentModelID
        # Find OCR Threshold
        result = db.query(model.FRMetaData).filter(model.FRMetaData.idInvoiceModel ==
                                                   modelID).first()
        errorThreshold = result.ErrorThreshold
        # Check for OCR error occurence
        occurence = db.query(func.count(model.OCRLogs.documentId)).filter(
            model.OCRLogs.documentId == invoiceID).scalar()
        # Check if  exceeds threshold
        if occurence >= errorThreshold:
            # raise notification
            pass
    except Exception as e:
        print(e)
        return {"Error": "DB error", "Desc": "Error while OCR error check"}
