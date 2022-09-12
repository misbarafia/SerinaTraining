import { Component, OnInit } from '@angular/core';
import { AbstractControl, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { SharedService } from 'src/app/services/shared/shared.service';

@Component({
  selector: 'app-service-providers',
  templateUrl: './service-providers.component.html',
  styleUrls: ['./service-providers.component.scss']
})
export class ServiceProvidersComponent implements OnInit {

  SPList = [];
  listLoading: boolean;
  spForm: FormGroup;
  filterString: string;
  filtered: any[];
  SPListDispaly = [];
  submitted: boolean = false;
  entity: any;
  selectedEntityId: any = 'ALL';
  onboardedSPList: any[];
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
  spNameForSearch: any;

  constructor(
    private sharedService: SharedService,
    private router: Router,
    private formBuilder: FormBuilder
  ) {}
  get f(): { [key: string]: AbstractControl } {
    return this.spForm.controls;
  }
  ngOnInit(): void {
    this.spForm = this.formBuilder.group({
      SPName: ['', Validators.required],
      Email: ['', [Validators.required, Validators.email]],
      Contact: [''],
      Address: [''],
      SPCode: [''],
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
    if (this.sharedService.storeServiceProviderList) {
      this.sharedService.readSPData().subscribe((data: any) => {
        this.SPList = data;
        this.SPListDispaly = this.SPList;
      });
    }
    // this.SPList = this.sharedService.SPList;
    if (this.SPList.length == 0) {
      this.APIParams = `?offset=1&limit=100`;
      this.getSPData(this.APIParams);
    } else {
      // setTimeout(() => {
      //   this.searchsp('');
      // }, 50);
      this.listLoading = true;
    }
    this.selectedEntityId = this.sharedService.selectedEntityId;
    this.onboard_status = this.sharedService.onboard_status;
    this.spNameForSearch = this.sharedService.spNameForSearch;
    this.getEntitySummary();
  }

  readOnboardedSPList() {
    this.sharedService.getOnboardedData().subscribe((data: any) => {
      let array = [];
      data.forEach((val) => {
        let mergeArray = { ...val.Entity, ...val.ServiceProvider };
        array.push(mergeArray);
      });
      this.onboardedSPList = array;
    });
  }

  addOnboardStatus() {
    let array = [];
    this.SPList.forEach((ele) => {
      this.onboardedSPList.forEach((val) => {
        if (ele.idServiceProvider === val.idServiceProvider) {
          ele.onboardStatus = true;
        }
      });
      array.push(ele);
    });
    this.SPList = array;
  }

  searchsp(searchText) {
    const filteredsp = this.SPList.filter((sp) => {
      return sp.ServiceProviderName.toLowerCase().includes(searchText.toLowerCase());
    });
    this.SPListDispaly = filteredsp;
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

  frUpdate(sp) {
    this.sharedService.SPDetails = sp;
    let spData: any = sp;
    sessionStorage.setItem('spData', JSON.stringify(spData));
    this.router.navigate(['IT_Utility/service-providers/Fr_update']);
  }

  saveSP() {
    if (this.spForm.invalid) {
      this.submitted = false;
      return;
    }
    this.submitted = true;
    let spobj = {
      SPName: this.spForm.controls['SPName'].value,
      Address: this.spForm.controls['Address'].value,
      City: this.spForm.controls['City'].value,
      Country: this.spForm.controls['Country'].value,
      Desc: this.spForm.controls['Desc'].value,
      SPCode: this.spForm.controls['SPCode'].value,
      Email: this.spForm.controls['Email'].value,
      Contact: this.spForm.controls['Contact'].value,
      Website: this.spForm.controls['Website'].value,
      Salutation: '',
      FirstName: this.spForm.controls['FirstName'].value,
      LastName: this.spForm.controls['LastName'].value,
      Designation: this.spForm.controls['Designation'].value,
      TradeLicense: this.spForm.controls['TradeLicense'].value,
      VATLicense: this.spForm.controls['VATLicense'].value,
      TRNNumber: this.spForm.controls['TRNNumber'].value,
    };
    let vu_id = JSON.parse(sessionStorage.getItem('currentLoginUser'))[
      'userdetails'
    ]['idUser'];
    this.sharedService.addSP(spobj, vu_id).subscribe((data) => {
      let spaccobj = {
        Account: this.spForm.controls['Account'].value,
        AccountType: this.spForm.controls['AccountType'].value,
        entityID: 1,
        entityBodyID: 1,
        City: this.spForm.controls['City'].value,
        Country: this.spForm.controls['Country'].value,
        LocationCode: this.spForm.controls['LocationCode'].value,
      };
      this.sharedService
        .addSPAccount(spaccobj, vu_id, data['idServiceProvider'])
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

  getSPData(data): void {
    this.sharedService.getServiceProviders(data).subscribe((data) => {
      let pushArray = [];
      let onboardBoolean: boolean;
      data.forEach((ele) => {
        let mergedData = { ...ele.Entity, ...ele.ServiceProvider };
        mergedData.OnboardedStatus = ele.OnboardedStatus;
        pushArray.push(mergedData);
      });
      this.SPListDispaly = this.SPList.concat(pushArray);
      console.log(data);
      
      this.listLoading = true;
      this.sharedService.storeServiceProviderList.next(this.SPListDispaly);
    });
  }

  filter() {
    this.listLoading = false;
    this.SPList = [];
    this.spNameForSearch = '';
    this.sharedService.spNameForSearch = '';
    this.offsetCount = 1;
    this.filtersForAPI();
    this.listLoading = true;
  }

  filtersForAPI() {
    if (this.selectedEntityId != 'ALL' && this.onboard_status == 'ALL') {
      this.APIParams = `?ent_id=${this.selectedEntityId}&offset=${this.offsetCount}&limit=100`;
      this.getSPData(this.APIParams);
    } else if (this.onboard_status != 'ALL' && this.selectedEntityId == 'ALL') {
      this.APIParams = `?onb_status=${this.onboard_status}&offset=${this.offsetCount}&limit=100`;
      this.getSPData(this.APIParams);
    } else if (this.selectedEntityId != 'ALL' && this.onboard_status != 'ALL') {
      this.APIParams = `?ent_id=${this.selectedEntityId}&onb_status=${this.onboard_status}&offset=${this.offsetCount}&limit=100`;
      this.getSPData(this.APIParams);
    } else if (this.spNameForSearch) {
      this.APIParams = `?ven_code=${this.spNameForSearch}&offset=${this.offsetCount}&limit=100`;
    } else {
      this.APIParams = `?offset=${this.offsetCount}&limit=100`;
      this.getSPData(this.APIParams);
    }
  }
  filteSP() {
    this.onboard_status = 'ALL';
    this.sharedService.onboard_status = 'ALL';
    this.selectedEntityId = 'ALL';
    this.sharedService.selectedEntityId = 'ALL';
    this.SPList = [];
    this.offsetCount = 1;
    this.APIParams = `?ven_code=${this.spNameForSearch}&offset=${this.offsetCount}&limit=100`;
    this.getSPData(this.APIParams);
    this.sharedService.spNameForSearch = this.spNameForSearch;
  }

}
