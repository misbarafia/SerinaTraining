var Excel = require('exceljs');
var wb = new Excel.Workbook();
var EventSource = require("eventsource");
var axios = require('axios');
var express = require('express');
var conf = require('./config.json');
var appInsights = require("applicationinsights");
appInsights.setup(conf.appInsightsKey).start(); // assuming ikey in env var. start() can be omitted to disable any non-custom data
var client = appInsights.defaultClient;
var nodeoutlook = require('nodejs-nodemailer-outlook')
var formrecognizer = require('./formrecognizer');
var app = express();
var bodyParser = require('body-parser')
app.use(bodyParser.urlencoded({limit: '50mb', extended: true}))
app.use(bodyParser.json({limit:'50mb'}))
app.post('/getVendorDetails',async function(req,res){
    let token = '',filepath = '';
    try{
        token = req.headers['token'];
        if(token != conf.accountkey){
           return res.json({"message":"Unauthorized Request","code":"401"});
        }
    }catch(ex){
        return res.json({"message":"Unauthorized Request","code":"401"});
    }
    let req_body = req.body;
    try{
        filepath = req_body['url'];
    }catch(ex){
        return res.json({"message":"Invalid file input","code":"402"})
    }
    try{
        let details = await formrecognizer.getVendorName(req_body);
        if(!details['entityID']){
            client.trackTrace({message: `ROVE HOTEL DEV,Bulk Mail Listener Entity Exception - No Entity found from Synonyms`});
            details['entityID'] = 'Not Found';
        }
        if(details['vendorName'] == ''){
            return res.json({"message":"exception","vendorName":details['vendorName'],"purchaseOrder":details['purchaseOrder'],"entityID":details["entityID"],"code":"200"})        
        }
        return res.json({"message":"success","vendorName":details['vendorName'],"purchaseOrder":details['purchaseOrder'],"entityID":details["entityID"],"code":"200"})    
    }catch(ex){
        client.trackTrace({message: `ROVE HOTEL DEV,Bulk Mail Listener VendorName Exception - No Vendor Found from Synonyms`});
        return res.json({"message":"exception","vendorName":'',"purchaseOrder":'',"code":"400"})    
    }
});

app.post('/bulk_upload',async function (req, res) {
    let token = '',userId = conf.userId;
    try{
        token = req.headers['token'];
        userId = req.headers['userid'];
    }catch(ex){
        res.json({"message":"Unauthorized Request","code":"401"});
    }
    
    let headers = {'Authorization':'Bearer '+token}
    let config = req.body;
    try{
        if(!config['url'] || !config['filetype']){
            res.json({"message":"Invalid json schema","code":"402"})
        }else{
            file_url = config['url']
            file_type = config['filetype']
            let resp = await axios.get(file_url, {responseType: 'arraybuffer'});
            if(resp.data){
                if(file_type == config.bulk_attachments[0]){
                    wb.xlsx.load(resp.data).then(function(){
                        let sh = wb.getWorksheet("Sheet1");
                        sh.eachRow(async function(row,rownumber){
                            if(row.number == 1){
                                if(config.accepted_headers != row.values[1].toLowerCase()){
                                    return res.json({"message":"Invalid Excel Structure","code":"101"});
                                }
                            }
                            if(row.number > 1){
                                let doc_url = row.values[1]['text'];
                                let resp = await axios.get(doc_url);
                                let content_type = resp.headers['content-type'];
                                let filename = doc_url.split("?")[0];
                                filename = filename.substring(filename.lastIndexOf('/')+1);
                                config["url"] = doc_url;
                                let details = await formrecognizer.getVendorName(config);
                                if(!details['entityID']){
                                    client.trackTrace({message: `ROVE HOTEL DEV,Bulk Mail Listener Entity Exception - No Entity found from Synonyms`});
                                    details['entityID'] = 'Not Found';
                                }
                                let vendorName = details['vendorName'];
                                if(vendorName == ''){
                                    client.trackTrace({message: `ROVE HOTEL DEV,Bulk Mail Listener VendorName Exception - No Vendor Found for file ${filename}`});
                                    SendMail('ROVE HOTEL DEV, No Vendor Exception',`<b> Cannot process file , No Vendor found for  file ${filename}</b>`,'','',[]);
                                    return res.json({"message":"No Vendor Found for file "+filename,"code":"200"})
                                }
                                let purchaseOrder = details['purchaseOrder'];
                                let entityID = details['entityID'];
                                let vendoraccountresp = await axios.get(`${config['host-endpoint']}/emailconfig/getvendoraccount/${vendorName}?entityID=${entityID}`,{headers:headers})
                                console.log(vendoraccountresp.data);
                                if(!(Object.keys(vendoraccountresp.data).includes('message'))){
                                    let vendorAccountID = vendoraccountresp.data.result[0].idVendorAccount;
                                    let eventSourceObj = {
                                        'file_path':doc_url,
                                        'vendorAccountID':vendorAccountID,
                                        'poNumber':purchaseOrder,
                                        'VendoruserID':userId,
                                        'filetype':content_type,
                                        'filename':filename,
                                        'source':'Mail',
                                        'sender':'',
                                        'entityID':entityID
                                    }
                                    console.log(eventSourceObj);
                                    const evtSource = new EventSource(`${config["host-endpoint"]}/ocr/status/stream?eventSourceObj=${encodeURIComponent(JSON.stringify(eventSourceObj))}&UploadType=${false}`);
                                    evtSource.addEventListener("update", (event) => {
                                    console.log(event.data);
                                    });
                                    evtSource.addEventListener("end", async (event) => {
                                    let final_data = JSON.parse(event.data);
                                    if(final_data.InvoiceID){
                                        evtSource.close();
                                        try {
                                            let headers = {'Authorization':'Bearer '+token}
                                            const response = await axios.get(`${config['host-endpoint']}/Vendor/submitVendorInvoice/1?re_upload=${false}&inv_id=${final_data.InvoiceID}`,{headers:headers});
                                            await axios.post(`${config['host-endpoint']}/fr/triggerbatch/${final_data.InvoiceID}`,{headers:headers})
                                        } catch (error) {
                                            console.error(error);
                                        }
                                    } else {
                                        evtSource.close();
                                    }
                                    });
                                    evtSource.onerror = (err)=> {
                                    evtSource.close()
                                    console.error("EventSource failed:", err);
                                    };
                                }else{
                                    client.trackTrace({message: `ROVE HOTEL DEV,Bulk Mail Listener No Vendor Account Exception - Filename: ${filename}`});
                                    SendMail('ROVE HOTEL DEV, No Vendor Account Exception',`<b> Cannot process file : ${filename}, No Vendor Account found for vendor ${vendorName}</b>`,'','',[]);
                                }
                                
                            }
                        })
                    });
                }
            }
        }
    }catch(ex){
        res.json({"message":"exception","code":"500"});
    }
    res.json({"message":"success","code":"200"})
});
app.post("/sharepoint_handler",async function(req,res){
    try{
        let token = ''
        try{
            token = req.headers['token'];
        }catch(ex){
            res.json({"message":"Unauthorized Request","code":"401"});
        }
        let frconfig = req.body;
        console.log(frconfig);
        let details = {'VendorName':'','purchaseOrder':''}
        try{
            details = await formrecognizer.getVendorName(frconfig);
            if(!details['entityID']){
                client.trackTrace({message: `ROVE HOTEL DEV,Bulk Mail Listener Entity Exception - No Entity found from Synonyms`});
                SendMail('ROVE HOTEL DEV, No Entity Found Exception',`<b> Cannot process file , No Entity Found from list of synonyms</b>`,'','',[],frconfig['sender']);
            }
        }catch(ex){
            client.trackTrace({message: `ROVE HOTEL DEV,Bulk Mail Listener VendorName Exception - No Vendor Found from Synonyms`});
            SendMail('ROVE HOTEL DEV, No Vendor Exception',`<b> Cannot process file , No Vendor found using synonyms</b>`,'','',[],frconfig['sender']);
        }
        let headers = {'Authorization':'Bearer '+token}
        let vendorName = details['vendorName'];
        let purchaseOrder = details['purchaseOrder'];
        let entityID = details['entityID'];
        let doc_url = frconfig["url"]
        let filename = frconfig["filename"]
        if(vendorName == ''){
            client.trackTrace({message: `ROVE HOTEL DEV,Bulk Mail Listener VendorName Exception - No Vendor Found for file ${filename}`});
            SendMail('ROVE HOTEL DEV, No Vendor Exception',`<b> Cannot process file , No Vendor found for  file ${filename}</b>`,'','',[],frconfig['sender']);
            return res.json({"message":"No Vendor Found for file "+filename,"code":"200"})
        }
        let vendoraccountresp = await axios.get(`${frconfig['host-endpoint']}/emailconfig/getvendoraccount/${vendorName}?entityID=${entityID}`,{headers:headers})
        console.log(vendoraccountresp.data);
        if(!(Object.keys(vendoraccountresp.data).includes('message'))){
            let vendorAccountID = vendoraccountresp.data.result[0].idVendorAccount;
            let content_type = frconfig["content_type"];
            let eventSourceObj = {
                'file_path':doc_url,
                'vendorAccountID':vendorAccountID,
                'poNumber':purchaseOrder,
                'VendoruserID':1,
                'filetype':content_type,
                'filename':filename,
                'source':'SharePoint',
                'sender': frconfig['sender'],
                'entityID':entityID
            }
            console.log(eventSourceObj);
            const evtSource = new EventSource(`${frconfig["host-endpoint"]}/ocr/status/stream?eventSourceObj=${encodeURIComponent(JSON.stringify(eventSourceObj))}&UploadType=${false}`);
            evtSource.addEventListener("update", (event) => {
            console.log(event.data);
            });
            evtSource.addEventListener("end", async (event) => {
            let final_data = JSON.parse(event.data);
            if(final_data.InvoiceID){
                evtSource.close();
                try {
                    let headers = {'Authorization':'Bearer '+token}
                    const response = await axios.get(`${frconfig['host-endpoint']}/Vendor/submitVendorInvoice/1?re_upload=${false}&inv_id=${final_data.InvoiceID}`,{headers:headers});
                    await axios.post(`${frconfig['host-endpoint']}/fr/triggerbatch/${final_data.InvoiceID}`,{headers:headers})
                } catch (error) {
                    console.error(error);
                }
            } else {
                evtSource.close();
            }
            });
            evtSource.onerror = (err)=> {
            evtSource.close()
            console.error("EventSource failed:", err);
            };
        }else{
            client.trackTrace({message: `ROVE HOTEL DEV,Bulk Mail Listener No Vendor Account Exception - Filename: ${filename}`});
            SendMail('ROVE HOTEL DEV, No Vendor Account Exception',`<b> Cannot process file : ${filename}, No Vendor Account found for vendor ${vendorName}</b>`,'','',[],frconfig['sender']); 
        }
        
    }catch(ex){
        console.log(ex)
        res.json({"message":"exception","code":"500"})
    }
    res.json({"message":"success","code":"200"})
})
app.get("/",function(req,res){
    res.send("Hello World!!");
})
var server = app.listen(3000, function () {
   var host = server.address().address
   var port = server.address().port
   console.log("Example app listening at http://%s:%s", host, port)
})

async function SendMail(sub,html,text,replyto,attachment,receiver){
    nodeoutlook.sendEmail({
        auth: {
            user: conf.mailsender,
            pass: conf.mailpassword
        },
        from: conf.mailsender,
        to: receiver,
        subject: sub,
        html: html,
        text: text,
        replyTo: replyto,
        attachments: attachment,
        onError: (e) => console.log(e),
        onSuccess: (i) => console.log(i)
    });
}