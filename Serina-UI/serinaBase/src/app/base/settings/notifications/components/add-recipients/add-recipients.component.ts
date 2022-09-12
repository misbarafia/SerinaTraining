import { AlertService } from './../../../../../services/alert/alert.service';
import { MessageService } from 'primeng/api';
import { SettingsService } from 'src/app/services/settings/settings.service';
import { Subscription } from 'rxjs';
import { DataService } from 'src/app/services/dataStore/data.service';
import { Router, ActivatedRoute } from '@angular/router';
import { FormGroup, FormBuilder } from '@angular/forms';
import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-add-recipients',
  templateUrl: './add-recipients.component.html',
  styleUrls: ['./add-recipients.component.scss'],
})
export class AddRecipientsComponent implements OnInit {
  noticationSettingsData: FormGroup;
  recipitentsList = [];
  subscriptionEntity: Subscription;
  entity: any;
  nty_id: any;
  routeIdCapture: Subscription;
  selectedEntityId: any;
  headerText: string;
  isDefaultRecepients: boolean;
  cc_addr: any;
  to_addr = [];

  constructor(
    private fb: FormBuilder,
    private router: Router,
    private dataService: DataService,
    private settingsService: SettingsService,
    private activatedRoute: ActivatedRoute,
    private messageService: MessageService,
    private alertService: AlertService
  ) {}

  ngOnInit(): void {
    this.readEntityData();
    this.inIt();
  }
  inIt() {
    this.routeIdCapture = this.activatedRoute.params.subscribe((data) => {
      this.nty_id = data.id;
      if (this.nty_id == 1) {
        this.headerText = 'System Notifications';
      } else if (this.nty_id == 2) {
        this.headerText = 'OCR Notifications';
      } else if (this.nty_id == 3) {
        this.headerText = 'ERP Notifications';
      } else if (this.nty_id == 4) {
        this.headerText = 'Batch Process Notifications';
      } else if (this.nty_id == 5) {
        this.headerText = 'Role/User Management Notifications';
      } else if (this.nty_id == 6) {
        this.headerText = 'Exceptions Notifications';
      } else if (this.nty_id == 7) {
        this.headerText = 'Settings Notifications';
      }

      if (this.selectedEntityId) {
        this.readRecipientsData();
        this.getRecipientsEmails();
      } else {
        this.backToSettings();
      }
    });
  }

  saveSettings(value) {
    value.bcc_addr = [];
    console.log(value);
    if(this.isDefaultRecepients == true){
      if(value.to_addr.length >= 1){
        this.saveRecipients(value);
      } else {
        this.alertService.errorObject.detail = 'Please add atleast one email';
        this.messageService.add(this.alertService.errorObject);
      }
    } else {
      this.saveRecipients(value);
    }
  }

  saveRecipients(value){
    this.settingsService
    .saveNotificationRecipientsData(this.nty_id, this.selectedEntityId, value)
    .subscribe(
      (data) => {
        console.log(data);
        this.alertService.addObject.detail = 'Settings saved.';
        this.messageService.add(this.alertService.addObject);
      },
      (err) => {
        this.alertService.errorObject.detail = 'Server error.';
        this.messageService.add(this.alertService.errorObject);
      }
    );
  }
  selectedRecipients(event) {
    let emails = [];
    event.value.forEach((element) => {
      emails.push(element.email);
    });
    this.to_addr = this.to_addr.concat(emails);
    this.to_addr = [...new Set(this.to_addr)];
  }
  backToSettings() {
    this.router.navigate(['/customer/settings/notificationSettings']);
  }

  readEntityData() {
    this.subscriptionEntity = this.dataService.getEntity().subscribe(
      (res) => {
        this.entity = res;
        if (this.entity.length > 0) {
          this.selectedEntityId = this.entity[0].idEntity;
        }
      },
      (err) => {
        console.log('error');
      }
    );
  }

  onSelectEntity(en_id) {
    this.selectedEntityId = en_id;
    this.readRecipientsData();
    this.getRecipientsEmails();
  }

  getRecipientsEmails() {
    this.settingsService
      .readRecipients(this.selectedEntityId)
      .subscribe((data: any) => {
        this.recipitentsList = data.individual_users;
      });
  }
  readRecipientsData() {
    this.settingsService
      .readNotificationRecipientsData(this.nty_id, this.selectedEntityId)
      .subscribe((data: any) => {
        console.log(data);
        this.isDefaultRecepients = data.result[0].isDefaultRecepients;
        this.isDefaultRecepients = data.result[0].isDefaultRecepients;
        this.to_addr = data.result[0].notificationrecipient.to_addr;
        this.cc_addr = data.result[0].notificationrecipient.cc_addr;
      });
  }
  ngOnDestroy() {
    this.subscriptionEntity.unsubscribe();
    this.routeIdCapture.unsubscribe();
  }
}
