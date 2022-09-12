import { SharedService } from 'src/app/services/shared.service';
import { DocumentService } from './../../services/vendorPortal/document.service';
import { Component, OnInit } from '@angular/core';
import { PermissionService } from 'src/app/services/permission.service';
import { NgxSpinnerService } from 'ngx-spinner';
import { Location } from '@angular/common';
import { MessageService } from 'primeng/api';
@Component({
  selector: 'app-roles-vendor',
  templateUrl: './roles-vendor.component.html',
  styleUrls: ['./roles-vendor.component.scss']
})
export class RolesVendorComponent implements OnInit {
  viewType = 'user'
  updateroleData;
  appied_permission_def_id: number;
  displayResponsive:boolean;
  displayAddUserDialog:boolean;
  displayEditUserDialog:boolean;
  primengConfig: any;
  vendorUserReadData: any[];
  showPaginator: boolean;
  DisplayRoleName: any;
  userName: any;
  userEmail: any;
  userCode: any;
  designation: any;
  editRoleName: any;

  createUserCode: string;
  createUserName: string;
  emailIdInvite: string;
  InviteRole: string;
  createVfirstName:string;
  createVlastName:string;
  createVAccount:string;
  vendorAccount;

  errorObject = {
    severity: "error",
    summary: "error",
    detail: "Something went wrong"
  }
  addObject = {
    severity: "info",
    summary: "Added",
    detail: "Created Successfully"
  }
  updateObject = {
    severity: "info",
    summary: "Updated",
    detail: "Updated Successfully"
  }
  userBoolean: boolean;
  userNotBoolean: boolean;
  idVendorAccount: any;
  deleteBtnText: string;
  deleteBtnTextBoolean: boolean;
  vendoruserid: any;
  resetVendorMail: any;
  deactivateBoolean: boolean;
  vendorResetBtnBoolean: boolean;

  constructor(private permissionService: PermissionService,
    private docService : DocumentService,
    private messageService: MessageService,
    private SpinnerService: NgxSpinnerService,
    private sharedService : SharedService ,
    private _location: Location) { }

  ngOnInit(): void {
    if(this.permissionService.addUsersBoolean == true){
      this.DisplayVendorUserDetails();
      this.getDisplayTotalRoles();
      // this.getVendorAccountsData();
    } else {
      alert("Authorization error occured");
      this._location.back();
    }
  }
  DisplayVendorUserDetails() {
    const finalArray= [];
    // this.roles = [];
    this.docService.readVendorUsers().subscribe((data: any) => {
      console.log(data)
      if(data){
        data.forEach(element => {
          const mergedData = { ...element.AccessPermission, ...element.AccessPermissionDef,...element.User,...element.Vendor};
          finalArray.push(mergedData)
        });
        this.vendorUserReadData = finalArray;
        console.log(this.vendorUserReadData)
        if (this.vendorUserReadData.length > 10) {
          this.showPaginator = true;
        }
      }
    })
  }
  getDisplayTotalRoles() {
    this.SpinnerService.show();
    this.docService.displayRolesData()
      .subscribe((data: any) => {
        this.SpinnerService.hide();
        this.DisplayRoleName = data.roles
      });
  }
  editUser(value) {
    console.log(value)
    this.docService.cuserID = value.idVendorUser;
    this.displayEditUserDialog= true;
    this.userName = value.UserName;
    this.userEmail = value.Email;
    this.userCode = value.UserCode
    this.designation = value.Designation;
    this.editRoleName = value.NameOfRole;
   }

  UpdateUser() {
    let editVendor = 
      {
        "UserName": this.userName,
        "Email": this.userEmail,
        "Contact": "string",
        "idAccessPermissionDef": this.appied_permission_def_id
      }
    console.log(editVendor);
    this.docService.updateVendorUser(JSON.stringify(editVendor)).subscribe((data: any) => {
      console.log(data)
      if (data) {
        // const userData = data.customer_user_details
        // let selectrole = {
        //   "applied_uid": this.sharedService.cuserID,
        //   "isUser": true,
        //   "appied_permission_def_id": this.appied_permission_def_id
        // }
        // this.sharedService.editRole(JSON.stringify(selectrole)).subscribe((data: any) => { })
        this.messageService.add(this.updateObject);
        this.DisplayVendorUserDetails();
        this.displayEditUserDialog = false;
      } else {
        this.messageService.add(this.errorObject);
      }

    }, error=>{
      alert(error.statusText)
    })
  }
  selectRole(e) {
    let item = this.DisplayRoleName.filter((item) => {
      return e.indexOf(item.NameOfRole) > -1;
    })
    this.appied_permission_def_id = item[0].idAccessPermissionDef
  }
  // getVendorAccountsData(){
  //   this.docService.readVendorAccountsData().subscribe((data:any)=>{
  //     this.vendorAccount = data
  //   })
  // }
  selectVendorAccount(value){
    const accontData = this.vendorAccount.filter((element=>{
      return value === element.Account;
    }));
    this.idVendorAccount = accontData[0].idVendorAccount;
  }

  createVendorUser(){
    let vendorData = {
      "n_ven_user": {
        "firstName": this.createVfirstName,
        "lastName": this.createVlastName,
        "email": this.emailIdInvite,
        "role_id": 11,
        "uservendoraccess": [
          {
            "vendorUserID": 0,
            "vendorCode": "string",
            "entityID": [
              0
            ],
            "vendorAccountID": [
              0
            ]
          }
        ]
      },
      "n_cred": {
        "LogName": this.createUserName,
        "LogSecret": "string"
      }
    }
    this.docService.addVendorUser(JSON.stringify(vendorData)).subscribe((data:any)=>{
      this.addObject.detail = data.result;
      this.messageService.add(this.addObject);
      this.displayAddUserDialog = false;
      this.createVfirstName = '';
      this.createVlastName = '';
      this.emailIdInvite = '';
     this.DisplayVendorUserDetails();
    },error =>{
      this.errorObject.detail = error.statusText;
      this.messageService.add(this.addObject);
    })
  }

  userCheck(name){
    console.log(name)
    this.sharedService.userCheck(name).subscribe((data:any)=>{
      if(!data.LogName){
        this.userBoolean = true;
        this.userNotBoolean = false;
      } else{
        this.userNotBoolean = true;
        this.userBoolean = false;
      }
    })
  }
  resetPassword(){
    this.sharedService.resetPassword(this.userEmail).subscribe((data:any)=>{ });
  }
  // resetPasswordVendor(mail){
  //   this.sharedService.resetPassword(mail).subscribe((data:any)=>{});
  // }
  resetPasswordVendor(mail){
    this.deleteBtnText = "Are you sure you want to Reset this Account?";
    this.displayResponsive = true;
    this.vendorResetBtnBoolean = true;
    this.deactivateBoolean = false;
    this.resetVendorMail = mail;
  }

  resetPassVendorAPI(){
    this.sharedService.resetPassword(this.resetVendorMail).subscribe((data:any)=>{
      console.log(data);
      this.addObject.detail = data.result;
      this.errorObject.detail = data.result;
      if(data.result != 'failed mail'){
        this.messageService.add(this.addObject);
        this.displayResponsive = false;
        this.DisplayVendorUserDetails();
      }else {
        this.messageService.add(this.errorObject);
      }
    },error=>{
      this.errorObject.detail = error.statusText;
      this.messageService.add(this.errorObject);
    });
  }
  confirmationPopUp(id){
    this.deleteBtnText = "Are you sure you want to Activate/deactivate this Account?";
    this.displayResponsive=true;
    this.vendorResetBtnBoolean = false;
    this.deactivateBoolean = true;
    this.vendoruserid = id;
  }

  activa_deactive(){
    this.sharedService.activate_deactivate(this.vendoruserid ).subscribe((data:any)=>{
      console.log(data)
      this.addObject.detail = data.result;
      this.errorObject.detail = data.result;
      if(data.result != 'failed mail'){
        this.messageService.add(this.addObject);
        this.displayResponsive = false;
        this.vendoruserid = null;
        this.DisplayVendorUserDetails();
      }else {
        this.messageService.add(this.errorObject);
      }
    },error=>{
      this.errorObject.detail = error.statusText;
      this.messageService.add(this.errorObject);
    })
  }
}
