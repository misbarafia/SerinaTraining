import { Subscription } from 'rxjs';
import { DataService } from './../../services/dataStore/data.service';
import { SettingsService } from './../../services/settings/settings.service';
import { Location } from '@angular/common';
import { PermissionService } from './../../services/permission.service';
import { ActivatedRoute, Router } from '@angular/router';
import { Component, OnInit, ViewChild, ElementRef } from '@angular/core';
import {
  ConfirmationService,
  MessageService,
  PrimeNGConfig
} from "primeng/api";
import { SharedService } from 'src/app/services/shared.service';
import { NgxSpinnerService } from 'ngx-spinner';


export interface UserData {
  name: string;
  role: string;
  userId: string;
  designation: string;
  entities: number;
  emailId: string;
  mobile: string;
}
export interface updateUserEntityData {
  idUserAccess?: number,
  EntityID?: number,
  EntityBodyID?: number,
  DepartmentID?: number
}

export interface dropdownData {
  Entity: string;
  value: dropdownDatavalue[]
}
export interface dropdownDatavalue {
  name: string;
}

export interface selectedValue {
  idUserAccess?: number,
  entity?: string;
  entityBody?: string;
  entityDept?: string;
  EntityID?: number,
  EntityBodyID?: number,
  DepartmentID?: number
}
@Component({
  selector: 'app-roles',
  templateUrl: './roles.component.html',
  styleUrls: ['./roles.component.scss']
})
export class RolesComponent implements OnInit {
  normalRole: boolean = true;
  checked1: boolean = false;
  initialView: boolean = true;
  users: UserData[];
  usersData;
  roles = [];
  NameOfRole: any;
  Flevel: any = null;

  selectedEntityName;
  selectedEntityBodyName;
  selectedEntityDeptName;

  createUserCode: string;
  createUserName: string;
  emailIdInvite: string;
  InviteRole: string;
  InviteUserPassword: string;
  InviteFlevel: any;
  createUserDesignation;

  createRoleRequiredBoolean: boolean = false;
  newRoleName: string;
  newRoleDescription:string;
  
  events1: any[];

  loginUserData: any;
  visible = true;
  filteredEntities: any[];
  dEntityBody: dropdownData[] = [];
  dEntityDept: dropdownData[] = [];
  filterDentityBody: any[] = [];
  filterDentityDept: any[] = [];

  selectedEntitys: selectedValue[] = [];
  CreateNewRole: boolean = false;
  editUserdata: boolean = false;
  saveRoleBoolean: boolean;

  roletype: string;
  CustomerUserReadData;
  vendorAdminReadData;

  userName: string;
  firstName: string;
  lastName: string;
  designation;
  userEmail: string;
  userCode: any;
  custuserid: any;
  editRoleName: string;
  selectedEntityBody: any;
  selectedEntityDept: any;
  entityList: any;
  selectedEntityId: any;
  entityBodyList: any[];
  entityDeptList: any;

  showPaginator: boolean;
  DisplayRoleName: any[];

  roleInfoDetails: any;
  someParameterValue;

  AddorModifyUserBoolean: boolean = false;
  userRoleBoolean: boolean = false;
  invoiceBoolean: boolean = false;
  viewInvoiceBoolean: boolean = false;
  editInvoiceBoolean: boolean = false;
  changeApproveBoolean: boolean = false;
  financeApproveBoolean: boolean = false;
  spTriggerBoolean = false;
  vendorTriggerBoolean = false;
  configAccessBoolean:boolean =false;
  dashboardAccessBoolean:boolean = false;
  vendorPageBoolean = false;
  settingsPageBoolean = false;
  GRNPageBoolean = false;
  exceptionPageBoolean = false;

  userAccess: number = 0;
  userRoleAccess = 0;
  invoiceAccess = 0;

  AccessPermissionTypeId: number;

  deleteBtnText: string;

  errorObject = {
    severity: "error",
    summary: "error",
    detail: "Something went wrong"
  }
  addObject = {
    severity: "success",
    summary: "Success",
    detail: "Created Successfully"
  }
  updateObject = {
    severity: "info",
    summary: "Updated",
    detail: "Updated Successfully"
  }

  viewType = 'user'
  updateroleData;
  appied_permission_def_id: number;
  displayResponsive: boolean;
  displayAddUserDialog: boolean;
  headerEdituserboolean: boolean
  updateUserEnt_body_id: number;
  updateUserEnt_dept_id: number;
  updateUsersEntityInfo: updateUserEntityData[] = [];
  updateEntityUserDummy: updateUserEntityData[] = [];
  userBoolean: boolean;
  userNotBoolean: boolean;
  resetBtnText: string;
  vendorList: any;
  vendorCreate: string;
  createVAccount: string;
  createVlastName: string;
  createVfirstName: string;
  idVendor: number;
  idVendorAccount: any;
  vendorSuperUsersReadData: any;
  showPaginatorSp: boolean;
  deleteBtnTextBoolean: boolean;
  deleteRoleBoolean: boolean;
  deactivateBoolean: boolean;
  resetVendorMail: any;
  vendorResetBtnBoolean: boolean;
  userResetBtnBoolean: boolean;
  max_role_amount = 0;
  role_priority:number;

  financeapproveDisplayBoolean:boolean;
  addRoleBoolean: boolean;
  vendorsSubscription:Subscription;
  entitySubscription :Subscription;
  filteredVendors: any;
  entitySelection:any[];
  entityForVendorCreation = [];
  vendorEntityCodes: any;
  vendorCode: any;

  row_customer: number = 10;
  row_vendor : number = 10;
  first_cust :number = 0;
  first_vendor :number = 0;
  constructor(private dataService: DataService,
    private messageService: MessageService,
    private sharedService: SharedService,
    private router: Router,
    public routeIn: ActivatedRoute,
    private permissionService: PermissionService,
    private SpinnerService: NgxSpinnerService,
    private _location: Location,
    private settingsService : SettingsService,
    private primengConfig: PrimeNGConfig) {
    routeIn.params.subscribe(params => {
      this.setupComponent(params['someParam']);
    })
  }

  ngOnInit(): void {
    this.inIt();
  }

  inIt(){
    if (this.permissionService.addUsersBoolean == true) {
      this.router.navigate(['/customer/roles', 'createdUsers']);
      this.someParameterValue = 'createdUsers';
      this.primengConfig.ripple = true;
      this.DisplayCustomerUserDetails();
      this.toGetEntity();
      this.getDisplayTotalRoles();
      this.getVendorsListTocreateNewVendorLogin();
      this.getVendorSuperUserList();
      this.financeapproveDisplayBoolean = this.settingsService.finaceApproveBoolean;
      this.addRoleBoolean = this.permissionService.addUserRoleBoolean;
    } else {
      alert("Sorry!, you do not have access");
      this._location.back();
    }
  }
  setupComponent(someParam) {
    this.someParameterValue = someParam;
  }

  showDailog(e) {

    if(this.addRoleBoolean == true){
      this.deleteBtnText = "Are you sure you want to delete this Role?";
      this.deleteRoleBoolean = true;
      this.vendorResetBtnBoolean = false;
      this.userResetBtnBoolean = false;
      this.deactivateBoolean = false;
      this.displayResponsive = true;
      this.sharedService.ap_id = e.idAccessPermissionDef;
    } else {
      alert('Sorry, you do not have access!')
    }
  }

  DeleteRole() {
    this.sharedService.deleteRole().subscribe((data: any) => {
      if (data.result == "success") {
        this.messageService.add({
          severity: "success",
          summary: "Deleted",
          detail: "Deleted Successfully"
        });
        this.getDisplayTotalRoles();
      } else {
        this.messageService.add(this.errorObject);
      }
    });
    this.displayResponsive = false;
  }

  createRole() {
    if(this.addRoleBoolean == true){
      this.router.navigate(['/customer/roles', 'createNewRole']);
      this.SpinnerService.hide();
      this.roletype = 'Create New Role'
      this.normalRole = false;
      this.newRoleName = '';
      this.CreateNewRole = true;
      this.editUserdata = false;
      this.saveRoleBoolean = true;
    } else {
      alert('Sorry!, you do not have access')
    }

  }
  cancelRoles() {
    this.router.navigate(['/customer/roles', 'definedRoles']);
    this.normalRole = true;
    this.CreateNewRole = false;
    this.editUserdata = false;
  }
  saveRoles() {
    if (!this.newRoleName) {
      this.createRoleRequiredBoolean = true;
    }
    else {
      this.addandUpdaterole();
      this.sharedService.createRole(JSON.stringify(this.updateroleData)).subscribe((data: any) => {
        if (data.result) {
          this.messageService.add({
            severity: "success",
            summary: "Added",
            detail: "Role Created Successfully"
          });
          this.getDisplayTotalRoles();
          this.normalRole = true;
          this.CreateNewRole = false;
          this.editUserdata = false;
        } else {
          this.messageService.add(this.errorObject);
          this.getDisplayTotalRoles();
        }
      },
        error => {
          if(error.status == 400){
            this.errorObject.detail = 'Please provide other priorioty, the given priority is already taken.';
          } else {
            this.errorObject.detail = error.statusText;
          }
          this.messageService.add(this.errorObject);
        }
      )
      this.createRoleRequiredBoolean = false;
      this.normalRole = true;
      this.CreateNewRole = false;
      this.editUserdata = false;
    }

  }
  editRole(e) {
    if(this.addRoleBoolean == true){
      this.router.navigate(['/customer/roles', `${e.idAccessPermissionDef}editRoleDetails`]);
      this.sharedService.ap_id = e.idAccessPermissionDef;
      this.newRoleName = e.NameOfRole;
  
      this.roletype = 'Edit Role'
      this.normalRole = false;
      this.CreateNewRole = true;
      this.saveRoleBoolean = false;
      this.editUserdata = false;
      this.SpinnerService.show();
      this.max_role_amount = 0;
      this.sharedService.displayRoleInfo().subscribe((data: any) => {
        this.roleInfoDetails = data.roleinfo.AccessPermissionDef;
        this.role_priority = this.roleInfoDetails.Priority;
        if(data.roleinfo.AmountApproveLevel){
        this.max_role_amount = data.roleinfo.AmountApproveLevel.MaxAmount;
        }
        if (this.roleInfoDetails.User === 1) {
          this.AddorModifyUserBoolean = true;
        } else {
          this.AddorModifyUserBoolean = false;
        }
        if (this.roleInfoDetails.Permissions === 1) {
          this.userRoleBoolean = true;
        } else {
          this.userRoleBoolean = false;
        }
        if (this.roleInfoDetails.NewInvoice === 1) {
          this.invoiceBoolean = true;
        } else {
          this.invoiceBoolean = false;
        }
        this.vendorTriggerBoolean = this.roleInfoDetails.allowBatchTrigger;
        this.spTriggerBoolean = this.roleInfoDetails.allowServiceTrigger;
        this.configAccessBoolean = this.roleInfoDetails.isConfigPortal;
        this.dashboardAccessBoolean = this.roleInfoDetails.isDashboard;
        this.exceptionPageBoolean = this.roleInfoDetails.is_epa;
        this.GRNPageBoolean = this.roleInfoDetails.is_gpa;
        this.vendorPageBoolean = this.roleInfoDetails.is_vspa;
        this.settingsPageBoolean = this.roleInfoDetails.is_spa;
  
        if (this.roleInfoDetails.AccessPermissionTypeId === 4) {
          this.viewInvoiceBoolean = true;
          this.editInvoiceBoolean = true;
          this.changeApproveBoolean = true;
          this.financeApproveBoolean = true;
        } else if (this.roleInfoDetails.AccessPermissionTypeId === 3) {
          this.viewInvoiceBoolean = true;
          this.editInvoiceBoolean = true;
          this.changeApproveBoolean = true;
          this.financeApproveBoolean = false;
        } else if (this.roleInfoDetails.AccessPermissionTypeId === 2) {
          this.viewInvoiceBoolean = true;
          this.editInvoiceBoolean = true;
          this.changeApproveBoolean = false;
          this.financeApproveBoolean = false;
        } else if (this.roleInfoDetails.AccessPermissionTypeId === 1) {
          this.viewInvoiceBoolean = true;
          this.editInvoiceBoolean = false;
          this.changeApproveBoolean = false;
          this.financeApproveBoolean = false;
        } else if (this.roleInfoDetails.AccessPermissionTypeId === 0) {
          this.viewInvoiceBoolean = false;
          this.editInvoiceBoolean = false;
          this.changeApproveBoolean = false;
          this.financeApproveBoolean = false;
        }
        this.SpinnerService.hide();
      })
    } else {
      alert('Sorry, you do not have access!')
    }
    
  }
  changeUserPermission(e) {
    if (e.target.checked === true) {
      this.userAccess = 1;
      this.AddorModifyUserBoolean = true;
    } else {
      this.userAccess = 0;
      this.AddorModifyUserBoolean = false;
    }
  }
  changeUserRolePermission(e) {
    if (e.target.checked === true) {
      this.userRoleAccess = 1;
      this.userRoleBoolean = true;
    } else {
      this.userRoleAccess = 0;
      this.userRoleBoolean = false;
    }
  }
  changeInvoicePermission(e) {
    if (e.target.checked === true) {
      this.invoiceAccess = 1;
      this.invoiceBoolean = true;
    } else {
      this.invoiceAccess = 0;
      this.invoiceBoolean = false;
    }
  }
  changeSpTriggerPermission(e) {
    if (e.target.checked === true) {
      this.spTriggerBoolean = true;
    } else {
      this.spTriggerBoolean = false;
    }
  }
  changeVendorTriggerPermission(e) {
    if (e.target.checked === true) {
      this.vendorTriggerBoolean = true;
    } else {
      this.vendorTriggerBoolean = false;
    }
  }
  changeViewInvoice(e) {
    if (e.target.checked === true) {
      this.viewInvoiceBoolean = true;
    } else {
      this.viewInvoiceBoolean = false;
      this.editInvoiceBoolean = false;
      this.changeApproveBoolean = false;
      this.financeApproveBoolean = false;
    }
  }
  changeEditInvoice(e) {
    if (e.target.checked === true) {
      this.viewInvoiceBoolean = true;
      this.editInvoiceBoolean = true;
    } else {
      this.viewInvoiceBoolean = true;
      this.editInvoiceBoolean = false;
      this.changeApproveBoolean = false;
      this.financeApproveBoolean = false;
    }
  }
  changeChangeApproveInvoice(e) {
    if (e.target.checked === true) {
      this.viewInvoiceBoolean = true;
      this.editInvoiceBoolean = true;
      this.changeApproveBoolean = true;
    } else {
      this.viewInvoiceBoolean = true;
      this.editInvoiceBoolean = true;
      this.changeApproveBoolean = false;
      this.financeApproveBoolean = false;
    }
  }
  changeFinanceApproveInvoice(e) {
    if (e.target.checked === true) {
      this.viewInvoiceBoolean = true;
      this.editInvoiceBoolean = true;
      this.changeApproveBoolean = true;
      this.financeApproveBoolean = true;
    } else {
      this.financeApproveBoolean = false;
    }
  }
  addandUpdaterole() {
    if (this.viewInvoiceBoolean == true && this.editInvoiceBoolean == true && this.changeApproveBoolean == true && this.financeApproveBoolean == true) {
      this.AccessPermissionTypeId = 4
    } else if (this.viewInvoiceBoolean == true && this.editInvoiceBoolean == true && this.changeApproveBoolean == true && this.financeApproveBoolean == false) {
      this.AccessPermissionTypeId = 3;
    } else if (this.viewInvoiceBoolean == true && this.editInvoiceBoolean == true && this.changeApproveBoolean == false && this.financeApproveBoolean == false) {
      this.AccessPermissionTypeId = 2;
    } else if (this.viewInvoiceBoolean == true && this.editInvoiceBoolean == false && this.changeApproveBoolean == false && this.financeApproveBoolean == false) {
      this.AccessPermissionTypeId = 1;
    }

    this.updateroleData = {
      "NameOfRole": this.newRoleName,
      "Priority": this.role_priority,
      "User": this.AddorModifyUserBoolean,
      "Permissions": this.userRoleBoolean,
      "AccessPermissionTypeId": this.AccessPermissionTypeId,
      "allowBatchTrigger":  this.vendorTriggerBoolean,
      "isConfigPortal" : this.configAccessBoolean,
      "isDashboard" : this.dashboardAccessBoolean,
      "allowServiceTrigger": this.spTriggerBoolean,
      "NewInvoice": this.invoiceBoolean,
      "max_amount": this.max_role_amount,
      "is_epa": this.exceptionPageBoolean,
      "is_gpa": this.GRNPageBoolean,
      "is_vspa": this.vendorPageBoolean,
      "is_spa": this.settingsPageBoolean,
    }
  }

  updateRoleInfoData() {
    this.addandUpdaterole();
    this.sharedService.updateRoleData(JSON.stringify(this.updateroleData)).subscribe((data: any) => {
      if (data.result) {
        this.messageService.add(this.updateObject);
        this.getDisplayTotalRoles();
        this.normalRole = true;
        this.CreateNewRole = false;
        this.editUserdata = false;
      } else {
        this.messageService.add(this.errorObject);
      }
    },
      error => {
        console.log(error)
        this.errorObject.detail = error.statusText;
        this.messageService.add(this.errorObject);
      }
    )
  }

  toGetEntity() {
    this.entityList = [];
    this.sharedService.getEntityDept().subscribe((data: any) => {
      this.entityList = data;
    })
  }

  filterEntity(event) {
    let filtered: any[] = [];
    let query = event.query;
    for (let i = 0; i < this.entityList.length; i++) {
      let country = this.entityList[i];
      if (country.EntityName.toLowerCase().indexOf(query.toLowerCase()) == 0) {
        filtered.push(country);
      }
    }
    this.filteredEntities = filtered;
  }
  filterEntityBody(event) {
    if (this.entityBodyList) {
      let query = event.query;
      this.filterDentityBody = this.entityBodyList.filter((element) => {
        return element.EntityBodyName.toLowerCase().indexOf(query.toLowerCase()) == 0
      })
    } else {
      alert("Please select Entity")
    }
  }
  filterEntityDept(event) {
    if (this.entityDeptList) {
      let query = event.query;
      this.filterDentityDept = this.entityDeptList.filter((element) => {
        return element.DepartmentName.toLowerCase().indexOf(query.toLowerCase()) == 0
      })
    } else {
      alert("Please select Entitybody")
    }
  }
  onSelectEntity(value) {
    this.entityBodyList = [];
    this.entityDeptList = [];
    this.sharedService.selectedEntityId = value.idEntity;
    this.selectedEntityId = value.idEntity;
    ;
    this.sharedService.getEntitybody().subscribe((data: any) => {
      this.entityBodyList = data;
      // this.entityDeptList = this.entityBodyList[0].department
    });
    this.selectedEntitys.push({ entity: value.EntityName, EntityID: value.idEntity });
    this.updateUsersEntityInfo.push({ idUserAccess: null, EntityID: value.idEntity })
    this.selectedEntityName = value.EntityName;
  }
  onSelectEntityBody(e) {
    let ent_body_name = this.entityBodyList.filter((element => {
      return element.EntityBodyName == e.EntityBodyName;
    }))
    this.entityDeptList = ent_body_name[0].department
    // this.updateUsersEntityInfo.push({EntityBodyID: e.idEntityBody});
    this.updateUsersEntityInfo.forEach((value) => {
      if (value.EntityID == this.selectedEntityId && !value.EntityBodyID) {
        value.EntityBodyID = e.idEntityBody;
        this.updateUserEnt_body_id = e.idEntityBody;
      }
    })
    this.selectedEntitys.forEach((element) => {
      if (element.entity == this.selectedEntityName && (!element.entityBody || element.entityBody.length == 0)) {
        element.entityBody = e.EntityBodyName;
        element.EntityBodyID = e.idEntityBody;
        this.selectedEntityBodyName = e.EntityBodyName;
      }
    })
  }

  onSelectEntityDept(e) {
    this.updateUsersEntityInfo.forEach((value) => {
      if (value.EntityID == this.selectedEntityId && value.EntityBodyID == this.updateUserEnt_body_id && !value.DepartmentID) {
        value.DepartmentID = e.idDepartment;
        this.updateUserEnt_dept_id = e.idDepartment;
      }
    });
    let count = 0;
    this.selectedEntitys.forEach((element) => {
      if (element.entityDept === e.DepartmentName) {
        alert("Please select other Department")
      } else if (!element.entityDept || element.entityDept == '') {
        count = count + 1;
      } else {
        count = count + 1;
      }
    })
    if (count === this.selectedEntitys.length) {
      if (this.selectedEntitys[this.selectedEntitys.length - 1].entity == this.selectedEntityName &&
        this.selectedEntitys[this.selectedEntitys.length - 1].entityBody == this.selectedEntityBodyName &&
        (!this.selectedEntitys[this.selectedEntitys.length - 1].entityDept ||
          this.selectedEntitys[this.selectedEntitys.length - 1].entityDept.length == 0)) {
        this.selectedEntitys[this.selectedEntitys.length - 1].entityDept = e.DepartmentName;
        this.selectedEntitys[this.selectedEntitys.length - 1].DepartmentID = e.idDepartment;
        this.selectedEntityDeptName = e.DepartmentName;
      }
    }
  }

  onRemove(index, value) {
    if(this.selectedEntitys.length > 1){
      if (value.idUserAccess) {
        this.updateUsersEntityInfo
          .push({
            idUserAccess: value.idUserAccess,
            EntityID: value.EntityID,
            EntityBodyID: value.EntityBodyID,
            DepartmentID: value.DepartmentID
          })
      } else {
        let Ent_id = value.EntityID ? value.EntityID : null
        let Ent_body_id = value.EntityBodyID ? value.EntityBodyID : null;
        let Ent_dept_id = value.DepartmentID ? value.DepartmentID : null;
        this.updateUsersEntityInfo.forEach((element, index) => {
          if (Ent_id && Ent_body_id && Ent_dept_id) {
            if (element.EntityID == Ent_id && element.EntityBodyID == Ent_body_id && element.DepartmentID == Ent_dept_id) {
              this.updateUsersEntityInfo.splice(index, 1);
            }
          } else if (Ent_id && Ent_body_id) {
            if (element.EntityID == Ent_id && element.EntityBodyID == Ent_body_id) {
              this.updateUsersEntityInfo.splice(index, 1);
            }
          }
          else {
            if (element.EntityID == Ent_id) {
              this.updateUsersEntityInfo.splice(index, 1);
            }
          }
        })
      }
      this.selectedEntitys.splice(index, 1);
    } else {
      this.errorObject.detail = "Atleast one entity required"
      this.messageService.add(this.errorObject);
    }
  };

  editUser(value) {
    this.router.navigate(['/customer/roles', `${value.idUser}editUser`]);
    if (value.isActive == 0) {
      this.resetBtnText = "Resend Activation Link";
    } else {
      this.resetBtnText = "Reset Account";
    }
    this.sharedService.cuserID = value.idUser;
    this.headerEdituserboolean = true;
    this.normalRole = false;
    this.CreateNewRole = false;
    this.editUserdata = true;
    this.firstName = value.firstName;
    this.lastName = value.lastName;
    this.userEmail = value.email;
    this.userCode = value.UserCode;
    this.editRoleName = value.NameOfRole;
    if (value && value.MaxAmount) {
      this.Flevel = value.MaxAmount;
    }

    this.sharedService.readEntityUserData(value.idUser).subscribe((data: any) => {
      data.result.forEach(element => {
        if (!element.EntityBody && !element.Department) {
          this.selectedEntitys.push({ entity: element.Entity.EntityName, entityBody: element.EntityBody, entityDept: element.Department, idUserAccess: element.UserAccess.idUserAccess, EntityID: element.Entity.idEntity, EntityBodyID: element.EntityBody, DepartmentID: element.Department });
          this.updateEntityUserDummy.push({ idUserAccess: element.UserAccess.idUserAccess, EntityID: element.Entity.idEntity, EntityBodyID: element.EntityBody, DepartmentID: element.Department });
        }
        else if (!element.Department) {
          this.selectedEntitys.push({ entity: element.Entity.EntityName, entityBody: element.EntityBody.EntityBodyName, entityDept: element.Department, idUserAccess: element.UserAccess.idUserAccess, EntityID: element.Entity.idEntity, EntityBodyID: element.EntityBody.idEntityBody, DepartmentID: element.Department });
          this.updateEntityUserDummy.push({ idUserAccess: element.UserAccess.idUserAccess, EntityID: element.Entity.idEntity, EntityBodyID: element.EntityBody.idEntityBody, DepartmentID: element.Department });
        }
        else {
          this.selectedEntitys.push({ entity: element.Entity.EntityName, entityBody: element.EntityBody.EntityBodyName, entityDept: element.Department.DepartmentName, idUserAccess: element.UserAccess.idUserAccess, EntityID: element.Entity.idEntity, EntityBodyID: element.EntityBody.idEntityBody, DepartmentID: element.Department.idDepartment });
          this.updateEntityUserDummy.push({ idUserAccess: element.UserAccess.idUserAccess, EntityID: element.Entity.idEntity, EntityBodyID: element.EntityBody.idEntityBody, DepartmentID: element.Department.idDepartment });
        }
      });
    })
  }

  canceleditUser() {
    this.router.navigate(['/customer/roles', 'createdUsers']);
    this.normalRole = true;
    this.CreateNewRole = false;
    this.editUserdata = false;
    this.selectedEntitys = [];
    this.updateUsersEntityInfo = [];
    this.userNotBoolean = false;
    this.userBoolean = false;
  }
  UpdateUser() {
    let editUser = {
      "User": {
        "firstName": this.firstName,
        "lastName": this.lastName,
        "UserName": this.userName,
        "email": this.userEmail
      },
      "userentityaccess": this.updateUsersEntityInfo
      
    }
      this.sharedService.updatecustomeruser(JSON.stringify(editUser)).subscribe((data: any) => {
        if (data.result == 'Updated') {
          const userData = data.customer_user_details
          let selectrole = {
            "applied_uid": this.sharedService.cuserID,
            "isUser": true,
            "appied_permission_def_id": this.appied_permission_def_id
          };
          this.sharedService.editRole(JSON.stringify(selectrole)).subscribe((data: any) => { });
          let amountApproval = {
            "applied_uid": this.sharedService.cuserID,
            "isUser": true,
            "MaxAmount": this.Flevel
          };
          // this.sharedService.newAmountApproval(JSON.stringify(amountApproval)).subscribe((data: any) => { });
          this.messageService.add(this.updateObject);
          this.ngOnInit();
  
          this.normalRole = true;
          this.CreateNewRole = false;
          this.editUserdata = false;
          this.selectedEntitys = [];
          this.firstName = '';
          this.lastName = '';
          this.updateUsersEntityInfo = [];
        } else {
          this.messageService.add(this.errorObject);
        }
  
      }, error => {
        alert(error.statusText)
      })

  }

  DisplayCustomerUserDetails() {
    this.roles = [];
    this.sharedService.readcustomeruser().subscribe((data: any) => {
      let usersList = []
      data.forEach(element => {
        let mergedData = { ...element.AccessPermission, ...element.AccessPermissionDef,...element.rnk, ...element.User ,...element.AmountApproveLevel,...element.rnk};
        usersList.push(mergedData)
      });
      this.CustomerUserReadData = usersList;
      if (this.CustomerUserReadData.length > 10) {
        this.showPaginator = true;
      }
    })
  }

  createCustomerUserPage() {
    this.headerEdituserboolean = false;
    this.normalRole = false;
    this.CreateNewRole = false;
    this.editUserdata = true;
    this.userName = '';
    this.userEmail = '';
    this.editRoleName = '';
    this.Flevel = '';
    this.selectedEntitys = [];
  }

  userCheck(name) {
    this.sharedService.userCheck(name).subscribe((data: any) => {
      if (!data.LogName) {
        this.userBoolean = true;
        this.userNotBoolean = false;
      } else {
        this.userNotBoolean = true;
        this.userBoolean = false;
      }
    })
  }

  toCreateUser() {
    let requiredError = {
      severity: "error",
      summary: "Fill required fields",
      detail: "Please fill all the given fields"
    }
    if (this.updateUsersEntityInfo.length > 0 && this.userName != '' && this.userNotBoolean == false) {

      if (this.Flevel == "") {
        this.Flevel = null;
      }
      let createUserData = {
        "n_cust": {
          "email": this.userEmail,
          "firstName": this.firstName,
          "lastName": this.lastName,
          "userentityaccess": this.updateUsersEntityInfo,
          "role_id": this.appied_permission_def_id,
          "max_amount": this.Flevel,
        },
        "n_cred": {
          "LogName": this.userName,
          "LogSecret": "string"
        }
      }
      this.sharedService.createNewUser(JSON.stringify(createUserData)).subscribe((data) => {
        this.messageService.add(this.addObject);
        this.normalRole = true;
        this.CreateNewRole = false;
        this.editUserdata = false;
        this.selectedEntitys = [];
        this.updateUsersEntityInfo = [];
        this.userNotBoolean = false;
        this.userBoolean = false;
        this.firstName = '';
        this.lastName = '';
        this.DisplayCustomerUserDetails();
      }, error => {
        if (error.status == 422) {
          this.messageService.add(requiredError);
        } else {
          this.errorObject.detail = error.statusText;
          this.messageService.add(this.errorObject)
        }
      });

    } else {
      this.messageService.add(requiredError);
    }

  }

  selectRole(e) {
    let item = this.DisplayRoleName.filter((item) => {
      return e.indexOf(item.NameOfRole) > -1;
    })
    this.appied_permission_def_id = item[0].idAccessPermissionDef
  }

  changeUserRole(e, value) {
    let item = this.DisplayRoleName.filter((item) => {
      return value.indexOf(item.NameOfRole) > -1;
    })
    let roleData = {
      "applied_uid": e.idUser,
      "isUser": true,
      "appied_permission_def_id": item[0].idAccessPermissionDef
    }
    this.sharedService.editRole(JSON.stringify(roleData)).subscribe((data: any) => {
      if (data.result == "success") {
        this.messageService.add({
          severity: "success",
          summary: "Role changed",
          detail: "Role Changed Successfully"
        });
      } else {
        this.messageService.add(this.errorObject);
      }
    })
  }
  getDisplayTotalRoles() {
    this.SpinnerService.show();
    this.sharedService.displayRolesData()
      .subscribe((data: any) => {
        this.SpinnerService.hide();
        this.DisplayRoleName = data.roles;
        this.DisplayRoleName = this.DisplayRoleName.sort((a,b)=> b.isDefault - a.isDefault);
      })
  }

  getVendorsListTocreateNewVendorLogin() {
    this.sharedService.getVendorUniqueData('?offset=1&limit=100').subscribe((data: any) => {
      this.vendorList = data;
      console.log(this.vendorList)
    });
  }
  filterVendor(event) {
    let query = event.query.toLowerCase();
    if(query != ''){
      console.log(query);
      this.sharedService.getVendorUniqueData(`?offset=1&limit=100&ven_name=${query}`).subscribe((data:any)=>{
        this.filteredVendors = data;
      });
    } else {
      this.filteredVendors = this.vendorList;
    }
  }

  selectVendor(value) {
    console.log(value)
    // const accontData = this.vendorList.filter((element => {
    //   return value === element.VendorName;
    // }));
    this.vendorCode = value.VendorCode;
    this.readEntityForVendorOnboard(value.VendorCode);

    // this.entityForVendorCreation = accontData[0].entity_ids;
    // 
    // console.log(accontData,this.entityForVendorCreation)

    // this.idVendor = accontData[0].idVendor;
  }

  onSelectedEntityCode(value){
  }

  readEntityForVendorOnboard(ven_code){
    this.sharedService.getVendorsCodesToCreateNewlogin(ven_code).subscribe((data: any) => {
      this.entityForVendorCreation = data.ent_details;
      this.entitySelection = this.entityForVendorCreation;
    })
  }
  createVendorSuprUser() {
    let entityIdArray = [];
    this.entitySelection.forEach(ent_id=>{
      entityIdArray.push(ent_id.idEntity);
    })
    let vendorSpUserData = {
      "n_ven_user": {
        "firstName": this.createVfirstName,
        "lastName": this.createVlastName,
        "email": this.emailIdInvite,
        "role_id": 7,
        "uservendoraccess": [
          {
            "vendorUserID": 0,
            "vendorCode": this.vendorCode,
            "entityID": entityIdArray,
            "vendorAccountID": null
          }
        ]
      },
      "n_cred": {
        "LogName": this.createUserName,
        "LogSecret": "string",
        "userID": 0
      }
    };
    this.sharedService.createVendorSuperUser(JSON.stringify(vendorSpUserData)).subscribe((data: any) => {
      this.messageService.add(this.addObject);
      this.displayAddUserDialog = false;
      this.createVfirstName = '';
      this.createVlastName = '';
      this.emailIdInvite = '';
      this.getVendorSuperUserList();
    }, error => {
      this.errorObject.detail = error.statusText;
      this.messageService.add(this.errorObject);
    })
  }

  getVendorSuperUserList() {
    this.sharedService.readVendorSuperUsersList().subscribe((data: any) => {
      let vendorUsersList = [];
      data.forEach(element => {
        let mergerdObject = {...element.AccessPermission,...element.AccessPermissionDef,...element.User,...element.Vendor}
        // mergerdObject.idVendorUserAccess = element.idVendorUserAccess;
        vendorUsersList.push(mergerdObject)
      });
      this.vendorAdminReadData = vendorUsersList;
      if (this.vendorAdminReadData.length > 10) {
        this.showPaginatorSp = true;
      }
    })
  }
  resetPassword() {
    this.deleteBtnText = "Are you sure you want to Reset this Account?";
    this.vendorResetBtnBoolean = false;
    this.userResetBtnBoolean = true;
    this.deactivateBoolean = false;
    this.deleteRoleBoolean = false;
    this.displayResponsive = true;
  }
  resetPasswordUserAPI() {
    this.sharedService.resetPassword(this.userEmail).subscribe((data: any) => {
      this.displayResponsive = false;
      this.addObject.detail = data.result;
      this.errorObject.detail = data.result;
      if (data.result != 'failed mail') {
        this.messageService.add(this.addObject);
        this.displayResponsive = false;
        this.DisplayCustomerUserDetails();
      } else {
        this.messageService.add(this.errorObject);
      }
    }, error => {
      this.errorObject.detail = error.statusText;
      this.messageService.add(this.errorObject);
    });
  }
  resetPasswordVendor(mail) {
    this.deleteBtnText = "Are you sure you want to Reset this Account?";
    this.displayResponsive = true;
    this.vendorResetBtnBoolean = true;
    this.userResetBtnBoolean = false;
    this.deactivateBoolean = false;
    this.deleteRoleBoolean = false;
    this.resetVendorMail = mail;
  }

  resetPassVendorAPI() {
    this.sharedService.resetPassword(this.resetVendorMail).subscribe((data: any) => {
      this.addObject.detail = data.result;
      this.errorObject.detail = data.result;
      if (data.result != 'failed mail') {
        this.messageService.add(this.addObject);
        this.displayResponsive = false;
        this.getVendorSuperUserList();
      } else {
        this.messageService.add(this.errorObject);
      }
    }, error => {
      this.errorObject.detail = error.statusText;
      this.messageService.add(this.errorObject);
    });
  }

  confirmationPopUp(id,text) {
    this.deleteBtnText = `Are you sure you want to ${text} this Account?`;
    this.deactivateBoolean = true;
    this.deleteRoleBoolean = false;
    this.vendorResetBtnBoolean = false;
    this.userResetBtnBoolean = false;
    this.displayResponsive = true;
    this.custuserid = id;
  }

  activa_deactive() {
    this.sharedService.activate_deactivate(this.custuserid).subscribe((data: any) => {
      this.addObject.detail = data.result;
      this.messageService.add(this.addObject);
      this.displayResponsive = false;
      this.custuserid = null;
      this.DisplayCustomerUserDetails();
      this.getVendorSuperUserList();
    }, error => {
      this.errorObject.detail = error.statusText;
      this.messageService.add(this.errorObject);
    })
  }
  paginate(event,type){
    console.log(event)
    if(type == 'vendor'){
      this.row_vendor = event.rows;
      this.first_vendor = event.first;
    } else {
      this.row_customer = event.rows;
      this.first_cust = event.first;
    }
  }
}
