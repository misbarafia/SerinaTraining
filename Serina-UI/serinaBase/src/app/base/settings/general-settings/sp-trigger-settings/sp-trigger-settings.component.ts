import { Location } from '@angular/common';
import { MessageService } from 'primeng/api';
import { AlertService } from './../../../../services/alert/alert.service';
import { SettingsService } from './../../../../services/settings/settings.service';
import { Router } from '@angular/router';
import { Component, OnInit, ViewChild } from '@angular/core';
import { FormControl } from '@angular/forms';
import { NgxSpinnerService } from 'ngx-spinner';
import { CronGenComponent, CronOptions } from 'ngx-cron-editor';

@Component({
  selector: 'app-sp-trigger-settings',
  templateUrl: './sp-trigger-settings.component.html',
  styleUrls: ['./sp-trigger-settings.component.scss']
})
export class SpTriggerSettingsComponent implements OnInit {
  public cronExpression = ' 0 0 1/1 * *';
  public isCronDisabled = false;
  public cronOptions: CronOptions = {
    formInputClass: 'form-control cron-editor-input',
    formSelectClass: 'form-control cron-editor-select',
    formRadioClass: 'cron-editor-radio',
    formCheckboxClass: 'cron-editor-checkbox',

    defaultTime: '00:00:00',

    hideMinutesTab: true,
    hideHourlyTab: false,
    hideDailyTab: false,
    hideWeeklyTab: false,
    hideMonthlyTab: true,
    hideYearlyTab: true,
    hideAdvancedTab: true,
    hideSpecificWeekDayTab: true,
    hideSpecificMonthWeekTab: false,

    use24HourTime: true,
    hideSeconds: false,

    cronFlavor: 'standard'
  };

  @ViewChild('cronEditorDemo')
  cronEditorDemo: CronGenComponent;

  cronForm: FormControl;
  scheduleTrigger = [
    { id: 1, type : "Hourly" },
    { id: 1, type : "Daily" },
    { id: 1, type : "Weekly" }
  ]
  scheduleTriggerHours = [ 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23];
  scheduleTriggerMints = [ 0,5,10,15,20,25,30,35,40,45,50,55];
  selectedTriggerType: any;
  scheduleBoolean: boolean = false;
  triggerBoolean: boolean = false;
  idAccountSchedule: any;
  currentTriggerExpression: any;
  fomratExpression = "{minute} {hour} {day} {month} {day-of-week}"
  heading: string;

  constructor(private router : Router,
    private settingService : SettingsService,
    private SpinnerService: NgxSpinnerService,
    private alertService : AlertService,
    private location : Location,
    private MessageService : MessageService) { }
  ngOnInit(): void {
    this.cronForm = new FormControl(this.cronExpression);
    
    if(this.router.url.includes('ServiceInvoicesBatchTriggerSettings')){
      this.heading = "Service";
      this.getSettingsSP();
    } else {
      this.heading = "Vendor";
    }
  }

  cronFlavorChange() {
    this.cronEditorDemo.options = this.cronOptions;
  }
  backToSettings() {
    this.router.navigate(['/customer/settings/generalSettings'])
  }

  scheduleToggle(val) {
    this.scheduleBoolean = val.target.checked;
  }

  triggerToggle(val) {
    this.triggerBoolean = val.target.checked;
  }
  getSettingsSP() {
    this.settingService.readServiceTriggerSettings().subscribe((data:any)=>{
      this.idAccountSchedule = data.result.idAccountSchedule;
      this.scheduleBoolean =  data.result.isScheduleActive;
      this.triggerBoolean =  data.result.isTriggerActive;
      this.currentTriggerExpression = data.result.schedule;
    })
  }
  updateTriggerSettings() {
    this.SpinnerService.show();
    const updateTriggerData = {
      "idAccountSchedule":  this.idAccountSchedule,
      "schedule": this.cronForm.value,
      "isScheduleActive": this.scheduleBoolean,
      "isTriggerActive": this.triggerBoolean
    }
    console.log(updateTriggerData)
    this.settingService.serviceBatchTriggerUpdate(JSON.stringify(updateTriggerData)).subscribe((data:any)=>{
      console.log(data);
      this.SpinnerService.hide();
      this.alertService.updateObject.detail = "Settings updated";
      this.MessageService.add(this.alertService.updateObject);
      this.getSettingsSP();
    }, err=>{
      this.alertService.errorObject.detail = err.statusText;
      this.MessageService.add(this.alertService.errorObject);
      this.SpinnerService.hide();
    });
  }

  selctedtype(val) {
    console.log(val);
    this.selectedTriggerType = val;
  }
  selctedtypeHours(val) {
    console.log(val);
  }
  selctedtypeMins(val) {
    console.log(val);
  }

  onCancel() {
    this.location.back();
  }

}

