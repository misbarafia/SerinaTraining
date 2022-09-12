import { DataService } from './../../../services/dataStore/data.service';

import { SharedService } from 'src/app/services/shared.service';
import { Component, OnInit,  AfterViewInit, Input, Output, EventEmitter, ViewChild } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { ImportExcelService } from 'src/app/services/importExcel/import-excel.service';
import { NgxSpinnerService } from "ngx-spinner";
import {
  ConfirmationService,
  MessageService,
  PrimeNGConfig
} from "primeng/api";
import { TaggingService } from 'src/app/services/tagging.service';
import { CdkDragDrop, moveItemInArray } from '@angular/cdk/drag-drop';
import { MatSidenav } from '@angular/material/sidenav';
export interface UserData {
  name: string;
  contact: string;
  lastModified: string;
  status: string;
  emailId: string;
  id: string;
}

@Component({
  selector: 'app-vendor-details',
  templateUrl: './vendor-details.component.html',
  styleUrls: ['./vendor-details.component.scss', './../vendor.component.scss']
})
export class VendorDetailsComponent implements OnInit, AfterViewInit {
  @Input() vendoraccountreaddata;
  @Input() vendorbyidreaddata;
  @Input() vendorreaddata;
  @Input() venderdetails;
  @Input() showPaginator: boolean;
  @Output() displayIntitalVendorDataBoolean: EventEmitter<boolean> = new EventEmitter();
  users: UserData[] = [];

  vendorData = [];
  VendorAccount = [];
  itemsList = ["item 1", "item 2", "item 3"]

  openFilter: boolean = false;

  selectedVender: string;
  selectedVenderPriceList: any;
  selectedCountry: any;

  selectedCustomer: string;
  initialViewVendor: boolean;
  vendorList: boolean = true;

  vendorDetailsForm: FormGroup;
  submitted = false;
  selectedCities1: string[];
  savedataboolean: boolean;
  first = 0;
  last: number;

  rows;

  vendorUpdateName = '';
  vendorUpdateCompany = '';
  vendorUpdateVenderCode = '';
  vendorUpdateEmail;
  vendorUpdateDesc;
  vendorUpdateContact;
  vendorUpdateAddress;
  vendorUpdateCity;
  vendorUpdateCountry;

  editable: boolean = false;
  savebooleansp = false;
  columnVenderSite: { field: string; header: string; }[];
  updateColumns: any[];
  VendorinvoiceColumns: any[];
  columnstodisplayVendorInvoice: any[];
  allVendorInvoiceColumns: any[];
  visibleVendorColumns: boolean;
  readVendorInviceDisplayArray: any[];
  editBtnBoolean: boolean = true;
  bgColorCode:any;
  allSearchInvoiceString: any;

  @ViewChild('sidenav') sidenav :MatSidenav;
  events: string[] = [];
  opened: boolean;
  vendorsListData = [];
  close(reason: string) {
    this.sidenav.close();
  }

  constructor(private fb: FormBuilder,
    private route: Router,
    private storageService: DataService,
    private tagService: TaggingService,
    private sharedService: SharedService,
    private messageService: MessageService,
    private ImportExcelService : ImportExcelService,
    private SpinnerService: NgxSpinnerService,
    private primengConfig: PrimeNGConfig) {

  }

  ngOnInit() {
    this.first = this.storageService.vendorPaginationFirst;
    this.rows = this.storageService.vendorPaginationRowLength;
    this.bgColorCode = this.storageService.bgColorCode;
    this.columnVenderSite = [
      { field: 'Account', header: 'Vendor site ID' },
      { field: 'EntityName', header: 'Entity' },
      { field: 'LocationCode', header: 'Location' },
      { field: 'City', header: 'Address' },
      { field: 'Contact', header: 'Contact' },
      { field: 'noOfInvoices', header: 'No of invoices' },
      { field: 'noOfPo', header: 'No of PO' }
    ];
    this.initialViewVendor = this.sharedService.initialViewVendorBoolean;
    this.venderdetails = this.sharedService.vendorFullDetails;
    this.vendorreaddata = this.storageService.vendorsListData;
    this.primengConfig.ripple = true;
    // this.DisplayVendorDetails();
    this.DisplayVendorAccountDetails();
    this.DisplayVendorDetailsById();
    this.readVendorInvoiceData();
    this.readColumnsVendorInvoice();
    this.readVendorMasterData(this.venderdetails.idVendorAccount);
  }
  ngAfterViewInit() {

  }

  viewFullDetails(e) {
    this.initialViewVendor = false;
    this.sharedService.initialViewVendorBoolean = false;
    this.sharedService.vendorFullDetails = e;
    this.venderdetails = e
    this.sharedService.vendorID = e.idVendor;
    this.DisplayVendorAccountDetails();
    this.DisplayVendorDetailsById();
    this.readVendorInvoiceData();
    this.readVendorMasterData(e.idVendorAccount);

  }
  colseDiv() {
    this.initialViewVendor = true;
    this.sharedService.initialViewVendorBoolean = true;
    this.route.navigate(['/customer/vendor'])
    this.displayIntitalVendorDataBoolean.emit(true);
  }

  get f() { return this.vendorDetailsForm.controls; }
  onSubmit() {
    this.submitted = true;
    // stop here if form is invalid
    // if (this.vendorDetailsForm.invalid) {
    //     return;
    // }

    // display form values on success
    this.sharedService.createvendor(JSON.stringify(this.vendorDetailsForm.value)).subscribe((data) => {
      if (data.result == 'Updated') {
        this.messageService.add({
          severity: "info",
          summary: "added",
          detail: "Created Successfully"
        });
        this.vendorList = true;
        // this.DisplayVendorDetails();
        this.DisplayVendorDetailsById();
        this.DisplayVendorAccountDetails();
        // this.vendorDetailsForm.reset();
      } else {
        this.messageService.add({
          severity: "error",
          summary: "error",
          detail: "Something went wrong"
        });
      }
    });
  }
  onCancel() {
    // this.initialViewVendor = true;
    // this.vendorList = true;
    this.editable = false;
    this.savebooleansp = false;
    this.editBtnBoolean = true;
  }
  selectedPayment(e) {
  }
  onSelectCol(e, value) {
    if (e.target.checked == true) {
    }
  }
  editVenderData(e) {
    this.vendorList = false;
  }
  onEdit() {
    this.editBtnBoolean = false;
    this.editable = true;
    this.savebooleansp = true;
  }
  DisplayVendorDetails(offset,limit) {
    this.SpinnerService.show();
    this.sharedService.readvendors(`?offset=${offset}&limit=${limit}`).subscribe((data: any) => {
      if (data) {
        let pushArray = [];
        let onboardBoolean:boolean;
        data.forEach(ele=>{
          let mergedData = {...ele.Entity,...ele.Vendor};
          mergedData.idVendorAccount = ele.idVendorAccount;
          if(ele.OnboardedStatus == 'Onboarded'){
            onboardBoolean = true
          } else {
            onboardBoolean = false
          }
          mergedData.OnboardedStatus = onboardBoolean;
          pushArray.push(mergedData);
        })
        
        this.vendorreaddata = this.storageService.vendorsListData.concat(pushArray);
        this.storageService.vendorsListData = this.vendorreaddata;
        if (this.vendorreaddata.length > 10) {
          this.showPaginator = true;
        }
        this.SpinnerService.hide();
      }
    })
  }
  DisplayVendorAccountDetails() {
    this.SpinnerService.show();
    this.sharedService.readvendoraccountSite().subscribe((data:any) => {
      if(data.length >0){
        let res = [];
        data.forEach(element => {
         let respose = {...element.Entity,...element.VendorAccount};
         res.push(respose);
        });
        this.vendoraccountreaddata = res;
      }
      // var res = [];
      // for (var x in this.vendoraccountreaddata) {
      //   this.vendoraccountreaddata.hasOwnProperty(x) && res.push(this.vendoraccountreaddata[x])
      // }
      if (this.vendoraccountreaddata.length > 10) {
        this.showPaginator = true;
      }
      this.SpinnerService.hide();
    })
  }
  DisplayVendorDetailsById() {
    this.SpinnerService.show();
    this.sharedService.readvendorbyid().subscribe((data:any) => {
      if(data.length > 0){
        this.vendorbyidreaddata = data;
        this.vendorUpdateName = data[0].Name;
        this.vendorUpdateCompany = '';
        this.vendorUpdateVenderCode = data[0].VenderCode;
        this.vendorUpdateEmail = data[0].Email;
        this.vendorUpdateDesc = data[0].Desc;
        this.vendorUpdateContact = data[0].Contact;
        this.vendorUpdateAddress = data[0].Address;
        this.vendorUpdateCity = data[0].City;
        this.vendorUpdateCountry = data[0].Country;
      }
      this.SpinnerService.hide();
    })
  }
  readVendorMasterData(ven_acc_id) {
    this.sharedService.readItemListData(ven_acc_id).subscribe((data:any)=>{
      this.itemsList = data.result;
    })
  }

  updatevendor(e) {
    if (e) {
      let updateVendorData = {
        "Name": this.vendorUpdateName,
        "Address": this.vendorUpdateAddress,
        "City": this.vendorUpdateCity,
        "Country": this.vendorUpdateCountry,
        "Desc": this.vendorUpdateDesc,
        "VenderCode": this.vendorUpdateVenderCode,
        "Email": this.vendorUpdateEmail,
        "Contact": this.vendorUpdateContact,
        "website": e[0].Website,
        "Salutation": '',
        "FirstName": e[0].FirstName,
        "LastName": e[0].LastName,
        "Designation": e[0].Designation,
        "TradeLicense": e[0].TradeLicense,
        "VATLicense": e[0].VATLicense,
        "TLExpiryDate": e[0]['TLExpiryDate'],
        "VLExpiryDate": e[0]['VLExpiryDate'],
        "TRNNumber": e[0]['TRNNumber']
      }
      this.sharedService.updatevendor(JSON.stringify(updateVendorData)).subscribe((data) => {
        if (data.result == 'updated') {
          this.messageService.add({
            severity: "info",
            summary: "Updated",
            detail: "Updated Successfully"
          });
          this.vendorList = true;

          // this.DisplayVendorDetails();
          this.DisplayVendorDetailsById();
          this.DisplayVendorAccountDetails();
          this.editable = false;
          this.savebooleansp = false;
          this.editBtnBoolean = true;
        } else {
          this.messageService.add({
            severity: "error",
            summary: "error",
            detail: "Something went wrong"
          });
        }
      }, error => {
        alert(error.statusText)
      });
    }


  }
  editvendor(e) {
    this.savedataboolean = false;
    this.vendorList = false;
    this.vendorDetailsForm.patchValue({
      Name: e[0].Name,
      VenderCode: e[0].VenderCode,
      Address: e[0].Address,
      City: e[0].City,
      Country: e[0].Country,
      Desc: e[0].Desc,
      Email: e[0].Email,
      Contact: e[0].Contact,
      Company: e[0].Company,
      Phone: e[0].Phone,
      State: e[0].State,
      zipcode: e[0].zipcode
    })
  }


  viewInvoice(e) {
    this.route.navigate([`customer/invoice/InvoiceDetails/${e.idDocument}`])
    this.tagService.createInvoice = true;
    this.tagService.displayInvoicePage = false;
    this.tagService.editable = false;
    this.sharedService.invoiceID = e.idDocument;
  }

  readVendorInvoiceData() {
    this.sharedService.readVendorInvoices().subscribe((data: any) => {
      let pushedVendorInvoices = [];
      data.data.forEach(element => {
        let arrayVendorInvoices = { ...element.Entity, ...element.EntityBody, ...element.Document, ...element.Vendor, ...element.VendorAccount };
        arrayVendorInvoices.docstatus = element.docstatus;
        pushedVendorInvoices.push(arrayVendorInvoices)
      });
      this.readVendorInviceDisplayArray = pushedVendorInvoices;
    })
  }

  readColumnsVendorInvoice() {
    this.sharedService.readColumnInvoice('VEN').subscribe((data: any) => {
      this.updateColumns = [];
      const pushedInvoiceColumnsArray = []
      data.col_data.forEach(element => {
        let arrayColumn = { ...element.DocumentColumnPos, ...element.ColumnPosDef, };
        pushedInvoiceColumnsArray.push(arrayColumn)
      });
      this.VendorinvoiceColumns = pushedInvoiceColumnsArray.filter(ele => {
        return ele.isActive == 1
      })
      const arrayOfColumnId = []
      this.VendorinvoiceColumns.forEach(e => {
        arrayOfColumnId.push(e.dbColumnname);
      });
      this.columnstodisplayVendorInvoice = arrayOfColumnId;
      // this.allColumns = pushedInvoiceColumnsArray;
      this.VendorinvoiceColumns = this.VendorinvoiceColumns.sort((a, b) => a.documentColumnPos - b.documentColumnPos)
      this.allVendorInvoiceColumns = pushedInvoiceColumnsArray.sort((a, b) => a.documentColumnPos - b.documentColumnPos)

      this.allVendorInvoiceColumns.forEach(val => {
        let activeBoolean;
        if (val.isActive == 1) {
          activeBoolean = true
        } else {
          activeBoolean = false
        }
        this.updateColumns.push({ idtabColumn: val.idDocumentColumn, ColumnPos: val.documentColumnPos, isActive: activeBoolean })

      });
    })
  }

  onOptionDrop(event: CdkDragDrop<any[]>) {
    moveItemInArray(this.allVendorInvoiceColumns, event.previousIndex, event.currentIndex);

    this.allVendorInvoiceColumns.forEach((e, index) => {
      this.updateColumns.forEach(val => {
        if (val.idtabColumn === e.idDocumentColumn) {
          val.ColumnPos = index + 1;
        }
      })
    });

  }
  activeColumn(e, value) {
    this.updateColumns.forEach(val => {
      if (val.idtabColumn == value.idDocumentColumn) {
        val.isActive = e.target.checked
      }
    })
  }

  updateColumnPosition() {
    this.sharedService.updateColumnPOs(this.updateColumns, 'VEN').subscribe((data: any) => {
      this.readColumnsVendorInvoice();
    })
    // this.visibleVendorColumns = false;
    this.sidenav.close();
  }
  showSidebar() {
    // this.visibleVendorColumns = true;
    this.sidenav.toggle();
  }
  paginate(event) {
    this.first = event.first;
    this.storageService.vendorPaginationFirst = this.first;
    this.storageService.vendorPaginationRowLength = event.rows;
    if(this.first >= this.storageService.pageCountVariable){
      this.storageService.pageCountVariable = event.first;
      this.storageService.offsetCount++
      this.DisplayVendorDetails(this.storageService.offsetCount,50)
    }
    
  }
  searchInvoiceDataV(value){
    this.allSearchInvoiceString = value.filteredValue;
  }
  exportExcel() {
    if (this.allSearchInvoiceString && this.allSearchInvoiceString.length > 0) {
      this.ImportExcelService.exportExcel(this.allSearchInvoiceString);
    } else if(this.readVendorInviceDisplayArray && this.readVendorInviceDisplayArray.length > 0) {
      this.ImportExcelService.exportExcel(this.readVendorInviceDisplayArray);
    }  else {
      alert("No Data to import")
    }
  }

}