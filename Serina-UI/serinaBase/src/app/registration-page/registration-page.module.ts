import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { RegistrationPageRoutingModule } from './registration-page-routing.module';
import { importFilesModule } from '../base/importFiles.module';
import {PasswordModule} from 'primeng/password';
import { RegistrationComponent } from './registration/registration.component';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';


@NgModule({
  declarations: [RegistrationComponent],
  imports: [
    CommonModule,
    RegistrationPageRoutingModule,
    importFilesModule,
    FormsModule,
    ReactiveFormsModule,
    PasswordModule
  ]
})
export class RegistrationPageModule { }
