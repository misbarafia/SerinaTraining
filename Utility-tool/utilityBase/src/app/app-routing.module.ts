import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { AuthGuard } from './services/auth/auth-guard.service';

const routes: Routes = [
  {
    path:'login',
    loadChildren: () =>import('./login/login.module').then(m=>m.LoginModule)
  },
  {
    path:'IT_Utility',
    loadChildren: () =>import('./utility/utility.module').then(m=>m.UtilityModule),canActivate:[AuthGuard]
  },
  { path: '', redirectTo: '/login', pathMatch: 'full' },
  {
    path: '**', 
    redirectTo: '/login'
  }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
