import { DataService } from './../../services/dataStore/data.service';
import { AlertService } from './../../services/alert/alert.service';
import { ImportExcelService } from './../../services/importExcel/import-excel.service';
import { MessageService } from 'primeng/api';
import { PermissionService } from './../../services/permission.service';

import { Router } from '@angular/router';
import { SharedService } from 'src/app/services/shared.service';
import { TaggingService } from './../../services/tagging.service';
import { Component, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { Table } from 'primeng/table';
import { DateFilterService } from 'src/app/services/date/date-filter.service';
import { NgxSpinnerService } from 'ngx-spinner';

@Component({
  selector: 'app-edited',
  templateUrl: './edited.component.html',
  styleUrls: [
    './edited.component.scss',
    './../invoice/all-invoices/all-invoices.component.scss',
  ],
})
export class EditedComponent implements OnInit, OnDestroy {
  showPaginator: boolean = false;
  invoiceListBoolean: boolean = true;
  users = [];
  EditedinvoiceDispalyData: any;
  allEditedInvoiceLength: any;
  inprogressData: any;
  inprogressLength: number;
  tobeApprovedData: any;
  tobeApprovedLength: number;
  @ViewChild('edit') edit: Table;
  @ViewChild('editIn') editIn: Table;
  @ViewChild('editApprove') editApprove: Table;

  viewType: string;
  cols: any;
  showPaginatorInvoice: boolean;
  showPaginatorInprogress: boolean;
  showPaginatortobeApprove: boolean;
  invoiceEditedColumn = [
    { field: 'docheaderID', header: 'Invoice Number' },
    { field: 'VendorName', header: 'Vendor Name' },
    { field: 'Account', header: 'Vendor A/C' },
    { field: 'documentdescription', header: 'Description' },
    { field: 'documentDate', header: 'Invoice Date' },
    { field: 'UpdatedOn', header: 'Last Modified' },
    { field: 'totalAmount', header: 'Amount' },
  ];
  inprogessColumn = [
    { field: 'docheaderID', header: 'Invoice Number' },
    { field: 'assigned_to', header: 'Assigned To' },
    { field: 'VendorName', header: 'Vendor Name' },
    { field: 'Account', header: 'Vendor A/C' },
    { field: 'documentdescription', header: 'Description' },
    { field: 'documentDate', header: 'Invoice Date' },
    { field: 'UpdatedOn', header: 'Last Modified' },
    { field: 'totalAmount', header: 'Amount' },
  ];
  tobeApprovedColumn = [
    { field: 'docheaderID', header: 'Invoice Number' },
    { field: 'edited_by', header: 'Edited By' },
    { field: 'VendorName', header: 'Vendor Name' },
    { field: 'Account', header: 'Vendor A/C' },
    { field: 'documentdescription', header: 'Description' },
    { field: 'documentDate', header: 'Invoice Date' },
    { field: 'UpdatedOn', header: 'Last Modified' },
    { field: 'totalAmount', header: 'Amount' },
  ];
  invoiceColumnField = [];
  inprogressColumnField = [];
  toBeApproveColumnField = [];
  invoiceColumnHeader = [];
  inprogressColumnHeader = [];
  toBeApproveColumnHeader = [];

  editPermissionBoolean: boolean;
  changeApproveBoolean: boolean;
  allSearchInvoiceString: unknown[];

  rangeDates: Date[];
  minDate: any;
  maxDate: any;
  heading: string;
  dashboardViewBoolean: boolean;

  constructor(
    private tagService: TaggingService,
    private sharedService: SharedService,
    private permissionService: PermissionService,
    private dateFilterService: DateFilterService,
    private messageService: MessageService,
    private SpinnerService: NgxSpinnerService,
    private alertService: AlertService,
    private ImportExcelService: ImportExcelService,
    private dataService: DataService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.viewType = this.tagService.editedTabValue;
    this.addPermissions();
    // this.getEditedInvoiceData();
    this.tagService.type = 'Invoice';
    this.prepareColumnsArray();
    this.dateRange();
    this.findRoute();
  }

  findRoute() {
    if (
      this.router.url.includes(
        'ExceptionManagement/Service_ExceptionManagement'
      )
    ) {
      this.columnsBasedOnRoute();
      this.heading = 'Service based OCR Exceptions';
      this.getServiceInvoiceData();
    } else {
      this.heading = 'PO based OCR Exceptions';
      this.getEditedInvoiceData();
    }
    if (this.router.url.includes('home')) {
      this.dashboardViewBoolean = true;
    } else {
      this.dashboardViewBoolean = false;
    }
  }

  dateRange() {
    this.dateFilterService.dateRange();
    this.minDate = this.dateFilterService.minDate;
    this.maxDate = this.dateFilterService.maxDate;
  }

  columnsBasedOnRoute() {
    this.invoiceEditedColumn = [
      { field: 'docheaderID', header: 'Invoice Number' },
      { field: 'ServiceProviderName', header: 'Serviceprovider Name' },
      { field: 'Account', header: 'Serviceprovider A/C' },
      { field: 'documentdescription', header: 'Description' },
      { field: 'documentDate', header: 'Invoice Date' },
      { field: 'UpdatedOn', header: 'Last Modified' },
      { field: 'totalAmount', header: 'Amount' },
    ];
    this.inprogessColumn = [
      { field: 'docheaderID', header: 'Invoice Number' },
      { field: 'assigned_to', header: 'Assigned To' },
      { field: 'ServiceProviderName', header: 'Serviceprovider Name' },
      { field: 'Account', header: 'Serviceprovider A/C' },
      { field: 'documentdescription', header: 'Description' },
      { field: 'documentDate', header: 'Invoice Date' },
      { field: 'UpdatedOn', header: 'Last Modified' },
      { field: 'totalAmount', header: 'Amount' },
    ];
    this.tobeApprovedColumn = [
      { field: 'docheaderID', header: 'Invoice Number' },
      { field: 'edited_by', header: 'Edited By' },
      { field: 'ServiceProviderName', header: 'Serviceprovider Name' },
      { field: 'Account', header: 'Serviceprovider A/C' },
      { field: 'documentdescription', header: 'Description' },
      { field: 'documentDate', header: 'Invoice Date' },
      { field: 'UpdatedOn', header: 'Last Modified' },
      { field: 'totalAmount', header: 'Amount' },
    ];

    this.invoiceEditedColumn.filter((element) => {
      this.invoiceColumnHeader.push(element.header);
      this.invoiceColumnField.push(element.field);
    });

    this.inprogessColumn.forEach((e) => {
      this.inprogressColumnHeader.push(e.header);
      this.inprogressColumnField.push(e.field);
    });

    this.tobeApprovedColumn.forEach((e1) => {
      this.toBeApproveColumnHeader.push(e1.header);
      this.toBeApproveColumnField.push(e1.field);
    });
  }

  // to prepare display columns array
  prepareColumnsArray() {
    this.invoiceEditedColumn.filter((element) => {
      this.invoiceColumnHeader.push(element.header);
      this.invoiceColumnField.push(element.field);
    });

    this.inprogessColumn.forEach((e) => {
      this.inprogressColumnHeader.push(e.header);
      this.inprogressColumnField.push(e.field);
    });

    this.tobeApprovedColumn.forEach((e1) => {
      this.toBeApproveColumnHeader.push(e1.header);
      this.toBeApproveColumnField.push(e1.field);
    });
  }

  // get Disaplyed edited page data
  getEditedInvoiceData() {
    this.SpinnerService.show();
    this.sharedService.readEditedInvoiceData().subscribe(
      (data: any) => {
        let invoiceArray = [];
        data.invoices.forEach((element) => {
          let invoices = {
            ...element.Document,
            ...element.DocumentHistoryLogs,
            ...element.Vendor,
            ...element.VendorAccount,
          };
          invoiceArray.push(invoices);
        });
        this.EditedinvoiceDispalyData = invoiceArray;
        this.allEditedInvoiceLength = this.EditedinvoiceDispalyData.length;
        if (this.EditedinvoiceDispalyData.length > 10) {
          this.showPaginatorInvoice = true;
        }

        let inprogressArray = [];
        data.inprogress.forEach((element) => {
          let inprogress = {
            ...element.Document,
            ...element.DocumentHistoryLogs,
            ...element.Vendor,
            ...element.VendorAccount,
          };
          inprogress.assigned_to = element.assigned_to;
          inprogressArray.push(inprogress);
        });
        this.inprogressData = inprogressArray;
        this.inprogressLength = this.inprogressData.length;
        if (this.inprogressData.length > 10) {
          this.showPaginatorInprogress = true;
        }

        let tobeApprovedArray = [];
        data.tobeapproved.forEach((element) => {
          let tobeApprove = {
            ...element.Document,
            ...element.DocumentHistoryLogs,
            ...element.Vendor,
            ...element.VendorAccount,
          };
          tobeApprove['edited_by'] = element['edited_by'];
          tobeApprovedArray.push(tobeApprove);
        });
        this.tobeApprovedData = tobeApprovedArray;
        this.tobeApprovedLength = this.tobeApprovedData.length;
        if (this.tobeApprovedData.length > 10) {
          this.showPaginatortobeApprove = true;
        }
        this.SpinnerService.hide();
      },
      (error) => {
        alert(error.statusText);
        this.SpinnerService.hide();
      }
    );
  }

  getServiceInvoiceData() {
    this.SpinnerService.show();
    this.sharedService.readEditedServiceInvoiceData().subscribe(
      (data: any) => {
        let invoiceArray = [];
        data.invoices.forEach((element) => {
          let invoices = {
            ...element.Document,
            ...element.DocumentHistoryLogs,
            ...element.ServiceProvider,
            ...element.ServiceAccount,
          };
          invoiceArray.push(invoices);
        });
        this.EditedinvoiceDispalyData = invoiceArray;
        this.allEditedInvoiceLength = this.EditedinvoiceDispalyData.length;
        if (this.EditedinvoiceDispalyData.length > 10) {
          this.showPaginatorInvoice = true;
        }

        let inprogressArray = [];
        data.inprogress.forEach((element) => {
          let inprogress = {
            ...element.Document,
            ...element.DocumentHistoryLogs,
            ...element.ServiceProvider,
            ...element.ServiceAccount,
          };
          inprogress.assigned_to = element.assigned_to;
          inprogressArray.push(inprogress);
        });
        this.inprogressData = inprogressArray;
        this.inprogressLength = this.inprogressData.length;
        if (this.inprogressData.length > 10) {
          this.showPaginatorInprogress = true;
        }

        let tobeApprovedArray = [];
        data.tobeapproved.forEach((element) => {
          let tobeApprove = {
            ...element.Document,
            ...element.DocumentHistoryLogs,
            ...element.ServiceProvider,
            ...element.ServiceAccount,
          };
          tobeApprove['edited_by'] = element['edited_by'];
          tobeApprovedArray.push(tobeApprove);
        });
        this.tobeApprovedData = tobeApprovedArray;
        this.tobeApprovedLength = this.tobeApprovedData.length;
        if (this.tobeApprovedData.length > 10) {
          this.showPaginatortobeApprove = true;
        }
        this.SpinnerService.hide();
      },
      (error) => {
        alert(error.statusText);
        this.SpinnerService.hide();
      }
    );
  }
  chooseEditedpageTab(value) {
    this.viewType = value;
    this.tagService.editedTabValue = value;
  }

  // to see Invoice details
  viewInvoice(e) {
    this.router.navigate([
      'customer/ExceptionManagement/InvoiceDetails/' + e.idDocument,
    ]);
    this.sharedService.invoiceID = e.idDocument;
    this.invoiceListBoolean = false;
    this.tagService.editable = false;
  }

  // edit invoice details if something wrong
  editInvoice(e, value) {
    if (value == 'submit') {
      if (this.permissionService.editBoolean == true) {
        this.router.navigate([
          'customer/ExceptionManagement/InvoiceDetails/' + e.idDocument,
        ]);
        this.invoiceListBoolean = false;
        this.tagService.editable = true;
        this.sharedService.invoiceID = e.idDocument;
        this.tagService.submitBtnBoolean = true;
        this.tagService.headerName = 'Edit Invoice';
      } else {
        alert('Do not have access to edit');
      }
    } else if (value == 'approve') {
      if (this.permissionService.changeApproveBoolean == true) {
        this.router.navigate([
          'customer/ExceptionManagement/InvoiceDetails/' + e.idDocument,
        ]);
        this.invoiceListBoolean = false;
        this.tagService.editable = true;
        this.sharedService.invoiceID = e.idDocument;
        this.tagService.approveBtnBoolean = true;
        this.tagService.headerName = 'Approve Invoice';
      } else {
        alert('Do not have Permission to Approve');
      }
    }
  }

  backToInvoice() {
    this.invoiceListBoolean = true;
  }

  addPermissions() {
    this.editPermissionBoolean = this.permissionService.editBoolean;
  }

  assignInvoice(inv_id) {
    this.SpinnerService.show();
    this.sharedService.assignInvoiceTo(inv_id).subscribe(
      (data: any) => {
        this.findRoute();
        if (data.result == 'updated') {
          this.alertService.updateObject.detail =
            'Invoice assigned to you successfully';
          this.messageService.add(this.alertService.updateObject);
          this.dataService.invoiceLoadedData = [];
        } else {
          this.messageService.add(this.alertService.errorObject);
        }
        this.SpinnerService.hide();
      },
      (error) => {
        alert(error.statusText);
        this.SpinnerService.hide();
      }
    );
  }
  searchInvoiceDataV(value) {
    this.allSearchInvoiceString = this.edit.filteredValue;
  }
  searchImporteditIN(value) {
    // console.log(value)
    // console.log(this.editIn);
    this.allSearchInvoiceString = this.editIn.filteredValue;
  }
  searchImporteditApprove(value) {
    this.allSearchInvoiceString = this.editApprove.filteredValue;
    // this.tobeApprovedData.filter(ele =>{
    //   console.log(ele.keys)
    // })
    // console.log(this.editApprove);
  }
  exportExcel() {
    console.log(this.editIn.filteredValue);
    let exportData = [];
    if (this.tagService.editedTabValue == 'invoice') {
      exportData = this.EditedinvoiceDispalyData;
    } else if (this.tagService.editedTabValue == 'Inprogess') {
      exportData = this.inprogressData;
    } else {
      exportData = this.tobeApprovedData;
    }
    if (this.allSearchInvoiceString && this.allSearchInvoiceString.length > 0) {
      this.ImportExcelService.exportExcel(this.allSearchInvoiceString);
    } else if (exportData && exportData.length > 0) {
      this.ImportExcelService.exportExcel(exportData);
    } else {
      alert('No Data to import');
    }
  }

  toggleRejection(popover, comments: string[]) {
    if (popover.isOpen()) {
      popover.close();
    } else {
      popover.open({ comments: comments });
    }
  }
  ngOnDestroy() {
    // this.tagService.editedTabValue = 'invoice'
  }
}
