import { ErrorPageComponent } from './error-page/error-page.component';
import { LoginPageComponent } from './login/login-page/login-page.component';
import { NgModule, Component } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { AuthGuard } from './services/auth/auth-guard.service';
import { VendorPortalAuthGaurd } from './services/auth/vendor-portal-auth-gaurd.service';

const routes: Routes = [
  {
    path: 'login',
    loadChildren: () => import('./login/login.module').then(m => m.LoginModule)
  },
  {
    path: 'customer',
    loadChildren: () => import('./base/base.module').then(m => m.BaseModule),canActivate: [AuthGuard]
  },
  {
    path: 'vendorPortal',
    loadChildren: () => import('./main-content/main-content.module').then(m => m.MainContentModule),canActivate: [VendorPortalAuthGaurd]
  },
  {
    path: 'registration-page',
    loadChildren: () => import('./registration-page/registration-page.module').then(m => m.RegistrationPageModule)
  },
  { path: '', redirectTo: '/login', pathMatch: 'full' },
  // {
  //   path: '404',
  //   component: ErrorPageComponent
  // },
  {
    path: '**', 
    redirectTo: '/login'
  }
];

@NgModule({
  imports: [RouterModule.forRoot(routes,{ enableTracing: false })],
  exports: [RouterModule]
})
export class AppRoutingModule { }
