var { MailListener } = require("mail-listener6"); 
var EventSource = require("eventsource");
var conf = require("./config.json");
const storage = require("@azure/storage-blob");
const axios = require('axios');
const sessionStorage = require('node-sessionstorage');
var appInsights = require("applicationinsights");
var nodeoutlook = require('nodejs-nodemailer-outlook')
appInsights.setup(conf.appInsightsKey).start(); // assuming ikey in env var. start() can be omitted to disable any non-custom data
var client = appInsights.defaultClient;
(async () => {
  let config = await getConfig();
  const blobServiceClient = storage.BlobServiceClient.fromConnectionString(config.connectStr);
  let mailListener = new MailListener({
    username: config.username,
    password: config.password,
    host: config.host,
    port: 993, // imap port
    tls: true,
    connTimeout: 10000, // Default by node-imap
    authTimeout: 5000, // Default by node-imap,
    debug: console.log, // Or your custom function with only one incoming argument. Default: null
    tlsOptions: { rejectUnauthorized: false },
    mailbox: config.folder, // mailbox to monitor
    searchFilter: ["NEW","UNSEEN",["SINCE", new Date().toUTCString()]], // the search filter being used after an IDLE notification has been retrieved
    markSeen: true, // all fetched email willbe marked as seen and not fetched next time
    fetchUnreadOnStart: true, // use it only if you want to get all unread email on lib start. Default is `false`,
  });
  mailListener.start(); // start listening

  // stop listening
  //mailListener.stop();

  mailListener.on("server:connected", function(){
    console.log("imapConnected");
  });

  mailListener.on("mailbox", function(mailbox){
    console.log("Total number of mails: ", mailbox.messages.total); // this field in mailbox gives the total number of emails
  });

  mailListener.on("server:disconnected", function(){
    console.log("imapDisconnected");
    mailListener.start();
  });

  mailListener.on("error", function(err){
    console.log(err);
  });

  mailListener.on("headers", function(headers, seqno){
    
  });

  mailListener.on("body", function(body, seqno){
    
  })

  mailListener.on("attachment", function(attachment, path, seqno){
    
  });

  mailListener.on("mail",async function(mail, seqno) {
    let token = '';
    let resp = await axios.post(`${conf['host-endpoint']}/login`,{"username":conf.loginuser,"password":conf.loginpass});
    if(resp.data.token){
      token = resp.data.token;
    }
    let userId = conf.userId;
    let configresp = await axios.get(`${conf["host-endpoint"]}/emailconfig/getemailconfig/${userId}`,{headers:{'Authorization':`Bearer ${token}`}});
    if(configresp.data.message == 'success'){
      let config = configresp.data.config;
      let accepted_attachments = config.accepted_attachments
      let bulk_accepted_att = config.bulk_attachments
      let headers = {'Authorization':'Bearer '+token}
      if(mail.attachments.length > 0){
        let acceptedDomain = "";
        let acceptedMail = "";
        if(config.acceptedDomains != ""){
          for(let d of config.acceptedDomains){
            if(mail.from.text.toLowerCase().includes(d.toLowerCase())){
              acceptedDomain = d;
            }
          }
        }
        let acceptEm = false;
        let acceptEd = false;
        if(acceptedDomain != ""){
          acceptEd = true;
        }else{
          acceptedDomain = mail.from.text.split("@").length > 0 ? mail.from.text.split("@")[1].split(">")[0] : mail.from.text;
        }
        if(!Object.keys(config).includes('acceptedDomains')){
          acceptEd = true;
        }
        if(!acceptEd){
          console.log("Invalid domain");
          client.trackTrace({message: `ROVE HOTEL DEV, Mail Listener, Type: Invalid domain ${acceptedDomain}, Filename: None, EmailId: ${mail.from.text.split("<")[1].split(">")[0]}, Date: ${new Date().toISOString()}`});
          SendMail('ROVE HOTEL DEV, Mail Listener Domain Exception',`<b>Invalid domain ${acceptedDomain}</b>`,'','',[],mail.from.text.split("<")[1].split(">")[0]);
          return;
        }
        if(config.acceptedEmails != ""){
          const acceptEmail = config.acceptedEmails.some(element => {
            return element.toLowerCase() === mail.from.text.split("<")[1].split(">")[0].toLowerCase();
          });
          acceptEm = acceptEmail;
          acceptedMail = mail.from.text.split("<")[1].split(">")[0];
          if(!acceptEm){
            console.log("Invalid email id");
            client.trackTrace({message: `ROVE HOTEL DEV, Mail Listener, Type: Invalid Sender, Filename: None, EmailId: ${acceptedMail}, Date: ${new Date().toISOString()}`});
            SendMail('ROVE HOTEL DEV, Mail Email-Sender Exception',`<b>Invalid Sender ${acceptedMail}</b>`,'','',[],mail.from.text.split("<")[1].split(">")[0]);
          }
        }
        if(!Object.keys(config).includes('acceptedEmails')){
          acceptEm = true;
        }
        if((config.acceptedDomains == "" && config.acceptedEmails == "") || acceptEm || acceptEd){
          for(let att of mail.attachments){
            console.log(`attachment ${att.contentType}`)
            if(att.contentDisposition == 'attachment' && accepted_attachments.includes(att.contentType)){
                const containerClient = blobServiceClient.getContainerClient(config.containerName);
                const content = att.content;
                const blobName = "Uploadeddocs/"+att.filename;
                const blockBlobClient = containerClient.getBlockBlobClient(blobName);
                await blockBlobClient.upload(content, content.length);
                const cerds = new storage.StorageSharedKeyCredential(config.accountname,config.accountkey);
                var startDate = new Date();
                var expiryDate = new Date();
                startDate.setTime(startDate.getTime() - 5*60*1000);
                expiryDate.setTime(expiryDate.getTime() + 24*60*60*1000);
                const containerSAS = storage.generateBlobSASQueryParameters({
                    expiresOn : expiryDate,
                    permissions: storage.ContainerSASPermissions.parse("rwl"),
                    protocol: storage.SASProtocol.Https,
                    containerName: config.containerName,
                    startsOn: startDate,
                    version:"2018-03-28",
                    contentType:att.contentType
                },cerds).toString();
                let filepath = `https://${config.accountname}.blob.core.windows.net/${config.containerName}/Uploadeddocs/${att.filename}?${containerSAS}`
                config["url"] = filepath;
                let vendorresp = await axios.post(`${config["bulk_upload_url"]}/getVendorDetails`,config,{headers:{"token":config.accountkey}})
                console.log(vendorresp.data);
                if(vendorresp.data["message"] == "success"){
                  if(vendorresp.data["vendorName"] != "DU"){
                    let entityID = vendorresp.data["entityID"];
                    if(entityID == 'Not Found'){
                      SendMail('ROVE HOTEL DEV, Entity Not Found Exception',`<b> Cannot process file : ${att.filename}, No Entity match from list of synonyms</b>`,'','',[],mail.from.text.split("<")[1].split(">")[0]);
                      return;
                    }
                    let vendoraccountresp = await axios.get(`${config['host-endpoint']}/emailconfig/getvendoraccount/${vendorresp.data["vendorName"]}?entityID=${entityID}`,{headers:headers})
                    console.log(vendoraccountresp.data);
                    if(!(Object.keys(vendoraccountresp.data).includes('message'))){
                      let purchaseOrder = vendorresp.data["purchaseOrder"];
                      let vendorAccountID = vendoraccountresp.data.result[0].idVendorAccount;
                        let eventSourceObj = {
                        'file_path':filepath,
                        'vendorAccountID':vendorAccountID,
                        'poNumber':purchaseOrder,
                        'VendoruserID':userId,
                        'filetype':att.contentType,
                        'filename':att.filename,
                        'source':'Mail',
                        'sender':mail.from.text.split("<")[1].split(">")[0],
                        'entityID':entityID
                      }
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
                            await axios.get(`${config['host-endpoint']}/Vendor/submitVendorInvoice/1?re_upload=${false}&inv_id=${final_data.InvoiceID}`,{headers:headers});
                            await axios.post(`${config['host-endpoint']}/fr/triggerbatch/${final_data.InvoiceID}`,{headers:headers})
                          } catch (error) {
                            console.error(error);
                          }
                      } else {
                          evtSource.close();
                        }
                      });
                      evtSource.onerror = (err)=> {
                        evtSource.close();
                        console.error("EventSource failed:", err);
                      };
                    }else{
                      console.log(`No Vendor Account found for document ${att.filename}`);
                      client.trackTrace({message: `ROVE HOTEL DEV, Mail Listener, Type: No Vendor Match, Filename: ${att.filename}, EmailId: ${mail.from.text.split("<")[1].split(">")[0]}, Date: ${new Date().toISOString()}`});
                      SendMail('ROVE HOTEL DEV, No Vendor Account Exception',`<b> Cannot process file : ${att.filename}, No Vendor Account found for vendor ${vendorresp.data["vendorName"]}</b>`,'','',[],mail.from.text.split("<")[1].split(">")[0]);
                    }
                  }else{
                    let resp = await axios.post(`${config["host-endpoint"]}/ocr/status/saveutility`,{'filename':att.filename,"filepath":filepath},{headers:headers})
                    console.log(`DU bill uploaded ${resp.data}`);
                  }
                  
                }else{
                  console.log(`No matching vendor found for document ${att.filename}`);
                  client.trackTrace({message: `ROVE HOTEL DEV, Mail Listener, Type: No Vendor Match, Filename: ${att.filename}, EmailId: ${mail.from.text.split("<")[1].split(">")[0]}, Date: ${new Date().toISOString()}`});
                  SendMail('ROVE HOTEL DEV, No Vendor Exception',`<b> Cannot process file : ${att.filename}, No Vendor found </b>`,'','',[],mail.from.text.split("<")[1].split(">")[0]);
                }
                
            }else if(att.contentDisposition == 'inline'){
              console.log("Signature Detecture in Email");
              client.trackTrace({message: `ROVE HOTEL DEV, Signature Detected in email: ${att.filename}, File type of ${att.contentType}`});
              
            }else if(bulk_accepted_att.includes(att.contentType)){
              console.log("Invalid file type");
              client.trackTrace({message: `ROVE HOTEL DEV, Mail Listener, Type: Filetype Exception, Filename: ${att.filename}, EmailId: ${mail.from.text.split("<")[1].split(">")[0]}, Date: ${new Date().toISOString()}`});
              SendMail('ROVE HOTEL DEV, Filetype Exception',`<b> Cannot process file : ${att.filename}, File type ${att.contentType} not supported </b>`,'','',[],mail.from.text.split("<")[1].split(">")[0]);
            
              // const containerClient = blobServiceClient.getContainerClient(config.containerName);
              // const content = att.content;
              // const blobName = "Uploadeddocsbulk/"+att.filename;
              // const blockBlobClient = containerClient.getBlockBlobClient(blobName);
              // await blockBlobClient.upload(content, content.length);
              // const cerds = new storage.StorageSharedKeyCredential(config.accountname,config.accountkey);
              // var startDate = new Date();
              // var expiryDate = new Date();
              // startDate.setTime(startDate.getTime() - 5*60*1000);
              // expiryDate.setTime(expiryDate.getTime() + 24*60*60*1000);
              // const containerSAS = storage.generateBlobSASQueryParameters({
              //     expiresOn : expiryDate,
              //     permissions: storage.ContainerSASPermissions.parse("rwl"),
              //     protocol: storage.SASProtocol.Https,
              //     containerName: config.containerName,
              //     startsOn: startDate,
              //     version:"2018-03-28",
              //     contentType:att.contentType
              // },cerds).toString();
              // let filepath = `https://${config.accountname}.blob.core.windows.net/${config.containerName}/Uploadeddocsbulk/${att.filename}?${containerSAS}`
              // config["url"] = filepath;
              // config["filetype"] = att.contentType
              // await axios.post(`${config["bulk_upload_url"]}/bulk_upload`,config,{headers:{"Token":token,"userId":userId}});
            }else{
              console.log("Invalid file type");
              client.trackTrace({message: `ROVE HOTEL DEV, Mail Listener, Type: Filetype Exception, Filename: ${att.filename}, EmailId: ${mail.from.text.split("<")[1].split(">")[0]}, Date: ${new Date().toISOString()}`});
              SendMail('ROVE HOTEL DEV, Filetype Exception',`<b> Cannot process file : ${att.filename}, File type ${att.contentType} not supported </b>`,'','',[],mail.from.text.split("<")[1].split(">")[0]);
            }
          }
        }
      }
    }
  })
})().catch(console.error);

async function getConfig(){
  let userId = conf.userId;
  if(sessionStorage.getItem("token")){
    token = sessionStorage.getItem("token");
  }else{
      let resp = await axios.post(`${conf['host-endpoint']}/login`,{"username":conf.loginuser,"password":conf.loginpass});
      if(resp.data.token){
        token = resp.data.token;
        sessionStorage.setItem("token",resp.data.token);
      }
  }
  let configresp = await axios.get(`${conf["host-endpoint"]}/emailconfig/getemailconfig/${userId}`,{headers:{'Authorization':`Bearer ${token}`}});
  if(configresp.data.message == "success"){
    return configresp.data.config;
  }else{
    return {}
  }
}
async function SendMail(sub,html,text,replyto,attachment,mailreceiver){
nodeoutlook.sendEmail({
    auth: {
        user: conf.mailsender,
        pass: conf.mailpassword
    },
    from: conf.mailsender,
    to: mailreceiver,
    subject: sub,
    html: html,
    text: text,
    replyTo: replyto,
    attachments: attachment,
    onError: (e) => console.log(e),
    onSuccess: (i) => console.log(i)
});
}

//Attahcment format
// [
//   {
//       filename: 'text1.txt',
//       content: 'hello world!'
//   },
//   {   // binary buffer as an attachment
//       filename: 'text2.txt',
//       content: new Buffer('hello world!','utf-8')
//   },
//   {   // file on disk as an attachment
//       filename: 'text3.txt',
//       path: '/path/to/file.txt' // stream this file
//   },
//   {   // filename and content type is derived from path
//       path: '/path/to/file.txt'
//   },
//   {   // stream as an attachment
//       filename: 'text4.txt',
//       content: fs.createReadStream('file.txt')
//   },
//   {   // define custom content type for the attachment
//       filename: 'text.bin',
//       content: 'hello world!',
//       contentType: 'text/plain'
//   },
//   {   // use URL as an attachment
//       filename: 'license.txt',
//       path: 'https://raw.github.com/nodemailer/nodemailer/master/LICENSE'
//   },
//   {   // encoded string as an attachment
//       filename: 'text1.txt',
//       content: 'aGVsbG8gd29ybGQh',
//       encoding: 'base64'
//   },
//   {   // data uri as an attachment
//       path: 'data:text/plain;base64,aGVsbG8gd29ybGQ='
//   },
//   {
//       // use pregenerated MIME node
//       raw: 'Content-Type: text/plain\r\n' +
//            'Content-Disposition: attachment;\r\n' +
//            '\r\n' +
//            'Hello world!'
//   }
// ]

// it's possible to access imap object from node-imap library for performing additional actions. E.x.
//mailListener.imap.move(:msguids, :mailboxes, function(){})