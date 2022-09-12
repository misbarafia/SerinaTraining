import { DatePipe } from '@angular/common';
import { DataService } from 'src/app/services/dataStore/data.service';
import { Subscription } from 'rxjs';
import { Component, OnInit } from '@angular/core';
import { ChartsService } from 'src/app/services/dashboard/charts.service';
import { ServiceInvoiceService } from 'src/app/services/serviceBased/service-invoice.service';
import { SharedService } from 'src/app/services/shared.service';
import { DateFilterService } from 'src/app/services/date/date-filter.service';
import { NgxSpinnerService } from 'ngx-spinner';

@Component({
  selector: 'app-process-reports',
  templateUrl: './process-reports.component.html',
  styleUrls: ['./process-reports.component.scss'],
})
export class ProcessReportsComponent implements OnInit {
  vendorsData: any[];
  invoiceAmountData: any;
  invoiceAgechartData: any;
  invoiceBysourceChartdata: any;
  entity: any;
  invCountByvendor: any;
  vendorSummary: any;
  totalUploaded: number;
  invoicedInERP: number;
  rejectedCount: number;
  pendingCount: number;
  errorCount: number;
  sourceData = [];
  noDataPAboolean: boolean;
  noDataVndrCountboolean: boolean;
  noDataAgeboolean: boolean;
  noDataSourceboolean: boolean;

  vendorsSubscription : Subscription;

  minDate: Date;
  maxDate: Date;
  rangeDates: Date[];
  filterData: any[];
  filteredVendors: any;
  invoiceByEntityChartdata: any;
  noDataSourceEntityboolean: boolean;
  selectedVendor = 'ALL';
  selectedSourceValue = 'ALL';
  selectedEntityValue = 'ALL';
  selectedDateValue = '';
  selectedVendorValue: any;

  constructor(
    private chartsService: ChartsService,
    private sharedService: SharedService,
    private serviceProviderService: ServiceInvoiceService,
    private dataService : DataService,
    private dateFilterService: DateFilterService,
    private SpinnerService: NgxSpinnerService,
    private datePipe : DatePipe
  ) {}

  ngOnInit(): void {
    this.readInvSummmary('');
    this.readVendors();
    this.readSource();
    this.chartsData();
    this.dateRange();
    this.getEntitySummary();
    this.readvendorAmount('');
    this.readInvCountByVendor('');
    this.readInvCountBySource('');
    this.readInvAgeReport('');

    setTimeout(() => {
      this.setConatinerForCharts();
    }, 800);
  }

  setConatinerForCharts() {
    if (this.invoiceAmountData.length > 1) {
      this.noDataPAboolean = false;
      this.chartsService.drawColumnChart(
        'vendor_clm_chart',
        '#7E7E7E',
        'Invoice Pending by Amount',
        this.invoiceAmountData
      );
    } else {
      this.noDataPAboolean = true;
    }
    if (this.invCountByvendor.length > 1) {
      this.noDataVndrCountboolean = false;
      this.chartsService.drawStckedChart_X('bar_chart', this.invCountByvendor);
    } else {
      this.noDataVndrCountboolean = true;
    }
    if (this.invoiceAgechartData.length > 1) {
      this.noDataAgeboolean = false;
      this.chartsService.drawColumnChart(
        'vendor_clm_chart1',
        '#F4D47C',
        'Ageing Report',
        this.invoiceAgechartData
      );
    } else {
      this.noDataAgeboolean = true;
    }
    if (this.invoiceBysourceChartdata.length > 1) {
      this.noDataSourceboolean = false;
      this.chartsService.drawPieChart(
        'pie_chart',
        'Invoice Count by Source Type',
        this.invoiceBysourceChartdata
      );
    } else {
      this.noDataSourceboolean = true;
    }
    // if (this.invoiceByEntityChartdata.length > 1) {
      // this.noDataSourceEntityboolean = false;
    //   this.chartsService.drawPieChart(
    //     'pie_chart_entity',
    //     'Invoice Count by Entity',
    //     this.invoiceByEntityChartdata
    //   );
    // } else {
    //   this.noDataSourceEntityboolean = true;
    // }
  }

  readVendors() {
    this.sharedService.getVendorUniqueData(`?offset=1&limit=100`).subscribe((data: any) => {
      let vendorData = [];
      const all_vendor_obj = {
        VendorCode : null,
        VendorName : 'ALL',
      }
      vendorData.unshift(all_vendor_obj);
      this.vendorsData = vendorData;
    });
  }

  filterVendor(event) {
    // let query = event.query.toLowerCase();
    // let filteredGroups = [];

    // for (let optgroup of this.vendorsData) {
    //   this.filteredVendors = this.vendorsData.filter((val) =>
    //     val.VendorName.toLowerCase().includes(query)
    //   );
    // }
    let query = event.query.toLowerCase();
    if(query != ''){
      console.log(query);
      this.sharedService.getVendorUniqueData(`?offset=1&limit=100&ven_name=${query}`).subscribe((data:any)=>{
        this.filteredVendors = data;
      });
    } else {
      this.filteredVendors = this.vendorsData;
    }
  }


  selectVendor(event){
    this.selectedVendorValue = event;
    this.selectedVendor = event.VendorName;
    // let vendor = ''
    // if(event.VendorName != 'ALL'){
    //   vendor = `?vendor=${event.VendorName}`
    // }
    
    // this.chartsData();
    // this.readInvSummmary(vendor);
    // this.readvendorAmount(vendor);
    // this.readInvCountByVendor(vendor);
    // this.readInvCountBySource(vendor);
    // this.readInvAgeReport(vendor);
    // this.getEntitySummary();
    // this.readSource();
    // setTimeout(() => {
    //   this.setConatinerForCharts();
    // }, 800);
  }

  chartsData() {
    this.invoiceAmountData = [
      ['Vendor', 'Amount'],
      // ['Mehtab', 8000],
      // ['Alpha Data', 10000],
      // ['First Choice', 1900],
      // ['Metscon', 21000],
    ];
    this.invoiceAgechartData = [
      ['age', 'InvoiceCount'],
      // ['0-10', 80, ''],
      // ['11-20', 10, ''],
      // ['21-30', 19, ''],
      // ['>31', 21, ''],
    ];

    this.invoiceBysourceChartdata = [
      ['Source', 'Count'],
      // ['Email', 110, 'color:#89D390'],
      // ['Serina Portal ', 50, 'color:#5167B2'],
      // ['Share Point', 50, 'color:#FB4953'],
    ];
    this.invoiceByEntityChartdata = [
      ['Source', 'Count'],
      ['AGI', 110],
      ['AG Masonry ', 50],
      ['AG Nasco', 50],
    ]
    this.invCountByvendor = [
      ['Vendor', 'Invoices'],
      // ['Mehtab', 80],
      // ['Alpha Data', 10],
      // ['First Choice', 19],
      // ['Metscon', 210],
    ];
  }

  getEntitySummary() {
    this.serviceProviderService.getSummaryEntity().subscribe((data: any) => {
      this.entity = data.result;
    });
  }
  selectEntityFilter(e) {
    this.selectedEntityValue = e;
    // let entity = '';
    // if(e != ""){
    //   entity = `?entity=${e}`
    // }
    // this.chartsData();
    // this.readInvSummmary(entity);
    // this.readvendorAmount(entity);
    // this.readInvCountByVendor(entity);
    // this.readInvCountBySource(entity);
    // this.readInvAgeReport(entity);
    // this.selectedVendor = '';
    // this.readSource();
    // setTimeout(() => {
    //   this.setConatinerForCharts();
    // }, 500);
  }

  readSource(){
    this.sourceData = [
      { id: 1, sourceType: 'Web' },
      { id: 2, sourceType: 'Mail' },
      { id: 3, sourceType: 'SharePoint' },
    ];
  }
  selectedSource(e){
    this.selectedSourceValue = e;
    // let source = '';
    // if(e != ""){
    //   source = `?source=${e}`
    // } 
    // this.chartsData();
    // this.readInvSummmary(source);
    // this.readvendorAmount(source);
    // this.readInvCountByVendor(source);
    // this.readInvCountBySource(source);
    // this.readInvAgeReport(source);
    // this.getEntitySummary();
    // this.selectedVendor = '';
    // setTimeout(() => {
    //   this.setConatinerForCharts();
    // }, 500);
  }

  readInvCountByVendor(filter) {
    this.SpinnerService.show();
    this.chartsService.getInvoiceCountByVendorData(filter).subscribe((data: any) => {
      data.data.forEach((element) => {
        this.invCountByvendor[0] = ['Vendor','Invoices'];
        this.invCountByvendor.push([element.VendorName, element.count]);
      });
      this.readRejectedInvCountByVendor(filter);
      this.SpinnerService.hide();
    }, err=>{
      this.SpinnerService.hide();
    });
  }
  readRejectedInvCountByVendor(filter) {
    this.SpinnerService.show();
    this.chartsService.getRejectInvoicesCount(filter).subscribe((data: any) => {
      data.data.forEach((element) => {
        this.invCountByvendor[0] = ['Vendor', 'Invoices','Rejected'];
        this.invCountByvendor.forEach(val=>{
          if(element.VendorName == val[0]){
            val[1] = Number(val[1]) - Number(element.count);
            val[2] = element.count;
          } else if(val[2] == undefined){
            val[2] = 0;
          }
        });
      });
      this.SpinnerService.hide();
    }, err=>{
      this.SpinnerService.hide();
    });
  }

  readInvCountBySource(filter) {
    this.SpinnerService.show();
    this.chartsService.getInvoiceCountBySource(filter).subscribe((data: any) => {
      data.data.forEach((element) => {
        if (element.sourcetype != null) {
          this.invoiceBysourceChartdata.push([
            element.sourcetype,
            parseInt(element.count),
          ]);
        }
        this.SpinnerService.hide();
      });
    }, err=>{
      this.SpinnerService.hide();
    });
  }
  readvendorAmount(filter) {
    this.SpinnerService.show();
    this.chartsService.getPendingInvByAmount(filter).subscribe((data: any) => {
      data.data.forEach((element) => {
        this.invoiceAmountData.push([
          element.VendorName,
          parseInt(element.amount),
        ]);
      });
      this.SpinnerService.hide();
    }, err=>{
      this.SpinnerService.hide();
    });
  }
  readInvAgeReport(filter) {
    this.SpinnerService.show();
    this.chartsService.getAgeingReport(filter).subscribe((data: any) => {
      for (const count in data.data) {
        this.invoiceAgechartData.push([count, parseInt(data.data[count])]);
      }
      this.SpinnerService.hide();
    }, err=>{
      this.SpinnerService.hide();
    });
  }

  readInvSummmary(filter) {
    this.SpinnerService.show();
    this.chartsService.getvendorBasedSummary(filter).subscribe((data: any) => {
      this.vendorSummary = data.data;
      this.totalUploaded = this.vendorSummary.totaluploaded[0].count;
      this.invoicedInERP = this.vendorSummary.erpinvoice[0].count;
      this.pendingCount = this.vendorSummary.pending[0].count;
      this.rejectedCount = this.vendorSummary.rejected[0].count;
      this.errorCount = this.vendorSummary.errorinv[0].count;
      this.SpinnerService.hide();
    }, err=>{
      this.SpinnerService.hide();
    });
  }

  dateRange() {
    this.dateFilterService.dateRange();
    this.minDate = this.dateFilterService.minDate;
    this.maxDate = this.dateFilterService.maxDate;
  }

  filterByDate(date) {

    this.selectedDateValue = '';
    console.log(date,this.selectedEntityValue,this.selectedSourceValue)
    let query = '';
    let date1: any;
    let date2: any
    if (date != '' && date != undefined) {
      date1 = this.datePipe.transform(date[0], 'yyyy-MM-dd');
      date2 = this.datePipe.transform(date[1], 'yyyy-MM-dd');
      console.log(date1, date2);
      this.selectedDateValue = date
    }
    if (
      this.selectedVendor != 'ALL' &&
      this.selectedEntityValue == 'ALL' &&
      this.selectedSourceValue == 'ALL' &&
      this.selectedDateValue == ''
    ) {
      let encodeString = encodeURIComponent(this.selectedVendor);
      query = `?vendor=${encodeString}`;
    } else if (
      this.selectedVendor == 'ALL' &&
      this.selectedEntityValue != 'ALL' &&
      this.selectedSourceValue == 'ALL' &&
      this.selectedDateValue == ''
    ) {
      query = `?entity=${this.selectedEntityValue}`;
    } else if (
      this.selectedVendor == 'ALL' &&
      this.selectedEntityValue == 'ALL' &&
      this.selectedSourceValue != 'ALL' &&
      this.selectedDateValue == ''
    ) {
      query = `?source=${this.selectedSourceValue}`;
    } else if (
      this.selectedVendor == 'ALL' &&
      this.selectedEntityValue == 'ALL' &&
      this.selectedSourceValue == 'ALL' &&
      this.selectedDateValue != ''
    ) {
      query = `?date=${date1}To${date2}`;
    } else if (
      this.selectedVendor != 'ALL' &&
      this.selectedEntityValue != 'ALL' &&
      this.selectedSourceValue == 'ALL' &&
      this.selectedDateValue == ''
    ) {
      let encodeString = encodeURIComponent(this.selectedVendor);
      query = `?vendor=${encodeString}&entity=${this.selectedEntityValue}`;
    } else if (
      this.selectedVendor != 'ALL' &&
      this.selectedEntityValue != 'ALL' &&
      this.selectedSourceValue != 'ALL' &&
      this.selectedDateValue == ''
    ) {
      let encodeString = encodeURIComponent(this.selectedVendor);
      query = `?vendor=${encodeString}&entity=${this.selectedEntityValue}&source=${this.selectedSourceValue}`;
    } else if (
      this.selectedVendor != 'ALL' &&
      this.selectedEntityValue != 'ALL' &&
      this.selectedSourceValue != 'ALL' &&
      this.selectedDateValue != ''
    ) {
      let encodeString = encodeURIComponent(this.selectedVendor);
      query = `?vendor=${encodeString}&entity=${this.selectedEntityValue}&source=${this.selectedSourceValue}&date=${date1}To${date2}`;
    } else if (
      this.selectedVendor == 'ALL' &&
      this.selectedEntityValue != 'ALL' &&
      this.selectedSourceValue != 'ALL' &&
      this.selectedDateValue != ''
    ) {
      query = `?entity=${this.selectedEntityValue}&source=${this.selectedSourceValue}&date=${date1}To${date2}`;
    } else if (
      this.selectedVendor == 'ALL' &&
      this.selectedEntityValue != 'ALL' &&
      this.selectedSourceValue == 'ALL' &&
      this.selectedDateValue != ''
    ) {
      query = `?entity=${this.selectedEntityValue}&date=${date1}To${date2}`;
    } else if (
      this.selectedVendor == 'ALL' &&
      this.selectedEntityValue != 'ALL' &&
      this.selectedSourceValue != 'ALL' &&
      this.selectedDateValue == ''
    ) {
      query = `?entity=${this.selectedEntityValue}&source=${this.selectedSourceValue}`;
    } else if (
      this.selectedVendor == 'ALL' &&
      this.selectedEntityValue == 'ALL' &&
      this.selectedSourceValue != 'ALL' &&
      this.selectedDateValue != ''
    ) {
      query = `?source=${this.selectedSourceValue}&date=${date1}To${date2}`;
    }

    console.log(query)
    this.chartsData();
    this.readInvSummmary(query);
    this.readvendorAmount(query);
    this.readInvCountByVendor(query);
    this.readInvCountBySource(query);
    this.readInvAgeReport(query);
    // this.readSource();
    // this.getEntitySummary();
    setTimeout(() => {
      this.setConatinerForCharts();
    }, 1000);
  }
  clearDates(){
    this.selectedDateValue = '';
  }
}
