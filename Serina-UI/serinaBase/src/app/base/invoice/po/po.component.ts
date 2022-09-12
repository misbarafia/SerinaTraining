import { TaggingService } from './../../../services/tagging.service';
import {
  Component,
  EventEmitter,
  Input,
  OnInit,
  Output,
  ViewChild,
} from '@angular/core';
import { Router } from '@angular/router';
import { SharedService } from 'src/app/services/shared.service';
import { Table } from 'primeng/table';
import { AuthenticationService } from 'src/app/services/auth/auth-service.service';
import { DataService } from 'src/app/services/dataStore/data.service';

@Component({
  selector: 'app-po',
  templateUrl: './po.component.html',
  styleUrls: [
    './po.component.scss',
    './../all-invoices/all-invoices.component.scss',
  ],
})
export class PoComponent implements OnInit {
  @Input() users;
  @Input() poColumns;
  @Input() columnstodisplayPO;
  @Input() showPaginatorPOTable;
  @Output() public sideBarBoolean: EventEmitter<boolean> =
    new EventEmitter<boolean>();
  @Output() public searchPOData: EventEmitter<any> = new EventEmitter<any>();

  @ViewChild('PO') PO: Table;

  showPaginator: boolean;
  displayInvoicePage: boolean = true;
  createInvoice: boolean = false;
  cols: any;
  userType: string;

  first = 0;
  last: number;
  rows;
  rangeDates: Date[];
  bgColorCode: { id: number; bgcolor: string; textColor: string }[];

  constructor(
    private tagService: TaggingService,
    private router: Router,
    private authService: AuthenticationService,
    private storageService: DataService,
    private sharedService: SharedService
  ) {
    this.cols = [
      // { field: 'idInvoice', header: 'Invoice ID' },
      { field: 'poNumber', header: 'PO Number' },
      { field: 'supplierAccountID', header: 'Vender ID' },
      { field: 'ServiceproviderName', header: 'Vender Name' },
      { field: 'entityID', header: 'Entity' },
      { field: 'entityBodyID', header: 'Entity Site' },
      { field: 'modified', header: 'Location' },
      { field: 'InvoiceStatusID', header: 'Status' },
      { field: 'amount', header: 'Amount' },
    ];
  }

  ngOnInit(): void {
    this.first = this.storageService.poPaginationFisrt;
    this.rows = this.storageService.poPaginationRowLength;
    this.bgColorCode = this.storageService.bgColorCode;
    this.userType = this.authService.currentUserValue['user_type'];
    if (this.users && this.users.length > 10) {
      this.showPaginator = true;
    }
  }
  toCreateNew(e) {
    if (this.userType == 'vendor_portal') {
      this.router.navigate([
        `/vendorPortal/invoice/InvoiceDetails/${e.idDocument}`,
      ]);
    } else if (this.userType == 'customer_portal') {
      this.router.navigate([`customer/invoice/InvoiceDetails/${e.idDocument}`]);
    }
    this.tagService.createInvoice = true;
    this.tagService.displayInvoicePage = false;
    this.tagService.editable = false;
    this.sharedService.invoiceID = e.idDocument;
    this.tagService.type = 'PO';
  }
  backToInvoice() {
    this.createInvoice = false;
    this.displayInvoicePage = true;
  }
  showSidebar() {
    this.sideBarBoolean.emit(true);
  }
  searchInvoice(value) {
    this.searchPOData.emit(this.PO);
  }

  paginate(event) {
    console.log(event);
    this.first = event.first;
    this.storageService.poPaginationFisrt = this.first;
    this.storageService.poPaginationRowLength = event.rows;
  }
}
