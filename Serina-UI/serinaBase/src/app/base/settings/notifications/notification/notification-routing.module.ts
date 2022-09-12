import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { AddRecipientsComponent } from '../components/add-recipients/add-recipients.component';

import { NotificationComponent } from '../components/notification/notification.component';

const routes: Routes = [
  { 
    path:'', 
    component : NotificationComponent 
  },
  { 
    path:'systemNotifications/:id', 
    component : AddRecipientsComponent 
  },
  { 
    path:'OCRNotifications/:id', 
    component : AddRecipientsComponent 
  },
  { 
    path:'ERPNotifications/:id', 
    component : AddRecipientsComponent 
  },
  { 
    path:'batchNotifications/:id', 
    component : AddRecipientsComponent 
  },
  { 
    path:'userMangementNotifications/:id', 
    component : AddRecipientsComponent 
  },
  { 
    path:'exceptionsNotifications/:id', 
    component : AddRecipientsComponent 
  },
  { 
    path:'settingsNotifications/:id', 
    component : AddRecipientsComponent 
  },
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class NotificationRoutingModule { }
