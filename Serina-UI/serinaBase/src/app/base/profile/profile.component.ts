import { Component, OnInit } from '@angular/core';
import { AuthenticationService } from 'src/app/services/auth/auth-service.service';

@Component({
  selector: 'app-profile',
  templateUrl: './profile.component.html',
  styleUrls: ['./profile.component.scss']
})
export class ProfileComponent implements OnInit {
loginUser:any;
editable:boolean =false;

  constructor(private authService: AuthenticationService) { }

  ngOnInit(): void {
    this.loginUser = this.authService.currentUserValue;
  }
  onEdit(){
    this.editable= true;
  }
  onSave(){
    this.editable= false;
  }
  onCancel(){
    this.editable= false;
  }

}
