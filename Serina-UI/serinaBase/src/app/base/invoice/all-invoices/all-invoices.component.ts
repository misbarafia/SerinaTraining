import { AlertService } from './../../../services/alert/alert.service';
import { NgxSpinnerService } from 'ngx-spinner';
import { SharedService } from 'src/app/services/shared.service';
import { Router } from '@angular/router';
import { TaggingService } from './../../../services/tagging.service';
import {
  Component,
  EventEmitter,
  Input,
  OnChanges,
  OnInit,
  Output,
  SimpleChanges,
  ViewChild,
} from '@angular/core';
import { CdkDragDrop, moveItemInArray } from '@angular/cdk/drag-drop';
import { Table } from 'primeng/table';
import { AuthenticationService } from 'src/app/services/auth/auth-service.service';
import { DataService } from 'src/app/services/dataStore/data.service';
import { MessageService } from 'primeng/api';

export interface statusArray {
  name:string;
}

@Component({
  selector: 'app-all-invoices',
  templateUrl: './all-invoices.component.html',
  styleUrls: ['./all-invoices.component.scss'],
})
export class AllInvoicesComponent implements OnInit, OnChanges {
  @Input() tableData;
  @Input() invoiceColumns;
  @Input() columnsToDisplay;
  @Input() showPaginatorAllInvoice;
  @Input() columnLength;
  @Output() public searchInvoiceData: EventEmitter<any> =
    new EventEmitter<any>();
  @Output() public sideBarBoolean: EventEmitter<boolean> =
    new EventEmitter<boolean>();
    @Output() public paginationEvent: EventEmitter<any> =
    new EventEmitter<boolean>();
  showPaginator: boolean;
  // columnsToDisplay =[];
  _selectedColumns: any[];
  visibleSidebar2;
  cols;
  status = {
    1: 'Accepted',
    2: 'Rejected',
    3: 'Paid',
  };

  @ViewChild('allInvoice', { static: true }) allInvoice: Table;
  hasSearch: boolean = false;
  statusId: any;
  displayStatus: any;
  previousAvailableColumns: any[];
  select: any;
  userType: string;
  first = 0;
  last: number;
  rows = 10;
  bgColorCode;
  FilterData = [];
  selectedStatus: any;
  statusData: any;
  checkstatusPopupBoolean:boolean;
  statusText:string;
  statusText1: string;
  portal_name: string;

  constructor(
    private tagService: TaggingService,
    public router: Router,
    private authService: AuthenticationService,
    private storageService: DataService,
    private sharedService: SharedService,
    private AlertService :AlertService,
    private messageService :MessageService,
    private spinnerService : NgxSpinnerService
  ) {}
  ngOnChanges(changes: SimpleChanges): void {
    if (changes.tableData && changes.tableData.currentValue && changes.tableData.currentValue.length > 0) {
      this.FilterData = this.tableData;
      let mergedStatus = [ 'All'];
      this.tableData.forEach(ele=>{
        mergedStatus.push(ele.docstatus)
      })
      this.statusData = new Set(mergedStatus);
    }
  }

  ngOnInit(): void {
    this.userType = this.authService.currentUserValue['user_type'];
    this.bgColorCode = this.storageService.bgColorCode;
    this.visibleSidebar2 = this.sharedService.sidebarBoolean;
    this.getRowsData();
    // this.getColumnData();
    if (this.tableData) {
      if (this.tableData.length > 10) {
        this.showPaginator = true;
      }
      if (this.statusId) {
        this.displayStatus = this.status[this.statusId];
      }
    }
    if (this.userType == 'customer_portal') {
      this.portal_name = 'customer';
    } else if (this.userType == 'vendor_portal') {
      this.portal_name = 'vendorPortal';
      
    }
  }

  getRowsData() {
    if (this.router.url.includes('allInvoices')) {
      this.first = this.storageService.allPaginationFirst;
      this.rows = this.storageService.allPaginationRowLength;
    } 
    else if (this.router.url.includes('PO') ) {
      this.first = this.storageService.poPaginationFisrt;
      this.rows = this.storageService.poPaginationRowLength;
    }
    else if (this.router.url.includes('archived')) {
      this.first = this.storageService.archivedPaginationFisrt;
      this.rows = this.storageService.archivedPaginationRowLength;
    } 
    else if (this.router.url.includes('rejected')) {
      this.first = this.storageService.rejectedPaginationFisrt;
      this.rows = this.storageService.rejectedPaginationRowLength;
    } 
    else if (this.router.url.includes('ServiceInvoices')) {
      this.first = this.storageService.servicePaginationFisrt;
      this.rows = this.storageService.servicePaginationRowLength;
    } 
  }
  

  trackAllInvoice(index, allInvoice) {
    return allInvoice ? allInvoice.idDocument : undefined;
  }
  viewInvoiceDetails(e) {
    console.log(e)
    let route:string;
    if(e.documentStatusID == 12 || e.documentStatusID == 13){
      route = 'PODetails';
    } else {
      route = 'InvoiceDetails';
    }
    if (this.userType == 'vendor_portal') {
      this.router.navigate([
        `/vendorPortal/invoice/${route}/${e.idDocument}`,
      ]);
    } else if (this.userType == 'customer_portal') {
      if(e.documentsubstatusID != 30){
        this.router.navigate([`customer/invoice/${route}/${e.idDocument}`]);
      } else {
        this.router.navigate([`customer/invoice/comparision-docs/${e.idDocument}`]);
      }
    }
    this.tagService.createInvoice = true;
    this.tagService.displayInvoicePage = false;
    this.tagService.editable = false;
    this.sharedService.invoiceID = e.idDocument;
    // if (this.router.url.includes('/customer/invoice/PO')) {
    //   this.tagService.type = 'PO';
    // } else {
    //   this.tagService.type = 'Invoice';
    // }
  }
  filter(value) {
    this.tableData = this.FilterData;
    if (value != 'All') {
      this.tableData = this.tableData.filter(
        (val) => value == val.docstatus
      );
      this.first = 0
    }
  }
  viewStatusPage(e) {
    this.sharedService.invoiceID = e.idDocument;
    this.router.navigate([`${this.portal_name}/invoice/InvoiceStatus/${e.idDocument}`]);
   
  }
  showSidebar() {
    this.sideBarBoolean.emit(true);
  }

  paginate(event) {
    this.paginationEvent.emit(event);
  }

  searchInvoice(value) {
    this.searchInvoiceData.emit(this.allInvoice);
  }

  checkStatus(e){
    this.spinnerService.show();
    let urlStr = ''
    if(this.router.url.includes('payment-details-vendor')){
      urlStr = 'InvoicePaymentStatus';
    } else {
      urlStr = 'InvoiceStatus';
    }
    this.sharedService.checkInvStatus(e.idDocument,urlStr).subscribe((data:any)=>{

      if(urlStr == 'InvoiceStatus'){
        this.statusText = data.Message;
        if(data.IsPosted == 'Yes'){
          this.statusText1 = 'Posted to ERP'
        } else {
          this.statusText1 = 'Not Posted to ERP'
        }
      } else {
        this.statusText = data['Payment Status'];
        this.statusText1 = `Payment date : ${data['Payment Date']}`;
      }
      this.checkstatusPopupBoolean = true;
      this.spinnerService.hide();
    }, (err)=>{
      this.spinnerService.hide();
      this.AlertService.errorObject.detail = 'Server error';
      this.messageService.add(this.AlertService.errorObject);
    })
  }

  reUpload(val){
    console.log(val);
    this.router.navigate([`/${this.portal_name}/uploadInvoices`]);
    this.storageService.reUploadData = val;
  }
}
