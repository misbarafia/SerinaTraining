import { Router } from '@angular/router';
import { SharedService } from 'src/app/services/shared/shared.service';
import { Component, OnInit } from '@angular/core';
import {
  AbstractControl,
  FormBuilder,
  FormGroup,
  Validators,
} from '@angular/forms';

@Component({
  selector: 'app-vendors',
  templateUrl: './vendors.component.html',
  styleUrls: ['./vendors.component.scss'],
})
export class VendorsComponent implements OnInit {
  vendorsList = [];
  listLoading: boolean;
  vendorForm: FormGroup;
  filterString: string;
  filtered: any[];
  vendorsListDispaly = [];
  submitted: boolean = false;
  entity: any;
  selectedEntityId: any = 'ALL';
  onboardedVendorList: any[];
  onboard_status: any = 'ALL';
  onBoardArray = [
    { name: 'ALL', value: 'ALL' },
    { name: 'Onboarded', value: true },
    { name: 'Not-Onboarded', value: false },
  ];
  throttle = 300;
  scrollDistance = 7;
  offsetCount = 1;
  APIParams: string;
  vendorNameForSearch: any;

  constructor(
    private sharedService: SharedService,
    private router: Router,
    private formBuilder: FormBuilder
  ) {}
  get f(): { [key: string]: AbstractControl } {
    return this.vendorForm.controls;
  }
  ngOnInit(): void {
    this.vendorForm = this.formBuilder.group({
      VendorName: ['', Validators.required],
      Email: ['', [Validators.required, Validators.email]],
      Contact: [''],
      Address: [''],
      VendorCode: [''],
      Desc: [''],
      Website: [''],
      FirstName: [''],
      LastName: [''],
      Designation: [''],
      TRNNumber: [''],
      TradeLicense: [''],
      VATLicense: [''],
      Account: ['', Validators.required],
      AccountType: ['', Validators.required],
      Country: [''],
      City: [''],
      LocationCode: [''],
    });
    if (this.sharedService.storeVendorsList) {
      this.sharedService.readVendorData().subscribe((data: any) => {
        this.vendorsList = data;
        this.vendorsListDispaly = this.vendorsList;
      });
    }
    // this.vendorsList = this.sharedService.vendorList;
    if (this.vendorsList.length == 0) {
      this.APIParams = `?offset=1&limit=100`;
      this.getVendorsData(this.APIParams);
      // this.readOnboardedVendorsList();
    } else {
      // setTimeout(() => {
      //   this.searchVendor('');
      // }, 50);
      this.listLoading = true;
    }
    this.selectedEntityId = this.sharedService.selectedEntityId;
    this.onboard_status = this.sharedService.onboard_status;
    this.vendorNameForSearch = this.sharedService.vendorNameForSearch;
    this.getEntitySummary();
  }

  readOnboardedVendorsList() {
    this.sharedService.getOnboardedData().subscribe((data: any) => {
      let array = [];
      data.forEach((val) => {
        let mergeArray = { ...val.Entity, ...val.Vendor };
        array.push(mergeArray);
      });
      this.onboardedVendorList = array;
    });
  }

  addOnboardStatus() {
    let array = [];
    this.vendorsList.forEach((ele) => {
      this.onboardedVendorList.forEach((val) => {
        if (ele.idVendor === val.idVendor) {
          ele.onboardStatus = true;
        }
      });
      array.push(ele);
    });
    this.vendorsList = array;
  }

  searchVendor(searchText) {
    const filteredVendor = this.vendorsList.filter((vendor) => {
      return vendor.VendorName.toLowerCase().includes(searchText.toLowerCase());
    });
    this.vendorsListDispaly = filteredVendor;
  }

  getEntitySummary() {
    this.sharedService.getSummaryEntity().subscribe((data: any) => {
      this.entity = data.result;
    });
  }
  selectEntity(value) {
    this.selectedEntityId = value;
    this.sharedService.selectedEntityId = value;
  }
  selectedType(val) {
    this.onboard_status = val;
    this.sharedService.onboard_status = val;
  }

  frUpdate(vendor) {
    this.sharedService.vendorDetails = vendor;
    let vendorData: any = vendor;
    sessionStorage.setItem('vendorData', JSON.stringify(vendorData));
    this.router.navigate(['IT_Utility/vendors/Fr_update']);
  }

  saveVendor() {
    if (this.vendorForm.invalid) {
      this.submitted = false;
      return;
    }
    this.submitted = true;
    let vendorobj = {
      VendorName: this.vendorForm.controls['VendorName'].value,
      Address: this.vendorForm.controls['Address'].value,
      City: this.vendorForm.controls['City'].value,
      Country: this.vendorForm.controls['Country'].value,
      Desc: this.vendorForm.controls['Desc'].value,
      VendorCode: this.vendorForm.controls['VendorCode'].value,
      Email: this.vendorForm.controls['Email'].value,
      Contact: this.vendorForm.controls['Contact'].value,
      Website: this.vendorForm.controls['Website'].value,
      Salutation: '',
      FirstName: this.vendorForm.controls['FirstName'].value,
      LastName: this.vendorForm.controls['LastName'].value,
      Designation: this.vendorForm.controls['Designation'].value,
      TradeLicense: this.vendorForm.controls['TradeLicense'].value,
      VATLicense: this.vendorForm.controls['VATLicense'].value,
      TRNNumber: this.vendorForm.controls['TRNNumber'].value,
    };
    let vu_id = JSON.parse(sessionStorage.getItem('currentLoginUser'))[
      'userdetails'
    ]['idUser'];
    this.sharedService.addVendor(vendorobj, vu_id).subscribe((data) => {
      let vendoraccobj = {
        Account: this.vendorForm.controls['Account'].value,
        AccountType: this.vendorForm.controls['AccountType'].value,
        entityID: 1,
        entityBodyID: 1,
        City: this.vendorForm.controls['City'].value,
        Country: this.vendorForm.controls['Country'].value,
        LocationCode: this.vendorForm.controls['LocationCode'].value,
      };
      this.sharedService
        .addVendorAccount(vendoraccobj, vu_id, data['idVendor'])
        .subscribe((data) => {
          (<HTMLButtonElement>document.getElementById('closebtn')).click();
          location.reload();
          this.submitted = false;
        });
    });
  }
  onScroll() {
    this.offsetCount++;
    this.filtersForAPI();
  }

  getVendorsData(data): void {
    this.sharedService.getVendors(data).subscribe((data) => {
      let pushArray = [];
      let onboardBoolean: boolean;
      data.forEach((ele) => {
        let mergedData = { ...ele.Entity, ...ele.Vendor };
        mergedData.OnboardedStatus = ele.OnboardedStatus;
        pushArray.push(mergedData);
      });
      this.vendorsListDispaly = this.vendorsList.concat(pushArray);
      this.listLoading = true;
      this.sharedService.storeVendorsList.next(this.vendorsListDispaly);
    });
  }

  filter() {
    this.listLoading = false;
    this.vendorsList = [];
    this.vendorNameForSearch = '';
    this.sharedService.vendorNameForSearch = '';
    // let booleanValue:boolean;
    // if(this.onboard_status == 'true'){
    //   booleanValue = true;
    // } else if(this.onboard_status == 'false') {
    //   booleanValue = false;
    // }
    // if(this.selectedEntityId != 'ALL' && this.onboard_status == 'ALL'){
    //   this.vendorsListDispaly = this.vendorsList.filter(v=>{
    //     return this.selectedEntityId == v.idEntity;
    //   });
    // } else if(this.selectedEntityId == 'ALL' && this.onboard_status != 'ALL'){
    //   this.vendorsListDispaly = this.vendorsList.filter(v=>{
    //     return v.onboardStatus == booleanValue;
    //   });
    // } else if(this.selectedEntityId != 'ALL' && this.onboard_status != 'ALL'){
    //   this.vendorsListDispaly = this.vendorsList.filter(v=>{
    //     return this.selectedEntityId == v.idEntity &&  v.onboardStatus == booleanValue;
    //   });
    // } else {
    //   this.vendorsListDispaly = this.vendorsList;
    // }
    this.offsetCount = 1;
    this.filtersForAPI();
    this.listLoading = true;
  }

  filtersForAPI() {
    if (this.selectedEntityId != 'ALL' && this.onboard_status == 'ALL') {
      this.APIParams = `?ent_id=${this.selectedEntityId}&offset=${this.offsetCount}&limit=100`;
      this.getVendorsData(this.APIParams);
    } else if (this.onboard_status != 'ALL' && this.selectedEntityId == 'ALL') {
      this.APIParams = `?onb_status=${this.onboard_status}&offset=${this.offsetCount}&limit=100`;
      this.getVendorsData(this.APIParams);
    } else if (this.selectedEntityId != 'ALL' && this.onboard_status != 'ALL') {
      this.APIParams = `?ent_id=${this.selectedEntityId}&onb_status=${this.onboard_status}&offset=${this.offsetCount}&limit=100`;
      this.getVendorsData(this.APIParams);
    } else if (this.vendorNameForSearch) {
      this.APIParams = `?ven_code=${this.vendorNameForSearch}&offset=${this.offsetCount}&limit=100`;
    } else {
      this.APIParams = `?offset=${this.offsetCount}&limit=100`;
      this.getVendorsData(this.APIParams);
    }
  }
  filteVendor() {
    this.onboard_status = 'ALL';
    this.sharedService.onboard_status = 'ALL';
    this.selectedEntityId = 'ALL';
    this.sharedService.selectedEntityId = 'ALL';
    this.vendorsList = [];
    this.offsetCount = 1;
    this.APIParams = `?ven_code=${this.vendorNameForSearch}&offset=${this.offsetCount}&limit=100`;
    this.getVendorsData(this.APIParams);
    this.sharedService.vendorNameForSearch = this.vendorNameForSearch;
  }
}
