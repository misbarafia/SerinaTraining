import { MessageService } from 'primeng/api';
import { RegistrationService } from './../../services/registration/registration.service';
import { Router, ActivatedRoute } from '@angular/router';
import { FormGroup, FormBuilder, Validators } from '@angular/forms';
import { Component, OnInit } from '@angular/core';
import jwt_decode from "jwt-decode";
import { PasswordStrengthValidator } from '../password-validators';
import { DatePipe } from '@angular/common';

@Component({
  selector: 'app-registration',
  templateUrl: './registration.component.html',
  styleUrls: ['./registration.component.scss']
})
export class RegistrationComponent implements OnInit {
  registrationForm:FormGroup;
  predefinedFormData:any;
  fieldTextType: boolean;
  linkActiveBoolean:boolean = true;
  routeIdCapture: any;
  token: any;
  userData: any;
  errorDivBoolean: boolean;
  emailId: string;

  constructor(private fb:FormBuilder,
    private activatedRoute: ActivatedRoute,
    private datePipe: DatePipe,
    private router:Router,
    private messageService : MessageService,
    private registrationService : RegistrationService) {

   }

  ngOnInit(): void {
    this.routeIdCapture = this.activatedRoute.params.subscribe(params => {
      this.token= params['id'];
        }) ;
    this.decode();
  }
  toggleFieldTextType() {
    this.fieldTextType = !this.fieldTextType;
  }
  savePasswordforNewuser(){
    console.log('data');
    const passwordData = {
      "activation_code": this.token,
      "password": this.registrationForm.value.password
    };

    this.registrationService.savenewUserPassword(JSON.stringify(passwordData)).subscribe((data:any)=>{
      console.log(data);
      if(data.result == "Account Activated"){
        this.messageService.add({
          severity: "success",
          summary: "Password Saved",
          detail: "Account Activated Successfully"
        });
        this.router.navigate(["/"]);
      }
    },error=>{
      console.log(error)
      this.messageService.add({
        severity: "error",
        summary: "error",
        detail: "User already activated"
      });
    })
  }
  decode(){
    const decoded = jwt_decode( this.token);

    this.userData = decoded;
    console.log(this.userData)
    this.registrationForm = this.fb.group({
      userName: [{value:this.userData.username , disabled:true}],
      firstName: [{value:this.userData.firstName , disabled:true}],
      lastName: [{value:this.userData.lastName , disabled:true}],
      password:['', Validators.compose([
        Validators.required, Validators.minLength(8), PasswordStrengthValidator])],
      reEnterPassword:['', Validators.required]
    })

    const date = new Date();
    const createDate = this.datePipe.transform(date,'yyyy-MM-dd');
    console.log(createDate)
    if(this.userData.exp_date <= createDate){
      this.linkActiveBoolean = false;
    }
  }
  confirmPassword(value){
    if(this.registrationForm.value.password != value){
      this.errorDivBoolean = true;
    } else{
      this.errorDivBoolean = false;
    }
  }
  resendActivationLink(){
    this.registrationService.resendVerificationLink(this.token,this.emailId).subscribe((data:any)=>{
      this.messageService.add({
        severity: "success",
        summary: "Link Sent",
        detail: "Activation link sent to your Email, please check"
      });
    }, error=>{
      if(error.status == 400){
        this.messageService.add({
          severity: "error",
          summary: "error",
          detail: "Please enter a valid Email which is present in Serina"
        });
      } else {
        this.messageService.add({
          severity: "error",
          summary: "error",
          detail: "Please contact admin"
        });
      }
    });
  }


}
