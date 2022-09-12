import { ProcessMetricsComponent } from './home/process-metrics/process-metrics.component';
import { NotificationsVendorComponent } from './notifications-vendor/notifications-vendor.component';
import { VendorContactComponent } from './vendor-contact/vendor-contact.component';
import { PaymentStatusVendorComponent } from './payment-status-vendor/payment-status-vendor.component';
import { UploadSectionComponent } from './upload-section/upload-section.component';
import { ActionCenterVendorComponent } from './action-center-vendor/action-center-vendor.component';
import { AllInvoicesComponent } from './../base/invoice/all-invoices/all-invoices.component';
import { DocumentStatusComponent } from './document-status/document-status.component';
import { ProfileVendorComponent } from './profile-vendor/profile-vendor.component';
import { RolesVendorComponent } from './roles-vendor/roles-vendor.component';
import { VendorBaseComponent } from './vendor-base/vendor-base.component';

import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import{ HomeComponent} from '../main-content/home/home.component';
import { PoComponent } from '../base/invoice/po/po.component';
import { GrnComponent } from '../base/invoice/grn/grn.component';
import { ArchivedComponent } from '../base/invoice/archived/archived.component';
import { ViewInvoiceComponent } from '../base/invoice/view-invoice/view-invoice.component';
import { CanDeactivateGuard } from '../base/can-deactivate/can-deactivate.guard';
import { ErrorPageComponent } from '../error-page/error-page.component';
import { DetailedReportsComponent } from './home/detailed-reports/detailed-reports.component';
import { Comparision3WayComponent } from '../base/exception-management/comparision3-way/comparision3-way.component';
import { BatchProcessComponent } from '../base/exception-management/batch-process/batch-process.component';
import { InvoiceStatusComponent } from '../base/invoice-status/invoice-status.component';

const routes: Routes = [
  {
    path: '',
    component: VendorBaseComponent, children:[
          {
            path: 'home',
            component: HomeComponent,
            children:[
              { path:'processMetrics',
                component: ProcessMetricsComponent,
              },
              { path:'detailedReports',component: DetailedReportsComponent },
              { path: '' , redirectTo:'processMetrics', pathMatch:'full'}
            ]
          },
          {
            path: 'uploadInvoices',
            component: UploadSectionComponent,
          },
          {
            path: 'invoice',
            component: DocumentStatusComponent,
            children:[
              { path:'allInvoices', component:AllInvoicesComponent },
              { path:'PO', component:PoComponent },
              { path: 'GRN', component:GrnComponent },
              { path: 'archived' , component:ArchivedComponent },
              { path: 'rejected' , component:ArchivedComponent },
              { path: 'GRNExceptions' , component:ArchivedComponent },
              { path: '' , redirectTo:'allInvoices', pathMatch:'full'}
            ]
          },
          {
            path: 'invoice/InvoiceDetails/vendorUpload/:id',
            component: ViewInvoiceComponent,
          },
          {
            path: 'invoice/InvoiceDetails/:id',
            component: ViewInvoiceComponent,
          },
          {
            path: 'invoice/PODetails/:id',
            component: ViewInvoiceComponent,
          },
          {
            path: 'invoice/GRNDetails/:id',
            component: ViewInvoiceComponent,
          },
          {
            path: 'invoice/InvoiceStatus/:id',
            component: InvoiceStatusComponent,
          },
          {
            path: 'action-center',
            component: ActionCenterVendorComponent,
          },
          {
            path: 'action-center/InvoiceDetails/:id',
            component: ViewInvoiceComponent,
          },
          {
            path: 'payment-details-vendor',
            component: PaymentStatusVendorComponent,
          },
          {
            path: 'ExceptionManagement',
            component: BatchProcessComponent,
          },
          {
            path: 'ExceptionManagement/batchProcess',
            component: BatchProcessComponent,
          },
          {
            path: 'ExceptionManagement/batchProcess/comparision-docs/:id',
            component: Comparision3WayComponent,canDeactivate: [CanDeactivateGuard]
          },
          
          {
            path: 'ExceptionManagement/InvoiceDetails/:id',
            component: ViewInvoiceComponent,
          },
          {
            path: 'vendorUsers',
            component: RolesVendorComponent,
          },
          {
            path: 'vendorContacts',
            component: VendorContactComponent,
          },
          {
            path: 'profile',
            component: ProfileVendorComponent,
          },
          {
            path: 'notifications',
            component: NotificationsVendorComponent,
          },

          {
            path: '', redirectTo: 'uploadInvoices', pathMatch: 'full'
          },
          {
            path: '404',
            component: ErrorPageComponent
          },
          {
            path: '**', 
            redirectTo: '/404'
          }
    ]
  },
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class MainContentRoutingModule { }
