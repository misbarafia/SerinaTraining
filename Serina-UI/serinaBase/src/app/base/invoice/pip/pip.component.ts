import { ImportExcelService } from './../../../services/importExcel/import-excel.service';
import { DateFilterService } from './../../../services/date/date-filter.service';
import { SharedService } from 'src/app/services/shared.service';
import {
  Component,
  EventEmitter,
  Input,
  OnInit,
  Output,
  ViewChild,
} from '@angular/core';
import { Table } from 'primeng/table';
import { DataService } from 'src/app/services/dataStore/data.service';

@Component({
  selector: 'app-pip',
  templateUrl: './pip.component.html',
  styleUrls: [
    './pip.component.scss',
    './../all-invoices/all-invoices.component.scss',
  ],
})
export class PipComponent implements OnInit {
  @Output() public searchInvoiceData: EventEmitter<any> =
    new EventEmitter<any>();
  showPaginator: boolean;
  paymentData: any;
  displayInvoicePage: boolean = true;
  createInvoice: boolean = false;
  @ViewChild('payment') payment: Table;
  paymentDataLength: any;

  rangeDates: Date[];
  minDate: Date;
  maxDate: Date;
  bgColorCode: any;
  allSearchInvoiceString: any[];

  first = 0;
  rows = 10;
  columnsToDisplay: { dbColumnname: string; columnName: string }[];
  columnsFields = [];
  columnLength: number;

  constructor(
    private dateFilterService: DateFilterService,
    private storageService: DataService,
    private ImportExcelService: ImportExcelService,
    private SharedService: SharedService
  ) {}

  ngOnInit(): void {
    this.getPaymentStatusData();
    this.dateRange();
    this.prepareColumns();
    this.bgColorCode = this.storageService.bgColorCode;
  }
  searchInvoice(value) {
    this.searchInvoiceData.emit(this.payment);
  }

  dateRange() {
    this.dateFilterService.dateRange();
    this.minDate = this.dateFilterService.minDate;
    this.maxDate = this.dateFilterService.maxDate;
  }

  getPaymentStatusData() {
    this.SharedService.getPaymentStatusData().subscribe(
      (data: any) => {
        this.paymentData = data.data;
        this.paymentDataLength = this.paymentData.length;

        if (this.paymentDataLength > 10) {
          this.showPaginator = true;
        }
      },
      (error) => {
        alert(error.error);
      }
    );
  }

  searchInvoiceDataV(value) {
    this.allSearchInvoiceString = value.filteredValue;
  }

  exportExcel() {
    if (this.allSearchInvoiceString && this.allSearchInvoiceString.length > 0) {
      this.ImportExcelService.exportExcel(this.allSearchInvoiceString);
    } else if (this.paymentData && this.paymentData.length > 0) {
      this.ImportExcelService.exportExcel(this.paymentData);
    } else {
      alert('No Data to import');
    }
  }
  prepareColumns() {
    this.columnsToDisplay = [
      // { dbColumnname: 'VendorName', columnName: 'Vendor Name' },
      { dbColumnname: 'docheaderID', columnName: 'Invoice Number' },
      { dbColumnname: 'PODocumentID', columnName: 'PO Number' },
      { dbColumnname: 'EntityName', columnName: 'Entity' },
      { dbColumnname: 'documentDate', columnName: 'Invoice Date' },
      { dbColumnname: 'totalAmount', columnName: 'Amount' },
      // { dbColumnname: 'documentPaymentStatus', columnName: 'Status' },
    ];
    this.columnsToDisplay.forEach((e) => {
      this.columnsFields.push(e.dbColumnname);
    });
    this.columnLength = this.columnsToDisplay.length + 1;
  }

  paginate(event) {}
  checkStatus(val) {}
  showSidebar(event){}
}
