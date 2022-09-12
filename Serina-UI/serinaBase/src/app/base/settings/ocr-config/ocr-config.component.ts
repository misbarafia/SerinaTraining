import { Component, OnInit, ViewChild } from '@angular/core';
import { NgForm } from '@angular/forms';
import { ConfirmationService, MessageService } from 'primeng/api';
import { SharedService } from 'src/app/services/shared.service';

@Component({
  selector: 'app-ocr-config',
  templateUrl: './ocr-config.component.html',
  styleUrls: ['./ocr-config.component.scss']
})
export class OcrConfigComponent implements OnInit {
  userDetails = '_______';
  emailBodyDummy ='There is a mismatch details In the Invoice number_____, that is in the vendor name some mistake is there instead of ____there is _____. So, please check that.';
  emailBody ='There is a mismatch details In the Invoice number_____, that is in the vendor name some mistake is there instead of ____there is _____. So, please check that.';
  smsBody ='This is the format for the email body if you want you can change the data.'
  emailSubject: any;
  ntBody: any;
  SelectedTime:string;
  SelectDay:string;
  SelectedPriority:string;
  cThreshold:any = '70%';
  TolerancePerInv  ='20';
  TolerancePervendor = '10'
  InviteRole:string;
  visibleSidebar2;
  searchTag;
  filterString='';
  currentlyOpenedItemIndex = -1;
  viewTemplate:boolean;
  actions =[
    'Missing Key Labels data in OCR Extaction in Invoice',
    'Missing Label data in OCR Extraction ',
    'Low OCR confidance in Key Labels',
    'Low OCR Confidance in Other Labels',
    'Too many OCR Errors In Invoice',
    'Too many OCR errors from a Vendor/ Service Provider'
  ]
  Rhythm = ['Immediately','Daily summary ','Weekly summary ','Monthly summary '];
  time = ['9 AM-10 AM','10 AM-11 AM','11 AM-12 AM','12 AM-1 PM','1 PM-2 PM'];
  day = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];
  priority = ['Low','Medium','High','critical'];
  config=[
    {KeyLabelsList: ['invoice Number','Invoice Date','Amount','Due Date']},
    {ConfidanceThreshold:['60%','70%','80%']},
    {ToleranceLevelperInvoice:['10','20','25']},
    {ToleranceLevelperVendor:['5','10','15']}
  ]
  Tags=['invoice Number','Invoice Date','Amount','Due Date'];
  
  @ViewChild('form')
  form: NgForm;
  filtered: any;
  selectedRecipients:any;
  recipitentsList = [
    { id: 1, mail:'John@gmail.com'},
    { id: 1, mail:'RJohn@gmail.com'},
    { id: 1, mail:'JohnDoe@gmail.com'},
    { id: 1, mail:'John1232@gmail.com'},
  ]

  constructor(private sharedService: SharedService,
    private confirmationService: ConfirmationService,
    private messageService: MessageService,) { }

  
   
    submit(){
     console.log(this.form.submitted);
    }

  ngOnInit(): void {
    this.onFilterChange();
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

  setOpened(itemIndex) {
    this.currentlyOpenedItemIndex = itemIndex;
  }
  
  setClosed(itemIndex) {
    if(this.currentlyOpenedItemIndex === itemIndex) {
      this.currentlyOpenedItemIndex = -1;
    }
  }
  onFilterChange() {
    console.log("value")
    this.filtered = this.Tags.filter((invoice) => this.isMatch(invoice));
  }

  isMatch(item) {
    if (item instanceof Object) {
      return Object.keys(item).some((k) => this.isMatch(item[k]));
    } else {
      return item.toString().toLowerCase().indexOf(this.filterString) > -1
    }
  }

  selectedPO(event) {
    console.log(event)
  }

}
