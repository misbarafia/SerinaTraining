import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-detailed-reports',
  templateUrl: './detailed-reports.component.html',
  styleUrls: ['./detailed-reports.component.scss'],
})
export class DetailedReportsComponent implements OnInit {
  viewType = 'Expense';
  expenseTableData = [];
  tarrifTableData = [];
  invoiceTableData = [];

  columnsForExpense: any;
  columnsForTarif: any;
  columnsForInv: any;
  expenseColumnHeader = [];
  expenseColumnField = [];
  TarifColumnHeader = [];
  TarifColumnField = [];
  InvColumnHeader = [];
  InvColumnField = [];
  ColumnLengthExpense: any;
  ColumnLengthTarrif: any;
  ColumnLengthInv: any;

  showPaginatorExpense: boolean;
  showPaginatorTarrif: boolean;
  showPaginatorInvoice: boolean;
  constructor() {}

  ngOnInit(): void {
    this.prepareColumns();
  }

  prepareColumns() {
    this.columnsForExpense = [
      { field: 'ServiceProviderName', header: 'Service provider' },
      { field: 'entity', header: 'Company Name' },
      { field: 'docheaderID', header: 'Invoice Number' },
      { field: 'Account', header: 'Account Number' },
      { field: 'documentdescription', header: 'Location' },
      { field: 'documentDate', header: 'CM Bill Amount' },
      { field: 'UpdatedOn', header: 'PM Bill Amount' },
    ];
    this.columnsForTarif = [
      { field: 'ServiceProviderName', header: 'Service provider' },
      { field: 'docheaderID', header: 'Location Name' },
      { field: 'Account', header: 'Location Code' },
      { field: 'Account', header: 'Account Number' },
      { field: 'docheaderID', header: 'Invoice Number' },
      { field: 'documentDate', header: 'Type' },
      { field: 'UpdatedOn', header: 'Units' },
      { field: 'UpdatedOn', header: 'Slabs' },
    ];

    this.columnsForInv = [
      // { field: 'ServiceProviderName', header: 'Service provider' },
      { field: 'docheaderID', header: 'Company' },
      { field: 'Account', header: 'Account Number' },
      { field: 'Account', header: 'Downloaded Date' },

      { field: 'docheaderID', header: 'Invoice Number' },
      { field: 'documentDate', header: 'Invoice Date' },
      { field: 'UpdatedOn', header: 'Bill Amount' },
      { field: 'UpdatedOn', header: 'Voucher Number' },
      { field: 'UpdatedOn', header: 'Voucher Creation Date' },
      { field: 'UpdatedOn', header: 'Bill Type' },
      { field: 'UpdatedOn', header: 'OCR Status' },
      { field: 'UpdatedOn', header: 'Overall Status' },
    ];

    this.columnsForExpense.forEach((e) => {
      this.expenseColumnHeader.push(e.header);
      this.expenseColumnField.push(e.field);
    });
    this.columnsForTarif.forEach((e) => {
      this.TarifColumnHeader.push(e.header);
      this.TarifColumnField.push(e.field);
    });
    this.columnsForInv.forEach((e) => {
      this.InvColumnHeader.push(e.header);
      this.InvColumnField.push(e.field);
    });

    this.ColumnLengthExpense = this.columnsForExpense.length;
    this.ColumnLengthTarrif = this.columnsForTarif.length;
    this.ColumnLengthInv = this.columnsForInv.length;
  }

  choosepageTab(value) {
    this.viewType = value;
  }

  searchInvoiceDataV(value) {}
  showSidebar(boolean) {}
}
