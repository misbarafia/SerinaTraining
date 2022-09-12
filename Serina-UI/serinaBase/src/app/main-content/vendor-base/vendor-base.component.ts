import { ServiceInvoiceService } from './../../services/serviceBased/service-invoice.service';
import { DocumentService } from './../../services/vendorPortal/document.service';
import { SharedService } from './../../services/shared.service';
import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { Subscription } from 'rxjs';
import { AuthenticationService } from 'src/app/services/auth/auth-service.service';
import { PermissionService } from 'src/app/services/permission.service';
import { MatDialog } from '@angular/material/dialog';
import { ChangePasswordComponent } from 'src/app/base/change-password/change-password.component';
import { environment1 } from 'src/environments/environment.prod';
import { ExceptionsService } from 'src/app/services/exceptions/exceptions.service';
import { ChartsService } from 'src/app/services/dashboard/charts.service';

@Component({
  selector: 'app-vendor-base',
  templateUrl: './vendor-base.component.html',
  styleUrls: ['./vendor-base.component.scss']
})
export class VendorBaseComponent implements OnInit {
  userDetails:any;numberOfNotify: any;
  notifyArray: any;
  addUsersBoolean: boolean;
  returnUrl: any;
  last_login: string;
  showLogout: boolean;
  subscription:Subscription;
  displayResponsivepopup:boolean;
  BtnText ="Are you sure you want to Logout?"
  menubarBoolean: boolean;
  excpetionPageAccess: boolean;

  constructor(private router:Router,
    private route : ActivatedRoute,
    private SharedService:SharedService,
    private permissionService: PermissionService,
    private authService: AuthenticationService,
    private docService : DocumentService,
    public dialog: MatDialog,
    private chartService: ChartsService,
    private exceptionService: ExceptionsService,
    private serviceproviderService : ServiceInvoiceService) { 
      this.subscription = this.SharedService.getMessage().subscribe(message => {
        console.log("message", message);
        this.numberOfNotify = message.Arraylength;
        // if (this.SharedService.keepLogin === true) {
        //   this.userDetails = JSON.parse(localStorage.getItem('logInUser'));
        // } else {
        //   this.userDetails = JSON.parse(localStorage.getItem('logInUser'));
        // }
      });
   
  }

  ngOnInit(): void {
    this.userDetails = this.authService.currentUserValue;
    this.docService.userId = this.userDetails.userdetails.idUser;
    this.SharedService.userId = this.userDetails.userdetails.idUser;
    this.serviceproviderService.userId = this.userDetails.userdetails.idUser
    this.SharedService.isCustomerPortal = false;
    environment1.password = this.userDetails.token;
    environment1.username = JSON.parse(localStorage.getItem('username'));
    this.exceptionService.userId = this.userDetails.userdetails.idUser;
    this.serviceproviderService.userId = this.userDetails.userdetails.idUser;
    this.chartService.userId = this.userDetails.userdetails.idUser;
    const date = this.convertUTCDateToLocalDate(new Date(this.userDetails.last_login));
    this.last_login = this.userDetails.last_login;
    this.readVendor();
    this.getPermissions();
    // this.getNotification();
    
  }

  readVendor(){
    this.docService.readVendorContactData().subscribe((data:any)=>{
      console.log(data);
      this.SharedService.vendorReadID = data.idVendor;
    });
  }

  convertUTCDateToLocalDate(date) {
    // const newDate = new Date(date.getTime()+date.getTimezoneOffset()*60*1000);

    // const offset = date.getTimezoneOffset() / 60;
    // const hours = date.getHours();

    // newDate.setHours(hours - offset);

    // return newDate;   
  }
    // read User permissions
    getPermissions(){
      if (this.userDetails.permissioninfo.is_epa == 1) {
        this.excpetionPageAccess = true
        this.permissionService.excpetionPageAccess = true;
      }
      if(this.userDetails){
        if(this.userDetails.permissioninfo.User == 1){
          this.addUsersBoolean = true;
          this.permissionService.addUsersBoolean = true;
        }
  
        if(this.userDetails.permissioninfo.AccessPermissionTypeId == 1){
          this.permissionService.viewBoolean = true;
          this.permissionService.editBoolean = false;
          this.permissionService.changeApproveBoolean = false;
          this.permissionService.financeApproveBoolean = false;
        }
        else if(this.userDetails.permissioninfo.AccessPermissionTypeId == 2){
          this.permissionService.viewBoolean = true;
          this.permissionService.editBoolean = true;
          this.permissionService.changeApproveBoolean = false;
          this.permissionService.financeApproveBoolean = false;
        } else if(this.userDetails.permissioninfo.AccessPermissionTypeId == 3){
          this.permissionService.viewBoolean = true;
          this.permissionService.editBoolean = true;
          this.permissionService.changeApproveBoolean = true;
          this.permissionService.financeApproveBoolean = false;
        } else if(this.userDetails.permissioninfo.AccessPermissionTypeId == 4){
          this.permissionService.viewBoolean = true;
          this.permissionService.editBoolean = true;
          this.permissionService.changeApproveBoolean = true;
          this.permissionService.financeApproveBoolean = true;
        }
      }
    }
  
    // get Notifications
    getNotification() {
      this.SharedService.getNotification().subscribe((data: any) => {
        console.log(data)
        this.notifyArray = data;
        this.numberOfNotify = this.notifyArray.length;
        console.log('hia', this.numberOfNotify);
      })
    }
  isActive(){
    this.showLogout = !this.showLogout;
  }
  onClickedOutside(e: Event) {
    this.showLogout = false;
  }
  openDialog() {
    this.dialog.open(ChangePasswordComponent);
  }
  onClickMenu(){
    this.menubarBoolean = !this.menubarBoolean
  }
  logout(){
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}
