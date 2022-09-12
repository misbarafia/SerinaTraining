import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { CronEditorModule } from 'ngx-cron-editor';

import { GeneralSettingsRoutingModule } from './general-settings-routing.module';
import { importFilesModule } from '../../importFiles.module';
import { PasswordSettingsComponent } from './password-settings/password-settings.component';
import { SpTriggerSettingsComponent } from './sp-trigger-settings/sp-trigger-settings.component';


@NgModule({
  declarations: [PasswordSettingsComponent, SpTriggerSettingsComponent],
  imports: [
    CommonModule,
    GeneralSettingsRoutingModule,
    importFilesModule,
    FormsModule,
    ReactiveFormsModule,
    CronEditorModule
  ]
})
export class GeneralSettingsModule { }
