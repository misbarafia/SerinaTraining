import { SpTriggerSettingsComponent } from './sp-trigger-settings/sp-trigger-settings.component';
import { PasswordSettingsComponent } from './password-settings/password-settings.component';
import { FinanceApprovalSettingsComponent } from './finance-approval-settings/finance-approval-settings.component';
import { GeneralSettingsComponent } from './general-settings.component';
import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

const routes: Routes = [
  { 
    path:'', 
    component : GeneralSettingsComponent 
  },
  { 
    path: 'financeSettings',
    component : FinanceApprovalSettingsComponent
  },
  { 
    path: 'changePassword',
    component : PasswordSettingsComponent
  },
  {
    path: 'ServiceInvoicesBatchTriggerSettings',
    component: SpTriggerSettingsComponent
  },
  {
    path: 'VendorInvoicesBatchTriggerSettings',
    component: SpTriggerSettingsComponent
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class GeneralSettingsRoutingModule { }
