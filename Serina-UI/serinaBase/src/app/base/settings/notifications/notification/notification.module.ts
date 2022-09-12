import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { NotificationRoutingModule } from './notification-routing.module';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { importFilesModule } from 'src/app/base/importFiles.module';


@NgModule({
  declarations: [],
  imports: [
    CommonModule,
    NotificationRoutingModule,
    importFilesModule,
    FormsModule,
    ReactiveFormsModule,
  ]
})
export class NotificationModule { }
