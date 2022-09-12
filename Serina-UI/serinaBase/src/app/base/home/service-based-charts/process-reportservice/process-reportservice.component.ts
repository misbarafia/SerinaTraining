import { Subscription } from 'rxjs';
import { DataService } from 'src/app/services/dataStore/data.service';
import { Component, OnInit } from '@angular/core';
import { ChartsService } from 'src/app/services/dashboard/charts.service';
import { ServiceInvoiceService } from 'src/app/services/serviceBased/service-invoice.service';
import { SharedService } from 'src/app/services/shared.service';
import { DateFilterService } from 'src/app/services/date/date-filter.service';
import { NgxSpinnerService } from 'ngx-spinner';
import { DatePipe } from '@angular/common';

@Component({
  selector: 'app-process-reportservice',
  templateUrl: './process-reportservice.component.html',
  styleUrls: ['./process-reportservice.component.scss'],
})
export class ProcessReportserviceComponent implements OnInit {
  serviceData: any;
  invoiceBysourceChartdata: any;
  totalProcessedvalueChart: any;
  pendingInvoiceChartData: any;
  stackedChartData : any;
  entity: any;
  entitySubscription : Subscription;

  minDate: Date;
  maxDate: Date;
  rangeDates: Date[];

  noDataPendingboolean: boolean;
  noDataOverallboolean: boolean;
  noDataProcessboolean: boolean;
  noDataCountboolean: boolean;
  totolDownloadCount: number;
  totalProcessCount: number;
  totalPendingCount: number;

  selectedEntityValue = 'ALL';
  selectedDateValue = '';
  selectedServiceValue: any;

  constructor(
    private sharedService: SharedService,
    private chartsService: ChartsService,
    private dataStoreService: DataService,
    private dateFilterService: DateFilterService,
    private SpinnerService: NgxSpinnerService,
    private datePipe : DatePipe
  ) {}

  ngOnInit(): void {
    this.readService();
    this.chartsData();
    this.dateRange();
    this.getEntitySummary();
    this.readProcessVsDownloadData('');
    this.readProcessAmtData('');
    this.readPendingAmountData('');
    this.readOverallChartData('');
    setTimeout(() => {
      this.setContainers();
    }, 800);
  }

  setContainers(){
    if(this.totalProcessedvalueChart.length > 1){
      this.noDataProcessboolean = false;
      this.chartsService.drawColumnChart(
        'column_chart',
        '#A3B8C5',
        'Total Processed Value',
        this.totalProcessedvalueChart
      );
    } else {
      this.noDataProcessboolean = true;
    }

    if(this.stackedChartData.length>1){
      this.noDataCountboolean = false;
      this.chartsService.drawStackedChart('stack_chart',this.stackedChartData);
    } else {
      this.noDataCountboolean = true;
    }

    if(this.pendingInvoiceChartData.length>1){
      this.noDataPendingboolean = false;
      this.chartsService.drawColumnChart(
        'column_chart1',
        '#DCCAA6',
        'Pending Invoices by Amount',
        this.pendingInvoiceChartData
      );
    } else {
      this.noDataPendingboolean = true;
    }

    // this.chartsService.drawColumnChart('column_chart');
    // this.chartsService.drawColumnChartPending('column_chart1');
    if(this.invoiceBysourceChartdata.length>1){
      this.noDataOverallboolean = false;
      this.chartsService.drawPieChart(
        'pie_chart',
        'Overall Invoice Processed vs Downloaded',
        this.invoiceBysourceChartdata
      );
    } else {
      this.noDataOverallboolean = true;
    }

  }

  readService() {
    this.sharedService.readserviceprovider().subscribe((data: any) => {
      let mergerdArray = [];
      data.forEach(element => {
        let spData = {...element.Entity,...element.ServiceProvider};
        mergerdArray.push(spData);
      });
      const uniqueArray = mergerdArray.filter((v,i,a)=>{
        return a.findIndex(t=>(t.ServiceProviderName===v.ServiceProviderName))===i ;
      });
      this.serviceData = uniqueArray;
    });
  }

  chartsData() {
    this.invoiceBysourceChartdata = [
      ['Type', 'count'],
      // ['Processed', 110, 'color:#89D390'],
      // // ['Rejected - 50', 50, 'color:#5167B2'],
      // ['Downloaded', 250, 'color:#5167B2'],
    ];
    this.totalProcessedvalueChart = [
      ['Service Provider', 'Amount'],
      // ['SEWA', 8000],
      // ['DEWA', 10000],
      // ['SECO', 1900],
      // ['FEWA', 21000],
    ];
    this.pendingInvoiceChartData = [
      ['Service Provider', 'Pending Invoices'],
      // ['SEWA', 8],
      // ['DEWA', 10],
      // ['SECO', 10],
      // ['FEWA', 21],
    ];
    this.stackedChartData = [
      ['Service Provider', 'Processed', 'Downloaded'],
      // ['SEWA', 10, 24],
      // ['DEWA', 16, 22],
      // ['SECO', 28, 19],
      // ['FEWA', 28, 19],
    ]
  }

  readProcessVsDownloadData(filter){
    this.SpinnerService.show();
    this.chartsService.getProcessVsTotalSP(filter).subscribe((data:any)=>{
      data.data.processed.forEach((ele)=>{
        this.stackedChartData.push([ele.ServiceProviderName, ele.count]);
      })
      data.data.downloaded.forEach((ele1)=>{
        this.stackedChartData.forEach((val,index)=>{
          if(ele1.ServiceProviderName == val[0]){
            this.stackedChartData[index].splice(2,0,ele1.count);
          }
        });
      })
      this.SpinnerService.hide();
    },err=>{
      this.SpinnerService.hide();
    })
  }

  readProcessAmtData(filter){
    this.SpinnerService.show();
    this.chartsService.getProcessByAmountSP(filter).subscribe((data:any)=>{
      data.data.forEach(ele=>{
        this.totalProcessedvalueChart.push([ele.ServiceProviderName,ele.amount])
      });
      this.SpinnerService.hide();
    },err=>{
      this.SpinnerService.hide();
    })
  }

  readPendingAmountData(filter){
    this.SpinnerService.show();
    this.chartsService.getPendingInvByAmountSP(filter).subscribe((data:any)=>{
      data.data.forEach(ele=>{
        this.pendingInvoiceChartData.push([ele.ServiceProviderName,ele.amount])
      });
      this.SpinnerService.hide();
    },err=>{
      this.SpinnerService.hide();
    })
  }

  readOverallChartData(filter){
    this.SpinnerService.show();
    this.chartsService.getProcessVsTotal_OverallSP(filter).subscribe((data:any)=>{
      this.invoiceBysourceChartdata[1] = ['Processed',data.data.processed];
      this.invoiceBysourceChartdata[2] = ['Downloaded',data.data.downloaded];

      this.totolDownloadCount = data.data.downloaded;
      this.totalProcessCount = data.data.processed;
      this.totalPendingCount = this.totolDownloadCount - this.totalProcessCount;
      this.SpinnerService.hide();
    },err=>{
      this.SpinnerService.hide();
    })
  }
  getEntitySummary() {
    this.entitySubscription = this.dataStoreService.entityData.subscribe((data: any) => {
      this.entity = data;
    });
  }

  selectEntityFilter(e) {
    this.selectedEntityValue = e;
    // let entity = '';
    // if(e != ""){
    //   entity = `?entity=${e}`
    // }
    // this.chartsData();
    // this.readProcessVsDownloadData(entity);
    // this.readProcessAmtData(entity);
    // this.readPendingAmountData(entity);
    // this.readOverallChartData(entity);
    // this.readService();
    // setTimeout(() => {
    //   this.setContainers();
    // }, 500);
  }

  selectedService(e){
    this.selectedServiceValue = e ;
    // let entity = '';
    // let encodeString = encodeURIComponent(e)
    // if(e != ""){
    //   entity = `?serviceprovider=${encodeString}`
    // }
    // this.chartsData();
    // this.readProcessVsDownloadData(entity);
    // this.readProcessAmtData(entity);
    // this.readPendingAmountData(entity);
    // this.readOverallChartData(entity);
    // this.getEntitySummary();
    // setTimeout(() => {
    //   this.setContainers();
    // }, 500);
  }
  dateRange() {
    this.dateFilterService.dateRange();
    this.minDate = this.dateFilterService.minDate;
    this.maxDate = this.dateFilterService.maxDate;
  }

  filterByDate(date) {
    this.selectedDateValue = '';
    console.log(date,this.selectedEntityValue)
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
      this.selectedServiceValue != 'ALL' &&
      this.selectedEntityValue == 'ALL' &&
      this.selectedDateValue == ''
    ) {
      let encodeString = encodeURIComponent(this.selectedServiceValue);
      query = `?serviceprovider=${encodeString}`;
    } else if (
      this.selectedServiceValue == 'ALL' &&
      this.selectedEntityValue != 'ALL' &&
      this.selectedDateValue == ''
    ) {
      query = `?entity=${this.selectedEntityValue}`;
    } else if (
      this.selectedServiceValue == 'ALL' &&
      this.selectedEntityValue == 'ALL' &&
      this.selectedDateValue != ''
    ) {
      query = `?date=${date1}To${date2}`;
    } else if (
      this.selectedServiceValue != 'ALL' &&
      this.selectedEntityValue != 'ALL' &&
      this.selectedDateValue == ''
    ) {
      let encodeString = encodeURIComponent(this.selectedServiceValue);
      query = `?serviceprovider=${encodeString}&entity=${this.selectedEntityValue}`;
    } else if (
      this.selectedServiceValue != 'ALL' &&
      this.selectedEntityValue == 'ALL' &&
      this.selectedDateValue != ''
    ) {
      let encodeString = encodeURIComponent(this.selectedServiceValue);
      query = `?serviceprovider=${encodeString}&date=${date1}To${date2}`;
    } else if (
      this.selectedServiceValue != 'ALL' &&
      this.selectedEntityValue != 'ALL' &&
      this.selectedDateValue != ''
    ) {
      let encodeString = encodeURIComponent(this.selectedServiceValue);
      query = `?serviceprovider=${encodeString}&entity=${this.selectedEntityValue}&date=${date1}To${date2}`;
    } else if (
      this.selectedServiceValue == 'ALL' &&
      this.selectedEntityValue != 'ALL' &&
      this.selectedDateValue != ''
    ) {
      query = `?entity=${this.selectedEntityValue}&date=${date1}To${date2}`;
    }

    console.log(query)
    this.chartsData();
    this.readProcessVsDownloadData(query);
    this.readProcessAmtData(query);
    this.readPendingAmountData(query);
    this.readOverallChartData(query);
    setTimeout(() => {
      this.setContainers();
    },1000);

  }
  clearDates(){
    this.selectedDateValue = '';
  }
}
