import { VendorItemListComponent } from './vendor-item-list/vendor-item-list.component';
import { VendorDetailsComponent } from './vendor-details/vendor-details.component';
import { VendorComponent } from './vendor.component';
import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

const routes: Routes = [
  { path: '', component: VendorComponent,
  children:[
    { path: 'vendorDetails', component:VendorDetailsComponent }
  ] 
},
  { path: 'item_master' , component :VendorItemListComponent}
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class VendorRoutingModule { }
