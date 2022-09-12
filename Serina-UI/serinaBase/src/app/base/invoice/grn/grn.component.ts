import { TaggingService } from './../../../services/tagging.service';
import {
  Component,
  EventEmitter,
  Input,
  OnInit,
  Output,
  ViewChild,
} from '@angular/core';
import { Table } from 'primeng/table';
import { Router } from '@angular/router';
import { SharedService } from 'src/app/services/shared.service';
import { AuthenticationService } from 'src/app/services/auth/auth-service.service';
import { DataService } from 'src/app/services/dataStore/data.service';

@Component({
  selector: 'app-grn',
  templateUrl: './grn.component.html',
  styleUrls: [
    './grn.component.scss',
    './../all-invoices/all-invoices.component.scss',
  ],
})
export class GrnComponent implements OnInit {
  @Input() tableData;
  @Input() showPaginatorGRNTable;
  @Output() public searchInvoiceData: EventEmitter<any> =
    new EventEmitter<any>();
    @Output() public paginationEvent: EventEmitter<any> =
    new EventEmitter<any>();
  showPaginator: boolean;
  displayInvoicePage: boolean = true;
  createInvoice: boolean = false;

  @ViewChild('GRN') GRN: Table;
  userType: string;
  first:number;
  rows:number;

  constructor(
    private tagService: TaggingService,
    private router: Router,
    private authService: AuthenticationService,
    private sharedService: SharedService,
    private storageService: DataService,
  ) {}

  ngOnInit(): void {
    this.userType = this.authService.currentUserValue['user_type'];
    this.first = this.storageService.GRNPaginationFisrt;
    this.rows = this.storageService.GRNPaginationRowLength;
  }
  viewInvoice(e) {
    if (this.userType == 'vendor_portal') {
      this.router.navigate([
        `/vendorPortal/invoice/GRNDetails/${e.idDocument}`,
      ]);
    } else if (this.userType == 'customer_portal') {
      this.router.navigate([`customer/invoice/GRNDetails/${e.idDocument}`]);
    }
    this.tagService.createInvoice = true;
    this.tagService.displayInvoicePage = false;
    this.tagService.editable = false;
    this.sharedService.invoiceID = e.idDocument;
    this.tagService.type = 'GRN';
  }
  backToInvoice() {
    this.createInvoice = false;
    this.displayInvoicePage = true;
  }
  searchInvoice(value) {
    this.searchInvoiceData.emit(this.GRN);
  }
  paginate(event) {
    this.paginationEvent.emit(event);
  }
}
