import { AuthenticationService } from 'src/app/services/auth/auth-service.service';
import { Component, OnInit } from '@angular/core';
import { MatDialogRef } from '@angular/material/dialog';
import { MessageService } from 'primeng/api';
import { SettingsService } from 'src/app/services/settings/settings.service';

@Component({
  selector: 'app-change-password',
  templateUrl: './change-password.component.html',
  styleUrls: ['./change-password.component.scss']
})
export class ChangePasswordComponent implements OnInit {
  passwordMatchBoolean: boolean;

  constructor(public dialogRef: MatDialogRef<ChangePasswordComponent>,
    private settingService :  SettingsService,
    private messageService : MessageService,
    private authService : AuthenticationService) { }

  ngOnInit(): void {
  }

  savePassword(value){
    const passwordObj = {
      "old_pass": value.oldPassword,
      "new_pass": value.newpassword
    }
    this.settingService.changePassword(JSON.stringify(passwordObj)).subscribe((data:any)=>{
      this.messageService.add({
        severity: 'success',
        summary : "Saved",
        detail : "Password changed successfully"
      })
    this.dialogRef.close();
    setTimeout(()=>{
      this.authService.logout();
    },1000)
    },err=>{
      let errorObj = {
        severity: 'error',
        summary : "error",
        detail : "Please enter correct password"
      }
      if(err.status == 400){
        this.messageService.add(errorObj)
      } else {
        errorObj.detail = "Server error"
        this.messageService.add(errorObj);
      }
    })
  }

  checkPattren(val){
    let passClass:any = document.getElementsByClassName('checkColor');
    const number = new RegExp('(?=.*[0-9])');
    const lowerCase = new RegExp('(?=.*[a-z])');
    const upperCase = new RegExp('(?=.*[A-Z])');
    const specialChar = new RegExp('(?=.*[!@#$%^&*()_+.,/{}])');
    const minLength = new RegExp('(?=.{8,})')

    if(passClass.length>0){
      if(specialChar.test(val)){
        passClass[3].style.color ="green"
      } else {
        passClass[3].style.color ="red"
      }
  
      if(upperCase.test(val)){
        passClass[2].style.color ="green"
      } else {
        passClass[2].style.color ="red"
      }
  
      if(lowerCase.test(val)){
        passClass[1].style.color ="green"
      } else {
        passClass[1].style.color ="red"
      }
      if(number.test(val)){
        passClass[0].style.color ="green"
      } else {
        passClass[0].style.color ="red"
      }
      if(minLength.test(val)){
        passClass[4].style.color ="green"
      } else {
        passClass[4].style.color ="red"
      }
    }
  }

  testPassword(newPass, confirmPass) {

    if (newPass == confirmPass) {
      this.passwordMatchBoolean = false;
    } else {
      this.passwordMatchBoolean = true;
    }
  }

}
