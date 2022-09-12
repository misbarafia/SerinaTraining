import { Subscription } from 'rxjs';
import { MessageService } from 'primeng/api';
import { AlertService } from './../../../../services/alert/alert.service';
import { SettingsService } from './../../../../services/settings/settings.service';
import { Router } from '@angular/router';
import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-finance-approval-settings',
  templateUrl: './finance-approval-settings.component.html',
  styleUrls: ['./finance-approval-settings.component.scss']
})
export class FinanceApprovalSettingsComponent implements OnInit {
  financeApproveBoolean:boolean;
  readSettingsData : any;

  constructor( private router : Router,
    private settingsService : SettingsService,
    private MessageService : MessageService,
    private alertService : AlertService) { 
    }

  ngOnInit(): void {
    this.readfinanceSettingsData()
  }
  readfinanceSettingsData() {
    this.settingsService.readGeneralSettings().subscribe((data:any)=>{
      console.log(data);
      this.readSettingsData = data.data ;
      this.financeApproveBoolean = this.readSettingsData.isRoleBased;
    })
  }
  backToSettings() {
    this.router.navigate(['/customer/settings/generalSettings'])
  }
  changeFinanceApproveSettings(e){
    console.log(this.financeApproveBoolean)
    this.settingsService.financeApprovalSetting(e.target.checked).subscribe((data:any)=>{
      console.log(data);
      this.MessageService.add(this.alertService.updateObject)
    },error=>{
      console.log(error)
      this.alertService.errorObject.detail = error.statusText;
      this.MessageService.add(this.alertService.errorObject)
    })
    // if(confirm("Are you sure you want to change setting")){
    //   this.financeApproveBoolean = e.target.checked;
    //   console.log(this.financeApproveBoolean)
    //   this.settingsService.financeApprovalSetting(e.target.checked).subscribe((data:any)=>{
    //     console.log(data);
    //   })
    // } else if (this.financeApproveBoolean == false){
    //   console.log(this.financeApproveBoolean)
    //   this.financeApproveBoolean = true;
    //   console.log('f false');
    // } else if (this.financeApproveBoolean == true){
    //   this.financeApproveBoolean = false;
    //   console.log('f trur');
    // }
    
  }
}
