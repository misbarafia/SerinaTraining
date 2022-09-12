import { BaseRoutingModule } from './base-routing.module';
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { BaseTypeComponent } from './base-type/base-type.component';
import { HomeComponent } from './home/home.component';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { importFilesModule } from './importFiles.module';
import { SettingsModule } from './settings/settings.module';
import { DatePipe } from '@angular/common';
import { PdfViewerModule } from 'ng2-pdf-viewer';
import { ConfirmationService, MessageService } from 'primeng/api';

import { InvoiceComponent } from './invoice/invoice.component';
import { NonPoComponent } from './non-po/non-po.component';
import { RolesComponent } from './roles/roles.component';
import { ProfileComponent } from './profile/profile.component';
import { ApproveComponent } from './approve/approve.component';
import { EditedComponent } from './edited/edited.component';
import { NotificationsComponent } from './notifications/notifications.component';
import { ViewInvoiceComponent } from './invoice/view-invoice/view-invoice.component';

import { CanDeactivateGuard } from './can-deactivate/can-deactivate.guard';
import { FilterPipe } from './settings/ocr-config/filter.pipe';
import { PoComponent } from './invoice/po/po.component';
import { GrnComponent } from './invoice/grn/grn.component';
import { PipComponent } from './invoice/pip/pip.component';
import { ArchivedComponent } from './invoice/archived/archived.component';
import { AllInvoicesComponent } from './invoice/all-invoices/all-invoices.component';
import { EditUserComponent } from './roles/edit-user/edit-user.component';
import { SpDetailsComponent } from './non-po/sp-details/sp-details.component';
import { InvoiceStatusComponent } from './invoice-status/invoice-status.component';
import { SummaryComponent } from './non-po/summary/summary.component';
import { ServiceInvoicesHistoryComponent } from './non-po/service-invoices-history/service-invoices-history.component';
import { BulkUploadServiceComponent } from './non-po/bulk-upload-service/bulk-upload-service.component';
import { ExceptionManagementComponent } from './exception-management/exception-management.component';
import { BatchProcessComponent } from './exception-management/batch-process/batch-process.component';
import { InvokeBatchComponent } from './exception-management/invoke-batch/invoke-batch.component';
import { ServiceInvoiceExceptionsComponent } from './exception-management/service-invoice-exceptions/service-invoice-exceptions.component';
import { ExceptionTableComponent } from './exception-management/exception-table/exception-table.component';
import { Comparision3WayComponent } from './exception-management/comparision3-way/comparision3-way.component';
import { ServiceDocStatusComponent } from './invoice/service-doc-status/service-doc-status.component';
import { CustomerSummaryComponent } from './customer-summary/customer-summary.component';
import { BusinessChartsComponent } from './home/business-charts/business-charts.component';
import { SystemChartsComponent } from './home/system-charts/system-charts.component';
import { VendorBasedChartsComponent } from './home/vendor-based-charts/vendor-based-charts.component';
import { ServiceBasedChartsComponent } from './home/service-based-charts/service-based-charts.component';

import { MqttModule, IMqttServiceOptions } from 'ngx-mqtt';
import { environment, environment1 } from 'src/environments/environment.prod';
import { ProcessReportsComponent } from './home/vendor-based-charts/process-reports/process-reports.component';
import { ExceptionReportsComponent } from './home/vendor-based-charts/exception-reports/exception-reports.component';
import { ProcessReportserviceComponent } from './home/service-based-charts/process-reportservice/process-reportservice.component';
import { DetailedReportsComponent } from './home/service-based-charts/detailed-reports/detailed-reports.component';
import { TableComponent } from './home/service-based-charts/table/table.component';
import { ChangePasswordComponent } from './change-password/change-password.component';
import { CreateGRNComponent } from './create-grn/create-grn.component';

@NgModule({
  declarations: [
    BaseTypeComponent,
    FilterPipe,
    HomeComponent,
    InvoiceComponent,
    NonPoComponent,
    RolesComponent,
    ProfileComponent,
    ApproveComponent,
    EditedComponent,
    NotificationsComponent,
    ViewInvoiceComponent,
    PoComponent,
    GrnComponent,
    PipComponent,
    ArchivedComponent,
    AllInvoicesComponent,
    EditUserComponent,
    SpDetailsComponent,
    InvoiceStatusComponent,
    SummaryComponent,
    ServiceInvoicesHistoryComponent,
    BulkUploadServiceComponent,
    ExceptionManagementComponent,
    BatchProcessComponent,
    InvokeBatchComponent,
    ServiceInvoiceExceptionsComponent,
    ExceptionTableComponent,
    Comparision3WayComponent,
    ServiceDocStatusComponent,
    CustomerSummaryComponent,
    BusinessChartsComponent,
    SystemChartsComponent,
    VendorBasedChartsComponent,
    ServiceBasedChartsComponent,
    ProcessReportsComponent,
    ExceptionReportsComponent,
    ProcessReportserviceComponent,
    DetailedReportsComponent,
    TableComponent,
    ChangePasswordComponent,
    CreateGRNComponent,
  ],
  imports: [
    CommonModule,
    BaseRoutingModule,
    FormsModule,
    ReactiveFormsModule,
    importFilesModule,
    SettingsModule,
    PdfViewerModule,
  ],
  exports: [
    InvoiceComponent,
    NotificationsComponent,
    ViewInvoiceComponent,
    PoComponent,
    GrnComponent,
    PipComponent,
    ArchivedComponent,
    AllInvoicesComponent,
    TableComponent,
    ChangePasswordComponent,
    BatchProcessComponent,
    InvoiceStatusComponent
  ],
  providers: [
    DatePipe,
    ConfirmationService,
    MessageService,
    CanDeactivateGuard,
  ],
})
export class BaseModule {}
