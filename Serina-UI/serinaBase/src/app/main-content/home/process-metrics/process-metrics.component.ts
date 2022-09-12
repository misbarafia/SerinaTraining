import { DatePipe } from '@angular/common';
import { Component, Input, OnInit } from '@angular/core';
import { NgxSpinnerService } from 'ngx-spinner';
import { ChartsService } from 'src/app/services/dashboard/charts.service';
import { DateFilterService } from 'src/app/services/date/date-filter.service';
import { ImportExcelService } from 'src/app/services/importExcel/import-excel.service';
@Component({
  selector: 'process-metrics',
  templateUrl: './process-metrics.component.html',
  styleUrls: ['./process-metrics.component.scss']
})
export class ProcessMetricsComponent implements OnInit {
  @Input() exceptionData:any;
  totalInv: number;
  UnderProcessInv: number;
  PostedInv: number;
  CollectionsInv: number;
  RejectedInv: number;

  tabName;
  totalTableData = [];
  columnsForTotal = [];
  totalColumnHeader = [];
  totalColumnField = [];
  ColumnLengthtotal: any;
  showPaginatortotal: boolean;

  UnderProcessTableData = [];
  columnsForUnderProcess = [];
  UnderProcessColumnHeader = [];
  UnderProcessColumnField = [];
  ColumnLengthUnderProcess: any;
  showPaginatorUnderProcess: boolean;

  PostedTableData = [];
  columnsForPosted = [];
  PostedColumnHeader = [];
  PostedColumnField = [];
  ColumnLengthPosted: any;
  showPaginatorPosted: boolean;

  CollectionsTableData = [];
  columnsForCollections = [];
  CollectionsColumnHeader = [];
  CollectionsColumnField = [];
  ColumnLengthCollections: any;
  showPaginatorCollections: boolean;

  RejectedTableData = [];
  columnsForRejected = [];
  RejectedColumnHeader = [];
  RejectedColumnField = [];
  ColumnLengthRejected: any;
  showPaginatorRejected: boolean;

  minDate: Date;
  maxDate: Date;
  rangeDates: Date[];
  filterDataTotal: any[];
  filterDataUnderProcess: any[];
  filterDataPosted: any[];
  filterDataCollections: any[];
  filterDataRejected: any[];
  constructor(
    private chartsService: ChartsService,
    private SpinnerService: NgxSpinnerService,
    private ImportExcelService: ImportExcelService,
    private dateFilterService: DateFilterService,
    private datePipe: DatePipe,
  ) {}
  // ngOnChanges(changes: SimpleChanges): void {
  //   if (changes.exceptionData &&  changes.exceptionData.currentValue && changes.exceptionData.currentValue.data) {
  //     this.readExceptionData(this.exceptionData);
  //   }
  // }

  ngOnInit(): void {
    // this.tagService.editedTabValue = 'invoice';
    // this.tagService.aprrovalPageTab = 'vendorInvoice';
    // this.tagService.PostedProcessTab = 'normal';
    this.tabName = this.chartsService.exceptionVendorTab;
    this.dateRange();
    this.prepareColumns();
    this.readInvoicedData('');
    this.readTotalInvoiceData('');
    this.readUnderProcessData('');
    this.readCollectionsData('');
    this.readRejectedData('');

  }
  choosepageTab(value) {
    // this.filterByDate('');
    // delete this.rangeDates;
    this.tabName = value;
    console.log(value)
    this.chartsService.exceptionVendorTab = value;
        // this.totalTableData = this.filterDataTotal;
        // this.totalInv = this.totalTableData.length;
        // this.UnderProcessTableData = this.filterDataUnderProcess ;
        // this.UnderProcessInv = this.UnderProcessTableData.length;
        // this.PostedTableData  = this.filterDataPosted;
        // this.PostedInv = this.PostedTableData.length;
        // this.CollectionsTableData = this.filterDataCollections ;
        // this.CollectionsInv = this.CollectionsTableData.length;
        // this.RejectedTableData = this.filterDataRejected ;
        // this.RejectedInv = this.RejectedTableData.length;
  }

  prepareColumns() {
    this.columnsForTotal = [
      // { field: 'VendorName', header: 'Vendor Name' },
      { field: 'docheaderID', header: 'Invoice Number' },
      { field: 'PODocumentID', header: 'PO Number' },
      { field: 'EntityName', header: 'Entity' },
      { field: 'documentDate', header: 'Invoice Date' },
      { field: 'totalAmount', header: 'Amount' },
      // { field: 'sourcetype', header: 'source' },
    ];

    this.columnsForUnderProcess = [
      // { field: 'VendorName', header: 'Vendor Name' },
      { field: 'docheaderID', header: 'Invoice Number' },
      // { field: 'Account', header: 'Vendor Account' },
      { field: 'documentdescription', header: 'Description' },
      { field: 'documentDate', header: 'Invoice Date' },
      { field: 'docStatus', header: 'Status' },
      { field: 'totalAmount', header: 'Amount' },
    ];

    this.columnsForPosted = [
      // { field: 'VendorName', header: 'Vendor Name' },
      { field: 'docheaderID', header: 'Invoice Number' },
      // { field: 'PODocumentID', header: 'PO Number' },
      // { field: 'Name', header: 'Rule' },
      { field: 'docStatus', header: 'Status' },
      { field: 'documentDate', header: 'Invoice Date' },
      { field: 'documentDate', header: 'Posted Date' },
      { field: 'totalAmount', header: 'Amount' },
      // { field: 'Account', header: 'Actions' },
    ];

    this.columnsForCollections = [
      // { field: 'VendorName', header: 'Vendor Name' },
      { field: 'docheaderID', header: 'Invoice Number' },
      // { field: 'Account', header: 'Vendor Account' },
      // { field: 'Account', header: 'Approval Type' },
      { field: 'documentDate', header: 'Invoice Date' },
      { field: 'documentDate', header: 'Posted Date' },
      { field: 'documentDate', header: 'Payment Date' },
      // { field: 'UpdatedOn', header: 'Last Modified' },
      { field: 'totalAmount', header: 'Amount' },
    ];

    this.columnsForRejected = [
      // { field: 'VendorName', header: 'Vendor Name' },
      { field: 'docheaderID', header: 'Invoice Number' },
      { field: 'PODocumentID', header: 'PO Number' },
      { field: 'EntityName', header: 'Entity' },
      { field: 'documentDate', header: 'Invoice Date' },
      { field: 'documentdescription', header: 'Description' },
      { field: 'totalAmount', header: 'Amount' },
    ];
    this.columnsForTotal.forEach((e) => {
      this.totalColumnHeader.push(e.header);
      this.totalColumnField.push(e.field);
    });

    this.columnsForUnderProcess.forEach((e) => {
      this.UnderProcessColumnHeader.push(e.header);
      this.UnderProcessColumnField.push(e.field);
    });
    this.columnsForPosted.forEach((e) => {
      this.PostedColumnHeader.push(e.header);
      this.PostedColumnField.push(e.field);
    });
    this.columnsForCollections.forEach((e) => {
      this.CollectionsColumnHeader.push(e.header);
      this.CollectionsColumnField.push(e.field);
    });
    this.columnsForRejected.forEach((e) => {
      this.RejectedColumnHeader.push(e.header);
      this.RejectedColumnField.push(e.field);
    });

    this.ColumnLengthtotal = this.columnsForTotal.length;
    this.ColumnLengthUnderProcess = this.columnsForUnderProcess.length;
    this.ColumnLengthPosted = this.columnsForPosted.length;
    this.ColumnLengthCollections = this.columnsForCollections.length;
    this.ColumnLengthRejected = this.columnsForRejected.length;
  }

  readTotalInvoiceData(filter){
    this.chartsService.getTotalInvoiceData(filter).subscribe((data:any)=>{
      let mergedArr = [];
      data.data.forEach(ele=>{
        let arr = {...ele.Document,...ele.Entity};
        mergedArr.push(arr);
      });
      this.totalTableData = mergedArr;
      this.totalInv = this.totalTableData.length;
      if(this.totalInv>10){
        this.showPaginatortotal = true;
      }
    })
  }
  readUnderProcessData(filter){
    this.chartsService.getUnderprocessInvoiceData(filter).subscribe((data:any)=>{
      let mergedArr = [];
      data.data.forEach(ele=>{
        let arr = {...ele.Document,...ele.Entity};
        mergedArr.push(arr);
      });
      this.UnderProcessTableData = mergedArr;
      this.UnderProcessInv = this.UnderProcessTableData.length;
      if(this.UnderProcessInv>10){
        this.showPaginatorUnderProcess = true;
      }
    })
  }
  readInvoicedData(filter){
    this.chartsService.getInvoicedData(filter).subscribe((data:any)=>{
      let mergedArr = [];
      data.data.forEach(ele=>{
        let arr = {...ele.Document,...ele.Entity};
        mergedArr.push(arr);
      });
      this.PostedTableData = mergedArr;
      this.PostedInv = this.PostedTableData.length;
      if(this.PostedInv>10){
        this.showPaginatorPosted = true;
      }
    })
  }
  readCollectionsData(filter){
    this.chartsService.getCollectionData(filter).subscribe((data:any)=>{
      let mergedArr = [];
      data.data.forEach(ele=>{
        let arr = {...ele.Document,...ele.Entity};
        mergedArr.push(arr);
      });
      this.CollectionsTableData = mergedArr;
      this.CollectionsInv = this.CollectionsTableData.length;
      if(this.CollectionsInv>10){
        this.showPaginatorCollections = true;
      }
    })
  }
  readRejectedData(filter){
    this.chartsService.getRejectedData(filter).subscribe((data:any)=>{
      let mergedArr = [];
      data.data.forEach(ele=>{
        let arr = {...ele.Document,...ele.Entity};
        mergedArr.push(arr);
      });
      this.RejectedTableData = mergedArr;
      this.RejectedInv = this.RejectedTableData.length;
      if(this.RejectedInv>10){
        this.showPaginatorCollections = true;
      }
    })
  }
  searchInvoiceDataV(evnt){

  }

  dateRange() {
    this.dateFilterService.dateRange();
    this.minDate = this.dateFilterService.minDate;
    this.maxDate = this.dateFilterService.maxDate;
  }

  downloadReport(){
    if(this.tabName == 'Total') {
      this.ImportExcelService.exportExcel(this.totalTableData);
    } else if(this.tabName == 'UnderProcess'){
      this.ImportExcelService.exportExcel(this.UnderProcessTableData);
    } else if(this.tabName == 'Posted'){
      this.ImportExcelService.exportExcel(this.PostedTableData);
    } else if(this.tabName == 'Collections'){
      this.ImportExcelService.exportExcel(this.CollectionsTableData);
    } else if(this.tabName == 'Rejected'){
      this.ImportExcelService.exportExcel(this.RejectedTableData);
    }
  }

  filterByDate(date) {
    let date1: any = this.datePipe.transform(date[0], 'yyyy-MM-dd');
    let date2: any = this.datePipe.transform(date[1], 'yyyy-MM-dd');
    console.log(date1, date2);

    let dateFilter = '';
    if (date != '') {
      dateFilter = `?date=${date1}To${date2}`;
    }
    this.readInvoicedData(dateFilter);
    this.readTotalInvoiceData(dateFilter);
    this.readUnderProcessData(dateFilter);
    this.readCollectionsData(dateFilter);
    this.readRejectedData(dateFilter);
  }

  clearDates(){
    this.filterByDate('');
  }
}
