import { ServiceInvoiceService } from './../../../services/serviceBased/service-invoice.service';
import { formatDate } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { NgxSpinnerService } from 'ngx-spinner';
import { ConfirmationService, MessageService, PrimeNGConfig } from 'primeng/api';
import { SharedService } from 'src/app/services/shared.service';
import { TaggingService } from 'src/app/services/tagging.service';

export interface UserData {
  invoiceId: number;
  poNumber: number;
  VenderId: string;
  Vendername: string;
  entity: string;
  uploaded: string;
  modified: string;
  status: string;
  amount: string;
}

@Component({
  selector: 'app-service-invoices',
  templateUrl: './service-invoices.component.html',
  styleUrls: ['./service-invoices.component.scss','../../invoice/all-invoices/all-invoices.component.scss']
})
export class ServiceInvoicesComponent implements OnInit {

    vendorDetails: any;
     displayYear;
    minDate: Date;
    maxDate: Date;
    lastYear: number;
    users: UserData[] = [
      { invoiceId: 12, poNumber: 7894, VenderId: '3456', Vendername: 'Dr Nice', entity: 'Bajaj', uploaded: '01-01-2021', modified: '04-02-2021', status: 'un paid', amount: 'po2345' },
      { invoiceId: 12, poNumber: 7894, VenderId: '3456', Vendername: 'Dr Nice', entity: 'Bajaj', uploaded: '01-01-2021', modified: '04-02-2021', status: 'paid', amount: 'po2345' },
      { invoiceId: 12, poNumber: 7894, VenderId: '3456', Vendername: 'Dr Nice', entity: 'Bajaj', uploaded: '01-01-2021', modified: '04-02-2021', status: 'Cancelled', amount: 'po2345' },
      { invoiceId: 12, poNumber: 7894, VenderId: '3456', Vendername: 'Dr Nice', entity: 'Bajaj', uploaded: '01-01-2021', modified: '04-02-2021', status: 'paid', amount: 'po2345' },
      { invoiceId: 12, poNumber: 7894, VenderId: '3456', Vendername: 'Dr Nice', entity: 'Bajaj', uploaded: '01-01-2021', modified: '04-02-2021', status: 'paid', amount: 'po2345' },
      { invoiceId: 12, poNumber: 7894, VenderId: '3456', Vendername: 'Dr Nice', entity: 'Bajaj', uploaded: '01-01-2021', modified: '04-02-2021', status: 'paid', amount: 'po2345' },
      { invoiceId: 12, poNumber: 7894, VenderId: '3456', Vendername: 'Dr Nice', entity: 'Bajaj', uploaded: '01-01-2021', modified: '04-02-2021', status: 'Due', amount: 'po2345' },
      { invoiceId: 12, poNumber: 7894, VenderId: '3456', Vendername: 'Dr Nice', entity: 'Bajaj', uploaded: '01-01-2021', modified: '04-02-2021', status: 'paid', amount: 'po2345' },
      { invoiceId: 12, poNumber: 7894, VenderId: '3456', Vendername: 'Dr Nice', entity: 'Bajaj', uploaded: '01-01-2021', modified: '04-02-2021', status: 'paid', amount: 'po2345' },
      { invoiceId: 12, poNumber: 7894, VenderId: '3456', Vendername: 'Dr Nice', entity: 'Bajaj', uploaded: '01-01-2021', modified: '04-02-2021', status: 'paid', amount: 'po2345' },
      { invoiceId: 12, poNumber: 7894, VenderId: '3456', Vendername: 'Dr Nice', entity: 'Bajaj', uploaded: '01-01-2021', modified: '04-02-2021', status: 'paid', amount: 'po2345' },
      { invoiceId: 12, poNumber: 7894, VenderId: '3456', Vendername: 'Dr Nice', entity: 'Bajaj', uploaded: '01-01-2021', modified: '04-02-2021', status: 'paid', amount: 'po2345' },
      { invoiceId: 12, poNumber: 7894, VenderId: '3456', Vendername: 'Dr Nice', entity: 'Bajaj', uploaded: '01-01-2021', modified: '04-02-2021', status: 'paid', amount: 'po2345' },
      { invoiceId: 12, poNumber: 7894, VenderId: '3456', Vendername: 'Dr Nice', entity: 'Bajaj', uploaded: '01-01-2021', modified: '04-02-2021', status: 'paid', amount: 'po2345' },
      { invoiceId: 12, poNumber: 7894, VenderId: '3456', Vendername: 'Dr Nice', entity: 'Bajaj', uploaded: '01-01-2021', modified: '04-02-2021', status: 'paid', amount: 'po2345' },
    ]
  
    displayInvoicePage: boolean = true;
    fileUpload: boolean = false;
    createInvoice: boolean = false;
    isProceed: boolean = false;
    filterdate: Date;
    selectDate: string;

    openFilter: boolean = false;
  
    requiredFloor = ['Microsoft', 'IBM', 'Google'];
    cities = [
      { name: 'New York', code: 'NY' },
      { name: 'Rome', code: 'RM' },
      { name: 'London', code: 'LDN' },
      { name: 'Istanbul', code: 'IST' },
      { name: 'Paris', code: 'PRS' }
    ];
    selectedVender: string;
    selectedCustomer: string;
  
    imgWidth: any;
    imgHeight: any;
    rect: any;
    rectCoords = [];
    isEditable: boolean = false;
    imageUrl: string;
    showPaginator: boolean;
    invoiceListData: any;
    res: any[];
    errorData: any;
    errorDataLength: any[];
    showPaginatorError: boolean;
    erpStatus = ['Voucher Created', 'Voucher Not Created'];
  
    filename: string;
    viewType='invoice';
  
    isActiveIn: boolean = true;
    isActiveEr: boolean;
    erpVoucherStatus: any;
    serviceInvoiceLength: any;
    serviceErrorInvoiceLength: any;

    serviceInvoiceColumn = [
      { field: 'ServiceAccountNo', header: 'Service A/C' },
      { field: 'ServiceproviderName', header: 'SP Name' },
      { field: 'entityID', header: 'Entity Name' },
      { field: 'invoiceNumber', header: 'Invoice Number' },
      { field: 'documentDate', header: 'Invoice Date' },
      { field: 'downloadedDate', header: 'Downloaded Date' },
      { field: 'CreatedOn', header: 'Processed Date' },
      { field: 'voucherDate', header: 'Voucher Date' },
      { field: 'InvoiceErpStatusID', header: 'ERP Status' }
    ];
    serviceErrorInvoiceColumn = [
      { field: 'ServiceAccountNo', header: 'Service A/C' },
      { field: 'ServiceproviderName', header: 'SP Name' },
      { field: 'entityID', header: 'Entity Name' },
      { field: 'documentDate', header: 'Invoice Date' },
      { field: 'voucherDate', header: 'Voucher Date' },
      { field: 'invoiceNumber', header: 'OCR status' },
      { field: 'CreatedOn', header: 'Processed Date' },
      { field: 'InvoiceErpStatusID', header: 'ERP Status' }
    ];
  serviceInvoiceColumnHeader: any;
  serviceInvoiceColumnField: any;
  serviceErrorInvoiceColumnHeader: any;
  serviceErrorInvoiceColumnField: any;
    constructor(
      private route: Router,
      private confirmationService: ConfirmationService,
      private messageService: MessageService,
      private tagService: TaggingService,
      private SpinnerService: NgxSpinnerService,
      private sharedService: ServiceInvoiceService,
      private primengConfig: PrimeNGConfig) {

    }
  
    ngOnInit(): void {
      let today = new Date();
      let month = today.getMonth();
      let year = today.getFullYear();
      this.lastYear = year - 5;
      this.displayYear = `${this.lastYear}:${year}`;
      let prevYear = year - 5;
  
      this.minDate = new Date();
      this.minDate.setMonth(month);
      this.minDate.setFullYear(prevYear);
  
      this.maxDate = new Date();
      this.maxDate.setMonth(month);
      this.maxDate.setFullYear(year);
      if (!this.invoiceListData) {
        this.getInvoiceData("");
      }
    }

      // to prepare display columns array
  prepareColumnsArray(){
    this.serviceInvoiceColumn.filter(element =>{
      this.serviceInvoiceColumnHeader.push(element.header)
      this.serviceInvoiceColumnField.push(element.field)
    })

    this.serviceErrorInvoiceColumn.forEach(e1 =>{
      this.serviceErrorInvoiceColumnHeader.push(e1.header)
      this.serviceErrorInvoiceColumnField.push(e1.field)
    })
  }
  
    applyDatefilterforinvoice(){
      const format = 'yyyy-MM';
      const locale = 'en-US';
      try {
        this.selectDate = formatDate(this.filterdate.toLocaleDateString(), format, locale);
        // console.log(this.selectDate);
        this.getInvoiceData(this.selectDate);
      }
      catch (e) {
  
  
      }
      // this.getInvoiceData();
    }
  
    getInvoiceData(stdate: string) {
      // this.SpinnerService.show();
      // this.sharedService.getInvoice(stdate).subscribe(data => {
      //   console.log(data['ok']);
      //   this.invoiceListData = data['ok'].filter((data) => { return data.isOcrSuccess === 1 })
      //   // this.SpinnerService.hide();
      //   this.serviceInvoiceLength = this.invoiceListData.length;
      //   if (this.invoiceListData.length > 10) {
      //     this.showPaginator = true;
      //   }
      //   this.errorData = data['ok'].filter((data) => { return data.isOcrSuccess === 0 })
      //   this.serviceErrorInvoiceLength = this.errorData.length;
      //   console.log(this.errorData)
      //   if (this.errorData.length > 10) {
      //     this.showPaginatorError = true;
      //   }
  
  
      // })
    }
  
    invoiceTab() {
      this.isActiveIn = true;
      this.isActiveEr = false;
    }
    errorTab() {
      this.isActiveEr = true;
      this.isActiveIn = false;
    }
  
    openDialog() {
  
    }
    addVendorDetails() {
      console.log(this.vendorDetails.value);
    }
    public ngAfterViewInit() {
  
  
    }
  
  
  
    editInvoice(e) {
      console.log(e)
      this.sharedService.invoiceDetals = e.filePath;
      this.sharedService.invoiceId = e.idInvoice;
      this.erpVoucherStatus = e.InvoiceErpStatusID;
      this.filename = e.excelfilepath;
      this.createInvoice = true;
      this.displayInvoicePage = false;
      this.tagService.editable = true;
      this.sharedService.requiredBoolean = false;
    }
    editErrorInvoice(e){
      console.log(e)
      this.sharedService.invoiceDetals = e.filePath;
      this.sharedService.invoiceId = e.idInvoice;
      this.filename = e.excelfilepath;
      this.createInvoice = true;
      this.displayInvoicePage = false;
      this.tagService.editable = true;
      this.sharedService.requiredBoolean = true;
    }
  
    toViewInvoice(e) {
      console.log(e)
      this.sharedService.invoiceDetals = e.filePath;
      this.sharedService.invoiceId = e.idInvoice;
      this.createInvoice = true;
      this.displayInvoicePage = false;
      this.tagService.editable = false;
      this.sharedService.requiredBoolean = false;
    }
    uploadFileOption() {
      this.fileUpload = true;
      this.createInvoice = false;
      this.displayInvoicePage = false;
    }
    backToInvoice() {
      this.fileUpload = false;
      this.createInvoice = false;
      this.displayInvoicePage = true;
    }
  
    applyDatefilter(){
      // const format = 'yyyy-MM';
      // const locale = 'en-US';
      // try {
      //  this.stringDate = '?ftdate=' + formatDate(this.selectDate.toLocaleDateString(), format, locale);
      //  console.log(this.stringDate)
      //  this.getInvoiceData()
      // }
      // catch (error) {
      //   this.stringDate = '';
      //   this.getInvoiceData(this.stringDate)
      // }
    }
  
  
    confirm(event: Event) {
      console.log("data")
      this.confirmationService.confirm({
        target: event.target,
        message: "Are you sure that you want to proceed?",
        icon: "pi pi-exclamation-triangle",
        accept: () => {
          this.messageService.add({
            severity: "info",
            summary: "Confirmed",
            detail: "You have accepted"
          });
        },
        reject: () => {
          this.messageService.add({
            severity: "error",
            summary: "Rejected",
            detail: "You have rejected"
          });
        }
      });
    }
  
}
