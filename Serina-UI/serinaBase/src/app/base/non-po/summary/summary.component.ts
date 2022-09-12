import { MessageService } from 'primeng/api';
import { AlertService } from './../../../services/alert/alert.service';
import { ServiceInvoiceService } from './../../../services/serviceBased/service-invoice.service';
import { formatDate, DatePipe } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { SharedService } from 'src/app/services/shared.service';
import { NgxSpinnerService } from 'ngx-spinner';

@Component({
  selector: 'app-summary',
  templateUrl: './summary.component.html',
  styleUrls: ['./summary.component.scss']
})
export class SummaryComponent implements OnInit {
  summaryData: any;
  showPaginator: boolean;
  totalSuccess: any[];
  totalFail: any;
  selectDate: Date;
  stringDate = '';
  spTemplateData: any;
  selectedEntity;
  pendingCount: Array<{}> = [];
  stringdate1: string;
  displayEntityName = 'ALL';
  displayEntityNameDummy: any;
  displayYear;
  minDate: Date;
  maxDate: Date;
  lastYear: number;
  entity = [
    'ADDC', 'GICC', 'FEWA'
  ];
  selectedSp ="Filter ServiceProvider"
  serviceProviderNames: any;
  totalDownloads: any;
  total_pending: any;
  active_accounts: any;
  selectedMonth = 'Current Month'
  months: string[];

  constructor(private serviceProviderService : ServiceInvoiceService,
    private SpinnerService: NgxSpinnerService,
    private alertService : AlertService,
    private datePipe : DatePipe,
    private MessageService:MessageService) {
  }

  ngOnInit(): void {
    this.getDate();
    this.getSummary(this.stringDate);
    this.getEntitySummary();
    this.getServiceProviders();
  }

  getDate() {
    this.months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
    let today = new Date();
    let month = today.getMonth();
    this.selectedMonth = this.months[month];
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
  }
  applyDatefilter() {
    const format = 'yyyy-MM';
    const locale = 'en-US';
    try {
      const month = this.selectDate.getMonth();
      this.selectedMonth = this.months[month];
      // this.stringdate1 = formatDate(this.selectDate.toLocaleDateString(), format, locale);
      this.stringdate1 = this.datePipe.transform(this.selectDate, format);
      this.stringDate = '?ftdate=' + this.stringdate1;
      this.getSummary(this.stringDate);
    } catch (error) {
      this.stringDate = '';
      this.stringdate1 = '';
      this.getSummary(this.stringDate);
    }
    this.displayEntityName = this.displayEntityNameDummy;
    if (this.selectedEntity == '') {
          this.displayEntityName = 'ALL';
          this.selectedEntity = 'ALL';
        }
    this.selectedEntity = 'ALL';
  }

  getSummary(stringDate: any) {
    this.SpinnerService.show();
    this.serviceProviderService.getSummaryData(stringDate).subscribe((data: any) => {
      this.summaryData = data.result.drill_down_data;
      this.totalSuccess = data.result.total_processed;
      this.totalFail = data.result.total_failed;
      this.totalDownloads = data.result.total_downloaded;
      this.total_pending = data.result.total_pending;
      this.active_accounts = data.result.active_accounts;
      if (this.summaryData.length > 10) {
        this.showPaginator = true;
      }
      if (this.summaryData) {
        this.serviceProviderService.entityIdSummary = '';
        this.serviceProviderService.serviceIdSummary = '';
        this.displayEntityNameDummy = '';
      }
      this.SpinnerService.hide();
      this.getServiceProviders();
      this.getEntitySummary();
    },error=>{
      this.alertService.errorObject.detail = error.statusText;
      this.MessageService.add(this.alertService.errorObject);
      this.SpinnerService.hide();
    });

  }

  getEntitySummary() {
    this.serviceProviderService.getSummaryEntity().subscribe((data: any) => {
      this.entity = data.result;
    });
  }

  getServiceProviders() {
    this.serviceProviderService.getServiceProvider().subscribe((data: any) => {
      this.serviceProviderNames = data.result;
    });
  }

  selectEntityFilter(e) {
    
    let FilterEntity = this.entity.filter((ele:any) =>{
      return e == ele.idEntity;
    })
    this.displayEntityNameDummy = FilterEntity[0]['EntityName'];
    this.serviceProviderService.entityIdSummary = e;
  }

  selectServiceFilter(e) {
    this.serviceProviderService.serviceIdSummary = e ;
  }
}
