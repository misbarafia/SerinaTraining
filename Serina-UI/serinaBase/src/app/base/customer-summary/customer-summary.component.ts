import { AlertService } from './../../services/alert/alert.service';

import { ServiceInvoiceService } from './../../services/serviceBased/service-invoice.service';
import { DateFilterService } from './../../services/date/date-filter.service';
import { Component, OnInit, ViewChild } from '@angular/core';
import { Table } from 'primeng/table';
import { DatePipe } from '@angular/common';
import { MessageService } from 'primeng/api';
import { NgxSpinnerService } from 'ngx-spinner';

@Component({
  selector: 'app-customer-summary',
  templateUrl: './customer-summary.component.html',
  styleUrls: [
    './customer-summary.component.scss',
    '../invoice/all-invoices/all-invoices.component.scss',
  ],
})
export class CustomerSummaryComponent implements OnInit {
  @ViewChild('approve') approve: Table;
  rangeDates: Date[];
  summaryColumn = [
    { field: 'VendorName', header: 'Vendor Name' },
    { field: 'EntityName', header: 'Entity Name' },
    // { field: 'status', header: 'Status' },
    { field: 'TotalPages', header: 'Total Pages' },
    { field: 'TotalInvoices', header: 'Total Invoices' },
  ];
  summaryColumnSP = [
    { field: 'ServiceProviderName', header: 'Service Provider Name' },
    { field: 'EntityName', header: 'Entity Name' },
    // { field: 'status', header: 'Status' },
    { field: 'TotalPages', header: 'Total Pages' },
    { field: 'TotalInvoices', header: 'Total Invoices' },
  ];
  minDate: Date;
  maxDate: Date;
  summaryColumnField = [];
  summaryColumnHeader = [];
  customerSummary: any;
  showPaginatorSummary: boolean;
  totalSuccessPages: any;
  totalInvoices: any;

  summaryColumnFieldSP = [];
  summaryColumnHeaderSP = [];
  customerSummarySP: any;
  showPaginatorSummarySP: boolean;
  totalSuccessPagesSP: any;
  totalInvoicesSP: any;

  rowsPerPage = 10;
  ColumnLengthVendor: number;
  ColumnLengthSP: number;

  constructor(
    private dateFilterService: DateFilterService,
    private ServiceInvoiceService: ServiceInvoiceService,
    private datePipe: DatePipe,
    private messageService: MessageService,
    private SpinnerService: NgxSpinnerService,
    private alertService: AlertService
  ) {}

  ngOnInit(): void {
    this.dateRange();
    this.readSummary('');
    this.findColumns();
  }

  // display columns
  findColumns() {
    this.summaryColumn.forEach((e) => {
      this.summaryColumnHeader.push(e.header);
      this.summaryColumnField.push(e.field);
    });
    this.summaryColumnSP.forEach((e) => {
      this.summaryColumnHeaderSP.push(e.header);
      this.summaryColumnFieldSP.push(e.field);
    });

    this.ColumnLengthVendor = this.summaryColumn.length;
    this.ColumnLengthSP = this.summaryColumnSP.length;
  }

  // Set date range
  dateRange() {
    this.dateFilterService.dateRange();
    this.minDate = this.dateFilterService.minDate;
    this.maxDate = this.dateFilterService.maxDate;
  }

  // API to get summary page data
  readSummary(val) {
    this.SpinnerService.show();
    this.ServiceInvoiceService.getCutomerSummary(val).subscribe(
      (data: any) => {
        this.customerSummary = data.vendor_data.data;
        this.totalSuccessPages = data.vendor_data.summary.TotalPages;
        this.totalInvoices = data.vendor_data.summary.TotalInvoices;

        this.customerSummarySP = data.supplier_data.data;
        this.totalSuccessPagesSP = data.supplier_data.summary.TotalPages;
        this.totalInvoicesSP = data.supplier_data.summary.TotalInvoices;
        if (this.customerSummary) {
          if (this.customerSummary.length > 10) {
            this.showPaginatorSummary = true;
          }
        }
        if (this.customerSummarySP) {
          if (this.customerSummarySP.length > 10) {
            this.showPaginatorSummarySP = true;
          }
        }
        this.SpinnerService.hide();
      },
      (error) => {
        this.alertService.errorObject.detail = "Server error";
        this.messageService.add(this.alertService.errorObject);
        this.SpinnerService.hide();
      }
    );
  }

  // to filter the summary data
  filterData() {
    if (this.rangeDates) {
      const fromDate = this.datePipe.transform(
        this.rangeDates[0],
        'yyyy-MM-dd'
      );
      const endDate = this.datePipe.transform(this.rangeDates[1], 'yyyy-MM-dd');

      const format = `?ftdate=${fromDate}&endate=${endDate}`;
      this.readSummary(format);
    }
  }

  // clearing the dates
  clearDates() {
    this.readSummary('');
  }
}
