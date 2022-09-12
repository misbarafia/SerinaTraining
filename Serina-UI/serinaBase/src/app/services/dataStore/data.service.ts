
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class DataService {
  poLoadedData = [];
  invoiceLoadedData = [];
  GRNLoadedData = [];
  receiptLoadedData = [];

  VendorPortalpoLoadedData = [];
  VendorPortalinvoiceLoadedData = [];
  VendorPortalGRNLoadedData = [];
  VendorPortalreceiptLoadedData = [];

  // all invoices paagination variables
  allPaginationFirst = 0;
  allPaginationRowLength = 10;
  poPaginationFisrt = 0;
  poPaginationRowLength = 10;
  GRNPaginationFisrt = 0;
  GRNPaginationRowLength = 10;
  paymentPaginationFisrt = 0;
  paymentPaginationRowLength = 10;
  archivedPaginationFisrt = 0;
  archivedPaginationRowLength = 10;
  rejectedPaginationFisrt = 0;
  rejectedPaginationRowLength = 10;
  servicePaginationFisrt = 0;
  servicePaginationRowLength = 10;

  // Edited page pagination variables
  editInvoicesPaginationFisrt = 0;
  editInvoicesPaginationRowLength = 10;
  inProgressPaginationFisrt = 0;
  inProgressPaginationRowLength = 10;
  tobeApprovedPaginationFisrt = 0;
  tobeApprovedPaginationRowLength = 10;

  // Finance approval page pagination variables
  financePaginationFisrt = 0;
  financePaginationRowLength = 10;

  // vendor page
  vendorPaginationFirst = 0;
  vendorPaginationRowLength = 10;

  // serviceProvider page
  SPPaginationFirst = 0;
  SPPaginationRowLength = 10;
  updateColumns: any[];
  invoiceColumns: any[];
  columnstodisplayInvoice: any[];
  allColumns: any[];


  bgColorCode = [
    { id:0, name :'All', bgcolor: '#FEF9EC', textColor :'#F3BC45'},
    { id:1, name :'System Check In - Progress', bgcolor: '#FEF9EC', textColor :'#F3BC45'},
    { id:2, name :'Processing Document', bgcolor: '#F3F4FF', textColor :'#747BC8'},
    { id:3, name :'Finance Approval Completed', bgcolor: '#E0FFEF', textColor :'#1EAC60'},
    { id:4, name :'Need To Review', bgcolor: '#FEFFD6', textColor :'#CDD100'},
    { id:5, name :'Edit in Progress', bgcolor: '#FFE8FD', textColor :'#AE5BA7'},
    { id:6, name :'Awaiting Edit Approval', bgcolor: '#F7FFC8', textColor :'#8EA01F'},
    { id:7, name :'Sent to ERP', bgcolor: '#d0fbdd', textColor :'#14bb12'},
    { id:8, name :'Payment Cleared', bgcolor: '#ECF9ED', textColor :'#3EB948'},
    { id:9, name :'Payment Partially Paid', bgcolor: '#F1EBFF', textColor :'#6A5894'},
    { id:10, name :'Invoice Rejected', bgcolor: '#FFE8E8', textColor :'#FF3C3C'},
    { id:11, name :'Payment Rejected', bgcolor: '#FFE8E8', textColor :'#FF3C3C'},
    { id:12, name :'PO Open', bgcolor: '#ECF9ED', textColor :'#3EB948'},
    { id:13, name :'PO Closed', bgcolor: '#E9E9E9', textColor :'#4D4A4A'},
    { id:16, name :'ERP Exception', bgcolor: '#fff3e0', textColor :'#b7925b'},
    { id:15, name :'Mismatch value/s', bgcolor: '#ddebc5', textColor :'#818549'},
    { id:14, name :'Posted In ERP', bgcolor: '#d0fbdd', textColor :'#14bb12'},
  ]
  serviceinvoiceLoadedData: any[];
  approvalServicePaginationRowLength = 10;
  approvalServicePaginationFirst = 0;
  approvalVendorPaginationFirst = 0;
  approvalVendorPaginationRowLength = 10;
  exc_batch_edit_page_first = 0;
  exc_batch_edit_page_row_length = 10;
  exc_batch_approve_page_first = 0;
  exc_batch_approve_page_row_length = 10;
  entityData = new BehaviorSubject<any>([]);
  VendorsReadData = new BehaviorSubject<any>([]);
  vendorNameList = new BehaviorSubject<any>([]);
  vendorsListData = [];
  offsetCount = 1;
  pageCountVariable: number = 0;
  POtableLength: any;
  GRNTableLength: any;
  archivedDisplayData = [];
  ARCTableLength: any;
  rejectedDisplayData = [];
  rejectTableLength: number;
  GRNExceptionPaginationFisrt = 0;
  GRNExceptionPaginationRowLength= 10;
  GRNExcpDispalyData = [];
  GRNExcpTableLength: number;
  reUploadData: any;


  constructor() { }

  getEntity():Observable<any>{
    return this.entityData.asObservable();
   } 

   getVendorsData():Observable<any>{
    return this.VendorsReadData.asObservable();
  }

  getVendorNamesData():Observable<any>{
    return this.vendorNameList.asObservable();
  }
}
