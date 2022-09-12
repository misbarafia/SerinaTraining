import { ImportExcelService } from './../../../services/importExcel/import-excel.service';
import { NonPoComponent } from './../non-po.component';

import { element } from 'protractor';
import { SharedService } from 'src/app/services/shared.service';
import {
  Component,
  OnInit,
  ViewChild,
  AfterViewInit,
  Input,
  Output,
  EventEmitter,
  OnDestroy,
} from '@angular/core';
import {
  ControlContainer,
  FormArray,
  FormBuilder,
  FormControl,
  FormGroup,
  FormGroupDirective,
  Validators,
} from '@angular/forms';
import { ActivatedRoute, Router, UrlSegment } from '@angular/router';
import { DatePipe } from '@angular/common';
import * as FileSaver from 'file-saver';
import { NgxSpinnerService } from 'ngx-spinner';
import {
  ConfirmationService,
  MessageService,
  PrimeNGConfig,
} from 'primeng/api';
import { TaggingService } from 'src/app/services/tagging.service';
import { CdkDragDrop, moveItemInArray } from '@angular/cdk/drag-drop';
import { DataService } from 'src/app/services/dataStore/data.service';
import { MatSidenav } from '@angular/material/sidenav';

export interface UserData {
  name: string;
  uploaded: string;
  lastModified: string;
  status: string;
  emailId: string;
  id: string;
}
export interface costData {
  entityID: number;
  entityBodyID: number;
  departmentID: number;
  interco: string;
  description?: string;
  mainAccount: string;
  naturalAccountWater?: string;
  naturalAccountHousing?: string;
  costCenter: string;
  Element:string;
  project: string;
  product: string;
  segments: string,
  bsMovements: string,
  fixedAssetDepartment: string,
  fixedAssetGroup: string,
  elementFactor: number;
}
@Component({
  selector: 'app-sp-details',
  templateUrl: './sp-details.component.html',
  styleUrls: ['./sp-details.component.scss', './../non-po.component.scss'],
})
export class SpDetailsComponent implements OnInit, AfterViewInit, OnDestroy {
  initialViewVendor: boolean;
  // venderdetails;
  @Input() spDetails;
  @Input() spaccountreaddata;
  @Input() serviceproviderreaddata;
  @Input() spbyidreaddata;
  @Input() spinvoicereaddata;
  @Input() showPaginator;
  @Output() intialViewSp: EventEmitter<boolean> = new EventEmitter();
  @Output() displayAddspDialog: EventEmitter<boolean> = new EventEmitter();
  element_factor: number;
  viewType = 'invoice';
  users: UserData[];

  openFilter: boolean = false;

  selectedVender: string;
  selectedVenderPriceList: any;
  selectedCountry: any;

  selectedCustomer: string;

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

  accounts: FormArray;
  costAllocation: FormArray;
  submitted = false;
  savedatabooleansp: boolean;
  first = 0;

  rows = 10;

  p1: number = 1;
  last: number;
  mergedData: any[];
  finalArray = [];
  spAccountname: any;
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

  activerow: string;

  someParameterValue = null;
  // displayAddspDialog:boolean;

  displayAccountColumn = [
    'Account',
    'MeterNumber',
    'LocationCode',
    'EntityName',
    'EntityBodyName',
    'noOfInvoices',
    'noOfPo',
  ];
  items = ['item 1', 'item 2', 'item 3'];

  errorObject = {
    severity: 'error',
    summary: 'error',
    detail: 'Something went wrong',
  };
  addObject = {
    severity: 'info',
    summary: 'Added',
    detail: 'Created Successfully',
  };
  updateObject = {
    severity: 'info',
    summary: 'Updated',
    detail: 'Updated Successfully',
  };
  columnSPAccont: { field: string; header: string }[];
  visibleSPColumns: boolean;
  updateColumns: any;
  allSpInvoiceColumns: any;
  spInvoiceColumns: any[];
  columnstodisplaySpInvoice: any[];
  bgColorCode: any;
  source: string;
  EBS_costData: {};
  EDP_costData: {};
  CostArray: any[];
  mask: (string | RegExp)[];
  costBoolean: boolean;
  allSearchInvoiceString: any;
  disableCostAllocationBoolean: boolean;

  @ViewChild('sidenav') sidenav :MatSidenav;
  events: string[] = [];
  opened: boolean;
  filteredOP_unit: any[];
  OPUnits: any;
  close(reason: string) {
    console.log(reason)
    this.sidenav.close();
  }
  elementList = [];

  constructor(
    private fb: FormBuilder,
    private route: Router,
    public routeIn: ActivatedRoute,
    private ImportExcelService: ImportExcelService,
    private tagService: TaggingService,
    private messageService: MessageService,
    private sharedService: SharedService,
    private SpinnerService: NgxSpinnerService,
    private storageService: DataService,
    private datePipe: DatePipe,
    private primengConfig: PrimeNGConfig
  ) {
    routeIn.params.subscribe((params) => {
      this.setupComponent(params['someParam']);
    });
  }

  ngOnInit(): void {
    this.toGetEntity();
    this.bgColorCode = this.storageService.bgColorCode;
    this.initialViewVendor = this.sharedService.initialViewSpBoolean;
    this.vendorList = this.sharedService.spListBoolean;
    this.spDetails = this.sharedService.spDetailsArray;
    this.SpAccountDatails = this.initialForm();
    this.primengConfig.ripple = true;
    // this.DisplayServiceProviderDetails();
    
    this.prepareCostData();
    // this.viewFullDetails(e);
    this.DisplayspAccountDetails();
    this.DisplaySpDetailsById();
    this.DisplaySpInvoice();
    this.readColumnsSpInvoice();
    this.Inputmask();
    this.getElementData(this.spDetails);
    this.getOPunits();
  }
  Inputmask() {
    this.columnSPAccont = [
      { field: 'Account', header: 'A/c No' },
      // { field: 'MeterNumber', header: 'Meter Number' },
      // { field: 'LocationCode', header: 'Location Code' },
      { field: 'EntityName', header: 'Entity' },
      // { field: 'EntityBodyName', header: 'Entity site' },
      // { field: 'noOfInvoices', header: 'Narrative' },
      { field: 'downloadDate', header: 'Download Date' },
    ];
    this.mask = [
      /\d/,
      /\d/,
      '-',
      /\d/,
      /\d/,
      /\d/,
      /\d/,
      '-',
      /\d/,
      /\d/,
      '-',
      /\d/,
      /\d/,
      '-',
      /\d/,
      /\d/,
      /\d/,
      /\d/,
      /\d/,
      /\d/,
      '-',
      /\d/,
      /\d/,
      '-',
      /\d/,
      /\d/,
      /\d/,
    ];
  }
  setupComponent(someParam) {
    this.someParameterValue = someParam;
  }
  initialForm() {
    console.log(this.spDetails)
    return this.fb.group({
      entityID: [{ value: this.spDetails.idEntity, disabled: true }],
      serviceProviderNameAccount: [
        { value: this.spDetails.ServiceProviderName, disabled: true },
      ],
      Email: [''],
      UserName: ['', Validators.required],
      LogSecret: ['', Validators.required],
      URL: ['', Validators.required],
      subKeyWords: [''],
      Account: ['', Validators.required],
      MeterNumber: [''],
      Address: '',
      ScheduleDateTime: Date,
      isActive: [true],
      LocationCode: ['', Validators.required],
      operatingUnit: '',
      costDetails: this.fb.array([]),
    });
  }
  get f() {
    return this.SpAccountDatails.controls;
  }
  // add account
  acDetails(): FormArray {
    return this.SpAccountDatails.get('acDetails') as FormArray;
  }

  newacDetails(): FormGroup {
    return this.fb.group({
      Account: ['', Validators.required],
      MeterNumber: ['', Validators.required],
      LocationCode: ['', Validators.required],
      Address: '',
      day: '',
    });
  }

  addacDetails() {
    if (this.addSpAccountBoolean == true) {
      this.submitted = true;
      this.acDetails().push(this.newacDetails());
    } else {
      this.acDetails().push(this.newacDetails());
    }
  }

  removeQuantity(i: number) {
    this.acDetails().removeAt(i);
  }

  // add cost details
  costDetails(): FormArray {
    return this.SpAccountDatails.get('costDetails') as FormArray;
  }
  prepareCostData() {
    this.EBS_costData = {
      entityBodyID: ['', Validators.required],
      costCenter: ['', Validators.required],
      project: '',
      departmentID: [''],
      elementFactor: [''],
      interco: [''],
      mainAccount: ['', Validators.required],
      isActive_Alloc: [1],
      naturalAccountWater: '',
      naturalAccountHousing: '',
      product: '',
      segments: [''],
      bsMovements: [''],
      fixedAssetDepartment: [''],
      fixedAssetGroup: [''],
      Element: ['', Validators.required],
    };
    this.EDP_costData = {
      entityBodyID: ['', Validators.required],
      costCenter: ['', Validators.required],
      project: '',
      departmentID: [''],
      elementFactor: [''],
      interco: [''],
      isActive_Alloc: [1],
      mainAccount: ['', Validators.required],
      segments: '',
      bsMovements: '',
      fixedAssetDepartment: '',
      fixedAssetGroup: '',
      product: '',
      Element: ['', Validators.required],
    };
  }

  newcostDetails(): FormGroup {
    if (this.source == ('EBS' || 'ebs')) {
      return this.fb.group(this.EBS_costData);
    } else {
      return this.fb.group(this.EDP_costData);
    }
  }

  addcostDetails() {
    // stop here if form is invalid
    // if (this.SpAccountDatails.invalid) {
    //   this.errorObject.detail = "Please add required fields"
    //   this.messageService.add(this.errorObject);
    //   return;
    // }
    this.costBoolean = true;
    this.costDetails().push(this.newcostDetails());
  }

  removecostDetails(i: number) {
    if (confirm('Are you sure you want to delete!')) {
      this.costDetails().removeAt(i);
    }
  }

  handleChange(input) {
    if (input.value < 0) input.value = 0;
    if (input.value > 100) input.value = 100;
  }

  ngAfterViewInit() {}

  submitAccountdata() {}

  toCreateNew() {
    this.vendorList = false;
    this.sharedService.spListBoolean = false;
    this.savedatabooleansp = true;
  }

  toCreateNewAccount() {
    if(this.spDetails.idServiceProvider == 14){
      this.disableCostAllocationBoolean = true;
    } else {
      this.disableCostAllocationBoolean = false;
    }
    this.vendorList = false;
    this.createspAccount = true;
    this.addSpAccountBoolean = true;
    this.EditSpAccountBoolean = false;
    this.SpAccountDatails.patchValue({
      serviceProviderNameAccount: this.spDetails.ServiceProviderName,
      serviceProviderID: this.sharedService.spID,
      entityID : this.spDetails.idEntity,
      isActive: true,
    });
    this.selectedEntity(this.spDetails.idEntity);
  }

  viewFullDetails(e) {
    this.initialViewVendor = false;
    this.spDetails = e;
    this.sharedService.spDetailsArray = e;
    this.sharedService.spID = e.idServiceProvider;
    this.DisplayspAccountDetails();
    this.DisplaySpDetailsById();
    this.DisplaySpInvoice();
    this.getElementData(e);
  }

  getElementData(e){
    if((e.ServiceProviderName =='Dubai Electricity & Water Authority') || e.ServiceProviderName =='DUBAI ELECTRICITY AND WATER AUTHORITY'){
      this.elementList = [
        { id: 1, name: 'Water'},
        { id: 2, name: 'Electricity'},
        { id: 3, name: 'Housing'},
        { id: 4, name: 'Sewerage'},
        { id: 5, name: 'Others'},
      ]
    } else if(e.ServiceProviderName =='EMIRATES INTEGRATED TELECOMMUNICATIONS PJSC(DU)'){
      this.elementList = [
        { id: 1, name: 'Usage charges'},
        { id: 2, name: 'Monthly Fixed Charges'},
        { id: 3, name: 'TV Channels'},
        { id: 4, name: 'Others'}
      ]
    } else if(e.ServiceProviderName =='ETISALAT'){
      this.elementList = [
        { id: 1, name: 'Usage_Credit'},
        { id: 2, name: 'International_Calls'},
        { id: 3, name: 'Others'}
      ]
    } else {
      this.elementList = [
        { id: 1, name: 'Others'}
      ]
    }
  }

  colseDiv() {
    this.sharedService.initialViewSpBoolean = true;
    this.route.navigate(['/customer/serviceProvider']);
    this.initialViewVendor = this.sharedService.initialViewSpBoolean;
    this.intialViewSp.emit(true);
  }

  // get f() { return this.providerDetailsForm.controls; }

  onEdit() {
    this.editable = true;
    this.savebooleansp = true;
  }

  onCancelAccount() {
    this.vendorList = true;
    // this.sharedService.spListBoolean = true;
    this.createspAccount = false;
    this.submitted = false;
    this.SpAccountDatails = this.initialForm();
    this.SpAccountDatails.reset();
  }

  onCancel() {
    this.editable = false;
    this.savebooleansp = false;
  }

  DisplayServiceProviderDetails() {
    this.SpinnerService.show();
    this.sharedService.readserviceprovider().subscribe((data) => {
      this.serviceproviderreaddata = data;
      this.SpinnerService.hide();
      const res = [];
      for (var x in this.serviceproviderreaddata) {
        this.serviceproviderreaddata.hasOwnProperty(x) &&
          res.push(this.serviceproviderreaddata[x]);
      }
      if (res.length > 10) {
        this.showPaginator = true;
      }
    });
  }
  DisplayspAccountDetails() {
    this.spaccountreaddata = [];
    this.finalArray = [];
    this.SpinnerService.show();
    this.sharedService.readserviceprovideraccount().subscribe((data: any) => {
      data.forEach((element) => {
        this.mergedData = {
          ...element.Credentials,
          ...element.Entity,
          ...element.EntityBody,
          ...element.ServiceAccount,
        };
        this.finalArray.push(this.mergedData);
      });
      this.spaccountreaddata = this.finalArray;
      this.SpinnerService.hide();
    });
  }
  DisplaySpDetailsById() {
    this.SpinnerService.show();
    this.sharedService.readserviceproviderbyid().subscribe((data) => {
      this.spbyidreaddata = data;
      this.spUpdateName = data[0].ServiceProviderName;
      this.spUpdateCity = data[0].City;
      this.spUpdateCountry = data[0].Country;
      this.spUpdateLocationCode = data[0].LocationCode;
      this.spUpdateCompany = data[0].ServiceProviderName;
      this.SpinnerService.hide();
    });
  }

  updatesp() {
    let updatedSpData = {
      ServiceProviderName: this.spUpdateName,
      ServiceProviderCode: this.sharedService.spID,
      City: this.spUpdateCity,
      Country: this.spUpdateCountry,
      LocationCode: this.spUpdateLocationCode,
    };
    this.sharedService
      .updateserviceprovider(JSON.stringify(updatedSpData))
      .subscribe((data) => {
        if (data.result == 'Updated') {
          // this.venderdetails = data.record.ServiceProviderName;
          this.messageService.add(this.updateObject);
          this.vendorList = true;
          this.sharedService.spListBoolean = true;
          this.DisplayServiceProviderDetails();
          this.DisplaySpDetailsById();
          this.editable = false;
          this.savebooleansp = false;
        } else {
          this.messageService.add(this.errorObject);
        }
      });
  }

  quickAdd() {
    // this.SpAccountDatails = this.initialForm();
    this.SpAccountDatails.reset();
    this.SpAccountDatails.patchValue({
      serviceProviderNameAccount: this.spDetails.ServiceProviderName,
      serviceProviderID: this.sharedService.spID,
    });
  }

  toCreateNewSPAccount() {
    let sp_acct = {
      Account: this.SpAccountDatails.value.Account,
      entityID: +this.SpAccountDatails.value.entityID,
      Email: this.SpAccountDatails.value.Email || '',
      MeterNumber: this.SpAccountDatails.value.MeterNumber || '',
      LocationCode: this.SpAccountDatails.value.LocationCode,
      Address: this.SpAccountDatails.value.Address || '',
      operatingUnit: this.SpAccountDatails.value.operatingUnit || '',
      isActive: this.SpAccountDatails.value.isActive,
    };
    let sp_shed = {
      ScheduleDateTime: this.SpAccountDatails.value.ScheduleDateTime,
    };
    let sp_cred = {
      UserName: this.SpAccountDatails.value.UserName,
      LogSecret: this.SpAccountDatails.value.LogSecret,
      URL: this.SpAccountDatails.value.URL,
      entityID: +this.SpAccountDatails.value.entityID,
    };
    if (this.addSpAccountBoolean) {
      let costDetailsData = [];
      let elmentArray = [];
      this.SpAccountDatails.value.costDetails.forEach((element, index) => {
        element.entityBodyID = +element.entityBodyID;
        if (element.departmentID != null) {
          element.departmentID = +element.departmentID;
        }
        element.elementFactor = +element.elementFactor;

        elmentArray.push(element.elementFactor);
        let costObject = element;
        costObject.entityID = +this.SpAccountDatails.value.entityID;
        costDetailsData.push(costObject);
      });
      let ele_fact = elmentArray.reduce((a, b) => a + b, 0);

      let spAcountdata = {
        n_sp_acc: sp_acct,
        n_sp_sched: sp_shed,
        n_sp_cst: costDetailsData,
        n_cred: sp_cred,
      };
      // if (ele_fact == 100) {
      this.sharedService
        .createserviceprovideraccount(JSON.stringify(spAcountdata))
        .subscribe(
          (data: any) => {
            this.messageService.add(this.addObject);
            this.vendorList = true;
            this.createspAccount = false;
            this.DisplayspAccountDetails();
            this.SpAccountDatails = this.initialForm();
            this.accounts = new FormArray([]);
            this.costAllocation = new FormArray([]);
            this.SpAccountDatails.reset();
          },
          (error) => {
            this.messageService.add(this.errorObject);
          }
        );
      // } else {
      //   this.errorObject.detail = "Please add element factor properly"
      //   this.messageService.add(this.errorObject);
      // }
    }
    if (this.EditSpAccountBoolean) {
      let costDetailsData = [];
      let u_elmentArray = [];
      this.SpAccountDatails.value.costDetails.forEach((element, index) => {
        const { entityBodyID, departmentID, elementFactor } = element;
        element.entityBodyID = +entityBodyID;
        if (element.departmentID != null) {
          element.departmentID = +departmentID;
        }
        element.elementFactor = +elementFactor;
        u_elmentArray.push(element.elementFactor);
        let u_costObject = element;
        u_costObject.entityID = +this.SpAccountDatails.value.entityID;
        if (index < this.CostArray.length) {
          u_costObject.idAccountCostAllocation =
            this.CostArray[index].idAccountCostAllocation;
        } else {
          u_costObject.idAccountCostAllocation = null;
        }
        costDetailsData.push(u_costObject);
      });
      let u_ele_fact = u_elmentArray.reduce((a, b) => a + b, 0);
      // sp_acct['isActive'] = this.SpAccountDatails.value.isActive;
      let spUpdateAcountdata = {
        u_sp_acc: sp_acct,
        u_sp_sch: sp_shed,
        u_sp_cst_aloc: costDetailsData,
        u_cred: sp_cred,
      };
      // if (u_ele_fact == 100) {
      this.sharedService
        .updateSpAccount(JSON.stringify(spUpdateAcountdata))
        .subscribe(
          (data) => {
            this.messageService.add(this.updateObject);
            this.vendorList = true;
            this.createspAccount = false;
            this.DisplayspAccountDetails();
            this.SpAccountDatails = this.initialForm();
            this.accounts = new FormArray([]);
            this.costAllocation = new FormArray([]);
            this.SpAccountDatails.reset();
          },
          (error) => {
            this.messageService.add(this.errorObject);
          }
        );
      // } else {
      //   this.errorObject.detail = "Please add element factor properly"
      //   this.messageService.add(this.errorObject);
      // }
    }
  }

  updateSpAccount(data) {
    if(data.serviceProviderID == 14){
      this.disableCostAllocationBoolean = true;
    } else {
      this.disableCostAllocationBoolean = false;
    }
    this.sharedService.spAccountID = data.idServiceAccount;
    this.selectedEntityBodyId = data.entityBodyID;
    this.selectedEntityDeptId = data.departmentID;
    this.previousAccountData = data;

    if (data.EntityName) {
      this.selectedEntity(data.entityID);
      if (data.EntityBodyName) {
        this.selectedEntityBody(data.idEntityBody);
      }
    }

    this.entityBodyList = [];
    this.entityDeptList = [];

    let _cost;
    this.CostArray = [];
    data.account_cost.forEach((element) => {
      this.addcostDetails();
      const {
        entityBodyID,
        costCenter,
        project,
        departmentID,
        elementFactor,
        interco,
        mainAccount,
        segments,
        bsMovements,
        fixedAssetDepartment,
        fixedAssetGroup,
        naturalAccountWater,
        naturalAccountHousing,
        product,
        idAccountCostAllocation,
        isActive_Alloc,
        Element
      } = element.AccountCostAllocation;
      _cost = {
        entityBodyID: entityBodyID,
        costCenter: costCenter,
        project: project,
        Element: Element,
        elementFactor: elementFactor,
        interco: interco,
        mainAccount: mainAccount,
        naturalAccountWater: naturalAccountWater,
        naturalAccountHousing: naturalAccountHousing,
        product: product,
        segments: segments,
        bsMovements: bsMovements,
        fixedAssetDepartment: fixedAssetDepartment,
        fixedAssetGroup: fixedAssetGroup,
        isActive_Alloc: isActive_Alloc,
        idAccountCostAllocation: idAccountCostAllocation,
      };
      this.CostArray.push(_cost);
    });

    const FindSpName = this.serviceproviderreaddata.filter((element) => {
      return element.idServiceProvider == data.serviceProviderID;
    });
    if (data.isActive == 1) {
      this.SpAccountDatails.enable();
    } else {
      this.SpAccountDatails.disable();
    }
    this.SpAccountDatails.controls['isActive'].enable();
    // this.SpAccountDatails.controls['Account'].disable();
    this.SpAccountDatails.patchValue({
      Account: data.Account,
      entityID: data.entityID,
      serviceProviderNameAccount: FindSpName[0].ServiceProviderName,
      serviceProviderID: data.serviceProviderID,
      Email: data.Email,
      URL: data.URL,
      UserName: data.UserName,
      LogSecret: data.LogSecret,
      ScheduleDateTime: this.datePipe.transform(
        data.account_schedule.ScheduleDateTime,
        'yyyy-MM-dd'
      ),
      MeterNumber: data.MeterNumber,
      LocationCode: data.LocationCode,
      Address: data.Address,
      operatingUnit: data.operatingUnit,
      isActive: data.isActive,
      costDetails: this.CostArray,
    });

    this.vendorList = false;
    // this.sharedService.spListBoolean = false;
    this.createspAccount = true;
    this.addSpAccountBoolean = false;
    this.EditSpAccountBoolean = true;
  }

  accontAtiveToggle(val) {
    if (val === false) {
      this.SpAccountDatails.disable();
    } else {
      this.SpAccountDatails.enable();
    }
    this.SpAccountDatails.controls['isActive'].enable();
    // this.SpAccountDatails.controls['Account'].disable();
  }

  getOPunits(){
    this.sharedService.readOPUnits().subscribe((data:any)=>{
      this.OPUnits = data;
    })
  }

  selectOP_unit(event){

  }

  filterOP_unit(event){
    // let filtered: any[] = [];
    // let query = event.query;
    // for (let i = 0; i < this.entityList.length; i++) {
    //   let OPunits = this.entityList[i];
    //   if (OPunits.EntityName.toLowerCase().indexOf(query.toLowerCase()) == 0) {
    //     filtered.push(OPunits);
    //   }
    // }
    // this.filteredOP_unit = filtered;
  }

  createNewSp() {
    let newSpData = {
      ServiceProviderName: this.AddspName,
      ServiceProviderCode: this.erpsCode,
      City: this.citySp,
      Country: this.countrysp,
      LocationCode: this.LocationSp,
    };
    this.sharedService
      .createserviceprovider(JSON.stringify(newSpData))
      .subscribe((data) => {
        if (data.result == 'saved to db') {
          this.messageService.add(this.addObject);
          // this.vendorList=true;
          this.DisplayServiceProviderDetails();
          this.DisplaySpDetailsById();
          // this.venderdetails = data.record.ServiceProviderName;
          // this.displayAddspDialog = false;
        } else {
          this.messageService.add(this.errorObject);
        }
      });
  }

  toGetEntity() {
    this.entityList = [];
    this.sharedService.getEntityDept().subscribe((data: any) => {
      this.entityList = data;
    });
  }
  selectedEntity(value) {
    // this.entityBodyList = [];
    // this.entityDeptList = [];
    let item = this.entityList.filter((item) => {
      return value == item.idEntity;
    });
    this.source = item[0].sourceSystemType;
    this.sharedService.selectedEntityId = value;
    this.selectedEntityId = value;
    this.sharedService.getEntitybody().subscribe((data: any) => {
      this.entityBodyList = data;
    });
  }
  selectedEntityBody(value) {
    // this.entityDeptList = [];
    if (this.entityBodyList) {
      let item = this.entityBodyList.filter((item) => {
        return value == item.idEntityBody;
      });
      if (item.length > 0) {
        this.entityDeptList = item[0].department;
        this.selectedEntityBodyId = item[0]['idEntityBody'];
      }
    }
  }
  selectedEntityDept(value) {
    // let item = this.entityDeptList.filter((item) => {
    //   return value.indexOf(item.DepartmentName) > -1;
    // })
    this.selectedEntityDeptId = value;
  }

  viewInvoice(e) {
    this.route.navigate([`customer/invoice/InvoiceDetails/${e.idDocument}`]);
    this.tagService.createInvoice = true;
    this.tagService.displayInvoicePage = false;
    this.tagService.editable = false;
    this.sharedService.invoiceID = e.idDocument;
  }
  showAddSpDialog() {
    this.displayAddspDialog.emit(true);
  }
  // readVendorInvoiceData(){
  //   this.sharedService.readVendorInvoices().subscribe((data:any)=>{
  //     this.readVendorInviceDisplayArray = data.data
  //   })
  // }
  DisplaySpInvoice() {
    this.SpinnerService.show();
    this.sharedService.readServiceInvoice().subscribe((data: any) => {
      const invoicePushedArray = [];
      data.data.forEach((element) => {
        let invoiceData = {
          ...element.Document,
          ...element.Entity,
          ...element.EntityBody,
          ...element.ServiceProvider,
          ...element.ServiceAccount,
        };
        invoiceData.docstatus = element.docstatus;
        invoicePushedArray.push(invoiceData);
      });
      this.spinvoicereaddata = invoicePushedArray;
      this.SpinnerService.hide();
    });
  }
  readColumnsSpInvoice() {
    this.sharedService.readColumnInvoice('SER').subscribe((data: any) => {
      this.updateColumns = [];
      const pushedInvoiceColumnsArray = [];
      data.col_data.forEach((element) => {
        let arrayColumn = {
          ...element.DocumentColumnPos,
          ...element.ColumnPosDef,
        };
        pushedInvoiceColumnsArray.push(arrayColumn);
      });
      this.spInvoiceColumns = pushedInvoiceColumnsArray.filter((ele) => {
        return ele.isActive == 1;
      });
      const arrayOfColumnId = [];
      this.spInvoiceColumns.forEach((e) => {
        arrayOfColumnId.push(e.dbColumnname);
      });
      this.columnstodisplaySpInvoice = arrayOfColumnId;
      // this.allColumns = pushedInvoiceColumnsArray;
      this.spInvoiceColumns = this.spInvoiceColumns.sort(
        (a, b) => a.documentColumnPos - b.documentColumnPos
      );
      this.allSpInvoiceColumns = pushedInvoiceColumnsArray.sort(
        (a, b) => a.documentColumnPos - b.documentColumnPos
      );
      this.allSpInvoiceColumns.forEach((val) => {
        let activeBoolean;
        if (val.isActive == 1) {
          activeBoolean = true;
        } else {
          activeBoolean = false;
        }
        this.updateColumns.push({
          idtabColumn: val.idDocumentColumn,
          ColumnPos: val.documentColumnPos,
          isActive: activeBoolean,
        });
      });
    });
  }
  onOptionDrop(event: CdkDragDrop<any[]>) {
    moveItemInArray(
      this.allSpInvoiceColumns,
      event.previousIndex,
      event.currentIndex
    );

    this.allSpInvoiceColumns.forEach((e, index) => {
      this.updateColumns.forEach((val) => {
        if (val.idtabColumn === e.idDocumentColumn) {
          val.ColumnPos = index + 1;
        }
      });
    });
  }
  activeColumn(e, value) {
    this.updateColumns.forEach((val) => {
      if (val.idtabColumn == value.idDocumentColumn) {
        val.isActive = e.target.checked;
      }
    });
  }

  updateColumnPosition() {
    this.sharedService
      .updateColumnPOs(this.updateColumns, 'SER')
      .subscribe((data: any) => {
        this.readColumnsSpInvoice();
      });
    this.visibleSPColumns = false;
  }

  searchInvoiceDataV(value) {
    this.allSearchInvoiceString = value.filteredValue;
  }
  exportExcel() {
    if (this.allSearchInvoiceString && this.allSearchInvoiceString.length > 0) {
      this.ImportExcelService.exportExcel(this.allSearchInvoiceString);
    } else if (this.spinvoicereaddata && this.spinvoicereaddata.length > 0) {
      this.ImportExcelService.exportExcel(this.spinvoicereaddata);
    } else {
      alert('No Data to import');
    }
  }

  ngOnDestroy(): void {
    this.vendorList = false;
  }
}
