import { DataService } from 'src/app/services/dataStore/data.service';
import { AlertService } from './../../services/alert/alert.service';
import { ImportExcelService } from './../../services/importExcel/import-excel.service';
import { DateFilterService } from './../../services/date/date-filter.service';
import { SharedService } from 'src/app/services/shared.service';
import { TaggingService } from './../../services/tagging.service';
import { Component, OnInit, ViewChild } from '@angular/core';
import { Router } from '@angular/router';
import { DatePipe } from '@angular/common';

import { MessageService } from 'primeng/api';
import { CdkDragDrop, moveItemInArray } from '@angular/cdk/drag-drop';
import { NgxSpinnerService } from 'ngx-spinner';
import { AuthenticationService } from 'src/app/services/auth/auth-service.service';
import { MatSidenav } from '@angular/material/sidenav';

export interface UserData {
  invoiceId: number;
  poNumber: number;
  VenderId: string;
  Vendername: string;
  entity: string;
  uploaded: string;
  modified: string;
  status: string;
  amount: string;
  date: string;
}

export interface updateColumn {
  idtabColumn: number;
  ColumnPos: number;
  isActive: boolean;
}

@Component({
  selector: 'app-invoice',
  templateUrl: './invoice.component.html',
  styleUrls: ['./invoice.component.scss'],
  // changeDetection: ChangeDetectionStrategy.OnPush
  // encapsulation: ViewEncapsulation.Emulated
})
export class InvoiceComponent implements OnInit {
  displayInvoicePage: boolean = true;
  activeMenuName: string = 'invoice';
  users: UserData[];
  showPaginator: boolean;
  invoiceDispalyData = [];
  allInvoiceLength: number;
  showPaginatorAllInvoice: boolean;
  createInvoice: boolean;
  allSearchInvoiceString = [];
  visibleSidebar2: boolean;
  cols: any;
  invoiceColumns: any;
  poColumns: any;
  archivedColumns: any;
  allColumns: any;
  columnstodisplayInvoice: any[];
  columnstodisplayPO: any[];
  columnstodisplayArchived: any[];

  updateColumns: updateColumn[] = [];
  poDispalyData: any[];
  poArrayLength: number;
  GRNDispalyData: any[];
  GRNArrayLength: number;
  receiptDispalyData: any[];
  receiptArrayLength: number = 0;
  archivedDisplayData: any[] = [];
  archivedArrayLength: number;
  showPaginatorArchived: boolean;
  archivedLength: number;
  rejectedDisplayData: any[] = [];
  // rejectedArrayLength: number;
  showPaginatorRejected: boolean;
  rejectedLength: number;
  showPaginatorPOTable: boolean;
  showPaginatorGRNTable: boolean;
  userDetails: any;
  usertypeBoolean: boolean;

  rangeDates: Date[];
  routeName: string;
  lastYear: number;
  displayYear: string;
  minDate: Date;
  maxDate: Date;
  columnstodisplayService: any[];
  serviceColumns: any;
  showPaginatorServiceInvoice: boolean;
  serviceinvoiceDispalyData: any[];
  serviceInvoiceLength: any;
  allInColumnLength: any;
  allPOColumnLength: any;
  allARCColumnLength: any;
  allSRVColumnLength: any;
  filterData: any[];
  filterDataService: any[];
  totalInvoicesData: any[];
  filterDataArchived: any;

  @ViewChild('sidenav') sidenav: MatSidenav;
  events: string[] = [];
  opened: boolean;
  portal_name: string;
  invoiceTab: any;
  POTab: any;
  GRNTab: any;
  archivedTab: any;
  rejectedTab: any;
  serviceInvoiceTab: any;
  first: any;
  searchPOStr = '';
  searchGRNStr = '';
  GRNExceptionTab: any;
  GRNExcpLength: number;
  close(reason: string) {
    this.sidenav.close();
  }
  APIParams: string;
  offsetCountPO = 1;
  pageCountVariablePO = 0;
  offsetCountGRN = 1;
  pageCountVariableGRN = 0;

  GRNExcpDispalyData = [];
  GRNExcpColumns = [];
  showPaginatorGRNExcp: boolean;
  columnstodisplayGRNExcp = [];
  GRNExcpColumnLength: number;

  rejectedColumns: any = [];
  columnstodisplayrejected: any = [];
  rejectedColumnLength: number;

  constructor(
    public route: Router,
    private AlertService: AlertService,
    private sharedService: SharedService,
    private SpinnerService: NgxSpinnerService,
    private messageService: MessageService,
    private dataService: DataService,
    private storageService: DataService,
    private ImportExcelService: ImportExcelService,
    private dateFilterService: DateFilterService,
    private datePipe: DatePipe,
    private authService: AuthenticationService
  ) {}

  ngOnInit(): void {
    this.userDetails = this.authService.currentUserValue;
    this.APIParams = `?offset=1&limit=50`;
    if (this.userDetails.user_type == 'customer_portal') {
      this.usertypeBoolean = true;
      this.portal_name = 'customer';
    } else if (this.userDetails.user_type == 'vendor_portal') {
      this.usertypeBoolean = false;
      this.portal_name = 'vendorPortal';
      
    }
    this.routeForTabs();
    this.dateRange();
    this.findActiveRoute();
    this.restoreData();
    this.readGRNExceptionData();
    // this.getInvoiceData();
    // this.getDisplayPOData();
    // this.getDisplayGRNdata();
    // this.getDisplayReceiptdata();
    this.getInvoiceColumns();
    this.getPOColums();
    this.getArchivedColumns();
    this.getServiceColumns();
    this.getDisplayServiceInvoicedata();
    
    this.prepareColumns();
  }

  restoreData() {
    this.totalInvoicesData = this.dataService.invoiceLoadedData;
    // this.filterData = this.invoiceDispalyData;
    // this.allInvoiceLength = this.dataService.invoiceLoadedData.length;
    // if (this.allInvoiceLength > 10) {
    //   this.showPaginatorAllInvoice = true;
    // }
    this.filterForArchived();
    this.poDispalyData = this.dataService.poLoadedData;
    this.poArrayLength = this.dataService.POtableLength;
    if (this.poDispalyData.length > 10) {
      this.showPaginatorPOTable = true;
    }
    this.GRNDispalyData = this.dataService.GRNLoadedData;
    this.GRNArrayLength = this.dataService.GRNTableLength;
    if (this.GRNDispalyData.length > 10) {
      this.showPaginatorGRNTable = true;
    }
    this.archivedDisplayData = this.dataService.archivedDisplayData;
    this.archivedArrayLength = this.dataService.ARCTableLength;
    if (this.archivedDisplayData.length > 10) {
      this.showPaginatorArchived = true;
    }
    this.rejectedDisplayData = this.dataService.rejectedDisplayData;
    this.rejectedLength = this.dataService.rejectTableLength;
    if (this.rejectedDisplayData.length > 10) {
      this.showPaginatorRejected = true;
    }
    this.receiptDispalyData = this.dataService.receiptLoadedData;
    this.receiptArrayLength = this.dataService.receiptLoadedData.length;
    this.visibleSidebar2 = this.sharedService.sidebarBoolean;
    if (this.dataService.invoiceLoadedData.length == 0) {
      this.getInvoiceData();
    }
    if (this.dataService.poLoadedData.length == 0) {
      this.getDisplayPOData(this.APIParams);
    }
    if (this.dataService.GRNLoadedData.length == 0) {
      this.getDisplayGRNdata(this.APIParams);
    }
    if (this.dataService.archivedDisplayData.length == 0) {
      this.getDisplayARCData('');
    }
    if (this.dataService.rejectedDisplayData.length == 0) {
      this.getDisplayRejectedData('');
    }
    if (this.dataService.receiptLoadedData.length == 0) {
      // this.getDisplayReceiptdata();
    }
  }

  routeForTabs() {
    this.invoiceTab = `/${this.portal_name}/invoice/allInvoices`;
    this.POTab = `/${this.portal_name}/invoice/PO`;
    this.GRNTab = `/${this.portal_name}/invoice/GRN`;
    this.archivedTab = `/${this.portal_name}/invoice/archived`;
    this.rejectedTab = `/${this.portal_name}/invoice/rejected`;
    this.GRNExceptionTab = `/${this.portal_name}/invoice/GRNExceptions`;
    this.serviceInvoiceTab = `/${this.portal_name}/invoice/ServiceInvoices`;
  }

  prepareColumns() {
    this.GRNExcpColumns = [
      // { dbColumnname: 'VendorName', columnName: 'Vendor Name' },
      { dbColumnname: 'docheaderID', columnName: 'Invoice Number' },
      { dbColumnname: 'PODocumentID', columnName: 'PO Number' },
      { dbColumnname: 'GRNNumber', columnName: 'GRN Number' },
      { dbColumnname: 'EntityName', columnName: 'Entity' },
      { dbColumnname: 'RejectDescription', columnName: 'Description' },
      { dbColumnname: 'documentDate', columnName: 'Invoice Date' },
      { dbColumnname: 'totalAmount', columnName: 'Amount' },
      // { dbColumnname: 'documentPaymentStatus', columnName: 'Status' },
    ];
    this.rejectedColumns = [
      // { dbColumnname: 'VendorName', columnName: 'Vendor Name' },
      { dbColumnname: 'docheaderID', columnName: 'Invoice Number' },
      { dbColumnname: 'PODocumentID', columnName: 'PO Number' },
      { dbColumnname: 'EntityName', columnName: 'Entity' },
      { dbColumnname: 'documentdescription', columnName: 'Description' },
      { dbColumnname: 'documentDate', columnName: 'Invoice Date' },
      { dbColumnname: 'totalAmount', columnName: 'Amount' },
      // { dbColumnname: 'documentPaymentStatus', columnName: 'Status' },
    ];

    if (this.portal_name == 'customer') {
      this.rejectedColumns.unshift({
        dbColumnname: 'VendorName',
        columnName: 'Vendor Name',
      });
    }
    this.GRNExcpColumns.forEach((val) => {
      this.columnstodisplayGRNExcp.push(val.dbColumnname);
    });

    this.rejectedColumns.forEach((e) => {
      this.columnstodisplayrejected.push(e.dbColumnname);
    });

    this.GRNExcpColumnLength = this.GRNExcpColumns.length + 1;
    this.rejectedColumnLength = this.rejectedColumns.length + 1;
  }
  dateRange() {
    this.dateFilterService.dateRange();
    this.minDate = this.dateFilterService.minDate;
    this.maxDate = this.dateFilterService.maxDate;
  }

  findActiveRoute() {
    if (this.route.url == this.invoiceTab) {
      this.routeName = 'allInvoices';
    } else if (this.route.url == this.POTab) {
      this.routeName = 'PO';
    } else if (this.route.url == this.archivedTab) {
      this.routeName = 'archived';
    }
  }
  getInvoiceData() {
    this.SpinnerService.show();
    this.sharedService.getAllInvoice().subscribe(
      (data: any) => {
        const invoicePushedArray = [];
        if (data) {
          data.ok.Documentdata.forEach((element) => {
            let invoiceData = {
              ...element.Document,
              ...element.Entity,
              ...element.EntityBody,
              ...element.ServiceProvider,
              ...element.ServiceAccount,
              ...element.VendorAccount,
              ...element.Vendor,
            };
            // invoiceData.append('docStatus',element.docStatus)

            invoiceData['docstatus'] = element.docstatus;
            if (this.portal_name == 'vendorPortal') {
              if (invoiceData['docstatus'] == 'Need To Review') {
                invoiceData['docstatus'] = 'Under Review';
              }
            }
            invoicePushedArray.push(invoiceData);
          });
          this.totalInvoicesData = invoicePushedArray;
          this.filterForArchived();
          this.dataService.invoiceLoadedData = invoicePushedArray;
        }
        this.SpinnerService.hide();
      },
      (error) => {
        this.AlertService.errorObject.detail = error.statusText;
        this.messageService.add(this.AlertService.errorObject);
        this.SpinnerService.hide();
      }
    );
  }

  filterForArchived() {
    const archived = [];
    const allInvoices = [];
    const rejected = [];
    this.totalInvoicesData.forEach((ele) => {
      allInvoices.push(ele);
    });
    setTimeout(() => {
      // this.archivedDisplayData = archived;
      this.filterDataArchived = this.archivedDisplayData;
      // this.archivedLength = this.archivedDisplayData.length;
      // if (this.archivedDisplayData.length > 10) {
      //   this.showPaginatorArchived = true;
      // }
      this.invoiceDispalyData = allInvoices;
      // this.rejectedDisplayData = rejected;
      // this.rejectedLength = this.rejectedDisplayData.length;
      // if (this.rejectedDisplayData.length > 10) {
      //   this.showPaginatorRejected = true;
      // }

      this.filterData = this.invoiceDispalyData;
      this.allInvoiceLength = this.invoiceDispalyData.length;
      if (this.invoiceDispalyData.length > 10) {
        this.showPaginatorAllInvoice = true;
      }
    }, 500);
  }

  getDisplayPOData(data) {
    this.SpinnerService.show();
    this.sharedService.getPOData(data).subscribe(
      (data: any) => {
        const poPushedArray = [];
        if (data.ok) {
          data.ok.podata.forEach((element) => {
            let poData = {
              ...element.Document,
              ...element.Entity,
              ...element.EntityBody,
              ...element.ServiceProvider,
              ...element.ServiceAccount,
              ...element.VendorAccount,
              ...element.Vendor,
            };
            poData.docstatus = element.docstatus;
            poPushedArray.push(poData);
          });
        }
        this.poDispalyData =
          this.dataService.poLoadedData.concat(poPushedArray);
        this.dataService.poLoadedData = this.poDispalyData;
        this.poArrayLength = data.ok.total_po;
        this.dataService.POtableLength = data.ok.total_po;
        if (this.poDispalyData.length > 10) {
          this.showPaginatorPOTable = true;
        }
        this.SpinnerService.hide();
      },
      (error) => {
        this.AlertService.errorObject.detail = error.statusText;
        this.messageService.add(this.AlertService.errorObject);
        this.SpinnerService.hide();
      }
    );
  }

  getDisplayGRNdata(data) {
    this.SpinnerService.show();
    this.sharedService.getGRNdata(data).subscribe((data: any) => {
      this.GRNDispalyData = this.dataService.GRNLoadedData.concat(data.grndata);
      this.dataService.GRNLoadedData = data.grndata;
      this.dataService.GRNTableLength = data.grn_total;
      this.GRNArrayLength = data.grn_total;
      if (this.GRNDispalyData.length > 10) {
        this.showPaginatorGRNTable = true;
      }
      this.SpinnerService.hide();
    });
  }

  getDisplayARCData(data) {
    this.SpinnerService.show();
    this.sharedService.getARCdata(data).subscribe((data: any) => {
      const invoicePushedArray = [];
      data?.result?.ven?.ok?.Documentdata?.forEach((element) => {
        let invoiceData = {
          ...element.Document,
          ...element.Entity,
          ...element.EntityBody,
          ...element.VendorAccount,
          ...element.Vendor,
        };
        
        // invoiceData.append('docStatus',element.docStatus)

        invoiceData['docstatus'] = element.docstatus;
        invoicePushedArray.push(invoiceData);
      });

      data?.result?.ser?.ok?.Documentdata?.forEach((element) => {
        let invoiceData = {
          ...element.Document,
          ...element.Entity,
          ...element.EntityBody,
          ...element.ServiceProvider,
          ...element.ServiceAccount
        };
        invoiceData['docstatus'] = element.docstatus;
        invoicePushedArray.push(invoiceData);
      });
      this.archivedDisplayData.forEach((ele1) => {
        for (let name in ele1) {
          if (name == 'ServiceProviderName') {
            ele1['VendorName'] = ele1['ServiceProviderName'];
          }
        }
      });
      
      this.archivedDisplayData =
        this.dataService.archivedDisplayData.concat(invoicePushedArray);
      this.dataService.ARCTableLength = this.archivedDisplayData.length;
      this.archivedLength = this.archivedDisplayData.length;
      if (this.archivedDisplayData.length > 10) {
        this.showPaginatorArchived = true;
      }
      this.SpinnerService.hide();
    });
  }

  getDisplayRejectedData(data) {
    this.SpinnerService.show();
    this.sharedService.getRejecteddata(data).subscribe((data: any) => {
      const invoicePushedArray = [];
      data?.result?.ven?.ok?.Documentdata?.forEach((element) => {
        let invoiceData = {
          ...element.Document,
          ...element.Entity,
          ...element.EntityBody,
          ...element.DocumentHistoryLogs,
          ...element.VendorAccount,
          ...element.Vendor,
        };
        invoiceData['docstatus'] = element.docstatus;
        invoicePushedArray.push(invoiceData);
      });

      data?.result?.ser?.ok?.Documentdata?.forEach((element) => {
        let invoiceData = {
          ...element.Document,
          ...element.Entity,
          ...element.EntityBody,
          ...element.ServiceProvider,
          ...element.ServiceAccount
        };
        
        // invoiceData.append('docStatus',element.docStatus)

        invoiceData['docstatus'] = element.docstatus;
        invoicePushedArray.push(invoiceData);
      });
      this.rejectedDisplayData.forEach((ele1) => {
        for (let name in ele1) {
          if (name == 'ServiceProviderName') {
            ele1['VendorName'] = ele1['ServiceProviderName'];
          }
        }
      });
      this.rejectedDisplayData =
        this.dataService.rejectedDisplayData.concat(invoicePushedArray);
      this.dataService.rejectTableLength = this.rejectedDisplayData.length;
      this.rejectedLength = this.rejectedDisplayData.length;
      if (this.rejectedDisplayData.length > 10) {
        this.showPaginatorRejected = true;
      }
      this.SpinnerService.hide();
    });
  }

  readGRNExceptionData(){
    this.sharedService.getGRNExceptionData('').subscribe((data:any)=>{
      const invoicePushedArray = [];
      data?.result?.ok?.Documentdata?.forEach((element) => {
        let invoiceData = {
          ...element.Document,
          ...element.Entity,
          ...element.EntityBody,
          ...element.VendorAccount,
          ...element.Vendor,
          ...element.GrnReupload
        };
        invoiceData['docstatus'] = element.docstatus;
        invoicePushedArray.push(invoiceData);
      });
      this.GRNExcpDispalyData =
        this.dataService.GRNExcpDispalyData.concat(invoicePushedArray);
      this.dataService.GRNExcpTableLength = this.GRNExcpDispalyData.length;
      this.GRNExcpLength = this.GRNExcpDispalyData.length;
      if (this.GRNExcpDispalyData.length > 10) {
        this.showPaginatorGRNExcp = true;
      }
    })
  }

  getDisplayServiceInvoicedata() {
    this.SpinnerService.show();
    this.sharedService.getServiceInvoices().subscribe(
      (data: any) => {
        const invoicePushedArray = [];
        if (data) {
          data.ok.Documentdata.forEach((element) => {
            let invoiceData = {
              ...element.Document,
              ...element.Entity,
              ...element.EntityBody,
              ...element.ServiceProvider,
              ...element.ServiceAccount,
            };
            // invoiceData.append('docStatus',element.docStatus)
            invoiceData['docstatus'] = element.docstatus;
            invoicePushedArray.push(invoiceData);
          });
          const allInvoicesService = [];
          invoicePushedArray.forEach((ele) => {
            if (ele.documentStatusID == 14) {
              this.archivedDisplayData.push(ele);
            } else {
              allInvoicesService.push(ele);
            }
          });
          this.archivedDisplayData.forEach((ele1) => {
            for (let name in ele1) {
              if (name == 'ServiceProviderName') {
                ele1['VendorName'] = ele1['ServiceProviderName'];
              }
            }
          });
          // this.filterForArchived();
          setTimeout(() => {
            this.serviceinvoiceDispalyData = allInvoicesService;
            this.filterDataService = this.serviceinvoiceDispalyData;
            this.dataService.serviceinvoiceLoadedData = allInvoicesService;
            this.serviceInvoiceLength = this.serviceinvoiceDispalyData.length;
            if (this.serviceinvoiceDispalyData.length > 10) {
              this.showPaginatorServiceInvoice = true;
            }
            this.filterDataArchived = this.archivedDisplayData;
            this.archivedLength = this.archivedDisplayData.length;
            if (this.archivedDisplayData.length > 10) {
              this.showPaginatorArchived = true;
            }
          }, 500);
        }
        this.SpinnerService.hide();
      },
      (error) => {
        this.AlertService.errorObject.detail = error.statusText;
        this.messageService.add(this.AlertService.errorObject);
        this.SpinnerService.hide();
      }
    );
  }

  getColumnsData() {}

  getInvoiceColumns() {
    this.SpinnerService.show();
    this.updateColumns = [];
    this.sharedService.readColumnInvoice('INV').subscribe(
      (data: any) => {
        const pushedInvoiceColumnsArray = [];
        data.col_data.forEach((element) => {
          let arrayColumn = {
            ...element.DocumentColumnPos,
            ...element.ColumnPosDef,
          };
          pushedInvoiceColumnsArray.push(arrayColumn);
        });
        this.invoiceColumns = pushedInvoiceColumnsArray.filter((ele) => {
          return ele.isActive == 1;
        });
        const arrayOfColumnId = [];
        this.invoiceColumns.forEach((e) => {
          arrayOfColumnId.push(e.dbColumnname);
        });
        this.columnstodisplayInvoice = arrayOfColumnId;
        this.invoiceColumns = this.invoiceColumns.sort(
          (a, b) => a.documentColumnPos - b.documentColumnPos
        );
        this.allInColumnLength = this.invoiceColumns.length + 1;
        this.allColumns = pushedInvoiceColumnsArray.sort(
          (a, b) => a.documentColumnPos - b.documentColumnPos
        );
        this.allColumns.forEach((val) => {
          let activeBoolean;
          if (val.isActive == 1) {
            activeBoolean = true;
          } else {
            activeBoolean = false;
          }
          this.updateColumns.push({
            idtabColumn: val.idDocumentColumn,
            ColumnPos: val.documentColumnPos,
            isActive: activeBoolean,
          });
        });

        this.SpinnerService.hide();
        // this.invoiceColumns= pushedInvoiceColumnsArray;
      },
      (error) => {
        this.AlertService.errorObject.detail = error.statusText;
        this.messageService.add(this.AlertService.errorObject);
        this.SpinnerService.hide();
      }
    );
  }

  getPOColums() {
    this.updateColumns = [];
    this.sharedService.readColumnInvoice('PO').subscribe(
      (data: any) => {
        const pushedPOColumnsArray = [];
        data.col_data.forEach((element) => {
          let arrayColumn = {
            ...element.ColumnPosDef,
            ...element.DocumentColumnPos,
          };
          pushedPOColumnsArray.push(arrayColumn);
        });
        this.poColumns = pushedPOColumnsArray.filter((element) => {
          return element.isActive == 1;
        });
        const arrayOfColumnIdPO = [];
        this.poColumns.forEach((e) => {
          arrayOfColumnIdPO.push(e.dbColumnname);
        });
        this.columnstodisplayPO = arrayOfColumnIdPO;
        this.poColumns = this.poColumns.sort(
          (a, b) => a.documentColumnPos - b.documentColumnPos
        );
        this.allPOColumnLength = this.poColumns.length + 1;
        this.allColumns = pushedPOColumnsArray.sort(
          (a, b) => a.documentColumnPos - b.documentColumnPos
        );
        this.allColumns.forEach((val) => {
          let activeBoolean;
          if (val.isActive == 1) {
            activeBoolean = true;
          } else {
            activeBoolean = false;
          }
          this.updateColumns.push({
            idtabColumn: val.idDocumentColumn,
            ColumnPos: val.documentColumnPos,
            isActive: activeBoolean,
          });
        });
        // console.log(res)
        // console.log(pushedPOColumnsArray);
        // this.allColumns = pushedPOColumnsArray;
      },
      (error) => {
        alert(error.error.detail[0].msg);
      }
    );
  }

  getArchivedColumns() {
    this.updateColumns = [];
    this.sharedService.readColumnInvoice('ARC').subscribe(
      (data: any) => {
        const pushedArchivedColumnsArray = [];
        data.col_data.forEach((element) => {
          let arrayColumn = {
            ...element.DocumentColumnPos,
            ...element.ColumnPosDef,
          };
          pushedArchivedColumnsArray.push(arrayColumn);
        });
        this.archivedColumns = pushedArchivedColumnsArray.filter((element) => {
          return element.isActive == 1;
        });
        const arrayOfColumnIdArchived = [];
        this.archivedColumns.forEach((e) => {
          arrayOfColumnIdArchived.push(e.dbColumnname);
        });
        this.columnstodisplayArchived = arrayOfColumnIdArchived;
        this.allColumns = pushedArchivedColumnsArray.sort(
          (a, b) => a.documentColumnPos - b.documentColumnPos
        );
        this.archivedColumns = this.archivedColumns.sort(
          (a, b) => a.documentColumnPos - b.documentColumnPos
        );
        this.allARCColumnLength = this.archivedColumns.length + 1;
        // this.allColumns = pushedPOColumnsArray
        this.allColumns.forEach((val) => {
          let activeBoolean;
          if (val.isActive == 1) {
            activeBoolean = true;
          } else {
            activeBoolean = false;
          }
          this.updateColumns.push({
            idtabColumn: val.idDocumentColumn,
            ColumnPos: val.documentColumnPos,
            isActive: activeBoolean,
          });
        });
      },
      (error) => {
        alert(error.statusText);
      }
    );
  }

  getServiceColumns() {
    this.SpinnerService.show();
    this.updateColumns = [];
    this.sharedService.readColumnInvoice('INVS').subscribe(
      (data: any) => {
        const pushedArchivedColumnsArray = [];
        data.col_data.forEach((element) => {
          let arrayColumn = {
            ...element.DocumentColumnPos,
            ...element.ColumnPosDef,
          };
          pushedArchivedColumnsArray.push(arrayColumn);
        });
        this.serviceColumns = pushedArchivedColumnsArray.filter((element) => {
          return element.isActive == 1;
        });
        const arrayOfColumnIdArchived = [];
        this.serviceColumns.forEach((e) => {
          arrayOfColumnIdArchived.push(e.dbColumnname);
        });
        this.columnstodisplayService = arrayOfColumnIdArchived;
        this.allColumns = pushedArchivedColumnsArray.sort(
          (a, b) => a.documentColumnPos - b.documentColumnPos
        );
        this.serviceColumns = this.serviceColumns.sort(
          (a, b) => a.documentColumnPos - b.documentColumnPos
        );
        this.allSRVColumnLength = this.serviceColumns.length + 1;
        // this.allColumns = pushedPOColumnsArray
        this.allColumns.forEach((val) => {
          let activeBoolean;
          if (val.isActive == 1) {
            activeBoolean = true;
          } else {
            activeBoolean = false;
          }
          this.updateColumns.push({
            idtabColumn: val.idDocumentColumn,
            ColumnPos: val.documentColumnPos,
            isActive: activeBoolean,
          });
          this.SpinnerService.hide();
        });
      },
      (error) => {
        this.AlertService.errorObject.detail = error.statusText;
        this.messageService.add(this.AlertService.errorObject);
        this.SpinnerService.hide();
      }
    );
  }

  menuChange(value) {
    this.updateColumns = [];
    // this.tagService.activeMenuName = value;
    this.activeMenuName = value;
    // this.getInvoiceData();
    this.storageService.allPaginationFirst = 0;
    this.storageService.allPaginationRowLength = 10;
    if (value == 'invoice') {
      this.route.navigate([this.invoiceTab]);
      this.allSearchInvoiceString = [];
      // this.getInvoiceColumns();
    } else if (value == 'po') {
      // this.getPOColums();
      this.route.navigate([this.POTab]);
      this.allSearchInvoiceString = [];
    } else if (value == 'grn') {
      this.route.navigate([this.GRNTab]);
      this.allSearchInvoiceString = [];
    } else if (value == 'ServiceInvoices') {
      this.route.navigate([this.serviceInvoiceTab]);
      this.allSearchInvoiceString = [];
    } else if (value == 'archived') {
      this.route.navigate([this.archivedTab]);
      this.allSearchInvoiceString = [];
    } else if (value == 'rejected') {
      this.route.navigate([this.rejectedTab]);
      this.allSearchInvoiceString = [];
    } else if (value == 'GRNException') {
      this.route.navigate([this.GRNExceptionTab]);
      this.allSearchInvoiceString = [];
    }
  }
  searchInvoiceDataV(value) {
    this.allSearchInvoiceString = [];
    this.allSearchInvoiceString = value.filteredValue;
  }
  showSidebar(value) {
    // this.visibleSidebar2 = value;
    this.sidenav.toggle();
    if (this.route.url == this.invoiceTab) {
      this.getInvoiceColumns();
    } else if (this.route.url == this.POTab) {
      this.getPOColums();
    } else if (this.route.url == this.archivedTab) {
      this.getArchivedColumns();
    } else if (this.route.url == this.rejectedTab) {
      this.getArchivedColumns();
    } else if (this.route.url == this.GRNExceptionTab) {
      this.getArchivedColumns();
    } else if (this.route.url == this.serviceInvoiceTab) {
      this.getServiceColumns();
    }
  }

  exportExcel() {
    let exportData = [];
    if (this.route.url == this.invoiceTab) {
      exportData = this.invoiceDispalyData;
    } else if (this.route.url == this.POTab) {
      exportData = this.poDispalyData;
    } else if (this.route.url == this.GRNTab) {
      exportData = this.GRNDispalyData;
    } else if (this.route.url == this.archivedTab) {
      exportData = this.archivedDisplayData;
    } else if (this.route.url == this.rejectedTab) {
      exportData = this.rejectedDisplayData;
    } else if (this.route.url == this.GRNExceptionTab) {
      exportData = this.rejectedDisplayData;
    } else if (this.route.url == this.serviceInvoiceTab) {
      exportData = this.serviceinvoiceDispalyData;
    }
    if (this.allSearchInvoiceString && this.allSearchInvoiceString.length > 0) {
      this.ImportExcelService.exportExcel(this.allSearchInvoiceString);
    } else if (exportData && exportData.length > 0) {
      this.ImportExcelService.exportExcel(exportData);
    } else {
      alert('No Data to import');
    }
  }
  onOptionDrop(event: CdkDragDrop<any[]>) {
    moveItemInArray(this.allColumns, event.previousIndex, event.currentIndex);
    // if (this.route.url == '/customer/invoice/allInvoices') {
    this.allColumns.forEach((e, index) => {
      this.updateColumns.forEach((val) => {
        if (val.idtabColumn === e.idDocumentColumn) {
          val.ColumnPos = index + 1;
        }
      });
    });
  }
  order(v) {}
  activeColumn(e, value) {
    // if (this.route.url == '/customer/invoice/allInvoices') {
    this.updateColumns.forEach((val) => {
      if (val.idtabColumn == value.idDocumentColumn) {
        val.isActive = e.target.checked;
      }
    });
  }

  updateColumnPosition() {
    if (this.route.url == this.invoiceTab) {
      this.sharedService.updateColumnPOs(this.updateColumns, 'INV').subscribe(
        (data: any) => {
          this.getInvoiceColumns();
          this.AlertService.updateObject.detail =
            'Columns updated successfully';
          this.messageService.add(this.AlertService.updateObject);
        },
        (error) => {
          this.AlertService.errorObject.detail = error.statusText;
          this.messageService.add(this.AlertService.errorObject);
        }
      );
    } else if (this.route.url == this.POTab) {
      this.sharedService.updateColumnPOs(this.updateColumns, 'PO').subscribe(
        (data: any) => {
          this.getPOColums();
          this.AlertService.updateObject.detail =
            'Columns updated successfully';
          this.messageService.add(this.AlertService.updateObject);
        },
        (error) => {
          this.AlertService.errorObject.detail = error.statusText;
          this.messageService.add(this.AlertService.errorObject);
        }
      );
    } else if (
      this.route.url == this.archivedTab ||
      this.route.url == this.rejectedTab
    ) {
      this.sharedService.updateColumnPOs(this.updateColumns, 'ARC').subscribe(
        (data: any) => {
          this.getArchivedColumns();
          this.AlertService.updateObject.detail =
            'Columns updated successfully';
          this.messageService.add(this.AlertService.updateObject);
        },
        (error) => {
          this.AlertService.errorObject.detail = error.statusText;
          this.messageService.add(this.AlertService.errorObject);
        }
      );
    } else if (this.route.url == this.serviceInvoiceTab) {
      this.sharedService.updateColumnPOs(this.updateColumns, 'INVS').subscribe(
        (data: any) => {
          this.getServiceColumns();
          this.AlertService.updateObject.detail =
            'Columns updated successfully';
          this.messageService.add(this.AlertService.updateObject);
        },
        (error) => {
          this.AlertService.errorObject.detail = error.statusText;
          this.messageService.add(this.AlertService.errorObject);
        }
      );
    }
    this.sidenav.close();
  }

  filterByDate(date) {
    if (date != '') {
      const frmDate = this.datePipe.transform(date[0], 'yyyy-MM-dd');
      const toDate = this.datePipe.transform(date[1], 'yyyy-MM-dd');
      // this.filterData = [];
      if (this.route.url == this.invoiceTab) {
        this.invoiceDispalyData = this.filterData;
        this.invoiceDispalyData = this.invoiceDispalyData.filter((element) => {
          const dateF = new Date(element.documentDate).toISOString().split('T');

          return dateF[0] >= frmDate && dateF[0] <= toDate;
        });
        this.allInvoiceLength = this.invoiceDispalyData.length;
      } else if (this.route.url == this.serviceInvoiceTab) {
        this.serviceinvoiceDispalyData = this.filterDataService;
        this.serviceinvoiceDispalyData = this.serviceinvoiceDispalyData.filter(
          (element) => {
            const dateF = new Date(element.documentDate)
              .toISOString()
              .split('T');

            return dateF[0] >= frmDate && dateF[0] <= toDate;
          }
        );
        this.serviceInvoiceLength = this.serviceinvoiceDispalyData.length;
      } else if (this.route.url == this.archivedTab) {
        this.archivedDisplayData = this.filterDataArchived;
        this.archivedDisplayData = this.archivedDisplayData.filter(
          (element) => {
            const dateF = new Date(element.documentDate)
              .toISOString()
              .split('T');

            return dateF[0] >= frmDate && dateF[0] <= toDate;
          }
        );
        this.archivedLength = this.archivedDisplayData.length;
      }
    } else {
      this.invoiceDispalyData = this.filterData;
      this.allInvoiceLength = this.invoiceDispalyData.length;
    }
  }
  clearDates() {
    this.filterByDate('');
  }

  paginate(event) {
    this.first = event.first;
    if (this.route.url == this.invoiceTab) {
      this.storageService.allPaginationFirst = this.first;
      this.storageService.allPaginationRowLength = event.rows;
    } else if (this.route.url == this.POTab) {
      this.storageService.poPaginationFisrt = this.first;
      this.storageService.poPaginationRowLength = event.rows;
      if (this.first >= this.pageCountVariablePO) {
        this.pageCountVariablePO = event.first;
        if (this.searchPOStr == '') {
          this.offsetCountPO++;
          console.log(this.offsetCountPO);
          this.APIParams = `?offset=${this.offsetCountPO}&limit=50`;
          this.getDisplayPOData(this.APIParams);
        } else {
          this.offsetCountPO++;
          console.log(this.offsetCountPO);
          this.APIParams = `?offset=${this.offsetCountPO}&limit=50&uni_search=${this.searchPOStr}`;
          this.getDisplayPOData(this.APIParams);
        }
      }
    } else if (this.route.url == this.GRNTab) {
      this.storageService.GRNPaginationFisrt = this.first;
      this.storageService.GRNPaginationRowLength = event.rows;
      if (this.first >= this.pageCountVariableGRN) {
        this.pageCountVariableGRN = event.first;
        if (this.searchGRNStr == '') {
          this.offsetCountGRN++;
          this.APIParams = `?offset=${this.offsetCountGRN}&limit=50`;
          this.getDisplayGRNdata(this.APIParams);
        } else {
          this.offsetCountGRN++;
          this.APIParams = `?offset=${this.offsetCountGRN}&limit=50&uni_search=${this.searchGRNStr}`;
          this.getDisplayGRNdata(this.APIParams);
        }
      }
    } else if (this.route.url == this.archivedTab) {
      this.storageService.archivedPaginationFisrt = this.first;
      this.storageService.archivedPaginationRowLength = event.rows;
    } else if (this.route.url == this.rejectedTab) {
      this.storageService.rejectedPaginationFisrt = this.first;
      this.storageService.rejectedPaginationRowLength = event.rows;
    } else if (this.route.url == this.GRNExceptionTab) {
      this.storageService.GRNExceptionPaginationFisrt = this.first;
      this.storageService.GRNExceptionPaginationRowLength = event.rows;
    } else if (this.route.url == this.serviceInvoiceTab) {
      this.storageService.servicePaginationFisrt = this.first;
      this.storageService.servicePaginationRowLength = event.rows;
    }
  }

  filterString(event) {
    if (this.route.url == this.invoiceTab) {
    } else if (this.route.url == this.POTab) {
      this.offsetCountPO = 1;
      this.dataService.poLoadedData = [];
      this.searchPOStr = event;
      if (this.searchPOStr == '') {
        this.APIParams = `?offset=${this.offsetCountPO}&limit=50`;
        this.getDisplayPOData(this.APIParams);
      } else {
        this.APIParams = `?offset=${this.offsetCountPO}&limit=50&uni_search=${this.searchPOStr}`;
        this.getDisplayPOData(this.APIParams);
      }
    } else if (this.route.url == this.GRNTab) {
      this.offsetCountGRN = 1;
      this.dataService.GRNLoadedData = [];
      this.searchGRNStr = event;
      if (this.searchGRNStr == '') {
        this.APIParams = `?offset=${this.offsetCountGRN}&limit=50`;
        this.getDisplayGRNdata(this.APIParams);
      } else {
        this.APIParams = `?offset=${this.offsetCountGRN}&limit=50&uni_search=${this.searchGRNStr}`;
        this.getDisplayGRNdata(this.APIParams);
      }
    } else if (this.route.url == this.archivedTab) {
    } else if (this.route.url == this.rejectedTab) {
    } else if (this.route.url == this.serviceInvoiceTab) {
    }
  }
}
