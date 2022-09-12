import { MessageService } from 'primeng/api';
import { Component, OnInit } from '@angular/core';
import { FormBuilder, Validators, FormGroup } from '@angular/forms';
import { SharedService } from 'src/app/services/shared/shared.service';

@Component({
  selector: 'app-sharepoint-listener',
  templateUrl: './sharepoint-listener.component.html',
  styleUrls: ['./sharepoint-listener.component.scss']
})
export class SharepointListenerComponent implements OnInit {
  configData:FormGroup;
  sharepointData: any;
  editable:boolean;

  constructor(private fb:FormBuilder,
    private sharedService:SharedService,
    private messageService: MessageService) {
    this.configData = this.fb.group({
      client_id : ['',Validators.required],
      client_secret  : ['',Validators.required],
      site_url  : ['',Validators.required],
      folder  : [''],
      service_url: ['']
    })
   }

  ngOnInit(): void {
    this.readConfigData();
    this.configData.disable();
  }

  editBtnCilck(){
    this.configData.enable();
    this.editable = true;
  }

  onCancel(){
    this.editable = false;
    this.configData.disable();
  }
  saveConfigData(){
    console.log(this.configData.value)
    this.sharedService.saveSharePointConfig(JSON.stringify(this.configData.value)).subscribe(data=>{
      console.log(data);
      if(data.message == "success"){
        this.messageService.add({
          severity: "success",
          summary: "Updated",
          detail: data.details
        });
        this.editable = false;
        this.configData.disable();
      } else {
        this.messageService.add({
          severity: "error",
          summary: "error",
          detail: 'Some Error occured!'
        });
      }
      
    },error =>{
      this.messageService.add({
        severity: "error",
        summary: "error",
        detail: error.statusText
      });
    })
  }

  readConfigData(){
    this.sharedService.getSharepointconfig().subscribe((data:any)=>{
      this.sharepointData = data.config
      this.configData.patchValue({
        client_id : this.sharepointData.client_id,
        client_secret : this.sharepointData.client_secret,
        site_url : this.sharepointData.site_url,
        folder : this.sharepointData.folder,
        service_url : this.sharepointData.service_url,
      })
    })
  }

}
