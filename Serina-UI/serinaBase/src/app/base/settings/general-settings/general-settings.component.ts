import { SettingsService } from './../../../services/settings/settings.service';
import { Component, OnInit } from '@angular/core';
import { PermissionService } from 'src/app/services/permission.service';

@Component({
  selector: 'app-general-settings',
  templateUrl: './general-settings.component.html',
  styleUrls: ['./general-settings.component.scss']
})
export class GeneralSettingsComponent implements OnInit {
  isAdmin: boolean;
  finaceApproveDisplayBoolean : boolean;

  constructor(private permissionService : PermissionService,
    private SettingsService : SettingsService) { }

  ngOnInit(): void {
    this.isAdmin = this.permissionService.addUsersBoolean;
    this.finaceApproveDisplayBoolean = this.SettingsService.finaceApproveBoolean;
  }

  // readSettingsData() {
  //   this.SettingsService.readGeneralSettings().subscribe((data:any)=>{
  //     console.log(data);
  //   });
  // }

}
