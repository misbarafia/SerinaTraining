import { SharedService } from 'src/app/services/shared/shared.service';
import { AuthenticationService } from 'src/app/services/auth/auth.service';
import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit {
  userDetails:any;
  displaypopup:boolean = false;
  isAdmin: boolean;
  constructor(private authService : AuthenticationService,
    private sharedService : SharedService,public router:Router) { }

  ngOnInit(): void {
    this.userDetails = this.authService.currentUserValue;
    this.sharedService.userId = this.userDetails.userdetails.idUser;
    console.log(this.userDetails);
    if(this.userDetails.permissioninfo.User == 1){
      this.sharedService.isAdmin = true;
    } else {
      this.sharedService.isAdmin = false;
    }
    this.isAdmin = this.sharedService.isAdmin;
  }

  signOut(){
    this.authService.logout();
  }
  openPopup(){
    this.displaypopup = true;
  }

}
