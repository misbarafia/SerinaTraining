import { ExceptionsService } from './../../../services/exceptions/exceptions.service';
import { SharedService } from 'src/app/services/shared.service';
import { Router } from '@angular/router';
import { TaggingService } from './../../../services/tagging.service';
import {
  Component,
  EventEmitter,
  Input,
  OnInit,
  Output,
  SimpleChanges,
  ViewChild,
} from '@angular/core';
import { Table } from 'primeng/table';
import { AuthenticationService } from 'src/app/services/auth/auth-service.service';
import { DataService } from 'src/app/services/dataStore/data.service';
import { PermissionService } from 'src/app/services/permission.service';
import { NgxSpinnerService } from 'ngx-spinner';

@Component({
  selector: 'app-exception-table',
  templateUrl: './exception-table.component.html',
  styleUrls: ['./exception-table.component.scss'],
})
export class ExceptionTableComponent implements OnInit {
  @Input() columnsData;
  @Input() invoiceColumns;
  @Input() columnsToDisplay;
  @Input() showPaginatorAllInvoice;
  @Input() ColumnLength;
  @Output() public searchInvoiceData: EventEmitter<any> =
    new EventEmitter<any>();

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
  rows;
  bgColorCode;

  public counts = [
    'Meta data check ',
    'Item check',
    'Quantity check',
    'Unit price check',
    'Success',
  ];
  public orderStatus = 'Quantity check';
  dataLength: any;
  batchBoolean: boolean;
  dashboardViewBoolean: boolean;
  portalName: string;
  confirmText:string;
  displayResponsivepopup:boolean;

  constructor(
    private tagService: TaggingService,
    public router: Router,
    private permissionService: PermissionService,
    private authService: AuthenticationService,
    private ExceptionsService: ExceptionsService,
    private storageService: DataService,
    private sharedService: SharedService,
    private SpinnerService: NgxSpinnerService,
  ) {}

  ngOnInit(): void {
    this.initialData();
  }
  // ngOnChanges(changes: SimpleChanges) {
  //   console.log(changes.columnsData);
  //   this.columnsData = changes.columnsData.currentValue;
  // }
  initialData() {
    this.userType = this.authService.currentUserValue['user_type'];
    if(this.userType == 'vendor_portal'){
      this.portalName = 'vendorPortal';
    } else {
      this.portalName = 'customer';
    }
    this.bgColorCode = this.storageService.bgColorCode;
    this.visibleSidebar2 = this.sharedService.sidebarBoolean;

    if (this.router.url.includes('home')) {
      this.dashboardViewBoolean = true;
    } else {
      this.dashboardViewBoolean = false;
    }
    // this.getColumnData();
    if (this.columnsData) {
      console.log(this.columnsData);
      // if(this.columnsData.length > 10){

      //   this.showPaginator = true;
      // }
      if (this.statusId) {
        this.displayStatus = this.status[this.statusId];
      }
    }
    if (this.tagService.batchProcessTab == 'normal') {
      this.batchBoolean = true;
      this.first = this.storageService.exc_batch_edit_page_first;
      this.rows = this.storageService.exc_batch_edit_page_row_length;
    } else {
      this.batchBoolean = false;
      this.first = this.storageService.exc_batch_approve_page_first;
      this.rows = this.storageService.exc_batch_approve_page_row_length;
    }
  }

  viewInvoice(e) {
    // if(this.userType == 'vendor_portal'){
    //   this.router.navigate([`/vendorPortal/invoice/InvoiceDetails/${e.idDocument}`]);
    // } else if(this.userType == 'customer_portal'){
    //   this.router.navigate([`customer/invoice/InvoiceDetails/${e.idDocument}`]);
    // }
    console.log(e);
    if(this.router.url.includes('ExceptionManagement')){
      this.router.navigate([
        `/${this.portalName}/ExceptionManagement/batchProcess/comparision-docs/${e.idDocument}`,
      ]);
    } else {
      this.router.navigate([
        `/${this.portalName}/home/comparision-docs/${e.idDocument}`,
      ]);
    }
    
    
    this.tagService.createInvoice = true;
    this.tagService.displayInvoicePage = false;
    this.tagService.editable = false;
    this.sharedService.invoiceID = e.idDocument;
    this.tagService.type = 'Invoice';
    this.ExceptionsService.invoiceID = e.idDocument;
  }

  paginate(event) {
    console.log(event);
    this.first = event.first;
    if (this.tagService.batchProcessTab == 'normal') {
      this.storageService.exc_batch_edit_page_first = this.first;
      this.storageService.exc_batch_edit_page_row_length = event.rows;
    } else {
      this.storageService.exc_batch_approve_page_first = this.first;
      this.storageService.exc_batch_approve_page_row_length = event.rows;
    }

  }

  searchInvoice(value) {
    this.searchInvoiceData.emit(this.allInvoice);
  }

  // edit invoice details if something wrong
  editInvoice(e) {
    console.log(e);
    this.ExceptionsService.invoiceID = e.idDocument;
    console.log(this.ExceptionsService.invoiceID )
    this.tagService.editable = true;
    this.sharedService.invoiceID = e.idDocument;
    if(this.router.url == `/${this.portalName}/Create_GRN_inv_list`){
      this.router.navigate([
        `${this.portalName}/Create_GRN_inv_list/Inv_vs_GRN_details/${e.idDocument}`,
      ]);
    } else {
      this.SpinnerService.show();
      this.ExceptionsService.getDocumentLockInfo().subscribe((data:any)=>{
        console.log(data.result);
        this.SpinnerService.hide();
        if(data.result.Document.lock_status == false){
          if (this.tagService.batchProcessTab == 'normal') {
            if (this.permissionService.editBoolean == true) {
              if (e.documentsubstatusID == (29 || 4)) {
                this.ExceptionsService.selectedRuleId = e.ruleID;
                this.router.navigate([
                  `${this.portalName}/ExceptionManagement/InvoiceDetails/${ e.idDocument}`,
                ]);
              } else {
                this.router.navigate([
                  `${this.portalName}/ExceptionManagement/batchProcess/comparision-docs/${e.idDocument}`,
                ]);
              }
              // this.invoiceListBoolean = false;
              let sessionData = {
                "session_status": true
              }
              // this.ExceptionsService.updateDocumentLockInfo(JSON.stringify(sessionData)).subscribe((data:any)=>{})
              this.tagService.submitBtnBoolean = true;
              this.tagService.headerName = 'Edit Invoice';
            } else {
              this.displayResponsivepopup = true;
              this.confirmText = 'Sorry, you do not have access to edit';
            }
          } else if (this.tagService.batchProcessTab == 'editApproveBatch') {
            if (this.permissionService.changeApproveBoolean == true) {
              if (e.documentsubstatusID == (29 || 4)) {
                this.ExceptionsService.selectedRuleId = e.ruleID;
                this.router.navigate([
                  `${this.portalName}/ExceptionManagement/InvoiceDetails/${e.idDocument}`,
                ]);
              } else {
                this.router.navigate([
                  `${this.portalName}/ExceptionManagement/batchProcess/comparision-docs/${e.idDocument}`,
                ]);
              }
              // this.invoiceListBoolean = false;
              this.tagService.approveBtnBoolean = true;
              this.tagService.headerName = 'Approve Invoice';
              this.tagService.approvalType = e.Approvaltype;
            } else {
              this.displayResponsivepopup = true;
              this.confirmText = 'Sorry, you do not have Permission to Approve';
            }
          }
        } else {
          this.displayResponsivepopup = true;
          this.confirmText = `Sorry, "${data.result.User?.firstName} ${data.result.User?.lastName}" is doing changes for this invoice.`;
        }
      })

    }
  }
}
