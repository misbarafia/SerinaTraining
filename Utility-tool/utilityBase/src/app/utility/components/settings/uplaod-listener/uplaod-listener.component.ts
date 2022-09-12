import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Component, OnInit } from '@angular/core';
import { SharedService } from './../../../../services/shared/shared.service';
@Component({
  selector: 'app-uplaod-listener',
  templateUrl: './uplaod-listener.component.html',
  styleUrls: ['./uplaod-listener.component.scss']
})
export class UplaodListenerComponent implements OnInit {
  configData : FormGroup;
  exception:boolean =false;
  msg:string="";
  err:string="";
  saving:boolean=false;
  constructor(private fb:FormBuilder,private sharedService:SharedService) {
    this.configData = this.fb.group({
       host: [''],
       username : ['',[Validators.required,Validators.email]],
       password : ['',Validators.required],
       folder : [''],
       acceptedDomains:[''],
       acceptedEmails:[''],
       loginuser: ['',Validators.required],
       loginpass: ['',Validators.required]
    })
   }

  ngOnInit(): void {
    this.getmailConfig();
  }
  getmailConfig(){
    this.sharedService.getemailconfig().subscribe(data => {
      if(data['message'] == "success"){
       this.configData.patchValue({'username':data['config'].username,'password':data['config'].password,'host':data['config'].host,'folder':data['config'].folder,'loginuser':'','loginpass':'','acceptedDomains':data["config"]['acceptedDomains'],'acceptedEmails':data["config"]['acceptedEmails']})
      }
    })
  }

  saveConfigData() {
  }
  SavePassword(){
    let loginuser = (<HTMLInputElement>document.getElementById("loginuser")).value;
    let loginpass = (<HTMLInputElement>document.getElementById("loginpass")).value;
    this.configData.patchValue({'loginuser':loginuser,'loginpass':loginpass});
    if(this.configData.invalid){
      if(this.configData.controls['username'].value == ''){
        this.err = "Please enter valid email!"
      }
      if(this.configData.controls['password'].value == ''){
        this.err = "Please enter email password!"
      }
      if(this.configData.controls['loginpass'].value == ''){
        this.err = "Please enter valid account credentials!"
      }
      this.exception = true;
      return;
    }else{
      this.exception = false;
      this.err = "";
      this.saving = true;
      this.sharedService.saveemailconfig(this.configData.value).subscribe(data => {
        this.saving = false;
        if(data['message'] == "success"){
          this.msg = "Email Settings Saved!"
        }else{
          this.exception = true;
          this.msg = "";
          this.err = "Some Error occured!"
        }
      });
    }

  }
}
