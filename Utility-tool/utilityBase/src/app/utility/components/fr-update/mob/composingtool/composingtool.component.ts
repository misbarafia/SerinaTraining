import { HttpClient } from '@angular/common/http';
import { AfterViewInit, Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { SharedService } from 'src/app/services/shared/shared.service';

@Component({
  selector: 'app-composingtool',
  templateUrl: './composingtool.component.html',
  styleUrls: ['./composingtool.component.css']
})
export class ComposingtoolComponent implements OnInit,AfterViewInit {
  frp_id:any;
  p_name:any;
  pid:any;
  resp:any;
  previoustraining:any[]=[];
  models:any[]=[];
  nottrained:boolean=true;
  selectedmodels:any[]=[];
  disabled:boolean = true;
  composing:boolean = false;
  saving:boolean =false;
  modelName:string = "";
  modelId:string="";
  averageAccuracy:string="";
  composeresult:any;
  loaded:boolean = false;
  @Input() modelData:any;
  @Input() frConfigData:any; 
  @Input() showtab:any;
  @Output() changeTab = new EventEmitter<{'show1':boolean,'show2':boolean,'show3':boolean,'show4':boolean}>();
  constructor(private sharedService:SharedService) { }
  
  ngOnInit(): void {
      try {
        this.setup();
      }catch(ex){
        console.log(ex)
      }
  }
  ngAfterViewInit(): void {
    sessionStorage.setItem("modelData",JSON.stringify(this.modelData));
    sessionStorage.setItem("frConfigData",JSON.stringify(this.frConfigData));
  }
  navigatetoPage(page:string){
    if(page == 'tagging'){
      this.changeTab.emit({'show1':true,'show2':false,'show3':false,'show4':false});
    }else if(page == 'training'){
      this.changeTab.emit({'show1':false,'show2':true,'show3':false,'show4':false});
    }else if(page == 'composing'){
      this.changeTab.emit({'show1':false,'show2':false,'show3':true,'show4':false});
    }else{
      this.changeTab.emit({'show1':false,'show2':false,'show3':false,'show4':true});
    }
  }
  selectmodel(id,i){
    let model = this.models.filter(v => v.modelInfo.modelId == id)[0];
    let inp = (<HTMLInputElement>document.getElementById("model-"+i));
    if(inp.checked){
      inp.checked = false;
      this.selectedmodels = this.selectedmodels.filter(v => v != model);
    }else{
      inp.checked = true;
      this.selectedmodels.push(model);
    }
    if(this.selectedmodels.length > 1){
      this.disabled = false;
    }else{
      this.disabled = true;
    }
  }
  async setup(){
    this.loaded = false;
    if(!this.modelData){
      this.modelData = JSON.parse(sessionStorage.getItem("modelData"));
      this.frConfigData = JSON.parse(sessionStorage.getItem("frConfigData")); 
    }
    if(this.selectedmodels.length > 1){
      this.disabled = false;
    }else{
      this.disabled = true;
    }
    let result_id = null,modeltype = null;
    if(this.modelData.idVendorAccount){
      modeltype = 'vendor';
      result_id = this.modelData.idVendorAccount;
    }else{
      modeltype = 'sp';
      result_id = this.modelData.idServiceAccount;
    }
    this.sharedService.getModelsByVendor(modeltype,result_id).subscribe((data:any) =>{
      this.resp = data;
      this.loaded = true;
      console.log(this.resp);
      if(this.resp['message'] == 'success'){
        this.previoustraining = this.resp['result']
        if(this.previoustraining.length > 0){
          for(let p of this.previoustraining){
            let jsonobj = JSON.parse(p.training_result);
            this.models.push(jsonobj);
          }
          this.nottrained = false;
        }else{
          this.nottrained = true;
        }
      }
    })
  }
  
  async composeModels(){
    let modelIds:any[] = [];
    let modelName = (<HTMLInputElement>document.getElementById("modelname")).value;
    for(let s of this.selectedmodels){
      modelIds.push(s.modelInfo.modelId);
    }
    if(modelIds.length == 0){
      return;
    }
    if(modelIds.length >= 100){
      alert('Limit Reached! You can only compose 100 models at a time!');
      return;
    }
    this.composing = true;
    let modelsobj = {
      'modelName':modelName,
      'modelIds':modelIds
    }
    this.sharedService.composeModels(modelsobj).subscribe((data:any) => {
      this.resp = data;
      this.composing = false;
      if(this.resp['message'] == 'success'){
        if(this.resp['result']['message'] == 'success'){
          this.composeresult = this.resp['result']['result'];
          this.modelName = this.resp['result']['result']['modelInfo']['modelName'];
          this.modelId = this.resp['result']['result']['modelInfo']['modelId'];
          this.averageAccuracy = (Number(this.resp['result']['result']['composedTrainResults'][0]['averageModelAccuracy'] * 100)+ "%");
        }
      }
    })
  }
  async saveModel(){
    this.saving = true;
    let modelName = (<HTMLInputElement>document.getElementById("modelname")).value;
    let resultobj = {'training_result':JSON.stringify(this.composeresult),'composed_name':modelName,'vendorAccountId':this.modelData.idVendorAccount,'serviceAccountId':this.modelData.idServiceAccount}
    this.sharedService.saveComposedModel(resultobj).subscribe((data:any) => {
      this.resp = data;
      this.saving = false;
      this.models = [];
      this.selectedmodels = [];
      this.setup();
    })
  }
}
