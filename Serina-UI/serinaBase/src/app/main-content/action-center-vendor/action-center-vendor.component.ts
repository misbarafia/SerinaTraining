import { element } from 'protractor';
import { SharedService } from 'src/app/services/shared.service';
import { DocumentService } from './../../services/vendorPortal/document.service';
import { Component, OnInit } from '@angular/core';
import { TaggingService } from 'src/app/services/tagging.service';
import { PermissionService } from 'src/app/services/permission.service';
import { Router } from '@angular/router';
import { AllInvoicesComponent } from 'src/app/base/invoice/all-invoices/all-invoices.component';
import { DateFilterService } from 'src/app/services/date/date-filter.service';
@Component({
  selector: 'app-action-center-vendor',
  templateUrl: './action-center-vendor.component.html',
  styleUrls: ['./action-center-vendor.component.scss']
})
export class ActionCenterVendorComponent implements OnInit {
  showPaginator: boolean = false;
  invoiceListBoolean: boolean = true;
  users;
  EditedinvoiceDispalyData: any;
  allEditedInvoiceLength: any;
  inprogressData: any;
  inprogressLength: number;
  tobeApprovedData: any;
  tobeApprovedLength: number;

  viewType:string;
  cols: any;
  showPaginatorInvoice: boolean;
  showPaginatorInprogress: boolean;
  showPaginatortobeApprove: boolean;
  invoiceEditedColumn = [
    { field: 'docheaderID', header: 'Invoice Number' },
    { field: 'VendorName', header: 'Vendor Name' },
    { field: 'Account', header: 'Vendor A/C' },
    { field: 'documentdescription', header: 'Description' },
    { field: 'documentDate', header: 'Invoice Date' },
    { field: 'UpdatedOn', header: 'Last Modified' },
    { field: 'totalAmount', header: 'Amount' }
  ];
  inprogessColumn = [
    { field: 'docheaderID', header: 'Invoice Number' },
    // { field: 'poNumber', header: 'Assigned To' },
    { field: 'VendorName', header: 'Vendor Name' },
    { field: 'Account', header: 'Vendor A/C' },
    { field: 'documentdescription', header: 'Description' },
    { field: 'documentDate', header: 'Invoice Date' },
    { field: 'UpdatedOn', header: 'Last Modified' },
    { field: 'totalAmount', header: 'Amount' }
  ];
  tobeApprovedColumn = [
    { field: 'docheaderID', header: 'Invoice Number' },
    // { field: 'poNumber', header: 'Edited By' },
    { field: 'VendorName', header: 'Vendor Name' },
    { field: 'Account', header: 'Vendor A/C' },
    { field: 'documentdescription', header: 'Description' },
    { field: 'documentDate', header: 'Invoice Date' },
    { field: 'UpdatedOn', header: 'Last Modified' },
    { field: 'totalAmount', header: 'Amount' }
  ];
  invoiceColumnField = [];
  inprogressColumnField = [];
  toBeApproveColumnField = [];
  invoiceColumnHeader = [];
  inprogressColumnHeader= [];
  toBeApproveColumnHeader = [];

  editPermissionBoolean:boolean;
  changeApproveBoolean: boolean;
  minDate: any;
  maxDate: any;

  constructor(private tagService: TaggingService,
    private vendorPortalService: DocumentService,
    private sharedService :SharedService,
    private dateFilterService : DateFilterService,
    private permissionService : PermissionService,
    private router: Router) {

  }

  ngOnInit(): void {
   this.viewType = this.tagService.editedTabValue;
   this.addPermissions();
    this.getRejectedInvoiceData();
    this.getPendingInvoices();
    this.getApprovedInvoices();
    this.tagService.type = 'Invoice';
    this.prepareColumnsArray();
    this.dateRange();
  }

  dateRange(){
    this.dateFilterService.dateRange();
    this.minDate = this.dateFilterService.minDate;
    this.maxDate = this.dateFilterService.maxDate;
  }
  
  prepareColumnsArray(){
    this.invoiceEditedColumn.filter(element =>{
      this.invoiceColumnHeader.push(element.header)
      this.invoiceColumnField.push(element.field)
    })

    this.inprogessColumn.forEach(e=>{
      this.inprogressColumnHeader.push(e.header)
      this.inprogressColumnField.push(e.field)
    })

    this.tobeApprovedColumn.forEach(e1 =>{
      this.toBeApproveColumnHeader.push(e1.header)
      this.toBeApproveColumnField.push(e1.field)
    })
  }

  getRejectedInvoiceData() {
    this.vendorPortalService.getRejectedInvoices().subscribe((data: any) => {
      console.log(data);
      let invoiceArray = [];
      data.rejected.forEach(element => {
        let invoices = { ...element.Document, ...element.VendorAccount, ...element.EntityBody,...element.Entity,...element.Vendor,...element.User };
        invoices.documentdescription = element.documentdescription;
        invoiceArray.push(invoices);
      });
      this.EditedinvoiceDispalyData = invoiceArray;
      this.allEditedInvoiceLength = this.EditedinvoiceDispalyData.length;
      if (this.EditedinvoiceDispalyData.length > 10) {
        this.showPaginatorInvoice = true;
      }
    })
  }

  getPendingInvoices(){
    this.vendorPortalService.getPendingInvoices().subscribe((data:any)=>{
      let inprogressArray = [];
      data.pending.forEach(element => {
        let inprogress = { ...element.Document, ...element.VendorAccount, ...element.EntityBody,...element.Entity,...element.Vendor,...element.User };
        inprogress.documentdescription = element.documentdescription;
        inprogressArray.push(inprogress);
      });
      this.inprogressData = inprogressArray;
      this.inprogressLength = this.inprogressData.length 
      if (this.inprogressData.length > 10) {
        this.showPaginatorInprogress = true;
      }
    })
  }

  getApprovedInvoices(){
    this.vendorPortalService.getApprovedInvoices().subscribe((data:any)=>{
      let tobeApprovedArray = [];
      data.approved.forEach(element => {
        let tobeApprove = { ...element.Document, ...element.VendorAccount, ...element.EntityBody,...element.Entity,...element.Vendor,...element.User };
        tobeApprove.documentdescription = element.documentdescription;
        tobeApprovedArray.push(tobeApprove);
      });
      this.tobeApprovedData = tobeApprovedArray;
      this.tobeApprovedLength = this.tobeApprovedData.length ;
      if (this.tobeApprovedData.length > 10) {
        this.showPaginatortobeApprove = true;
      }
    })
  }

  chooseEditedpageTab(value){
    this.viewType = value;
    this.tagService.editedTabValue = value;
  }
  viewInvoice(e) {
    console.log(e);
    this.router.navigate(['vendorPortal/action-center/InvoiceDetails/' + e.idDocument])
    this.sharedService.invoiceID = e.idDocument;
    this.invoiceListBoolean = false;
    this.tagService.editable = false;
    this.tagService.headerName = 'View Invoice';
  }
  editInvoice(e,value) {

    if(value == 'submit'){
      if(this.permissionService.editBoolean == true){
        this.router.navigate(['vendorPortal/action-center/InvoiceDetails/' + e.idDocument])
        this.invoiceListBoolean = false;
        this.tagService.editable = true;
        this.sharedService.invoiceID = e.idDocument;
        this.tagService.submitBtnBoolean = true;
        this.tagService.headerName = 'Edit Invoice';
      } else {
        alert("Do not have Permission to edit")
      }
    } else if(value == 'approve'){
      if(this.permissionService.changeApproveBoolean == true){
        this.router.navigate(['vendorPortal/action-center/InvoiceDetails/' + e.idDocument])
        this.invoiceListBoolean = false;
        this.tagService.editable = true;
        this.sharedService.invoiceID = e.idDocument;
        this.tagService.approveBtnBoolean = true;
        this.tagService.headerName = 'Approve Invoice';
      } else {
        alert("Do not have Permission to Approve")
      }
    }

  }
  backToInvoice() {
    this.invoiceListBoolean = true;
  }
  addPermissions(){
    this.editPermissionBoolean = this.permissionService.editBoolean;
  }
  assignInvoice(inv_id){
    this.vendorPortalService.assignInvoiceTo(inv_id).subscribe((data:any)=>{
      this.getRejectedInvoiceData();
      this.getPendingInvoices();
    },error=>{
      alert(error.statusText);
    })
  }

  toggleRejection(popover, comments: string[]) {
    if (popover.isOpen()) {
      popover.close();
    } else {
      popover.open({comments: comments});
    }
  }
  ngOnDestroy(){
    // this.tagService.editedTabValue = 'invoice'
  }
}
