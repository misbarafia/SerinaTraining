import { PermissionService } from './../../../services/permission.service';
import { Router } from '@angular/router';
import { MessageService } from 'primeng/api';
import { AlertService } from './../../../services/alert/alert.service';
import { ExceptionsService } from './../../../services/exceptions/exceptions.service';
import { ImportExcelService } from './../../../services/importExcel/import-excel.service';
import { TaggingService } from './../../../services/tagging.service';
import { Component, OnInit } from '@angular/core';
import { NgxSpinnerService } from 'ngx-spinner';
import { Location } from '@angular/common';

@Component({
  selector: 'app-batch-process',
  templateUrl: './batch-process.component.html',
  styleUrls: ['./batch-process.component.scss'],
})
export class BatchProcessComponent implements OnInit {
  ColumnsForBatch = [
    { field: 'docheaderID', header: 'Invoice Number' },
    { field: 'VendorName', header: 'Vendor Name' },
    // { field: 'Name', header: 'Rule' },
    { field: 'CreatedOn', header: 'Date' },
    { field: 'PODocumentID', header: 'PO number' },
    { field: 'status', header: 'Status' },
    { field: 'totalAmount', header: 'Amount' },
  ];
  columnsData = [];
  showPaginatorAllInvoice: boolean;
  columnsToDisplay = [];

  ColumnsForBatchApproval = [
    { field: 'docheaderID', header: 'Invoice Number' },
    { field: 'VendorName', header: 'Vendor Name' },
    { field: 'Name', header: 'Rule' },
    // { field: 'documentdescription', header: 'Description' },
    // { field: 'All_Status', header: 'Status' },
    { field: 'Approvaltype', header: 'Approval Type' },
    { field: 'totalAmount', header: 'Amount' },
  ];
  columnsToDisplayBatchApproval = [];
  viewType: any;
  allSearchInvoiceString: any[];
  rangeDates: Date[];
  dataLength: number;
  columnsDataAdmin: any[];
  showPaginatorApproval: boolean;
  dataLengthAdmin: number;
  batchProcessColumnLength: number;
  approvalPageColumnLength: number;
  dashboardViewBoolean: boolean;
  constructor(
    private tagService: TaggingService,
    private ImportExcelService: ImportExcelService,
    private ngxSpinner: NgxSpinnerService,
    private MessageService: MessageService,
    private alertService: AlertService,
    private router: Router,
    private exceptionService: ExceptionsService,
    private permissionService : PermissionService,
    private _location :Location
  ) {}

  ngOnInit(): void {
    if(this.permissionService.excpetionPageAccess == true){

      this.viewType = this.tagService.batchProcessTab;
      if (this.router.url.includes('home')) {
        this.dashboardViewBoolean = true;
      } else {
        this.dashboardViewBoolean = false;
      }
      this.prepareColumnsArray();
      this.getBatchInvoiceData();
      // this.getApprovalBatchData();
    } else{
      alert("Sorry!, you do not have access");
      this.router.navigate(['customer/invoice/allInvoices'])
    }

  }

  // to prepare display columns array
  prepareColumnsArray() {
    if (this.dashboardViewBoolean == true) {
      this.ColumnsForBatch = this.ColumnsForBatch.filter((ele) => {
        return ele.header != 'Status';
      });
    }
    this.ColumnsForBatch.filter((element) => {
      this.columnsToDisplay.push(element.field);
      // this.invoiceColumnField.push(element.field)
    });
    this.ColumnsForBatchApproval.filter((ele) => {
      this.columnsToDisplayBatchApproval.push(ele.field);
    });

    this.batchProcessColumnLength = this.ColumnsForBatch.length + 1;
    this.approvalPageColumnLength = this.ColumnsForBatchApproval.length + 1;
  }

  chooseEditedpageTab(value) {
    this.viewType = value;
    this.tagService.batchProcessTab = value;
    this.allSearchInvoiceString = [];
  }

  searchInvoiceDataV(value) {
    // this.allSearchInvoiceString = []
    this.allSearchInvoiceString = value.filteredValue;
  }

  getBatchInvoiceData() {
    this.ngxSpinner.show();
    this.exceptionService.readBatchInvoicesData().subscribe(
      (data: any) => {
        const batchData = [];
        data.forEach((element) => {
          let mergeData = {
            ...element.Document,
            ...element.DocumentSubStatus,
            ...element.Rule,
            ...element.Vendor,
          };
          batchData.push(mergeData);
        });
        this.columnsData = batchData.sort((a,b)=>{
          let c = new Date(a.CreatedOn).getTime();
          let d = new Date(b.CreatedOn).getTime();
          return d-c });
        this.dataLength = this.columnsData.length;
        if (this.dataLength > 10) {
          this.showPaginatorAllInvoice = true;
        }
        this.ngxSpinner.hide();
      },
      (error) => {
        this.ngxSpinner.hide();
        this.alertService.errorObject.detail = error.statusText;
        this.MessageService.add(this.alertService.errorObject);
      }
    );
  }

  // getApprovalBatchData() {
  //   this.ngxSpinner.show();
  //   this.exceptionService.readApprovalBatchInvoicesData().subscribe(
  //     (data: any) => {
  //       const batchData = [];
  //       data.forEach((element) => {
  //         let mergeData = {
  //           ...element.Document,
  //           ...element.DocumentSubStatus,
  //           ...element.Rule,
  //           ...element.Vendor,
  //           ...element.DocumentRuleupdates,
  //         };
  //         mergeData.Approvaltype = element.Approvaltype;
  //         batchData.push(mergeData);
  //       });
  //       this.columnsDataAdmin = batchData;
  //       this.dataLengthAdmin = this.columnsDataAdmin.length;
  //       if (this.dataLengthAdmin > 10) {
  //         this.showPaginatorApproval = true;
  //       }
  //       this.ngxSpinner.hide();
  //     },
  //     (error) => {
  //       this.ngxSpinner.hide();
  //       this.alertService.errorObject.detail = error.statusText;
  //       this.MessageService.add(this.alertService.errorObject);
  //     }
  //   );
  // }
  exportExcel() {
    let exportData = [];
    if (this.tagService.batchProcessTab == 'normal') {
      exportData = this.columnsData;
    } else if (this.tagService.batchProcessTab == 'editApproveBatch') {
      exportData = this.columnsDataAdmin;
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
