import { ServiceInvoiceService } from './../../services/serviceBased/service-invoice.service';
import { AlertService } from './../../services/alert/alert.service';
import { HttpClient, HttpEventType } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { FormControl } from '@angular/forms';
import { Router } from '@angular/router';
import { FileUploader } from 'ng2-file-upload';
import { MessageService } from 'primeng/api';
import { throwError } from 'rxjs';
import { catchError, map } from 'rxjs/operators';
import { AuthenticationService } from 'src/app/services/auth/auth-service.service';
import { DataService } from 'src/app/services/dataStore/data.service';
import { SharedService } from 'src/app/services/shared.service';
import { TaggingService } from 'src/app/services/tagging.service';
import { DocumentService } from 'src/app/services/vendorPortal/document.service';
import { environment } from 'src/environments/environment';
// declare var EventSourcePolyfill: any;

@Component({
  selector: 'app-upload-section',
  templateUrl: './upload-section.component.html',
  styleUrls: ['./upload-section.component.scss'],
})
export class UploadSectionComponent implements OnInit {
  apiVersion = environment.apiVersion;
  progress: number;
  invoiceUploadDetails: string | Blob;
  selectedPONumber: any;
  OCRInput: string;
  OcrProgress: number;
  progressEvent;
  progressText: string = '...initializing';
  updateData: {};
  progressWidth: string;
  uplaodInvoiceDialog: boolean;

  processStage = '';

  public uploader: FileUploader = new FileUploader({
    isHTML5: true,
  });
  public hasBaseDropZoneOver: boolean = false;
  isDown: boolean = false;
  isuploadable: boolean = true;
  url: any;
  dragfile: boolean;
  name: any;
  type: any;
  size: any;
  isPdf: boolean;
  showInvoice: any;
  response: string;
  poNumbersList: any;
  filteredPO: any[];
  displaySelectPdfBoolean: boolean;
  vendorAccountId: number;
  vendorAccountName: any;
  vendorAccount = [];
  vendorAccountByEntity = [];
  selectedVendor: any;

  tabs = [];
  selected = new FormControl(0);
  tabtitle: string = '';
  isCustomerPortal: boolean;
  filteredVendors: any;
  tabData = [];
  entirePOData = [];
  evtSource: any;
  entity: any;
  selectedEntityId: any;
  GRNUploadID: any;
  reuploadBoolean: boolean;

  constructor(
    private http: HttpClient,
    public route: Router,
    private docService: DocumentService,
    private dataService: DataService,
    private alertService: AlertService,
    private tagService: TaggingService,
    private sharedService: SharedService,
    private authenticationService: AuthenticationService,
    private messageService: MessageService,
    private serviceProviderService: ServiceInvoiceService
  ) {}

  ngOnInit(): void {
    this.isCustomerPortal = this.sharedService.isCustomerPortal;
    this.GRNUploadID = this.dataService.reUploadData?.grnreuploadID;
    this.getEntitySummary();
    if(this.GRNUploadID != undefined && this.GRNUploadID != null){
      this.reuploadBoolean = true;
      this.vendorAccountId = this.dataService.reUploadData.idVendorAccount;
      this.selectedEntityId = this.dataService.reUploadData.idEntity;
    } else {
      this.reuploadBoolean = false;
    }

  }

  runEventSource(eventSourceObj) {
    this.evtSource = new EventSource(
      `${environment.apiUrl}/${
        this.apiVersion
      }/ocr/status/stream?eventSourceObj=${encodeURIComponent(
        JSON.stringify(eventSourceObj)
      )}`
    );
  }

  getEntitySummary() {
    this.serviceProviderService.getSummaryEntity().subscribe((data: any) => {
      this.entity = data.result;
    });
  }
  
  getVendorAccountsData(ent_id) {
    this.docService.readVendorAccountsData(ent_id).subscribe((data: any) => {
      this.vendorAccount = data.result;
    });
  }

  selectEntity(value){
    this.selectedEntityId = value;
    this.vendorAccount = [];
    this.displaySelectPdfBoolean = false;
    if (this.isCustomerPortal == true) {
      this.getCustomerVendors();
    } else {    
      this.getVendorAccountsData(value);
    }
  }

  getCustomerVendors() {
    this.sharedService
      .getVendorsListToCreateNewlogin(`?offset=1&limit=100&ent_id=${this.selectedEntityId}`)
      .subscribe((data: any) => {
        this.vendorAccount = data.vendorlist;
        this.filteredVendors = data.vendorlist;
      });
  }
  onSelectAccountByEntity(val) {
    if (val) {
      this.displaySelectPdfBoolean = true;
    } else {
      this.displaySelectPdfBoolean = false;
    }
    // this.vendorAccountName = val.Account;
    this.vendorAccountId = val;
  }

  // filterVendor(event){
  //   let filtered:any[] = [];
  //   let query = event.filter;
  //   for (let i = 0; i < this.vendorAccount.length; i++) {
  //     let account: any = this.vendorAccount[i];
  //     if (account.VendorName.toLowerCase().indexOf(query.toLowerCase()) == 0) {
  //       filtered.push(account);
  //     }
  //   }
  //   this.vendorAccount = filtered;
  // }

  filterVendor(event) {
    let query = event.query.toLowerCase();
    if(query != ''){
      this.sharedService.getVendorsListToCreateNewlogin(`?offset=1&limit=100&ent_id=${this.selectedEntityId}&ven_name=${query}`).subscribe((data:any)=>{
        this.filteredVendors = data.vendorlist;
      });
    } else {
      this.filteredVendors = this.vendorAccount;
    }
  }

  selectVendorAccount_vdr(value) {
    this.vendorAccountId = value;
    if (value) {
      this.displaySelectPdfBoolean = true;
    } else {
      this.displaySelectPdfBoolean = false;
    }
  }

  selectVendorAccount(value) {
    // this.vendorAccountId = value.vendoraccounts[0].idVendorAccount;
    // this.getPONumbers(this.vendorAccountId);
    this.getAccountsByEntity(value.idVendor);
  }

  getAccountsByEntity(vId) {
    this.sharedService
      .readCustomerVendorAccountsData(vId)
      .subscribe((data: any) => {
        this.vendorAccountByEntity = data.result;
        this.vendorAccountId = this.vendorAccountByEntity[0].idVendorAccount;
        if (this.vendorAccountId) {
          this.displaySelectPdfBoolean = true;
        } else {
          this.displaySelectPdfBoolean = false;
        }
      });
  }

  // filterPOnumber(event) {
  //   let filtered: any[] = [];
  //   let query = event.query;

  //   for (let i = 0; i < this.poNumbersList.length; i++) {
  //     let PO: any = this.poNumbersList[i];
  //     if (PO.PODocumentID.toLowerCase().indexOf(query.toLowerCase()) == 0) {
  //       filtered.push(PO);
  //     }
  //   }
  //   this.filteredPO = filtered;
  // }

  // selectedPO(event) {
  //   console.log(event)
  //   console.log(this.selectedPONumber);
  //   let arrayLegth = event.value.length;
  //   let tabsLength = 0;
  //   if (event.value.length == 0) {
  //     this.displaySelectPdfBoolean = false;
  //   } else {
  //     this.displaySelectPdfBoolean = true;
  //     this.addTab();
  //   }
  // }

  // addTab() {
  //   if(this.tabtitle != ''){
  //      this.tabs.push(this.tabtitle);
  //   }else{
  //     this.selectedPONumber.forEach(element => {
  //       if(!this.tabs.includes(element.PODocumentID)){
  //         this.tabs.push(element.PODocumentID);
  //         this.sharedService.readUploadPOData(element.idDocument).subscribe((data:any)=>{
  //           const pushedArrayHeader = [];
  //           data.result.headerdata.forEach(element => {
  //             let mergedArray = { ...element.DocumentData, ...element.DocumentTagDef };
  //             mergedArray.DocumentUpdates = element.DocumentUpdates
  //             pushedArrayHeader.push(mergedArray);
  //           });
  //           pushedArrayHeader['tabName'] = element.PODocumentID;
  //           this.entirePOData.push(pushedArrayHeader);
  //         });

  //       }
  //     });
  //   }

  //   this.tabtitle = '';

  // }
  // removeTab(index: number) {
  //   this.entirePOData.splice(index, 1);
  //   this.tabs.splice(index, 1);
  // }

  onSelectFile(event) {
    this.isuploadable = false;
    this.dragfile = false;
    this.invoiceUploadDetails = event.target.files[0];
    if (event.target.files && event.target.files[0]) {
      var reader = new FileReader();

      reader.readAsDataURL(event.target.files[0]); // read file as data url

      reader.onload = (event) => {
        // called once readAsDataURL is completed
        this.url = event.target.result;
        var img = new Image();
        img.onload = () => {};
      };
    }

    this.fileDataProcess(event);
    for (var i = 0; i < event.target.files.length; i++) {
      this.name = event.target.files[i].name;
      this.type = event.target.files[i].type;
      this.size = event.target.files[i].size;
    }
    this.size = this.size / 1024 / 1024;
  }

  cancelSelect() {
    this.invoiceUploadDetails = '';
    this.isuploadable = true;
  }

  // drop file in upload file selection
  fileDrop(event) {
    console.log(event[0]);
    this.invoiceUploadDetails = event[0];
    this.isuploadable = false;
    this.dragfile = true;

    if (event && event[0]) {
      var reader = new FileReader();

      reader.readAsDataURL(event[0]); // read file as data url

      reader.onload = (event) => {
        // called once readAsDataURL is completed
        this.url = event.target;
      };
    }
    for (var i = 0; i < event.length; i++) {
      this.name = event[i].name;
      this.type = event[i].type;
      this.size = event[i].size;
    }

    this.size = this.size / 1024 / 1024;
    this.fileDataProcess(event);
  }

  //file selction from upload file section
  fileSelect(event) {
    this.fileDataProcess(event);
  }

  //file data processing on file selection
  fileDataProcess(event) {
    console.log(event);
  }

  // identify drop file area
  fileOverBase(event) {
    // this.isuploadable=false;
    this.hasBaseDropZoneOver = event;
  }

  removeQueueLIst(index) {
    this.uploader.queue.splice(index, 1);
    if (this.uploader.queue.length == 0) {
      this.isuploadable = true;
    }
  }

  cancelQueue() {
    this.isuploadable = true;
    this.uploader.queue.length = 0;
    this.OcrProgress = 0;
    this.progress = null;
    this.evtSource.close();
  }

  // getPONumbers(id) {
  //   this.sharedService.getPoNumbers(id).subscribe((data: any) => {
  //     console.log(data)
  //     this.poNumbersList = data;
  //   })
  // }

  uploadInvoice() {
    this.processStage = '0/2 (step 1) : Uploading invoice started';
    this.progress = 1;
    const formData = new FormData();
    formData.append('file', this.invoiceUploadDetails);

    this.http
      .post(
        `${environment.apiUrl}/${this.apiVersion}/VendorPortal/uploadfile/${this.vendorAccountId}`,
        formData,
        {
          reportProgress: true,
          observe: 'events',
        }
      )
      .pipe(
        map((event: any) => {
          if (event.type == HttpEventType.UploadProgress) {
            this.progress = Math.round((100 / event.total) * event.loaded);
          } else if (event.type == HttpEventType.Response) {
            this.progress = null;
            this.OCRInput = event.body.filepath;
            let filetype = event.body.filetype;
            let filename = event.body.filename;
            this.messageService.add({
              severity: 'success',
              summary: 'File Uploaded',
              detail: 'File Uploaded, OCR Process started Successfully',
            });
            this.processStage =
              '1/2 (step 2): Upload invoice done, OCR in progress.';

            /* OCR Process Starts*/
            this.OcrProgress = 1;
            // this.progressText = document.getElementById("percText");
            // this.progressWidth = document.getElementById("precWidth");
            this.updateData = {};

            const headers = new Headers({
              'Content-Type': 'application/json',
              Authorization: `Bearer ${this.authenticationService.currentUserValue.token}`,
            });
            // var EventSource = EventSourcePolyfill;
            let eventSourceObj = {
              file_path: this.OCRInput,
              vendorAccountID: this.vendorAccountId,
              poNumber: '',
              VendoruserID: this.sharedService.userId,
              filetype: filetype,
              filename: filename,
              source: 'Web',
              sender: JSON.parse(localStorage.currentLoginUser).userdetails.email,
              entityID: this.selectedEntityId
            };
            this.runEventSource(eventSourceObj);
            this.evtSource.addEventListener('update', (event: any) => {
              // Logic to handle status updates
              this.updateData = JSON.parse(event.data);
              this.progressText = this.updateData['status'];
              this.progressWidth = this.updateData['percentage'];
              if (this.progressText == 'ERROR') {
                alert('ERROR');
              }
              // console.log(event)
            });
            this.evtSource.addEventListener('end', (event: any) => {
              console.log(event.data);
              this.progressEvent = JSON.parse(event.data);
              if (this.progressEvent.InvoiceID) {
                this.selectedPONumber = '';
                this.vendorAccountName = '';
                this.OcrProgress = null;
                this.uplaodInvoiceDialog = false;
                this.invoiceUploadDetails = '';
                this.evtSource.close();
                if (this.progressEvent.InvoiceID) {
                  if (this.isCustomerPortal == false) {
                    this.route.navigate([
                      `vendorPortal/invoice/InvoiceDetails/vendorUpload/${this.progressEvent.InvoiceID}`,
                    ]);
                  } else {
                    this.route.navigate([
                      `customer/invoice/InvoiceDetails/CustomerUpload/${this.progressEvent.InvoiceID}`,
                    ]);
                  }
                  // this.tagService.createInvoice = true;
                  // this.tagService.invoicePathBoolean = true;
                  this.tagService.isUploadScreen = true;
                  this.tagService.displayInvoicePage = false;
                  this.tagService.editable = true;
                  this.tagService.submitBtnBoolean = true;
                  this.sharedService.invoiceID = this.progressEvent.InvoiceID;
                  this.tagService.headerName = 'Review Invoice';
                }
              } else {
                this.alertService.errorObject.detail =
                  this.progressEvent['status'];
                console.log(this.progressEvent['status']);
                this.messageService.add(this.alertService.errorObject);
                this.OcrProgress = null;
                this.isuploadable = true;
                this.uplaodInvoiceDialog = false;
                this.invoiceUploadDetails = '';
                this.evtSource.close();
              }
            });
            this.evtSource.onerror = (err) => {
              this.messageService.add({
                severity: 'error',
                summary: 'error',
                detail: 'Something went wrong, Plase try again',
              });
              this.OcrProgress = null;
              this.processStage = '';
              console.error('EventSource failed:', err);
              this.evtSource.close();
            };
          }
        }),
        catchError((err: any) => {
          this.progress = null;
          this.evtSource.close();
          alert(err.message);
          return throwError(err.message);
        })
      )
      .toPromise();

    if (this.OCRInput) {
      console.log(1);
    }
  }
}
