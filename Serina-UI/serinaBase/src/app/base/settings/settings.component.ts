import { PermissionService } from './../../services/permission.service';
import { Router, ActivatedRoute } from '@angular/router';
import { SharedService } from 'src/app/services/shared.service';
import { Component, OnInit } from '@angular/core';
import {
  ConfirmationService,
  MessageService,
  PrimeNGConfig
} from "primeng/api";

@Component({
  selector: 'app-settings',
  templateUrl: './settings.component.html',
  styleUrls: ['./settings.component.scss']
})
export class SettingsComponent implements OnInit {
  userDetails = '_______';
  emailBodyDummy ='There is a mismatch details In the Invoice number_____, that is in the vendor name some mistake is there instead of ____there is _____. So, please check that.';
  emailBody ='There is a mismatch details In the Invoice number_____, that is in the vendor name some mistake is there instead of ____there is _____. So, please check that.';
  smsBody ='This is the format for the email body if you want you can change the data.'
  emailSubject: any;
  ntBody: any;
  activeMenuSetting:string;

  actions =[
    'Missing Key Labels data in OCR Extaction in Invoice',
    'Missing Label data in OCR Extraction ',
    'Low OCR confidance in Key Labels',
    'Low OCR Confidance in Other Labels',
    'Too many OCR Errors In Invoice',
    'Too many OCR errors from a Vendor/ Service Provider'
  ]
  isAdmin: boolean;

  constructor(private sharedService: SharedService,
              private router: Router,
              private route:ActivatedRoute,
              private PermissionService : PermissionService,
              private confirmationService: ConfirmationService,
              private messageService: MessageService,) { }

  ngOnInit(): void {
   if(this.PermissionService.settingsPageAccess == true){
    this.activeMenuSetting = this.sharedService.activeMenuSetting ;
    this.isAdmin = this.PermissionService.addUsersBoolean;
  } else{
    alert("Sorry!, you do not have access");
    this.router.navigate(['customer/invoice/allInvoices'])
  }
  }
  menuChange(value){
    this.sharedService.activeMenuSetting  = value;
    this.activeMenuSetting = this.sharedService.activeMenuSetting
  }

  getEmailTemplate(){
    this.sharedService.displayTemplate().subscribe((data:any)=>{
      console.log(data);
      this.emailSubject = data[0].subject;
      this.emailBody = data[0].template_body;
    })
  }
  updateTemplate(){
    let updateData={
      "template_body": this.emailBody,
      "subject":  this.emailSubject 
    }
    console.log(updateData)
    this.sharedService.updateTemplate(JSON.stringify(updateData)).subscribe((data:any)=>{
      console.log(data)
      if(data.result=='Updated'){
        this.messageService.add({
          severity: "info",
          summary: "Updated",
          detail: "Updated Successfully"
        });
      } else {
        this.messageService.add({
          severity: "error",
          summary: "error",
          detail: "Something went wrong"
        });
      }
    })
  }
  displayNTtemplate(){
    this.sharedService.displayNTtemplate().subscribe((data)=>{
      console.log(data);
      this.ntBody = data[2];
    })
  }
  updateNTtemplate(e){
    console.log(e);
    this.sharedService.NTtempalteId = e.idPullNotificationTemplate;
    let updateData={
      "templateMessage": e.templateMessage,
      "notificationTypeID": e.notificationTypeID,
      "notificationPriorityID": e.notificationPriorityID
    }
    this.sharedService.updateNTtemplate(JSON.stringify(updateData)).subscribe((data)=>{
      console.log(data);
      if(data[0]=='updated'){
        this.messageService.add({
          severity: "info",
          summary: "Updated",
          detail: "Updated Successfully"
        });
      } else {
        this.messageService.add({
          severity: "error",
          summary: "error",
          detail: "Something went wrong"
        });
      }
    })
  }

}
