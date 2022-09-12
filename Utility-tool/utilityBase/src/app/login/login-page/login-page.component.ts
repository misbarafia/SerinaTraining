import { Component, OnInit, ViewChild } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { AuthenticationService } from 'src/app/services/auth/auth.service';
import { SharedService } from 'src/app/services/shared/shared.service';



@Component({
  selector: 'app-login-page',
  templateUrl: './login-page.component.html',
  styleUrls: ['./login-page.component.scss']
})
export class LoginPageComponent implements OnInit {
  loginForm: FormGroup;
  loading = false;
  emailId: string;
  password: any;
  newPassword: any;
  sendMail: string;
  confirmPassword: any;
  passwordMatchBoolean: boolean;
  fieldTextType: boolean;
  fieldTextTypeReset1: boolean;
  fieldTextTypeReset: boolean;
  loginboolean: boolean = true;
  forgotboolean: boolean = false;
  resetPassword: boolean = false;
  successPassword: boolean = false;
  loginBooleanSend: boolean = false;

  keepMeLogin: boolean = false;
  otp: string;
  showOtpComponent = true;
  @ViewChild('ngOtpInput', { static: false }) ngOtpInput: any;
  config = {
    allowNumbersOnly: false,
    length: 6,
    isPasswordInput: false,
    disableAutoFocus: false,
    placeholder: '',
    inputStyles: {
      'width': '30px',
      'height': '30px'
    }
  };
  userDetails = [
    { 'userId': 'prathapDS', 'password': '12345678', 'AccountType': 'customer' },
    { 'userId': 'DS2021', 'password': '12345678', 'AccountType': 'vendor' }
  ]
  showOtpPanel: boolean;
  showSendbtn: boolean = true;
  showVerifyBtn: boolean = false;
  otpData: any;
  paswrd: any;

  returnUrl: string;
  error = '';
  token: any;
  popupText: any;
  alertDivBoolean: boolean;
  submitted: boolean = false;
  User_type: string;
  errorMail: boolean;
  errorMailText: any;


  constructor(private router: Router,
    private formBuilder: FormBuilder,
    private sharedService: SharedService,
    private route: ActivatedRoute,
    private authenticationService: AuthenticationService) {
    // redirect to home if already logged in
    if (this.authenticationService.currentUserValue) {
      this.router.navigate(['IT_Utility'])
      // this.User_type = this.authenticationService.currentUserValue.user_type;
      // if (this.User_type === 'customer_portal') {
      //   this.router.navigate(['/customer']);
      // } else if (this.User_type === 'vendor_portal') {
      //   this.router.navigate(['/vendorPortal']);
      // }
    }
  }

  ngOnInit(): void {
    this.loginForm = this.formBuilder.group({
      username: ['', Validators.required],
      password: ['', Validators.required]
    });

    // if(){
    //   if(this.User_type === 'customer_portal'){
    //     this.router.navigate(['/customer']);
    //   } else if(this.User_type === 'vendor_portal'){
    //     this.router.navigate(['/vendorPortal']);
    //   }
    // }

    this.returnUrl = this.route.snapshot.queryParams['returnUrl'] || 'IT_Utility';
    console.log(this.returnUrl)
  }
  toggleFieldTextType() {
    this.fieldTextType = !this.fieldTextType;
  }
  toggleFieldTextTypeReset() {
    this.fieldTextTypeReset = !this.fieldTextTypeReset;
  }
  toggleFieldTextTypeReset1() {
    this.fieldTextTypeReset1 = !this.fieldTextTypeReset1;
  }
  test(event) {

    console.log("event", event.target.value)

    if (this.newPassword == this.confirmPassword) {
      this.passwordMatchBoolean = false;
    } else {
      // alert('Enter same password')
      this.passwordMatchBoolean = true;
    }
  }
  forgot() {
    this.loginboolean = false;
    this.forgotboolean = true;
    this.resetPassword = false;
    this.successPassword = false;
  }
  tryLogin() {
    this.loginboolean = true;
    this.forgotboolean = false;
    this.resetPassword = false;
    this.successPassword = false;
    this.showOtpPanel = false;
    this.showSendbtn = true;
  }
  sendOtp() {
    this.loading = true;
    let mailData = {
      mail: [this.sendMail]
    }
    this.sharedService.sendMail(this.sendMail).subscribe((data) => {
      console.log(data);
      if (data.result == "successful") {
        this.loading = false;
        this.showOtpPanel = true;
        this.showSendbtn = false;
        this.loginboolean = false;
        this.forgotboolean = false;
        this.resetPassword = true;
        this.successPassword = false;
        this.errorMail = false;
      }
    },err =>{
      this.errorMail = true;
      this.errorMailText = err.statusText
      this.loading = false;
    })
  }
  verifyOtp() {
    
    // this.loading = true;
    // this.sharedService.verifyotp().subscribe((data) => {
    //   this.loading = false;
    //   if (data['OTP'] == this.otp) {
    //     this.loginboolean = false;
    //     this.forgotboolean = false;
    //     this.resetPassword = true;
    //     this.successPassword = false;
    //     this.showSendbtn = true;
    //     this.showOtpPanel = true;
    //   } else {
    //     alert("Enter valid OTP");
    //     this.showSendbtn = true;
    //     this.showOtpPanel = false;
    //   }
    //   console.warn(data['OTP'])
    //   this.otpData = data['OTP'];
    // })
    // console.log(this.otpData)
  }
  resetPass() {
    this.loading = true;
    let updatePassword = {
      "activation_code": this.otp,
      "password": this.paswrd
    } 
    console.log("password is: ", updatePassword)
    this.sharedService.updatepass(JSON.stringify(updatePassword)).subscribe(data => {
      console.log(data)
      this.loading = false;
      this.loginboolean = false;
      this.forgotboolean = false;
      this.resetPassword = false;
      this.successPassword = true;

    })
  }
  resetSuccess() {
    this.loginboolean = true;
    this.forgotboolean = false;
    this.resetPassword = false;
    this.successPassword = false;
  }
  // convenience getter for easy access to form fields
  get f() { return this.loginForm.controls; };

  login() {
    this.submitted = true;

    // stop here if form is invalid
    if (this.loginForm.invalid) {
      return;
    }

    this.loading = true;
    let data = {
      "username": this.f.username.value,
      "password": this.f.password.value
    }
    this.authenticationService.login(JSON.stringify(data))
      .subscribe(
        data => {
          console.log(data)
            this.loading = false;
            if(data.permissioninfo.isConfigPortal == 1){
              this.router.navigate([this.returnUrl]);
            } else {
              this.error = "Sorry!, you don't have access please conatct admin"
            }
            
        },
        error => {
          this.loading = false;
          console.log(error)
          if (error.status === 401) {
          this.error = "Username or/and password are incorrect.";
            this.alertDivBoolean = true
          } else {
          this.error = error.statusText;
          }

        });
  }
  storeUser(e) {
    // console.log(e.target.checked)
    // this.keepMeLogin = e.target.checked;
    // this.sharedService.keepLogin = e.target.checked;
  }
  onOtpChange(otp) {
    this.otp = otp;
  }
}
