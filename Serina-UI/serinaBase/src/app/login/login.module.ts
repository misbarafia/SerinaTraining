import { LoginRoutingModule } from './login-routing.module';
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LoginPageComponent } from './login-page/login-page.component';
import {FormsModule,ReactiveFormsModule} from '@angular/forms';
import { NgOtpInputModule } from  'ng-otp-input';


@NgModule({
  declarations: [LoginPageComponent],
  imports: [
    CommonModule,
    FormsModule,
    LoginRoutingModule,
    ReactiveFormsModule,
    NgOtpInputModule
  ]
})
export class LoginModule { }
