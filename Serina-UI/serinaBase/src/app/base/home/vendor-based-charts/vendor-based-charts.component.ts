import { Router } from '@angular/router';
import { Component, OnInit } from '@angular/core';
import { ChartsService } from 'src/app/services/dashboard/charts.service';
import { SharedService } from 'src/app/services/shared.service';
import { NgxSpinnerService } from 'ngx-spinner';
import { DatePipe } from '@angular/common';
import { DateFilterService } from 'src/app/services/date/date-filter.service';

@Component({
  selector: 'app-vendor-based-charts',
  templateUrl: './vendor-based-charts.component.html',
  styleUrls: ['./vendor-based-charts.component.scss'],
})
export class VendorBasedChartsComponent implements OnInit {
  vendorsData: any;
  viewType ;
  exceptionData: any;

  totalTableData = [];
  columnsForTotal = [];
  totalColumnHeader = [];
  totalColumnField = [];
  ColumnLengthtotal: any;
  showPaginatortotal: boolean;

  minDate: Date;
  maxDate: Date;
  rangeDates: Date[];
  filterDataTotal: any[];

  constructor(
    private chartsService: ChartsService,
    private sharedService: SharedService,
    private SpinnerService: NgxSpinnerService,
    private router : Router,
    private datePipe : DatePipe,
    private dateFilterService: DateFilterService,
  ) {}

  ngOnInit(): void {
    this.viewType = this.chartsService.vendorTabs;
    // this.readExceptionData();
    this.prepareColumns();
    this.readEmailExceptionData('');
    this.dateRange();
    if (this.router.url == '/customer/home/vendorBasedReports/processReports') {
      this.viewType = 'Process';
    } else if(this.router.url == '/customer/home/vendorBasedReports/exceptionReports'){
      this.viewType = 'Exception';
    } else {
      this.viewType = 'emailException';
    }
  }

  choosepageTab(value) {
    this.viewType = value;
    this.chartsService.vendorTabs = value;
    if (value == 'Process') {
      this.router.navigate(['/customer/home/vendorBasedReports/processReports']);
    } else if(value == 'Exception') {
      this.router.navigate(['/customer/home/vendorBasedReports/exceptionReports']);
    } else if(value == 'emailException') {
      this.router.navigate(['/customer/home/vendorBasedReports/emailExceptionReports']);
    }
  }

  prepareColumns() {
    this.columnsForTotal = [
      { field: 'Filename', header: 'File Name' },
      { field: 'EmailSender', header: 'Sender' },
      { field: 'Exception', header: 'Exception Type' },
      // { field: 'EntityName', header: 'Entity' },
      { field: 'UploadedDate', header: 'Upload Date' },
    ];

    this.columnsForTotal.forEach((e) => {
      this.totalColumnHeader.push(e.header);
      this.totalColumnField.push(e.field);
    });

    this.ColumnLengthtotal = this.columnsForTotal.length;
  }

  // readExceptionData() {
  //   this.SpinnerService.show();
  //   this.chartsService.getvendorExceptionSummary().subscribe((data) => {
  //     console.log(data);
  //     this.exceptionData = data;
  //     this.SpinnerService.hide();
  //   },(err)=>{
  //     this.SpinnerService.hide();
  //   });
  // }

  readEmailExceptionData(filter){
    this.chartsService.getEmailExceptionSummary(filter).subscribe((data:any)=>{
      this.totalTableData = data.data;
      this.filterDataTotal = this.totalTableData;
      if(this.totalTableData.length >10){
        this.showPaginatortotal = true;
      }
    })
  }

  dateRange() {
    this.dateFilterService.dateRange();
    this.minDate = this.dateFilterService.minDate;
    this.maxDate = this.dateFilterService.maxDate;
  }

  filterByDate(date) {
    // if(date != ''){
    //   let frmDate:any = this.datePipe.transform(date[0], "yyyy-MM-dd");
    //   let toDate:any = this.datePipe.transform(date[1], "yyyy-MM-dd");
    //   this.totalTableData = this.filterDataTotal;
    //   this.totalTableData = this.totalTableData.filter((element) => {
    //     const dateF = new Date(element.UploadedDate).toISOString().split('T');
    //     console.log(dateF[0],frmDate,toDate)
    //     return (dateF[0] >= frmDate && dateF[0] <= toDate)
    //   });
    //   if(this.totalTableData.length >10){
    //     this.showPaginatortotal = true;
    //   }
    //  } else {
    //   this.totalTableData = this.filterDataTotal;
    //  }

    let dateFilter = '';
    if(date != ""){
      let frmDate:any = this.datePipe.transform(date[0], "yyyy-MM-dd");
      let toDate:any = this.datePipe.transform(date[1], "yyyy-MM-dd");
      dateFilter = `?date=${frmDate}To${toDate}`;
    }
    if(this.viewType == 'emailException'){
      this.readEmailExceptionData(dateFilter);
    }
  }
  clearDates(){
    this.filterByDate('')
  }
}
