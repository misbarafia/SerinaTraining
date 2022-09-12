import { SharepointListenerComponent } from './sharepoint-listener/sharepoint-listener.component';
import { ChangePasswordComponent } from './change-password/change-password.component';
import { UplaodListenerComponent } from './uplaod-listener/uplaod-listener.component';
import { ConfigurationComponent } from './configuration/configuration.component';

import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { SettingsPageComponent } from './settings-page/settings-page.component';
import { EntityRoutingComponent } from './entity-routing/entity-routing.component';

const routes: Routes = [
  { path:'',
    component:SettingsPageComponent,
    children:[
      {
        path:'configuration',
        component : ConfigurationComponent
      },
      {
        path:'mail-listener',
        component : UplaodListenerComponent
      },
      {
        path:'sharepoint-listener',
        component : SharepointListenerComponent
      },
      {
        path:'entity-routing',
        component: EntityRoutingComponent
      },
      {
        path:'change-password',
        component : ChangePasswordComponent
      },
      {
        path: '',
        redirectTo:'mail-listener',
        pathMatch:'full'
      }
    ]
  },
  {
    path: '',
    redirectTo:'mail-listener',
    pathMatch:'full'
  }


  
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class SettingsRoutingModule { }
