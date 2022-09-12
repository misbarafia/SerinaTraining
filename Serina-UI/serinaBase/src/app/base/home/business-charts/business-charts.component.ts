import { Router } from '@angular/router';
import { ChartsService } from './../../../services/dashboard/charts.service';
import { Component, OnInit } from '@angular/core';
import { SharedService } from 'src/app/services/shared.service';
import { DateFilterService } from 'src/app/services/date/date-filter.service';

@Component({
  selector: 'app-business-charts',
  templateUrl: './business-charts.component.html',
  styleUrls: ['./business-charts.component.scss'],
})
export class BusinessChartsComponent implements OnInit {
  viewType = 'vendor';
  vendorsData: any;
  serviceData: any;
  minDate: Date;
  maxDate: Date;
  rangeDates: Date[];
  constructor(
    private chartsService: ChartsService,
    private sharedService: SharedService,
    private router: Router,
    private dateFilterService: DateFilterService
  ) {}

  ngOnInit(): void {
    this.dateRange();
    if (this.router.url.includes('vendorBasedReports')) {
      this.viewType = 'vendor';
    } else {
      this.viewType = 'service';
    }
  }

  dateRange() {
    this.dateFilterService.dateRange();
    this.minDate = this.dateFilterService.minDate;
    this.maxDate = this.dateFilterService.maxDate;
  }

  choosepageTab(value) {
    this.viewType = value;
    if (value == 'vendor') {
      this.router.navigate(['/customer/home/vendorBasedReports']);
    } else {
      this.router.navigate(['/customer/home/serviceBasedReports']);
    }
  }


}
