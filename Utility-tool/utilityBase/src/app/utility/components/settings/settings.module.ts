import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { ToastModule } from 'primeng/toast';
import {ChipsModule} from 'primeng/chips';

import { SettingsRoutingModule } from './settings-routing.module';
import { SettingsPageComponent } from './settings-page/settings-page.component';
import { ConfigurationComponent } from './configuration/configuration.component';
import { ChangePasswordComponent } from './change-password/change-password.component';
import { UplaodListenerComponent } from './uplaod-listener/uplaod-listener.component';
import { SharepointListenerComponent } from './sharepoint-listener/sharepoint-listener.component';
import { EntityRoutingComponent } from './entity-routing/entity-routing.component';


@NgModule({
  declarations: [SettingsPageComponent, ConfigurationComponent, ChangePasswordComponent, UplaodListenerComponent, SharepointListenerComponent, EntityRoutingComponent],
  imports: [
    CommonModule,
    SettingsRoutingModule,
    FormsModule,
    ReactiveFormsModule,
    ToastModule,
    ChipsModule
  ]
})
export class SettingsModule { }
