import { AlertService } from './../../../services/alert/alert.service';
import { ExceptionsService } from './../../../services/exceptions/exceptions.service';
import { AuthenticationService } from './../../../services/auth/auth-service.service';
import { DataService } from './../../../services/dataStore/data.service';
import { Subscription } from 'rxjs';
import { PermissionService } from './../../../services/permission.service';
import { Router, ActivatedRoute } from '@angular/router';
import { MessageService } from 'primeng/api';
import { NgxSpinnerService } from 'ngx-spinner';
import { SharedService } from 'src/app/services/shared.service';
import { TaggingService } from './../../../services/tagging.service';
import {
  ChangeDetectionStrategy,
  Component,
  HostListener,
  OnDestroy,
  OnInit,
  ViewChild,
} from '@angular/core';
import { fabric } from 'fabric';
import { Location } from '@angular/common';
import { FormBuilder, Validators, FormGroup } from '@angular/forms';
import * as $ from 'jquery';
import { PdfViewerComponent } from 'ng2-pdf-viewer';
import { DomSanitizer } from '@angular/platform-browser';
import IdleTimer from '../../idleTimer/idleTimer';

@Component({
  selector: 'app-view-invoice',
  templateUrl: './view-invoice.component.html',
  styleUrls: ['./view-invoice.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ViewInvoiceComponent implements OnInit, OnDestroy {
  @ViewChild('canvas') canvas;
  @ViewChild(PdfViewerComponent, { static: false })
  private pdfViewer: PdfViewerComponent;

  @ViewChild('pdfviewer') pdfviewer;
  vendorsSubscription: Subscription;
  isEditable: boolean;
  editable: boolean;
  rect: any;
  rectCoords: any;
  inputData = [];
  vendorDetails: FormGroup;
  isRect: boolean;
  isTagged: boolean = false;

  mergedArray: any;
  inputDisplayArray = [];
  vendorData = [];
  lineDisplayData: any;
  lineData = [];
  Itype: string;
  updateInvoiceData: any = [];
  imgArray: { id: string; url: string }[];
  headerName: string;
  editPermissionBoolean: boolean;
  changeApproveBoolean: boolean;
  financeApproveBoolean: boolean;
  fin_boolean: boolean;
  submitBtn_boolean: boolean;
  approveBtn_boolean: boolean;
  innerHeight: number;
  InvoiceHeight: number = 560;
  zoomdata: number = 1;
  showInvoice: any;
  page: number = 1;
  totalPages: number;
  isLoaded: boolean = false;
  invoiceID: any;
  routeIdCapture: Subscription;
  byteArray: Uint8Array;

  vendorDetalilsEditBoolean: boolean = false;
  displayrejectDialog: boolean;
  rejectOption = { value: '' };
  rejectionComments: string = '';

  vendorUplaodBoolean: boolean;

  isPdfAvailable: boolean;
  userDetails: any;
  isServiceData: boolean;
  serviceData: any;
  showPdf: boolean;
  btnText = 'View PDF';
  isImgBoolean: boolean;
  zoomVal: number = 0.8;
  rotation = 0;
  readvendorsData: any;
  timer: any;
  callSession: any;
  GRNUploadID: any;
  reuploadBoolean: boolean;
  vendorName: any;
  invoiceNumber = '';
  rejectpopBoolean: boolean;
  deletepopBoolean:boolean;
  checkItemBoolean:boolean;
  popUpHeader: string;
  lineTabBoolean: boolean;
  item_code: any;

  constructor(
    fb: FormBuilder,
    private tagService: TaggingService,
    private router: Router,
    private authService: AuthenticationService,
    private _location: Location,
    private activatedRoute: ActivatedRoute,
    private messageService: MessageService,
    private SpinnerService: NgxSpinnerService,
    private permissionService: PermissionService,
    private dataService: DataService,
    private exceptionService: ExceptionsService,
    private AlertService: AlertService,
    private SharedService: SharedService,
    private _sanitizer: DomSanitizer
  ) {}

  ngOnInit(): void {
    this.init();
    this.AddPermission();
    this.readVendors();
    if (this.tagService.editable == true) {
      this.updateSessionTime();
      this.idleTimer(180, 'Start');
      this.callSession = setTimeout(() => {
        this.updateSessionTime();
      }, 250000);
    }
  }
  init() {
    if (
      this.router.url.includes('invoice/InvoiceDetails/vendorUpload') ||
      this.router.url.includes('invoice/InvoiceDetails/CustomerUpload')
    ) {
      this.vendorUplaodBoolean = true;
    } else {
      this.vendorUplaodBoolean = false;
    }
    if (this.router.url.includes('InvoiceDetails')) {
      this.Itype = 'Invoice';
    } else if (this.router.url.includes('PODetails')) {
      this.Itype = 'PO';
    } else if (this.router.url.includes('GRNDetails')) {
      this.Itype = 'GRN';
    }
    this.routeIdCapture = this.activatedRoute.params.subscribe((params) => {
      this.SharedService.invoiceID = params['id'];
      this.exceptionService.invoiceID = params['id'];
      this.invoiceID = params['id'];
      this.getInvoiceFulldata();
      this.readFilePath();
    });
    this.onResize();
    // this.Itype = this.tagService.type;
    this.editable = this.tagService.editable;
    this.fin_boolean = this.tagService.financeApprovePermission;
    this.submitBtn_boolean = this.tagService.submitBtnBoolean;
    this.approveBtn_boolean = this.tagService.approveBtnBoolean;
    this.headerName = this.tagService.headerName;
    this.userDetails = this.authService.currentUserValue;

    this.showPdf = true;
    this.btnText = 'Close';
  }

  idleTimer(time, str) {
    this.timer = new IdleTimer({
      timeout: time, //expired after 180 secs
      clean: str,
      onTimeout: () => {
        if (this.router.url.includes('ExceptionManagement/InvoiceDetails')) {
          if (this.router.url.includes('vendorPortal')) {
            this.router.navigate(['/vendorPortal/ExceptionManagement']);
          } else {
            this.router.navigate(['/customer/ExceptionManagement']);
          }
          this.AlertService.errorObject.detail =
            'Session Expired for Editing Invoice';
          this.messageService.add(this.AlertService.errorObject);
        }
      },
    });
  }

  updateSessionTime() {
    let sessionData = {
      session_status: true,
    };
    this.exceptionService
      .updateDocumentLockInfo(JSON.stringify(sessionData))
      .subscribe((data: any) => {});
  }

  readVendors() {
    this.vendorsSubscription = this.dataService
      .getVendorsData()
      .subscribe((data: any) => {
        this.readvendorsData = data;
      });
  }
  AddPermission() {
    if (
      this.permissionService.editBoolean == true &&
      this.permissionService.changeApproveBoolean == false &&
      this.permissionService.financeApproveBoolean == false
    ) {
      this.editPermissionBoolean = true;
    } else if (
      this.permissionService.editBoolean == true &&
      this.permissionService.changeApproveBoolean == true &&
      this.permissionService.financeApproveBoolean == false
    ) {
      this.changeApproveBoolean = true;
    } else if (
      this.permissionService.editBoolean == true &&
      this.permissionService.changeApproveBoolean == true &&
      this.permissionService.financeApproveBoolean == true
    ) {
      this.financeApproveBoolean = true;
    }
  }
  getInvoiceFulldata() {
    this.SpinnerService.show();
    this.inputDisplayArray = [];
    this.lineData = [];
    this.SharedService.getInvoiceInfo().subscribe(
      (data: any) => {
        const pushedArrayHeader = [];
        data.ok.headerdata.forEach((element) => {
          this.mergedArray = {
            ...element.DocumentData,
            ...element.DocumentTagDef,
          };
          this.mergedArray.DocumentUpdates = element.DocumentUpdates;
          pushedArrayHeader.push(this.mergedArray);
        });
        this.inputData = pushedArrayHeader;
        let inv_num_data: any = this.inputData.filter((val) => {
          return (val.TagLabel == 'InvoiceId') || (val.TagLabel ==  'bill_number');
        });
        this.invoiceNumber = inv_num_data[0]?.Value;
        if (data.ok.vendordata) {
          this.isServiceData = false;
          this.vendorData = {
            ...data.ok.vendordata[0].Vendor,
            ...data.ok.vendordata[0].VendorAccount,
            ...data.ok.vendordata[0].VendorUser,
          };
          this.vendorName = this.vendorData['VendorName'];
        }
        if (data.ok.servicedata) {
          this.isServiceData = true;
          this.vendorData = {
            ...data.ok.servicedata[0].ServiceAccount,
            ...data.ok.servicedata[0].ServiceProvider,
          };
          this.vendorName = this.vendorData['ServiceProviderName'];
        }
        if (this.Itype == 'PO') {
          let count = 0;
          let array = data.ok.linedata;
          array.forEach((val) => {
            if (val.TagName == 'ItemId') {
              val.id = 1;
            } else if (val.TagName == 'Name') {
              val.id = 2;
            } else if (val.TagName == 'ProcurementCategory') {
              val.id = 3;
            } else if (val.TagName == 'PurchQty') {
              val.id = 4;
            } else if (val.TagName == 'UnitPrice') {
              val.id = 5;
            } else if (val.TagName == 'DiscAmount') {
              val.id = 6;
            } else if (val.TagName == 'DiscPercent') {
              val.id = 7;
            } else {
              count = count + 8;
              val.id = count;
            }
          });
          this.lineDisplayData = array.sort((a, b) => a.id - b.id);
        } else {
          this.lineDisplayData = data.ok.linedata;
          this.lineDisplayData.unshift({
            TagName: 'S.NO',
            idDocumentLineItemTags: 1,
          });
          if (this.editable) {
            this.lineDisplayData.push({
              TagName: 'Actions',
              idDocumentLineItemTags: 1,
            });
          }
          this.lineDisplayData.forEach((ele) => {
            if (ele.TagName == 'S.NO') {
              ele.linedata = this.lineDisplayData[1]?.linedata;
            } else if (ele.TagName == 'Actions') {
              ele.linedata = this.lineDisplayData[1]?.linedata;
            }
          });
        }
        this.SpinnerService.hide();
      },
      (error) => {
        this.SpinnerService.hide();
        this.messageService.add({
          severity: 'error',
          summary: 'error',
          detail: 'Server error',
        });
      }
    );
  }

  readFilePath() {
    this.showInvoice = '';
    this.SpinnerService.show();
    this.SharedService.getInvoiceFilePath().subscribe(
      (data: any) => {
        if (
          data.result.filepath &&
          data.result.content_type == 'application/pdf'
        ) {
          this.isPdfAvailable = false;
          this.isImgBoolean = false;
          this.byteArray = new Uint8Array(
            atob(data.result.filepath)
              .split('')
              .map((char) => char.charCodeAt(0))
          );
          this.showInvoice = window.URL.createObjectURL(
            new Blob([this.byteArray], { type: 'application/pdf' })
          );
        } else if (data.result.content_type == 'image/jpg') {
          this.isPdfAvailable = false;
          this.isImgBoolean = true;
          this.byteArray = new Uint8Array(
            atob(data.result.filepath)
              .split('')
              .map((char) => char.charCodeAt(0))
          );
          this.showInvoice = window.URL.createObjectURL(
            new Blob([this.byteArray], { type: 'image/jpg' })
          );
          this.loadImage();
        } else {
          this.isPdfAvailable = true;
          this.showInvoice = '';
        }
        this.SpinnerService.hide();
      },
      (error) => {
        this.SpinnerService.hide();
        this.messageService.add({
          severity: 'error',
          summary: 'error',
          detail: 'Server error',
        });
      }
    );
  }

  DownloadPDF() {
    let a = document.createElement('a');
    document.body.appendChild(a);
    a.href = this.showInvoice;
    a.download = String(`${this.vendorName}_${this.invoiceNumber}`);
    a.click();
    window.URL.revokeObjectURL(this.showInvoice);
    a.remove();
  }

  loadImage() {
    if (this.isImgBoolean == true) {
      setTimeout(() => {
        (<HTMLDivElement>document.getElementById('parentDiv')).style.transform =
          'scale(' + this.zoomVal + ')';
        this.canvas = <HTMLCanvasElement>document.getElementById('canvas1');
        let ctx = <CanvasRenderingContext2D>this.canvas.getContext('2d');
        let img = new Image();
        img.onload = function () {
          ctx.drawImage(img, 0, 0); // Or at whatever offset you like
        };
        img.src = this.showInvoice;
        this.canvas.height = 1300;
        this.canvas.width = 900;
      }, 50);
    }
  }
  onChangeValue(key, value, data) {
    // this.inputData[0][key]=value;
    let updateValue = {
      documentDataID: data.idDocumentData,
      OldValue: data.Value ||'',
      NewValue: value,
    };
    this.updateInvoiceData.push(updateValue);
  }
  onChangeLineValue(value, data) {
    let updateValue = {
      documentLineItemID: data.idDocumentLineItems,
      OldValue: data.Value ||'',
      NewValue: value,
    };
    this.updateInvoiceData.push(updateValue);
  }
  saveChanges() {
    if (this.updateInvoiceData.length != 0) {
      this.SharedService.updateInvoiceDetails(
        JSON.stringify(this.updateInvoiceData)
      ).subscribe(
        (data: any) => {
          this.messageService.add({
            severity: 'success',
            summary: 'Saved',
            detail: 'Changes saved successfully',
          });

          this.updateInvoiceData = [];
        },
        (err) => {
          this.updateInvoiceData = [];
          this.messageService.add({
            severity: 'error',
            summary: 'error',
            detail: 'Server error or Please check the data',
          });
        }
      );
    }
  }
  onSubmitData() {
    // this.SpinnerService.show();
    // console.log(this.updateInvoiceData);
    // this.SharedService.updateInvoiceDetails(JSON.stringify(this.updateInvoiceData)).subscribe((data: any) => {
    //   console.log(data);
    //   if (data.result == 'success') {
    //     this.messageService.add({
    //       severity: "info",
    //       summary: "Updated",
    //       detail: "Updated Successfully"
    //     });
    //     this.getInvoiceFulldata();
    //   } else {
    //     this.messageService.add({
    //       severity: "error",
    //       summary: "error",
    //       detail: "Something went wrong"
    //     });
    //   }
    //   this.updateInvoiceData = [];
    //   this.SpinnerService.hide();
    // })
  }
  // async ngAfterViewInit() {
  //   console.log(this.showInvoice)
  //   if(this.showInvoice != ''){
  //     console.log(this.showInvoice)
  //     this.canvas = new fabric.Canvas('canvas1')
  //   // if(this.tagService.invoicePathBoolean == true){
  //     fabric.Image.fromURL(this.showInvoice, (img) => {
  //       img.set({
  //         opacity: 0.9,
  //         scaleX: this.canvas.width/img.width,
  //         scaleY: this.canvas.height/img.height
  //       });
  //       console.log(img.width,img.height)
  //       this.canvas.setBackgroundImage(img, this.canvas.requestRenderAll.bind(this.canvas));
  //       this.canvas.requestRenderAll();
  //     });
  //   // } else if(this.tagService.poPathBoolean== true){
  //   //   fabric.Image.fromURL('assets/purchase-order-form.jpg', (img) => {
  //   //     img.set({
  //   //       opacity: 0.9,
  //   //       scaleX: this.canvas.width/img.width,
  //   //       scaleY: this.canvas.height/img.height,
  //   //       crossOrigin: "Annoymous"
  //   //     });
  //   //     console.log(img.width,img.height)
  //   //     this.canvas.setBackgroundImage(img, this.canvas.requestRenderAll.bind(this.canvas));
  //   //     this.canvas.requestRenderAll();
  //   //   });
  //   // } else if (this.tagService.GRNPathBoolean == true){
  //   //   fabric.Image.fromURL('assets/receipt-template-us-modern-red-750px.png', (img) => {
  //   //     img.set({
  //   //       opacity: 0.9,
  //   //       scaleX: this.canvas.width/img.width,
  //   //       scaleY: this.canvas.height/img.height,
  //   //       crossOrigin: "Annoymous"
  //   //     });
  //   //     console.log(img.width,img.height)
  //   //     this.canvas.setBackgroundImage(img, this.canvas.requestRenderAll.bind(this.canvas));
  //   //     this.canvas.requestRenderAll();
  //   //   });
  //   // }
  //   this.canvas.on('mouse:down', (option)=>{
  //     this.isEditable = true;
  //   })
  //   this.canvas.on('mouse:wheel', (opt)=> {
  //     this.isRect =false;
  //     var delta = opt.e.deltaY;
  //     var pointer = this.canvas.getPointer(opt.e);
  //     var zoom = this.canvas.getZoom();
  //     zoom = zoom - delta * 0.01;
  //     if (zoom >= 20) {
  //       zoom = 20;
  //     }
  //     if (zoom <= 1) {
  //       zoom = 1;
  //       this.canvas.viewportTransform = [1, 0, 0, 1, 0, 0]
  //     }
  //     this.canvas.zoomToPoint({
  //       x: opt.e.offsetX,
  //       y: opt.e.offsetY
  //     }, zoom);
  //     opt.e.preventDefault();
  //     opt.e.stopPropagation();
  //     this.panning();
  //   });
  //   }
  //   // this.imgArray.forEach((element, index) => {
  //   //   // this.canvas.push(new fabric.Canvas(element.id))
  //   //   this.canvas = new fabric.Canvas(element.id);
  //   //   fabric.Image.fromURL(element.url, (img) => {
  //   //     img.set({
  //   //       opacity: 0.9,
  //   //       scaleX: this.canvas.width / img.width,
  //   //       scaleY: this.canvas.height / img.height,
  //   //       crossOrigin: "Annoymous"
  //   //     });
  //   //     console.log(img.width, img.height)
  //   //     this.canvas.setBackgroundImage(img, this.canvas.requestRenderAll.bind(this.canvas));
  //   //     this.canvas.requestRenderAll();
  //   //   });
  //   //   this.canvas.on('mouse:down', (option) => {
  //   //     this.isEditable = true;
  //   //   })
  //   //   this.canvas.on('mouse:wheel', (opt) => {
  //   //     // this.isCircle = false;
  //   //     this.isRect = false;
  //   //     var delta = opt.e.deltaY;
  //   //     var pointer = this.canvas.getPointer(opt.e);
  //   //     var zoom = this.canvas.getZoom();
  //   //     zoom = zoom - delta * 0.01;
  //   //     if (zoom >= 20) {
  //   //       zoom = 20;
  //   //     }
  //   //     if (zoom <= 1) {
  //   //       zoom = 1;
  //   //       this.canvas.viewportTransform = [1, 0, 0, 1, 0, 0]
  //   //     }
  //   //     this.canvas.zoomToPoint({
  //   //       x: opt.e.offsetX,
  //   //       y: opt.e.offsetY
  //   //     }, zoom);
  //   //     opt.e.preventDefault();
  //   //     opt.e.stopPropagation();
  //   //     this.panning();
  //   //   });
  //   // })
  // }

  drawrectangleonHighlight() {
    var rect = new fabric.Rect({
      left: 100,
      top: 50,
      fill: 'rgba(255,0,0,0.5)',
      width: 100,
      height: 30,
      selectable: false,
      lockMovementX: true,
      lockMovementY: true,
      lockRotation: true,
      transparentCorners: true,
      hasControls: false,
    });

    this.canvas.add(rect);
    this.canvas.setActiveObject(rect);
    // document.getElementById(index + 1).scrollIntoView();
  }

  zoomin() {
    // this.isRect = false;
    // this.canvas.setZoom(this.canvas.getZoom() * 1.1);
    // this.panning();

    this.zoomVal = this.zoomVal + 0.2;
    if (this.zoomVal >= 2.0) {
      this.zoomVal = 1;
    }
    (<HTMLDivElement>document.getElementById('parentDiv')).style.transform =
      'scale(' + this.zoomVal + ')';
  }
  zoomout() {
    // this.isRect = false;
    // this.canvas.setZoom(this.canvas.getZoom() / 1.1);
    // this.panning();
    this.zoomVal = this.zoomVal - 0.2;
    if (this.zoomVal <= 0.5) {
      this.zoomVal = 1;
    }
    (<HTMLDivElement>document.getElementById('parentDiv')).style.transform =
      'scale(' + this.zoomVal + ')';
  }
  removeEvents() {
    this.canvas.off('mouse:down');
    this.canvas.off('mouse:up');
    this.canvas.off('mouse:move');
  }

  panning() {
    this.removeEvents();
    let panning = false;
    let selectable;
    this.canvas.on('mouse:up', (e) => {
      panning = false;
    });

    this.canvas.on('mouse:down', (e) => {
      panning = true;
      selectable = false;
    });
    this.canvas.on('mouse:move', (e) => {
      if (panning && e && e.e) {
        selectable = false;
        var units = 10;
        var delta = new fabric.Point(e.e.movementX, e.e.movementY);
        this.canvas.relativePan(delta);
      }
    });
  }

  addVendorDetails() {
    console.log(this.vendorDetails.value);
  }
  onVerify(e) {
    console.log(e);
  }
  submitChanges() {
    // if (this.vendorUplaodBoolean === false) {
    //   // let submitData = {
    //   //   "documentdescription": null
    //   // }
    //   // this.SpinnerService.show();
    //   // this.SharedService.submitChangesInvoice(JSON.stringify(submitData)).subscribe((data: any) => {
    //   //   this.dataService.invoiceLoadedData = [];
    //   //   if (data.result) {
    //   //     this.messageService.add({
    //   //       severity: "success",
    //   //       summary: "Updated",
    //   //       detail: "Updated Successfully"
    //   //     });
    //   //     this.SpinnerService.hide();
    //   //     setTimeout(() => {
    //   //       this._location.back()
    //   //     }, 1000);
    //   //   }
    //   // }, error => {
    //   //   this.messageService.add({
    //   //     severity: "error",
    //   //     summary: "error",
    //   //     detail: error.error
    //   //   });
    //   //   this.SpinnerService.hide();
    //   // })

    //   this.exceptionService.send_batch_approval_review(this.exceptionService.selectedRuleId).subscribe((data:any)=>{
    //     console.log(data);
    //     this.AlertService.addObject.detail = "Send to Batch review successfully";
    //     this.messageService.add(this.AlertService.addObject);
    //     // this.displayRuleDialog = false;
    //     setTimeout(() => {
    //       this._location.back();
    //     }, 2000);
    //   },error=>{
    //     this.AlertService.errorObject.detail = error.statusText;
    //     this.messageService.add(this.AlertService.errorObject);
    //   })
    // } else {

    this.getInvoiceFulldata();
    this.GRNUploadID = this.dataService.reUploadData?.grnreuploadID;
    if (this.GRNUploadID != undefined && this.GRNUploadID != null) {
      this.reuploadBoolean = true;
    } else {
      this.reuploadBoolean = false;
    }
    setTimeout(() => {
      let count = 0;
      let errorType: string;
      let errorTypeHead: string;
      let errorTypeLine: string;
      /* header Validation starts*/
      this.inputData.forEach((data: any) => {
        if (data.TagLabel == 'InvoiceTotal' || data.TagLabel == 'SubTotal') {
          if (data.Value == '' || isNaN(+data.Value)) {
            count++;
            errorTypeHead = 'AmountHeader';
          }
        } else if (
          data.TagLabel == 'PurchaseOrder' ||
          data.TagLabel == 'InvoiceDate' ||
          data.TagLabel == 'InvoiceId'
        ) {
          if (data.Value == '') {
            errorType = 'emptyHeader';
            count++;
          }
        }
      });
      /* header Validation end*/

      /* Line Details Validation starts*/
      this.lineDisplayData.forEach((element) => {
        if (
          element.TagName == 'Quantity' ||
          element.TagName == 'UnitPrice' ||
          element.TagName == 'AmountExcTax' ||
          element.TagName == 'Amount'
        ) {
          element.linedata.forEach((ele1) => {
            if (
              ele1.DocumentLineItems?.Value == '' ||
              isNaN(+ele1.DocumentLineItems?.Value)
            ) {
              count++;
              errorTypeLine = 'AmountLine';
            }
          });
        }
      });
      /* Line Details Validation end*/

      if (count == 0) {
        this.vendorSubmit();
      } else {
        /* Error reponse starts*/
        if (errorTypeHead == 'AmountHeader') {
          setTimeout(() => {
            this.messageService.add({
              severity: 'error',
              summary: 'error',
              detail:
                'Please verify SubTotal and InvoiceTotal in Header details',
            });
          }, 50);
        }
        if (errorType == 'emptyHeader') {
          this.AlertService.errorObject.detail =
            'Please Check PO Number, Invoice Date, InvoiceId fileds in header details';
          this.messageService.add(this.AlertService.errorObject);
        }
        if (errorTypeLine == 'AmountLine') {
          setTimeout(() => {
            this.messageService.add({
              severity: 'error',
              summary: 'error',
              detail:
                'Please verify Amount, Quntity, unitprice and AmountExcTax in Line details',
            });
          }, 10);
        }
        /* Error reponse end*/
      }
    }, 2000);
  }

  vendorSubmit() {
    this.SharedService.vendorSubmit(this.reuploadBoolean).subscribe(
      (data: any) => {
        this.dataService.invoiceLoadedData = [];
        this.SpinnerService.hide();
        if (this.router.url.includes('ExceptionManagement')) {
          this.AlertService.addObject.detail = 'send to batch successfully';
          this.AlertService.addObject.summary = 'sent';
          this.messageService.add(this.AlertService.addObject);
        } else {
          if (!this.GRNUploadID) {
            this.messageService.add({
              severity: 'success',
              summary: 'Uploaded',
              detail: 'Uploaded to serina successfully',
            });
          }
        }
        let query = '';
        if (this.GRNUploadID) {
          query = `?re_upload=${this.reuploadBoolean}&grnreuploadID=${this.GRNUploadID}`;
        } else {
          query = `?re_upload=${this.reuploadBoolean}`;
        }

        this.SharedService.triggerBatch(query).subscribe((data: any) => {
          if (
            this.vendorUplaodBoolean == true &&
            this.reuploadBoolean == true
          ) {
            if (data[0] == 0) {
              this.messageService.add({
                severity: 'error',
                summary: 'Rejected',
                detail: data[1],
              });
            } else {
              this.messageService.add({
                severity: 'success',
                summary: 'Uploaded',
                detail: data[1],
              });
            }
          }

          this.dataService.reUploadData = [];
        });
        setTimeout(() => {
          if (this.router.url.includes('ExceptionManagement')) {
            this._location.back();
          } else {
            if (this.userDetails.user_type == 'vendor_portal') {
              this.router.navigate(['vendorPortal/invoice/allInvoices']);
            } else {
              this.router.navigate(['customer/invoice/allInvoices']);
            }
          }
        }, 4000);
      },
      (error) => {
        this.messageService.add({
          severity: 'error',
          summary: 'error',
          detail: error.statusText,
        });
      }
    );
  }

  approveChanges() {
    // let approve = {
    //   "documentdescription": ""
    // }
    // this.SharedService.approveInvoiceChanges(JSON.stringify(approve)).subscribe((data: any) => {
    //   this.dataService.invoiceLoadedData = [];
    //   this.messageService.add({
    //     severity: "success",
    //     summary: "Approved",
    //     detail: "Changes approved successfully"
    //   });
    //   setTimeout(() => {
    //     this._location.back()
    //   }, 1000);
    // }, error => {
    //   this.messageService.add({
    //     severity: "error",
    //     summary: "error",
    //     detail: error.statusText
    //   });
    // })

    this.exceptionService.send_batch_approval().subscribe(
      (data: any) => {
        this.AlertService.addObject.detail = 'Send to batch successfully';
        this.messageService.add(this.AlertService.addObject);
        setTimeout(() => {
          this._location.back();
        }, 2000);
      },
      (error) => {
        this.AlertService.errorObject.detail = error.statusText;
        this.messageService.add(this.AlertService.errorObject);
      }
    );
  }

  financeApprove() {
    this.SharedService.financeApprovalPermission().subscribe(
      (data: any) => {
        this.dataService.invoiceLoadedData = [];
        this.messageService.add({
          severity: 'success',
          summary: 'Approved',
          detail: data.result,
        });
        setTimeout(() => {
          this._location.back();
        }, 1000);
      },
      (error) => {
        this.messageService.add({
          severity: 'error',
          summary: 'error',
          detail: error.statusText,
        });
      }
    );
  }

  Reject() {
    let rejectionData = {
      documentdescription: this.rejectionComments,
      userAmount: 0,
    };
    if (this.rejectOption.value == 'IT_reject') {
      this.SharedService.ITRejectInvoice(
        JSON.stringify(rejectionData)
      ).subscribe(
        (data: any) => {
          this.dataService.invoiceLoadedData = [];
          this.messageService.add({
            severity: 'success',
            summary: 'Rejected',
            detail: 'Successfully send rejection for IT',
          });
          this.displayrejectDialog = false;
          setTimeout(() => {
            this._location.back();
          }, 1000);
        },
        (error) => {
          this.messageService.add({
            severity: 'error',
            summary: 'error',
            detail: error.error,
          });
        }
      );
    } else {
      this.SharedService.vendorRejectInvoice(
        JSON.stringify(rejectionData)
      ).subscribe(
        (data: any) => {
          this.dataService.invoiceLoadedData = [];
          this.messageService.add({
            severity: 'success',
            summary: 'Rejected',
            detail: 'Successfully send rejection for Vendor',
          });
          this.displayrejectDialog = false;
          setTimeout(() => {
            this._location.back();
          }, 1000);
        },
        (error) => {
          this.messageService.add({
            severity: 'error',
            summary: 'error',
            detail: 'Something went wrong',
          });
        }
      );
    }
  }

  backToInvoice() {
    if (this.vendorUplaodBoolean === false) {
      this._location.back();
    } else {
      if (
        confirm(
          ` Are you sure you want cancel process ? \n if you click OK you will lost your invoice meta data.`
        )
      ) {
        this._location.back();
      }
    }
    // else {
    //   this._location.back();
    // }
  }
  @HostListener('window:resize', ['$event'])
  onResize() {
    this.innerHeight = window.innerHeight;
    if (this.innerHeight > 550 && this.innerHeight < 649) {
      this.InvoiceHeight = 500;
    } else if (this.innerHeight > 650 && this.innerHeight < 700) {
      this.InvoiceHeight = 560;
    } else if (this.innerHeight > 750) {
      this.InvoiceHeight = 660;
    }
  }
  zoomIn() {
    this.zoomdata = this.zoomdata + 0.1;
  }
  zoomOut() {
    this.zoomdata = this.zoomdata - 0.1;
  }
  afterLoadComplete(pdfData: any) {
    this.totalPages = pdfData.numPages;
    this.isLoaded = true;
  }
  textLayerRendered(e: CustomEvent) {}

  nextPage() {
    this.page++;
  }

  prevPage() {
    this.page--;
  }
  selectedText(): void {}

  search(stringToSearch: string) {
    this.pdfViewer.pdfFindController.executeCommand('find', {
      caseSensitive: false,
      findPrevious: undefined,
      highlightAll: true,
      phraseSearch: true,
      query: stringToSearch,
    });
  }

  rotate(angle: number) {
    this.rotation += angle;
  }

  convertInchToPixel(arr: any) {
    // let diagonalpixel = Math.sqrt(Math.pow(window.screen.width,2)+Math.pow(window.screen.height,2));
    // let diagonalinch = diagonalpixel/72;
    // let ppi = diagonalpixel/diagonalinch;
    let ppi = 96;
    let Height = arr.Height * ppi;
    let Width = arr.Width * ppi;
    let Xcord = arr.Xcord * ppi;
    let Ycord = arr.Ycord * ppi;
    return [Height, Width, Xcord, Ycord];
  }

  hightlight(val) {
    let boundingBox = this.convertInchToPixel(val);
    let hgt: number = boundingBox[0];
    let wdt = boundingBox[1];
    let xa = boundingBox[2];
    let ya = boundingBox[3];
    var pageno = parseInt('1');
    var pageView = this.pdfViewer.pdfViewer._pages[pageno - 1];
    //datas - array returning from server contains synctex output values
    var left = xa;
    var top = ya;
    var width = wdt;
    var height = hgt;
    //recalculating top value
    top = pageView.viewport.viewBox[3] - top;
    var valueArray = [left, top, left + width, top + height];
    let rect = pageView.viewport.convertToViewportRectangle(valueArray);
    // rect       = PDFJS.disableTextLayer.normalizeRect(rect);
    var x = Math.min(rect[0], rect[2]),
      width = Math.abs(rect[0] - rect[2]);
    var y = Math.min(rect[1], rect[3]),
      height = Math.abs(rect[1] - rect[3]);
    const element = document.createElement('div');
    element.setAttribute('class', 'overlay-div-synctex');
    element.style.left = x + 'px';
    element.style.top = y + 'px';
    element.style.width = width + 'px';
    element.style.height = height + 'px';
    element.style.position = 'absolute';
    element.style.backgroundColor = 'rgba(200,0,0,0.5)';
    $('*[data-page-number="' + pageno + '"]').append(element);
    this.pdfviewer.pdfViewer._scrollIntoView({
      pageDiv: pageView.div,
    });
  }

  onClick(e) {
    const textLayer = document.getElementsByClassName('TextLayer');
    const x =
      window.getSelection().getRangeAt(0).getClientRects()[0].left -
      textLayer[0].getBoundingClientRect().left;
    const y =
      window.getSelection().getRangeAt(0).getClientRects()[0].top -
      textLayer[0].getBoundingClientRect().top;
  }

  open_dialog(str, val) {
    if (str == 'reject') {
      this.popUpHeader = ' ADD Rejection Comments';
      this.rejectpopBoolean = true;
      this.deletepopBoolean = false;
      this.checkItemBoolean = false;
    } else if(str == 'delete'){
      this.popUpHeader = ' Please confirm';
      this.deletepopBoolean = true;
      this.rejectpopBoolean = false;
      this.checkItemBoolean = false;
      this.item_code = val.itemCode;
    } else {
      this.popUpHeader = "Check Item code availability";
      this.deletepopBoolean = false;
      this.rejectpopBoolean = false;
      this.checkItemBoolean = true;
    }
    this.displayrejectDialog = true;
  }
  removeLine(){
    this.exceptionService.removeLineData(this.item_code).subscribe((data:any)=>{
      if(data.status == "deleted"){
        this.AlertService.addObject.detail = "Line item deleted";
        this.messageService.add(this.AlertService.addObject);
        this.displayrejectDialog = false;
        this.getInvoiceFulldata();
      }
    },err=>{
      this.AlertService.errorObject.detail = "Server error";
      this.messageService.add(this.AlertService.errorObject);
      this.displayrejectDialog = false;
    })
  };

  CheckItemStatus(item){
    this.exceptionService.checkItemCode(item).subscribe((data:any)=>{
      if(data.status == "not exists"){
        let addLineData = {
          "documentID": this.invoiceID,
          "itemCode": item
        };
        this.exceptionService.addLineItem(JSON.stringify(addLineData)).subscribe((data:any)=>{
          this.AlertService.addObject.detail = "Line item Added";
          this.messageService.add(this.AlertService.addObject);
          this.getInvoiceFulldata();
        });
        this.displayrejectDialog = false;
      } else {
        this.AlertService.errorObject.detail = "Item code already exist, Please try other item code";
        this.messageService.add(this.AlertService.errorObject);
      }
    },err=>{
      this.AlertService.errorObject.detail = "Server error";
      this.messageService.add(this.AlertService.errorObject);
      this.displayrejectDialog = false;
    })
  }

  ngOnDestroy() {
    // if (this.tagService.editable == true) {
    let sessionData = {
      session_status: false,
    };
    this.exceptionService
      .updateDocumentLockInfo(sessionData)
      .subscribe((data: any) => {});
    clearTimeout(this.callSession);
    // }

    // this.idleTimer(0,"End");
    this.tagService.financeApprovePermission = false;
    this.tagService.approveBtnBoolean = false;
    this.tagService.submitBtnBoolean = false;
    this.vendorsSubscription.unsubscribe();
  }

  viewPdf() {
    this.showPdf = !this.showPdf;
    if (this.showPdf != true) {
      this.btnText = 'View PDF';
    } else {
      this.btnText = 'Close';
    }
    this.loadImage();
  }

  changeTab(val,tab) {
    if (val === 'show') {
      this.showPdf = true;
      this.btnText = 'Close';
    } else {
      this.showPdf = false;
      this.btnText = 'View PDF';
    }
    if(tab == 'line'){
      this.lineTabBoolean = true;
    } else {
      this.lineTabBoolean = false;
    }
    this.loadImage();
  }
}
