
import { TechExceptionComponent } from './tech-exception/tech-exception.component';
import { ReportsComponent } from './reports/reports.component';
import { OcrConfigComponent } from './ocr-config/ocr-config.component';
import { ModelExceptionComponent } from './model-exception/model-exception.component';
import { GeneralLogicComponent } from './general-logic/general-logic.component';
import { ERPExceptionComponent } from './erpexception/erpexception.component';
import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { SettingsComponent } from './settings.component';


const routes: Routes = [
  {
    path: '',
    component: SettingsComponent, children: [
      {
        path: 'erpexception',
        component: ERPExceptionComponent
      },
      {
        path: 'generalLogic',
        component: GeneralLogicComponent
      },
      {
        path: 'modelException',
        component: ModelExceptionComponent
      },
      {
        path: 'ocrConfig',
        component: OcrConfigComponent
      },
      {
        path: 'reportsException',
        component: ReportsComponent
      },
      {
        path: 'techException',
        component: TechExceptionComponent
      },
      {
        path: 'generalSettings',
        loadChildren:()=> import('./general-settings/general-settings.module').then(m=>m.GeneralSettingsModule)
      },
      {
        path: 'notificationSettings',
        loadChildren:()=> import('./notifications/notification/notification.module').then(m=>m.NotificationModule)
      },
      {
        path: '', redirectTo: 'generalSettings', pathMatch: 'full'
      }
    ]
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class SettingsRoutingModule { }
