var axios = require('axios');
var FuzzyMatching = require('fuzzy-matching');
var conf = require('./config.json');

async function getVendorName(config){
    let get_resp = {};
    let token = '';
    let resp = await axios.post(`${conf['host-endpoint']}/login`,{"username":conf.loginuser,"password":conf.loginpass});
    if(resp.data.token){
      token = resp.data.token;
    }
    let entity_resp = await axios.get(`${conf['host-endpoint']}/fr/get_entities`,{headers:{'Authorization':'Bearer'+token}});  
    let entityObj = {}
    for(let obj of entity_resp.data){
        entityObj[obj['idEntity']] = obj['Synonyms'] ? obj['Synonyms'].split(",") : "";
    }
    try{
        let post_resp = await axios.post(`${config['serina-endpoint']}/formrecognizer/documentModels/${config.model}:analyze?${config['fr-version']}&stringIndexType=textElements`,{"urlSource":config["url"]},{headers:{'Content-Type':'application/json','Ocp-Apim-Subscription-Key':config['fr-key']}});
        if(post_resp.status == 202){
            let get_url = post_resp.headers["operation-location"];
            let status = "notcomplete";
            while(status != "succeeded"){
                get_resp = await axios.get(get_url,{headers:{'Content-Type':'application/json','Ocp-Apim-Subscription-Key':config['fr-key']}});
                status = get_resp.data.status;
            }
        }
    }catch(ex){
        console.log(ex);
    }
    let ocrtext = get_resp.data.analyzeResult.content.toLowerCase();
    if(ocrtext.includes("du.ae/vat")){
        return {'vendorName':'DU','purchaseOrder':'','entityID':'13'}
    }
    let entityID,entityfound = false;
    for(let entitykey in entityObj){
        for(let v of entityObj[entitykey]){
            if(ocrtext.includes(v.toLowerCase())){
                entityID = entitykey;
                entityfound = true;
            }
            if(entityfound){
                break;
            }
        }
        if(entityfound){
            break;
        }
    }
    console.log(entityObj[entityID]);
    let PurchaseOrder = '';
    if(Object.keys(get_resp.data.analyzeResult.documents[0].fields).includes('PurchaseOrder')){
        if(get_resp.data.analyzeResult.documents[0].fields['PurchaseOrder'].confidence > 0.85){
            PurchaseOrder = get_resp.data.analyzeResult.documents[0].fields['PurchaseOrder'].valueString;
        }else{
            PurchaseOrder = '';
        }
    }
    let synonyms = config.synonyms;
    let vendorName = '';
    let match_found = false;
    for(let k of Object.keys(synonyms)){
        for(let v of synonyms[k]){
            if(ocrtext.includes(v.toLowerCase())){
                console.log(`Matched ${ocrtext}: ${v}`);
                vendorName = k;
                match_found = true;
            }
            if(match_found){
                break;
            }
        }
        if(match_found){
            break;
        }
    }
    // let match_found = false;
    // let highestobj = {'distance':0,'value':''};
    // try{
    //     for(let w of wordsArr){
    //         for(let k of Object.keys(synonyms)){
    //             let fm = new FuzzyMatching(synonyms[k]);
    //             let result = fm.get(w);
    //             if(result.distance == 1){
    //                 vendorName = k;
    //                 match_found = true;
    //             }else if(result.distance > 0.91 && result.distance < 0.99){
    //                 if(highestobj.distance <= result.distance){
    //                     highestobj = result;
    //                     highestobj.value = k;
    //                 }else{
    //                     highestobj = highestobj;
    //                 }
    //             }else{
    //                 if(highestobj.distance <= result.distance){
    //                     highestobj = result;
    //                     highestobj.value = k;
    //                 }else{
    //                     highestobj = highestobj;
    //                 }
    //             }
    //             if(match_found)
    //             break;
    //         }
    //         if(match_found)
    //         break;
    //     }
    // }catch(ex){
    //     match_found = false;
    // }
    // if(!match_found){
    //     console.log(highestobj);
    //     vendorName = highestobj.value;
    // }
    console.log(vendorName);
    return {'vendorName':vendorName,'purchaseOrder':PurchaseOrder,'entityID':entityID}
}

module.exports.getVendorName = getVendorName;
