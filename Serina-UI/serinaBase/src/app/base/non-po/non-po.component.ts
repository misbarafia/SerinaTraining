import { TaggingService } from './../../services/tagging.service';
import { element } from 'protractor';
import { SharedService } from 'src/app/services/shared.service';
import { Component, OnInit, ViewChild, AfterViewInit } from '@angular/core';
import { ControlContainer, FormArray, FormBuilder, FormControl, FormGroup, FormGroupDirective, Validators } from '@angular/forms';
import { ActivatedRoute, Router, UrlSegment } from '@angular/router';
import { DatePipe, Location } from '@angular/common';
import { NgxSpinnerService } from "ngx-spinner";
import {
  ConfirmationService,
  MessageService,
  PrimeNGConfig
} from "primeng/api";
import { PermissionService } from 'src/app/services/permission.service';


export interface UserData {
  name: string;
  uploaded: string;
  lastModified: string;
  status: string;
  emailId: string;
  id: string;
}
export function matcherFunction(url: UrlSegment[]) {
  if (url.length == 1) {
      const path = url[0].path;
       if(path.startsWith('invoice') 
         || path.startsWith('accountDetails') 
         || path.startsWith('itemList')
         || path.startsWith('spDetails') ){
        return {consumed: url};
      }
  }
  return null;
}

@Component({
  selector: 'app-non-po',
  templateUrl: './non-po.component.html',
  styleUrls: ['./non-po.component.scss']
})
export class NonPoComponent implements OnInit, AfterViewInit {
  viewType= 'invoice'
  users: UserData[] ;

  openFilter: boolean = false;

  selectedVender: string;
  selectedVenderPriceList: any;
  selectedCountry: any;

  selectedCustomer: string;
  venderdetails: any;
  initialViewVendor: boolean;
  vendorList: boolean;
  createSp: boolean;
  createspAccount: boolean = false;

  AddspName: string;
  erpsCode: any;
  LocationSp: any;
  addressSp: any;

  LocationCode;
  spName;
  citySp;
  countrysp;

  providerDetailsForm: FormGroup;
  accounts: FormArray;
  costAllocation: FormArray;
  submitted = false;
  savedatabooleansp: boolean
  first = 0;

  rows = 10;

  p1: number = 1;
  last: number;
  mergedData: any[];
  finalArray = [];
  serviceproviderreaddata: Object;
  spbyidreaddata: Object;
  spaccountreaddata: Object;
  showPaginator: boolean;
  spAccountname: any;
  spinvoicereaddata: Object;
  SpAccountDatails: FormGroup;
  addSpAccountBoolean: boolean;
  EditSpAccountBoolean: boolean;

  entityList: any[];
  entityBodyList: any[];
  entityDeptList: any[];

  editable: boolean = false;
  savebooleansp = false;

  spUpdateName: string = '';
  spUpdateCity: string = '';
  spUpdateCountry: string = '';
  spUpdateLocationCode: string = '';
  spUpdateEmail: string = '';
  spUpdateContact: string = '';
  spUpdateCompany: string = '';
  spUpdatezipcode: string = '';
  spUpdatePhone: string = '';
  spUpdateAddress: string = '';

  selectedEntityId: number;
  selectedEntityBodyId: number;
  selectedEntityDeptId: number;
  previousAccountData: any;

  activerow:string;

  someParameterValue = null;
  displayAddspDialog:boolean;

  errorObject ={
    severity: "error",
    summary: "error",
    detail: "Something went wrong"
  }
  addObject = {
    severity: "info",
    summary: "Added",
    detail: "Created Successfully"
  }
  updateObject ={
    severity: "info",
    summary: "Updated",
    detail: "Updated Successfully"
  }


  constructor(private fb: FormBuilder,
    private route: Router,
    public routeIn: ActivatedRoute,
    private confirmationService: ConfirmationService,
    private tagService:TaggingService,
    private messageService: MessageService,
    private sharedService: SharedService,
    private SpinnerService: NgxSpinnerService,
    private datePipe: DatePipe,
    private permissionService : PermissionService,
    private _location : Location,
    private router :Router,
    private primengConfig: PrimeNGConfig) {

      // if (this.route.url.endsWith('serviceProvider/invoice')) {
      //   this.viewType = 'invoice';
      // } else if (this.route.url.endsWith('serviceProvider/accountDetails')) {
      //   this.viewType = 'accountDetails'
      // } else if (this.route.url.endsWith('serviceProvider/itemList')) {
      //   this.viewType = 'itemList'
      // } else if (this.route.url.endsWith('serviceProvider/spDetails')) {
      //   this.viewType = 'spDetails'
      // } 

      // this.routeIn.url.subscribe(params => {
      //   console.log(params[0].path);
      // })
  }

  ngOnInit(): void {
    if(this.permissionService.vendor_SP_PageAccess == true){
      this.initialViewVendor = this.sharedService.initialViewSpBoolean;
      this.vendorList = this.sharedService.spListBoolean;
      this.venderdetails = this.sharedService.spDetailsArray;
      this.primengConfig.ripple = true;
      this.DisplayServiceProviderDetails();
      this.toGetEntity();
      if(this.initialViewVendor == false){
        // this.DisplayspAccountDetails();
        // this.DisplaySpDetailsById();
        // this.DisplaySpInvoice();
      }
    } else{
      alert("Sorry!, you do not have access");
      this.router.navigate(['customer/invoice/allInvoices'])
    }
    
  }


  ngAfterViewInit() {


  }

  submitAccountdata() {
  }
  toCreateNew() {
    this.vendorList = false;
    this.sharedService.spListBoolean = false;
    this.savedatabooleansp = true;
  }
  toCreateNewAccount() {
    this.vendorList = false;
    this.sharedService.spListBoolean = false;
    this.createspAccount = true;
    this.addSpAccountBoolean = true;
    this.EditSpAccountBoolean = false;
  }
  viewFullDetails(e) {
    // this.route.navigate([`/customer/serviceProvider/SpDetails/${e.idServiceProvider}`])
    // this.activerow = "activeSp";
    this.sharedService.initialViewSpBoolean = false
    this.initialViewVendor = this.sharedService.initialViewSpBoolean;
    // this.sharedService.vendorFullDetails = e;
    this.venderdetails = e;
    this.sharedService.spDetailsArray = e;
    this.sharedService.spID = e.idServiceProvider;
    // this.DisplayspAccountDetails();
    // this.DisplaySpDetailsById();
    // this.DisplaySpInvoice();

  }
  colseDiv() {
    this.sharedService.initialViewSpBoolean = true;
    this.initialViewVendor = this.sharedService.initialViewSpBoolean;
  }
  getDisplayInitialBoolean(value){
    this.initialViewVendor = value;
    if(value === true){
      this.ngOnInit();
    }
  }
  displayAddspDialogmethod(value){
    this.displayAddspDialog = value;
  }

  get f() { return this.providerDetailsForm.controls; }

  onEdit() {
    this.editable = true;
    this.savebooleansp = true;
  }
  onCancelAccount() {
    this.vendorList = true;
    this.sharedService.spListBoolean = true;
    this.createspAccount = false;
    this.SpAccountDatails.reset();
  }
  onCancel() {
    this.editable = false;
    this.savebooleansp = false;
    // this.initialViewVendor = true;
    // this.vendorList = true;
    // this.createspAccount = false;
    // this.SpAccountDatails.reset();
  }
  DisplayServiceProviderDetails() {
    this.SpinnerService.show();
    this.sharedService.readserviceprovider().subscribe((data:any) => {

      let mergerdArray = [];
      data.forEach(element => {
        let spData = {...element.Entity,...element.ServiceProvider};
        mergerdArray.push(spData);
      });
      this.serviceproviderreaddata = mergerdArray;
      this.SpinnerService.hide();
      var res = [];
      for (var x in this.serviceproviderreaddata) {
        this.serviceproviderreaddata.hasOwnProperty(x) && res.push(this.serviceproviderreaddata[x])
      }
      if (res.length > 10) {
        this.showPaginator = true;
      }
    }, err =>{
      this.SpinnerService.hide();
    })
  }
  // DisplayspAccountDetails() {
  //   this.spaccountreaddata = [];
  //   this.finalArray = []
  //   this.SpinnerService.show();
  //   this.sharedService.readserviceprovideraccount().subscribe((data: any) => {
  //     data.forEach(element => {
  //       this.mergedData = { ...element.AccountCostAllocation, ...element.Credentials, ...element.Entity, ...element.EntityBody, ...element.ServiceAccount };
  //       this.finalArray.push(this.mergedData)
  //     });
  //     this.spaccountreaddata = this.finalArray;
  //     this.SpinnerService.hide();
  //   })
  // }
  // DisplaySpDetailsById() {
  //   this.SpinnerService.show();
  //   this.sharedService.readserviceproviderbyid().subscribe((data) => {
  //     this.spbyidreaddata = data;
  //     this.spUpdateName = data[0].ServiceProviderName;
  //     this.spUpdateCity = data[0].City;
  //     this.spUpdateCountry = data[0].Country;
  //     this.spUpdateLocationCode = data[0].LocationCode;
  //     this.spUpdateEmail,
  //       this.spUpdateContact,
  //       this.spUpdateCompany = data[0].ServiceProviderName;
  //     this.spUpdatezipcode,
  //       this.spUpdatePhone,
  //       this.spUpdateAddress
  //     this.SpinnerService.hide();
  //   })
  // }

  createNewSp() {
    let newSpData = {
      "ServiceProviderName": this.AddspName,
      "ServiceProviderCode": this.erpsCode,
      "City": this.citySp,
      "Country": this.countrysp,
      "LocationCode": this.LocationSp
    }
    this.sharedService.createserviceprovider(JSON.stringify(newSpData)).subscribe((data) => {
      if (data.result == 'saved to db') {
        this.messageService.add(this.addObject);
        // this.vendorList=true;
        this.DisplayServiceProviderDetails();
        // this.DisplaySpDetailsById();
        // this.venderdetails = data.record.ServiceProviderName;
        this.displayAddspDialog = false;
      } else {
        this.messageService.add(this.errorObject);
      }
    });
  }

  toGetEntity() {
    this.entityList = [];
    this.sharedService.getEntityDept().subscribe((data: any) => {
      this.entityList = data;
    })
  }




}
