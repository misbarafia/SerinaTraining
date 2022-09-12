import { Component, Input, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { MessageService } from 'primeng/api';
import { SharedService } from 'src/app/services/shared.service';


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
  selector: 'app-edit-user',
  templateUrl: './edit-user.component.html',
  styleUrls: ['./edit-user.component.scss','../roles.component.scss']
})
export class EditUserComponent implements OnInit {
  @Input() DisplayRoleName: any[];
  @Input() editedUserData;
  userName: string;
  userEmail: string;
  editRoleName: string;
  Flevel: number;
  appied_permission_def_id: number;

  selectedEntityName;
  selectedEntityBodyName;
  selectedEntityDeptName;

  selectedEntityBody: any;
  selectedEntityDept: any;
  entityList: any;
  selectedEntityId: any;
  entityBodyList: any[];
  entityDeptList: any;

  filteredEntities: any[];

  dEntityBody: dropdownData[] = [];
  dEntityDept: dropdownData[] = [];
  filterDentityBody: any[] = [];
  filterDentityDept: any[] = [];
  updateUserEnt_body_id:number;
  updateUserEnt_dept_id:number;
  selectedEntitys: selectedValue[] = [];
  updateUsersEntityInfo: updateUserEntityData[] = [];

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
  constructor(private messageService: MessageService,
    private sharedService: SharedService,
    private router: Router) { }

  ngOnInit(): void {
    this.getEditUserDetails(this.sharedService.editedUserData);
  }
  getEditUserDetails(value) {
    // this.router.navigate(['/customer/roles',`${value.User.idUser}editUser`]);
    console.log(value)
    this.sharedService.cuserID = value.User.idUser
    // this.normalRole = false;
    // this.CreateNewRole = false;
    // this.editUserdata = true;
    this.userName = value.User.UserName;
    this.userEmail = value.User.email;
    // this.userCode = value.UserCode
    // this.designation = value.Designation;
    this.editRoleName = value.AccessPermissionDef.NameOfRole;
    this.Flevel = value.AmountApproveLevel.MaxAmount
    

    this.sharedService.readEntityUserData(value.User.idUser).subscribe((data:any)=>{
      console.log(data)
      data.forEach(element => {
        if( !element.EntityBody && !element.Department){
          this.selectedEntitys.push({entity:element.Entity.EntityName, entityBody:element.EntityBody, entityDept:element.Department,idUserAccess:element.UserAccess.idUserAccess , EntityID:element.Entity.idEntity, EntityBodyID:element.EntityBody, DepartmentID:element.Department});
          // this.updateEntityUserDummy.push({idUserAccess:element.UserAccess.idUserAccess, EntityID:element.Entity.idEntity, EntityBodyID:element.EntityBody, DepartmentID:element.Department});
        }
        else if( !element.Department){
          this.selectedEntitys.push({entity:element.Entity.EntityName, entityBody:element.EntityBody.EntityBodyName, entityDept:element.Department,idUserAccess:element.UserAccess.idUserAccess , EntityID:element.Entity.idEntity, EntityBodyID:element.EntityBody.idEntityBody, DepartmentID:element.Department});
          // this.updateEntityUserDummy.push({idUserAccess:element.UserAccess.idUserAccess, EntityID:element.Entity.idEntity, EntityBodyID:element.EntityBody.idEntityBody, DepartmentID:element.Department});
        }
        
        else{
          this.selectedEntitys.push({entity:element.Entity.EntityName, entityBody:element.EntityBody.EntityBodyName, entityDept:element.Department.DepartmentName,idUserAccess:element.UserAccess.idUserAccess , EntityID:element.Entity.idEntity, EntityBodyID:element.EntityBody.idEntityBody, DepartmentID:element.Department.idDepartment});
          // this.updateEntityUserDummy.push({idUserAccess:element.UserAccess.idUserAccess, EntityID:element.Entity.idEntity, EntityBodyID:element.EntityBody.idEntityBody, DepartmentID:element.Department.idDepartment});
        }
       
      });
    })
  }
  selectRole(e) {
    let item = this.DisplayRoleName.filter((item) => {
      return e.indexOf(item.NameOfRole) > -1;
    })
    this.appied_permission_def_id = item[0].idAccessPermissionDef
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
        // let country = this.dEntityBody['value'][element];
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
    })
    this.selectedEntitys.push({ entity: value.EntityName, EntityID: value.idEntity });
    this.updateUsersEntityInfo.push({ idUserAccess: null, EntityID: value.idEntity })
    this.selectedEntityName = value.EntityName;
    console.log(this.updateUsersEntityInfo);
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

    // this.updateUsersEntityInfo.push({DepartmentID : e.idDepartment});
    this.updateUsersEntityInfo.forEach((value) => {
      if (value.EntityID == this.selectedEntityId && value.EntityBodyID == this.updateUserEnt_body_id && !value.DepartmentID) {
        value.DepartmentID = e.idDepartment;
        this.updateUserEnt_dept_id = e.idDepartment;
      }

    })
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
    console.log(this.updateUsersEntityInfo);
  }
  onRemove(index,value) {
    console.log(value);
    console.log(this.updateUsersEntityInfo);
     if(value.idUserAccess){
      this.updateUsersEntityInfo
      .push({ idUserAccess: value.idUserAccess,
              EntityID: value.EntityID,
              EntityBodyID: value.EntityBodyID, 
              DepartmentID: value.DepartmentID
            })
     } else{
       let Ent_id = value.EntityID ? value.EntityID : null
       let Ent_body_id =  value.EntityBodyID ? value.EntityBodyID : null;
       let Ent_dept_id =  value.DepartmentID ? value.DepartmentID : null;
       console.log(Ent_id,Ent_body_id,Ent_dept_id);
       this.updateUsersEntityInfo.forEach((element,index)=>{
         if(Ent_id  && Ent_body_id && Ent_dept_id){
          if(element.EntityID == Ent_id && element.EntityBodyID == Ent_body_id && element.DepartmentID == Ent_dept_id ){
            this.updateUsersEntityInfo.splice(index,1);
          }
         } else if (Ent_id  && Ent_body_id){
          if(element.EntityID == Ent_id && element.EntityBodyID == Ent_body_id ){
            this.updateUsersEntityInfo.splice(index,1);
          }
         }
         else{
          if(element.EntityID == Ent_id){
            this.updateUsersEntityInfo.splice(index,1);
          }
         }
       })
      
     }
  
      this.selectedEntitys.splice(index, 1);
              console.log(this.updateUsersEntityInfo);
    }

    UpdateUser() {
      let editUser = {
        "up_cred": {
          "LogName": this.userName,
          "LogSecret": "string"
        },
        "u_cust": {
          "User": {
            "UserName": this.userName,
            // "UserCode": "string",
            // "Designation": "string",
            "email": this.userEmail
          },
          "userentityaccess": this.updateUsersEntityInfo
        }
      }
      this.sharedService.updatecustomeruser(JSON.stringify(editUser)).subscribe((data: any) => {
        if (data.Result == 'Updated') {
          const userData = data.customer_user_details
          let selectrole = {
            "applied_uid": this.sharedService.cuserID,
            "isUser": true,
            "appied_permission_def_id": this.appied_permission_def_id
          }
          console.log(selectrole);
          this.sharedService.editRole(JSON.stringify(selectrole)).subscribe((data: any) => { })
  
          let amountApproval = {
            "applied_uid": this.sharedService.cuserID,
            "isUser": true,
            "MaxAmount": this.Flevel
          }
  
          this.sharedService.newAmountApproval(JSON.stringify(amountApproval)).subscribe((data: any) => { })
          this.messageService.add(this.updateObject);
          this.ngOnInit();
        
          // this.normalRole = true;
          // this.CreateNewRole = false;
          // this.editUserdata = false;
          this.selectedEntitys=[];
          this.updateUsersEntityInfo = [];
        } else {
          this.messageService.add(this.errorObject);
        }
  
      }, error=>{
        alert(error.statusText)
      })
    }
    canceleditUser(){
      this.router.navigate(['/customer/roles']);
      this.selectedEntitys = [];
    }

}
