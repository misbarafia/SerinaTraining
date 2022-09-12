import { SharedService } from 'src/app/services/shared.service';
import { ImportExcelService } from 'src/app/services/importExcel/import-excel.service';
import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { NgxSpinnerService } from 'ngx-spinner';
import { AlertService } from 'src/app/services/alert/alert.service';
import { ExceptionsService } from 'src/app/services/exceptions/exceptions.service';
import { PermissionService } from 'src/app/services/permission.service';
import { TaggingService } from 'src/app/services/tagging.service';

@Component({
  selector: 'app-create-grn',
  templateUrl: './create-grn.component.html',
  styleUrls: ['./create-grn.component.scss']
})
export class CreateGRNComponent implements OnInit {
  ColumnsForGRN = [
    { field: 'docheaderID', header: 'Invoice Number' },
    { field: 'VendorName', header: 'Vendor Name' },
    // { field: 'Name', header: 'Rule' },
    { field: 'CreatedOn', header: 'Uploaded Date' },
    { field: 'PODocumentID', header: 'PO number' },
    // { field: 'status', header: 'Status' },
    { field: 'totalAmount', header: 'Amount' },
  ];
  columnsData = [];
  showPaginatorAllInvoice: boolean;
  columnsToDisplay = [];

  ColumnsForGRNApproval = [
    { field: 'docheaderID', header: 'Invoice Number' },
    { field: 'VendorName', header: 'Vendor Name' },
    { field: 'Name', header: 'Rule' },
    // { field: 'documentdescription', header: 'Description' },
    // { field: 'All_Status', header: 'Status' },
    { field: 'Approvaltype', header: 'Approval Type' },
    { field: 'totalAmount', header: 'Amount' },
  ];
  columnsToDisplayGRNApproval = [];
  viewType: any;
  allSearchInvoiceString: any[];
  rangeDates: Date[];
  dataLength: number;
  columnsDataAdmin: any[];
  showPaginatorApproval: boolean;
  dataLengthAdmin: number;
  GRNTableColumnLength: number;
  approvalPageColumnLength: number;
  constructor(
    private tagService: TaggingService,
    private ImportExcelService: ImportExcelService,
    private sharedService : SharedService,
    // private ngxSpinner: NgxSpinnerService,
    // private MessageService: MessageService,
    // private alertService: AlertService,
    private router: Router,
    // private exceptionService: ExceptionsService,
    private permissionService : PermissionService,
    // private _location :Location
  ) { }

  ngOnInit(): void {
    if(this.permissionService.GRNPageAccess == true){
      this.viewType = this.tagService.GRNTab;
      this.prepareColumnsArray();
      this.readTableData();
    } else{
      alert("Sorry!, you do not have access");
      this.router.navigate(['customer/invoice/allInvoices'])
    }

  }

  
  // to prepare display columns array
  prepareColumnsArray() {
    this.ColumnsForGRN.filter((element) => {
      this.columnsToDisplay.push(element.field);
      // this.invoiceColumnField.push(element.field)
    });
    this.ColumnsForGRNApproval.filter((ele) => {
      this.columnsToDisplayGRNApproval.push(ele.field);
    });

    this.GRNTableColumnLength = this.ColumnsForGRN.length + 1;
    this.approvalPageColumnLength = this.ColumnsForGRN.length + 1;
  }

  chooseEditedpageTab(value) {
    this.viewType = value;
    this.tagService.GRNTab = value;
    this.allSearchInvoiceString = [];
  }

  searchInvoiceDataV(value) {
    // this.allSearchInvoiceString = []
    this.allSearchInvoiceString = value.filteredValue;
  }

  exportExcel() {
    let exportData = [];
    if (this.tagService.batchProcessTab == 'normal') {
      exportData = this.columnsData;
    } else if (this.tagService.batchProcessTab == 'editApproveBatch') {
      exportData = this.columnsDataAdmin;
    }
    if (this.allSearchInvoiceString && this.allSearchInvoiceString.length > 0) {
      this.ImportExcelService.exportExcel(this.allSearchInvoiceString);
    } else if (exportData && exportData.length > 0) {
      this.ImportExcelService.exportExcel(exportData);
    } else {
      alert('No Data to import');
    }
  }

  readTableData(){
    this.sharedService.readReadyGRNData().subscribe((data:any)=>{
      console.log(data);
      let array = [];
      data.result.forEach(ele=>{
        let mergedArray = {...ele.Document,...ele.Vendor};
        array.push(mergedArray);
      });
      this.columnsData = array;

      this.dataLength = this.columnsData.length;
      if(this.dataLength >10){
        this.showPaginatorAllInvoice = true;
      }
    })
  }

}
