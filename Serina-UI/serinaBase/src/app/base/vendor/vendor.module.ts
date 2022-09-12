import { importFilesModule } from './../importFiles.module';
import { VendorComponent } from './vendor.component';
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { VendorRoutingModule } from './vendor-routing.module';
import { VendorInvoiceComponent } from './vendor-invoice/vendor-invoice.component';
import { VendorSitesComponent } from './vendor-sites/vendor-sites.component';
import { VendorDetailsComponent } from './vendor-details/vendor-details.component';
import { VendorItemListComponent } from './vendor-item-list/vendor-item-list.component';
import { BaseModule } from '../base.module';


@NgModule({
  declarations: [VendorComponent,VendorInvoiceComponent, VendorSitesComponent, VendorDetailsComponent, VendorItemListComponent],
  imports: [
    CommonModule,
    VendorRoutingModule,
    importFilesModule,
    BaseModule
  ]
})
export class VendorModule { }
