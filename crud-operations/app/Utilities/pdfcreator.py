from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib import colors
import pytz as tz
import os
from datetime import datetime
tz_region_name = os.getenv("serina_tz", "Asia/Dubai")
tz_region = tz.timezone(tz_region_name)

def createdoc(all_status,doc_data,docid):
    filename = "Invoice#"+str(docid)+"_JourneyMap.pdf"
    image = 'Utilities/serinaimg.jpg'
    subtitle = 'Invoice Journey Document'
    pdf = canvas.Canvas(filename)
    pdf.drawImage(image, 10, 780,120,50)
    pdf.setFillColor(colors.black)
    pdf.setFont("Courier-Bold", 18)
    pdf.drawCentredString(290, 750, subtitle)
    startX = 40
    startY = 580
    invoiceId = ''
    for s in all_status:
        invoiceId = s.docheaderID
        text = pdf.beginText(startX,startY)
        text.setFont("Courier-Bold", 10)
        color = colors.green
        if s.dochistorystatus == 'Invoice Uploaded':
            color = colors.blue
        elif s.dochistorystatus == 'OCR Error Found' or s.DocumentHistoryLogs.documentdescription == "Error in posting the invoice, but invoice saved as Pending invoice":
            color = colors.red
        text.setFillColor(color)
        if s.dochistorystatus == "":
            text.textline("\u2022 GRN Created in ERP & "+s.dochistorystatus)
        else:
            text.textLine("\u2022 "+ s.dochistorystatus if s.dochistorystatus is not None else "\u2022 "+ s.DocumentHistoryLogs.documentdescription)
        dt = s.DocumentHistoryLogs.CreatedOn
        pdf.drawText(text)
        text.setFillColor(colors.black)
        text.setFont("Courier", 10)
        text.textLine("Done By: "+ s.firstName if s.firstName is not None else ""+ " "+ s.lastName if s.lastName is not None else "")
        text.textLine("Date & Time: "+ dt.strftime('%d-%m-%Y %H:%M:%S %p'))
        text.setLeading(20)
        pdf.drawText(text)
        startY -= 70
    text = pdf.beginText(40,700)
    text.setFont("Courier-Bold", 12)
    text.setFillColor(colors.black)
    text.textLine("Invoice Number: "+ invoiceId)
    text.textLine("Invoice Date: "+ doc_data['InvoiceDate'])
    text.textLine("PO #: "+doc_data['PO'])
    text.textLine("GRN #: "+doc_data['GRN'])
    text.textLine("Entity: "+ doc_data['Entity'])
    text.textLine("Vendor/Service Provider: "+ doc_data['Vendor'])
    text.textLine("Date/Time: "+datetime.now(tz_region).strftime("%d-%m-%Y %H:%M:%S %p"))
    pdf.drawText(text)
    dslogo = 'Utilities/ds-logo.png'
    pdf.drawImage(dslogo, 10, 10,50,30)
    pdf.save()
    return filename