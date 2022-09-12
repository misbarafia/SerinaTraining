
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { importFilesModule } from './../importFiles.module';

import { SettingsRoutingModule } from './settings-routing.module';

import { SettingsComponent } from '../settings/settings.component';
import { OcrConfigComponent } from './ocr-config/ocr-config.component';
import { TechExceptionComponent } from './tech-exception/tech-exception.component';
import { ERPExceptionComponent } from './erpexception/erpexception.component';
import { GeneralLogicComponent } from './general-logic/general-logic.component';
import { ReportsComponent } from './reports/reports.component';
import { ModelExceptionComponent } from './model-exception/model-exception.component';
import { GeneralSettingsComponent } from './general-settings/general-settings.component';
import { FinanceApprovalSettingsComponent } from './general-settings/finance-approval-settings/finance-approval-settings.component';
import { NotificationComponent } from './notifications/components/notification/notification.component';
import { AddRecipientsComponent } from './notifications/components/add-recipients/add-recipients.component';


@NgModule({
  declarations: [
    SettingsComponent,
    OcrConfigComponent,
    ModelExceptionComponent,
    TechExceptionComponent,
    ERPExceptionComponent,
    GeneralLogicComponent,
    ReportsComponent,
    GeneralSettingsComponent,
    FinanceApprovalSettingsComponent,
    NotificationComponent,
    AddRecipientsComponent
  ],
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    importFilesModule,
    SettingsRoutingModule
  ]
})
export class SettingsModule { }
