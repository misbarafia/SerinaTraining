import { Router } from '@angular/router';
import { ServiceInvoiceService } from './../../../services/serviceBased/service-invoice.service';
import { AlertService } from './../../../services/alert/alert.service';
import { ExceptionsService } from './../../../services/exceptions/exceptions.service';
import { ImportExcelService } from './../../../services/importExcel/import-excel.service';
import { TaggingService } from './../../../services/tagging.service';
import { Component, OnInit } from '@angular/core';
import { NgxSpinnerService } from 'ngx-spinner';
import { MessageService } from 'primeng/api';
import { PermissionService } from 'src/app/services/permission.service';

@Component({
  selector: 'app-invoke-batch',
  templateUrl: './invoke-batch.component.html',
  styleUrls: [
    './invoke-batch.component.scss',
    '../../edited/edited.component.scss',
  ],
})
export class InvokeBatchComponent implements OnInit {
  ColumnsForInvokeBatch = [
    { field: 'PODocumentID', header: 'PO Number' },
    { field: 'docheaderID', header: 'Invoice Number' },
    { field: 'VendorName', header: 'Vendor Name' },
    { field: 'documentDate', header: 'Date' },
    { field: 'prvBatch', header: 'Prev Batch' },
    { field: 'Name', header: 'Selected rule' },
  ];
  columnsData = [];
  showPaginatorAllInvoice: boolean;
  columnsToDisplayInvoke = [];

  viewType: any;
  allSearchInvoiceString: any[];
  rangeDates: Date[];
  dataLength: number;
  showInvokeBtnBoolean: boolean;
  invokeBatchColumnLength: number;
  entity: any;
  selectedEntityId: any;
  erpTriggerBoolean: boolean;

  totalTableData = [];
  columnsForTotal = [];
  totalColumnHeader = [];
  totalColumnField = [];
  ColumnLengthtotal: any;
  showPaginatortotal: boolean;

  constructor(
    private tagService: TaggingService,
    private exceptionService: ExceptionsService,
    private ngxSpinner: NgxSpinnerService,
    private MessageService: MessageService,
    private alertService: AlertService,
    private router : Router,
    private ImportExcelService: ImportExcelService,
    private permissionService : PermissionService,
    private serviceProviderService : ServiceInvoiceService,
  ) {}

  ngOnInit(): void {
    if(this.permissionService.serviceTriggerBoolean === true) {
      this.viewType = this.tagService.InvokebatchProcessTab;
      this.prepareColumns();
      // this.readBatchData();
      this.tableDataForBatch();
      this.getEntitySummary();
    } else {
      this.router.navigate(['/customer/serviceProvider']);
      alert("Sorry, you do not have access");
    }

  }

  // to prepare display columns array
  prepareColumns() {
    this.columnsForTotal = [
      // { field: 'VendorName', header: 'Vendor Name' },
      // { field: 'docheaderID', header: 'Invoice Number' },
      // { field: 'PODocumentID', header: 'PO Number' },
      { field: 'EntityName', header: 'Entity' },
      { field: 'started_on', header: 'Started time' },
      { field: 'compeleted_on', header: 'End time' },
      { field: 'status', header: 'Status' },
    ];

    this.columnsForTotal.forEach((e) => {
      this.totalColumnHeader.push(e.header);
      this.totalColumnField.push(e.field);
    });

    this.ColumnLengthtotal = this.columnsForTotal.length;
  }
  chooseEditedpageTab(value) {
    this.viewType = value;
    this.tagService.InvokebatchProcessTab = value;
  }
  searchInvoiceDataV(value) {
    this.allSearchInvoiceString = [];
    this.allSearchInvoiceString = value.filteredValue;
  }

  exportExcel() {
    if (this.allSearchInvoiceString && this.allSearchInvoiceString.length > 0) {
      this.ImportExcelService.exportExcel(this.allSearchInvoiceString);
    } else if (this.columnsData && this.columnsData.length > 0) {
      this.ImportExcelService.exportExcel(this.columnsData);
    } else {
      alert('No Data to import');
    }
  }

  readBatchData() {
    this.ngxSpinner.show();
    this.exceptionService.readInvokeBatchData().subscribe(
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
        this.columnsData = batchData;
        this.dataLength = this.columnsData.length;
        if (this.dataLength > 10) {
          this.showPaginatorAllInvoice = true;
        }
        if (this.dataLength > 0) {
          this.showInvokeBtnBoolean = true;
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


  getEntitySummary() {
    this.serviceProviderService.getSummaryEntity().subscribe((data: any) => {
      this.entity = data.result;
    });
  }

  selectEntity(value){
    this.selectedEntityId = value;
    this.erpTriggerBoolean = true;
  }

  triggerBatch(){
    let triggerData = {
      "entity_ids": [
        this.selectedEntityId
      ]
    }
    this.serviceProviderService.triggerBatch(triggerData).subscribe(data=>{
      this.alertService.addObject.detail = data.result;
      this.MessageService.add(this.alertService.addObject);
    },err=>{
      this.alertService.errorObject.detail = "Server error"
      this.MessageService.add(this.alertService.errorObject);
    })
  }

  tableDataForBatch(){
    this.serviceProviderService.triggerBatchHistory().subscribe((data:any)=>{
      const batchData = [];
        data.result.forEach((element) => {
          let mergeData = {
            ...element.BatchTriggerHistory
          };
          mergeData.EntityName = element.EntityName
          batchData.push(mergeData);
        });
        this.totalTableData = batchData;
        if (this.totalTableData.length > 10) {
          this.showPaginatortotal = true;
        }
    })
  }
}
