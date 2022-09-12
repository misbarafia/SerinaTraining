
import { SharedService } from './../../services/shared.service';
import { PermissionService } from './../../services/permission.service';
import { Router } from '@angular/router';
import { TaggingService } from './../../services/tagging.service';
import { Component, OnInit, ViewChild } from '@angular/core';
import { ImportExcelService } from 'src/app/services/importExcel/import-excel.service';
import { Table } from 'primeng/table';
import { DateFilterService } from 'src/app/services/date/date-filter.service';
import { MessageService } from 'primeng/api';
import { NgxSpinnerService } from 'ngx-spinner';
import { DataService } from 'src/app/services/dataStore/data.service';

@Component({
  selector: 'app-approve',
  templateUrl: './approve.component.html',
  styleUrls: [
    './approve.component.scss',
    './../invoice/all-invoices/all-invoices.component.scss',
  ],
})
export class ApproveComponent implements OnInit {
  invoiceListBoolean: boolean = true;
  editPermissionBoolean: boolean;

  @ViewChild('approve') approve: Table;

  users;
  approvedData: any[];
  approvedDataSP: any[];
  ApprovedColumn = [
    { field: 'docheaderID', header: 'Invoice Number' },
    { field: 'VendorName', header: 'Vendor Name' },
    { field: 'Account', header: 'Vendor A/C' },
    // { field: 'documentdescription', header: 'Description' },
    { field: 'Approvaltype', header: 'Approval type' },
    { field: 'documentDate', header: 'Invoice Date' },
    { field: 'UpdatedOn', header: 'Last Modified' },
    { field: 'totalAmount', header: 'Amount' },
  ];
  ApprovedColumnSP = [
    { field: 'docheaderID', header: 'Invoice Number' },
    { field: 'ServiceProviderName', header: 'Service provider Name' },
    { field: 'Account', header: 'Service provider A/C' },
    { field: 'documentdescription', header: 'Description' },
    { field: 'documentDate', header: 'Invoice Date' },
    { field: 'UpdatedOn', header: 'Last Modified' },
    { field: 'totalAmount', header: 'Amount' },
  ];
  approvedColumnHeader = [];
  approvedColumnField = [];
  showPaginatorApproved: boolean;
  approvedDataLength: number;
  approvedColumnHeaderSP = [];
  approvedColumnFieldSP = [];
  showPaginatorApprovedSP: boolean;
  approvedDataLengthSP: number;
  allSearchInvoiceString: any = [];

  rangeDates: Date[];
  minDate: Date;
  maxDate: Date;
  viewType: any;
  first: any;
  rows: any;
  first_service: any;
  rows_service: any;
  ColumnLengthVendor: number;
  ColumnLengthSP: number;
  dashboardViewBoolean: boolean;

  constructor(
    private tagService: TaggingService,
    private router: Router,
    private sharedService: SharedService,
    private dateFilterService: DateFilterService,
    private messageService: MessageService,
    private SpinnerService: NgxSpinnerService,
    private storageService: DataService,
    private permissionService: PermissionService,
    private ImportExcelService: ImportExcelService
  ) {}

  ngOnInit(): void {
    this.init();
    this.readInvoiceApprovedData();
    this.readServiceInvoiceData();
    this.findColumns();
    this.dateRange();
  }

  init() {
    this.editPermissionBoolean = this.permissionService.editBoolean;
    this.tagService.headerName = 'Finance Approval';
    this.viewType = this.tagService.aprrovalPageTab;
    this.first = this.storageService.approvalVendorPaginationFirst;
    this.rows = this.storageService.approvalVendorPaginationRowLength;
    this.first_service = this.storageService.approvalServicePaginationFirst;
    this.rows_service = this.storageService.approvalServicePaginationRowLength;
    if (this.router.url.includes('home')) {
      this.dashboardViewBoolean = true;
    } else {
      this.dashboardViewBoolean = false;
    }
  }

  findColumns() {
    this.ApprovedColumn.forEach((e) => {
      this.approvedColumnHeader.push(e.header);
      this.approvedColumnField.push(e.field);
    });
    this.ApprovedColumnSP.forEach((e) => {
      this.approvedColumnHeaderSP.push(e.header);
      this.approvedColumnFieldSP.push(e.field);
    });
    this.ColumnLengthVendor = this.ApprovedColumn.length + 1;
    this.ColumnLengthSP = this.ApprovedColumnSP.length + 1;

    // console.log(this.ColumnLengthVendor,this.ColumnLengthSP)
  }

  dateRange() {
    this.dateFilterService.dateRange();
    this.minDate = this.dateFilterService.minDate;
    this.maxDate = this.dateFilterService.maxDate;
  }

  chooseApprovalpageTab(value) {
    this.viewType = value;
    this.tagService.aprrovalPageTab = value;
    this.allSearchInvoiceString = [];
  }

  viewInvoice(e) {
    this.router.navigate(['customer/approved/InvoiceDetails/' + e.idDocument]);
    this.invoiceListBoolean = false;
    this.tagService.editable = false;
  }
  editInvoice(e) {
    if (this.permissionService.financeApproveBoolean == true) {
      this.router.navigate([
        'customer/approved/InvoiceDetails/' + e.idDocument,
      ]);
      this.invoiceListBoolean = false;
      this.tagService.editable = true;
      this.tagService.financeApprovePermission = true;
      this.sharedService.invoiceID = e.idDocument;
    } else {
      alert('Do not have access to finance approve');
    }
  }
  backToInvoice() {
    this.invoiceListBoolean = true;
  }
  readInvoiceApprovedData() {
    this.SpinnerService.show();
    this.sharedService.readApprovedInvoiceData().subscribe(
      (data: any) => {
        let approvedArray = [];
        data.approved.forEach((element) => {
          let mergeArray = {
            ...element.Entity,
            ...element.EntityBody,
            ...element.FinancialApproval,
            ...element.Document,
            ...element.User,
            ...element.Vendor,
            ...element.VendorAccount,
          };
          mergeArray.documentdescription = element.documentdescription;
          mergeArray.Approvaltype = element.Approvaltype;
          approvedArray.push(mergeArray);
        });
        this.approvedData = approvedArray;
        this.approvedDataLength = this.approvedData.length;
        if (this.approvedData.length > 10) {
          this.showPaginatorApproved = true;
        }
        this.SpinnerService.hide();
      },
      (error) => {
        this.SpinnerService.hide();
      }
    );
  }

  readServiceInvoiceData() {
    this.SpinnerService.show();
    this.sharedService.readApprovedSPInvoiceData().subscribe(
      (data: any) => {
        let approvedArray = [];
        data.approved.forEach((element) => {
          let mergeArray = {
            ...element.Entity,
            ...element.EntityBody,
            ...element.Document,
            ...element.User,
            ...element.ServiceProvider,
            ...element.ServiceAccount,
          };
          mergeArray.documentdescription = element.documentdescription;
          approvedArray.push(mergeArray);
        });
        this.approvedDataSP = approvedArray;
        this.approvedDataLengthSP = this.approvedDataSP.length;
        if (this.approvedDataLengthSP > 10) {
          this.showPaginatorApprovedSP = true;
        }
        this.SpinnerService.hide();
      },
      (error) => {
        this.SpinnerService.hide();
      }
    );
  }

  paginateService(event) {
    console.log(event);
    this.first_service = event.first;
    this.storageService.approvalServicePaginationFirst = this.first_service;
    this.storageService.approvalServicePaginationRowLength = event.rows;
  }

  paginateVendor(event) {
    console.log(event);
    this.first = event.first;
    this.storageService.approvalVendorPaginationFirst = this.first;
    this.storageService.approvalVendorPaginationRowLength = event.rows;
  }

  searchImport(value) {
    this.allSearchInvoiceString = this.approve.filteredValue;
  }
  exportExcel() {
    let exportData = [];
    if (this.tagService.aprrovalPageTab == 'vendorInvoice') {
      exportData = this.approvedData;
    } else {
      exportData = this.approvedDataSP;
    }
    if (this.allSearchInvoiceString && this.allSearchInvoiceString.length > 0) {
      this.ImportExcelService.exportExcel(this.allSearchInvoiceString);
    } else if (exportData && exportData.length > 0) {
      this.ImportExcelService.exportExcel(exportData);
    } else {
      alert('No Data to import');
    }
  }
}
