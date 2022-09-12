import { BaseModule } from './../base/base.module';
import { importFilesModule } from './../base/importFiles.module';
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { MainContentRoutingModule } from './main-content-routing.module';

import { HomeComponent } from './home/home.component';
import { VendorBaseComponent } from './vendor-base/vendor-base.component';
import { RolesVendorComponent } from './roles-vendor/roles-vendor.component';
import { ProfileVendorComponent } from './profile-vendor/profile-vendor.component';
import { DocumentStatusComponent } from './document-status/document-status.component';
import { UploadSectionComponent } from './upload-section/upload-section.component';
import { PaymentStatusVendorComponent } from './payment-status-vendor/payment-status-vendor.component';
import { ActionCenterVendorComponent } from './action-center-vendor/action-center-vendor.component';
import { VendorContactComponent } from './vendor-contact/vendor-contact.component';
import { NotificationsVendorComponent } from './notifications-vendor/notifications-vendor.component';
import { ProcessMetricsComponent } from './home/process-metrics/process-metrics.component';
import { DetailedReportsComponent } from './home/detailed-reports/detailed-reports.component';


@NgModule({
  declarations: [HomeComponent, VendorBaseComponent, RolesVendorComponent, ProfileVendorComponent, DocumentStatusComponent, UploadSectionComponent, PaymentStatusVendorComponent, ActionCenterVendorComponent, VendorContactComponent, NotificationsVendorComponent, ProcessMetricsComponent, DetailedReportsComponent],
  imports: [
    CommonModule,
    MainContentRoutingModule,
    importFilesModule,
    BaseModule
  ],
  exports:[UploadSectionComponent]
})
export class MainContentModule { }
