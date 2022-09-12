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
  Component,
  HostListener,
  OnDestroy,
  OnInit,
  ViewChild,
} from '@angular/core';
import { fabric } from 'fabric';
import { Location } from '@angular/common';
import { FormBuilder, Validators, FormGroup, NgForm } from '@angular/forms';
import * as $ from 'jquery';
import { PdfViewerComponent } from 'ng2-pdf-viewer';
import { comaprisionLineData } from './testingLineData';
import { FormCanDeactivate } from '../../can-deactivate/form-can-deactivate';
import { SettingsService } from 'src/app/services/settings/settings.service';
import IdleTimer from '../../idleTimer/idleTimer';

@Component({
  selector: 'app-comparision3-way',
  templateUrl: './comparision3-way.component.html',
  styleUrls: [
    './comparision3-way.component.scss',
    '../../invoice/view-invoice/view-invoice.component.scss',
  ],
})
export class Comparision3WayComponent
  extends FormCanDeactivate
  implements OnInit
{
  @ViewChild('canvas') canvas;
  @ViewChild(PdfViewerComponent, { static: false })
  private pdfViewer: PdfViewerComponent;

  @ViewChild('pdfviewer') pdfviewer;
  @ViewChild('form')
  form: NgForm;
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
  displayRuleDialog: boolean;
  displayErrorDialog: boolean;
  SelectRuleOption = { value: '' };
  SelectErrorOption;
  givenErrors = ['Alternative', 'Identical', 'Adjustment', 'OCR Error'];
  givenRules: any;
  rejectionComments: string = '';

  grnCreateBoolean: boolean = false;
  GRNObject = [];

  isPdfAvailable: boolean;
  userDetails: any;
  showPdf: boolean;
  btnText = 'View PDF';
  lineCompareData;
  totalLineItems = ['abc', 'xyz'];
  selectedPONumber;
  poList = [,];
  filteredPO: any[];
  selectedRule = '3 way';
  lineItemsData: any;
  tagArray: any[];

  lineCount: any;
  save_rule_boolean: boolean;
  selectedRuleID: any;
  approvalType: any;
  currentTab = 'vendor';
  lineItems: any;
  inv_itemcode: any;
  po_itemcode: any;
  vendorAcId: any;
  mappedData: any;
  zoomVal: number = 0.8;

  isImgBoolean: boolean;
  financeapproveDisplayBoolean: boolean;
  displayrejectDialog: boolean;
  // lineDescription ="Select Line items";
  timer: any;
  callSession: any;
  invoiceNumber = '';
  vendorName: any;

  constructor(
    fb: FormBuilder,
    private tagService: TaggingService,
    private router: Router,
    private authService: AuthenticationService,
    private _location: Location,
    private activatedRoute: ActivatedRoute,
    private exceptionService: ExceptionsService,
    private AlertService: AlertService,
    private messageService: MessageService,
    private SpinnerService: NgxSpinnerService,
    private permissionService: PermissionService,
    private dataService: DataService,
    private settingService: SettingsService,
    private SharedService: SharedService
  ) {
    super();
  }

  ngOnInit(): void {
    this.initialData();
    this.readFilePath();
    this.AddPermission();
    
    
  }

  idleTimer(time, str) {
    this.timer = new IdleTimer({
      timeout: time, //expired after 180 secs
      clean: str,
      onTimeout: () => {
        if (this.router.url.includes('comparision-docs')) {
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

  initialData() {
    this.routeIdCapture = this.activatedRoute.params.subscribe((params) => {
      this.SharedService.invoiceID = params['id'];
      this.exceptionService.invoiceID = params['id'];
    });
    if (this.router.url.includes('Create_GRN_inv_list')) {
      if (this.permissionService.GRNPageAccess == true) {
        this.grnCreateBoolean = true;
        this.tagService.headerName = 'Create GRN';
        this.readGRNInvData();
        if(this.grnCreateBoolean){
          this.currentTab =  'line'
        }
      } else {
        alert('Sorry!, you do not have access');
        this.router.navigate(['customer/invoice/allInvoices']);
      }
    } else {
      this.getInvoiceFulldata();
      this.getRulesData();
      this.readLineItems();
      this.readErrorTypes();
      this.readMappingData();
      if (this.tagService.editable == true && this.grnCreateBoolean == false) {
      this.updateSessionTime();
      this.idleTimer(180, 'Start');
      this.callSession = setTimeout(() => {
        this.updateSessionTime();
      }, 250000);
    }
    }
    this.onResize();
    this.Itype = this.tagService.type;
    this.editable = this.tagService.editable;
    this.fin_boolean = this.tagService.financeApprovePermission;
    this.submitBtn_boolean = this.tagService.submitBtnBoolean;
    this.approveBtn_boolean = this.tagService.approveBtnBoolean;
    this.headerName = this.tagService.headerName;
    this.userDetails = this.authService.currentUserValue;
    this.approvalType = this.tagService.approvalType;
    this.financeapproveDisplayBoolean =
      this.settingService.finaceApproveBoolean;

    // this.showInvoice = "/assets/New folder/MEHTAB 9497.pdf"
    this.lineCompareData = comaprisionLineData;
  }
  getRulesData() {
    this.exceptionService.readBatchRules().subscribe((data: any) => {
      this.givenRules = data;
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

  changeTab(val) {
    this.currentTab = val;
  }

  getInvoiceFulldata() {
    this.SpinnerService.show();
    this.inputDisplayArray = [];
    this.lineData = [];
    this.showInvoice = '';
    this.exceptionService.getInvoiceInfo().subscribe(
      (data: any) => {
        this.lineDisplayData = data.linedata.Result;
        this.lineDisplayData.forEach((element) => {
          this.lineCount = element.items;
        });

        const pushedArrayHeader = [];
        data.headerdata.forEach((element) => {
          this.mergedArray = {
            ...element.DocumentData,
            ...element.DocumentTagDef,
          };
          this.mergedArray.DocumentUpdates = element.DocumentUpdates;
          pushedArrayHeader.push(this.mergedArray);
        });
        this.inputData = pushedArrayHeader;
        let inv_num_data:any = this.inputData.filter(val=>{
          return val.TagLabel == 'InvoiceId';
        })
        this.invoiceNumber = inv_num_data[0]?.Value;
        this.vendorData = {
          ...data.Vendordata[0].Vendor,
          ...data.Vendordata[0].VendorAccount,
          ...data.Vendordata[0].VendorUser,
        };
        this.vendorAcId = this.vendorData['idVendorAccount'];
        this.vendorName = this.vendorData['VendorName'];
        this.selectedRule = data.ruledata[0].Name;
        this.poList = data.all_pos;

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

  readGRNInvData() {
    this.SharedService.readReadyGRNInvData().subscribe(
      (data: any) => {
        this.lineDisplayData = data.ok.linedata;
        let dummyLineArray = this.lineDisplayData;
        dummyLineArray.forEach((ele, i, array) => {
          if (ele.TagName == 'Quantity') {
            ele.TagName = 'Inv - Quantity';
            ele.linedata?.forEach((ele2, index) => {
              ele.grndata?.forEach((ele3) => {
                ele.grndata[index].old_value = ele2.Value;
              });
            });
          } else if (ele.TagName == 'UnitPrice') {
            ele.TagName = 'Inv - UnitPrice';
          }
          if (ele.TagName == 'AmountExcTax') {
            ele.TagName = 'Inv - AmountExcTax';
          }

          setTimeout(() => {
            if (
              ele.TagName == 'Inv - Quantity' &&
              (ele.grndata == null || ele.grndata.length == 0)
            ) {
              array.splice(2, 0, {
                TagName: 'GRN - Quantity',
                linedata: ele.linedata,
              });
              array.splice(7, 0, {
                TagName: 'Comments',
                linedata: ele.linedata,
              });
            } else if (
              ele.TagName == 'Inv - Quantity' &&
              ele.grndata != null &&
              ele.grndata &&
              ele.grndata.length != 0
            ) {
              array.splice(2, 0, {
                TagName: 'GRN - Quantity',
                linedata: ele.grndata,
              });
              array.splice(7, 0, {
                TagName: 'Comments',
                linedata: ele.grndata,
              });
              let poQty = [];
              let poBalQty = [];
              ele.podata.forEach((v) => {
                if (v.TagName == 'PurchQty') {
                  poQty.push(v);
                } else if (v.TagName == 'RemainInventPhysical') {
                  poBalQty.push(v);
                }
              });
              if (poQty.length > 0) {
                array.splice(8, 0, { TagName: 'PO quantity', linedata: poQty });
                array.splice(9, 0, {
                  TagName: 'PO balance quantity',
                  linedata: poBalQty,
                });
              }
            } else if (
              ele.TagName == 'Inv - UnitPrice' &&
              (ele.grndata == null || ele.grndata.length == 0)
            ) {
              array.splice(4, 0, {
                TagName: 'GRN - UnitPrice',
                linedata: ele.linedata,
              });
            } else if (
              ele.TagName == 'Inv - UnitPrice' &&
              ele.grndata != null &&
              ele.grndata &&
              ele.grndata.length != 0
            ) {
              array.splice(4, 0, {
                TagName: 'GRN - UnitPrice',
                linedata: ele.grndata,
              });
            } else if (
              ele.TagName == 'Inv - AmountExcTax' &&
              (ele.grndata == null || ele.grndata.length == 0)
            ) {
              array.splice(6, 0, {
                TagName: 'GRN - AmountExcTax',
                linedata: ele.linedata,
              });
            } else if (
              ele.TagName == 'Inv - AmountExcTax' &&
              ele.grndata != null &&
              ele.grndata &&
              ele.grndata.length != 0
            ) {
              array.splice(6, 0, {
                TagName: 'GRN - AmountExcTax',
                linedata: ele.grndata,
              });
            }
          }, 10);
        });

        this.lineDisplayData = dummyLineArray;
        setTimeout(() => {
          this.lineDisplayData = this.lineDisplayData.filter((v) => {
            return !(
              v.TagName.includes('UnitPrice') ||
              v.TagName.includes('AmountExcTax')
            );
          });
        }, 100);
        let arr = dummyLineArray;
        setTimeout(() => {
          arr.forEach((ele1) => {
            if (ele1.TagName.includes('GRN') || ele1.TagName == 'Description') {
              this.GRNObject.push(ele1.linedata);
            }
            if (ele1.TagName == 'GRN - Quantity') {
              ele1.linedata?.forEach((el) => {
                el.is_quantity = true;
              });
            }
            this.GRNObject = [].concat(...this.GRNObject);
          });
          this.GRNObject.forEach((val) => {
            if (!val.old_value) {
              val.old_value = val.Value;
            }
          });
        }, 100);

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
        let inv_num_data:any = this.inputData.filter(val=>{
          return val.TagLabel == 'InvoiceId';
        })
        this.invoiceNumber = inv_num_data[0].Value;
        this.vendorData = {
          ...data.ok.vendordata[0].Vendor,
          ...data.ok.vendordata[0].VendorAccount,
        };
        this.vendorAcId = this.vendorData['idVendorAccount'];
        this.vendorName = this.vendorData['VendorName'];
        // this.selectedRule = data.ok.ruledata[0].Name;
        // this.poList = data.all_pos;

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
    this.SpinnerService.show();
    this.exceptionService.readFilePath().subscribe(
      (data: any) => {
        if (data.filepath && data.content_type == 'application/pdf') {
          this.isPdfAvailable = false;
          this.isImgBoolean = false;
          this.byteArray = new Uint8Array(
            atob(data.filepath)
              .split('')
              .map((char) => char.charCodeAt(0))
          );
          this.showInvoice = window.URL.createObjectURL(
            new Blob([this.byteArray], { type: 'application/pdf' })
          );
        } else if (data.content_type == 'image/jpg') {
          this.isPdfAvailable = false;
          this.isImgBoolean = true;
          this.byteArray = new Uint8Array(
            atob(data.filepath)
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

  DownloadPDF(){
    let a = document.createElement("a");
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

  drawrectangleonHighlight(index) {
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

    this.canvas[index].add(rect);
    this.canvas[index].setActiveObject(rect);
    document.getElementById(index + 1).scrollIntoView();
  }

  zoomin(index) {
    this.isRect = false;
    this.canvas[index].setZoom(this.canvas[index].getZoom() * 1.1);
    this.panning(index);
  }

  zoomout(index) {
    this.isRect = false;
    this.canvas[index].setZoom(this.canvas[index].getZoom() / 1.1);
    this.panning(index);
  }

  removeEvents(index) {
    this.canvas[index].off('mouse:down');
    this.canvas[index].off('mouse:up');
    this.canvas[index].off('mouse:move');
  }

  panning(index) {
    this.removeEvents(index);
    let panning = false;
    let selectable;
    this.canvas[index].on('mouse:up', (e) => {
      panning = false;
    });

    this.canvas[index].on('mouse:down', (e) => {
      panning = true;
      selectable = false;
    });
    this.canvas[index].on('mouse:move', (e) => {
      if (panning && e && e.e) {
        selectable = false;
        var units = 10;
        var delta = new fabric.Point(e.e.movementX, e.e.movementY);
        this.canvas[index].relativePan(delta);
      }
    });
  }

  addVendorDetails() {
  }
  onVerify(e) {
  }
  submitChanges() {
    // if (this.userDetails.user_type == 'customer_portal') {
    //   let submitData = {
    //     "documentdescription": " "
    //   }
    //   this.SpinnerService.show();
    //   this.SharedService.submitChangesInvoice(JSON.stringify(submitData)).subscribe((data: any) => {
    //     this.dataService.invoiceLoadedData = [];
    //     if (data.result) {
    //       this.messageService.add({
    //         severity: "success",
    //         summary: "Updated",
    //         detail: "Updated Successfully"
    //       });
    //       this.SpinnerService.hide();
    //       setTimeout(() => {
    //         this._location.back()
    //       }, 1000);
    //     }
    //   }, error => {
    //     this.messageService.add({
    //       severity: "error",
    //       summary: "error",
    //       detail: error.error
    //     });
    //     this.SpinnerService.hide();
    //   })
    // } else if (this.userDetails.user_type == 'vendor_portal') {
    //   this.SharedService.vendorSubmit().subscribe((data: any) => {
    //     console.log(data);
    //     this.messageService.add({
    //       severity: "success",
    //       summary: "Uploaded",
    //       detail: "Uploaded to serina successfully"
    //     });
    //     setTimeout(() => {
    //       this.router.navigate(['vendorPortal/invoice/allInvoices']);
    //     }, 1000);
    //   }, error => {
    //     this.messageService.add({
    //       severity: "error",
    //       summary: "error",
    //       detail: error.statusText
    //     });
    //   })
    // }
  }

  approveChangesManual() {
    this.exceptionService.send_manual_approval().subscribe(
      (data: any) => {
        this.AlertService.addObject.detail =
          'Send to Manual approval successfully';
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

  approveChangesBatch() {
    this.getInvoiceFulldata();
    setTimeout(() => {
      let count = 0;
      let errorType: string;
      let errorTypeHead: string;
      let errorTypeLine: string;
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
            count++;
            errorType = 'emptyHeader';
          }
        }
      });

      this.lineDisplayData.forEach((element) => {
        if (
          element.tagname == 'Quantity' ||
          element.tagname == 'UnitPrice' ||
          element.tagname == 'AmountExcTax' ||
          element.tagname == 'Amount'
        ) {
          element.items.forEach((ele) => {
            ele.linedetails.forEach((ele1) => {
              if (
                ele1.invline[0].DocumentLineItems?.Value == '' ||
                isNaN(+ele1.invline[0].DocumentLineItems?.Value)
              ) {
                count++;
                errorType = 'emptyHeader';
              }
            });
          });
        }
      });
      if (count == 0) {
        this.sendToBatch();
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

  sendToBatch() {
    this.exceptionService.send_batch_approval().subscribe(
      (data: any) => {
        this.dataService.invoiceLoadedData = [];
        this.SpinnerService.hide();
        this.AlertService.addObject.detail = 'send to batch successfully';
        this.AlertService.addObject.summary = 'sent';
        this.messageService.add(this.AlertService.addObject);
        let boolean = false;
        this.SharedService.triggerBatch(`?re_upload=${boolean}`).subscribe((data: any) => {});
        setTimeout(() => {
          if (this.router.url.includes('ExceptionManagement')) {
            this._location.back();
          }
        }, 3000);
      },
      (error) => {
        this.messageService.add({
          severity: 'error',
          summary: 'error',
          detail: 'Server error',
        });
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

  open_modal() {
    this.displayRuleDialog = true;
    this.save_rule_boolean = true;
  }

  send_review_modal() {
    this.displayRuleDialog = true;
    this.save_rule_boolean = false;
  }

  save_rule() {
    this.selectedRule = this.SelectRuleOption.value['Name'];
    this.selectedRuleID = this.SelectRuleOption.value['idDocumentRules'];
    this.displayRuleDialog = false;
  }

  sendReview() {
    this.selectedRule = this.SelectRuleOption.value['Name'];
    this.selectedRuleID = this.SelectRuleOption.value['idDocumentRules'];
    this.exceptionService
      .send_batch_approval_review(this.selectedRuleID)
      .subscribe(
        (data: any) => {
          this.AlertService.addObject.detail =
            'Send to Batch review successfully';
          this.messageService.add(this.AlertService.addObject);
          this.displayRuleDialog = false;
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

  reviewManualApprove() {
    if (confirm(`Are you sure you want to send for Manual approval?`)) {
      this.exceptionService.send_review_manual().subscribe(
        (data: any) => {
          this.AlertService.addObject.detail =
            'Send to Manual approval review successfully';
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
  }

  backToInvoice() {
    if (
      !this.router.url.includes('vendorUpload') ||
      !this.router.url.includes('CustomerUpload')
    ) {
      this._location.back();
    } else if (
      this.router.url.includes('vendorUpload') &&
      this.router.url.includes('CustomerUpload') &&
      this.submitBtn_boolean == true
    ) {
      if (
        confirm(
          ` Are you sure you want cancel process ? \n if you click OK you will lost your invoice meta data.`
        )
      ) {
        this._location.back();
      }
    } else {
      this._location.back();
    }
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
  hightlight(val) {
    var pageno = parseInt('1');
    var pageView = this.pdfViewer.pdfViewer._pages[pageno - 1];
    //datas - array returning from server contains synctex output values
    var left = parseInt('530px');
    var top = parseInt('660px');
    var width = parseInt('50px');
    var height = parseInt('20px');
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

  viewPdf() {
    this.showPdf = !this.showPdf;
    if (this.showPdf != true) {
      this.btnText = 'View PDF';
    } else {
      this.btnText = 'Close';
    }
  }

  filterPO(event) {
    let filtered: any[] = [];
    let query = event.query;
    for (let i = 0; i < this.poList.length; i++) {
      let country = this.poList[i];
      if (
        country.PODocumentID.toLowerCase().indexOf(query.toLowerCase()) == 0
      ) {
        filtered.push(country);
      }
    }
    this.filteredPO = filtered;
  }

  onSelectPO(value) {
    if (confirm(`Are you sure you want to change PO Number?`)) {
      this.exceptionService.updatePONumber(value.PODocumentID).subscribe(
        (data: any) => {
          this.AlertService.addObject.detail = 'PO Number updated successfully';
          this.messageService.add(this.AlertService.addObject);
          this.getInvoiceFulldata();
        },
        (error) => {
          this.AlertService.errorObject.detail = error.statusText;
          this.messageService.add(this.AlertService.errorObject);
        }
      );
    }
  }

  readLineItems() {
    this.exceptionService.readLineItems().subscribe((data: any) => {
      this.lineItems = data.description;
    });
  }

  readErrorTypes() {
    this.exceptionService.readErrorTypes().subscribe((data: any) => {
      this.givenErrors = data.description;
    });
  }

  lineMapping(val, el, val1) {
    let itemCodeArray = [];
    let presetBoolean: boolean = false;

    this.inv_itemcode = val;
    this.po_itemcode = el;
    if (itemCodeArray.length > 1) {
      presetBoolean = itemCodeArray.includes(el);
    }
    if (this.mappedData?.length > 0) {
      let presetArray = this.mappedData?.filter((ele1) => {
        return ele1.ItemMetaData.itemcode == el;
      });
      if (presetArray.length > 0) {
        presetBoolean = true;
      }
    }
    if (presetBoolean) {
      if (confirm('Lineitem already mapped, you want to change it again')) {
        this.displayErrorDialog = true;
      }
    } else {
      itemCodeArray.push(el);
      this.displayErrorDialog = true;
    }

    // if(el != val1){

    // }
  }

  cancelSelectErrorRule() {
    this.displayErrorDialog = false;
  }

  updateLine() {
    this.exceptionService
      .updateLineItems(
        this.inv_itemcode,
        this.po_itemcode,
        this.SelectErrorOption,
        this.vendorAcId
      )
      .subscribe(
        (data: any) => {
          this.displayErrorDialog = false;
          this.AlertService.addObject.detail = 'Line item updated successfully';
          this.messageService.add(this.AlertService.addObject);
          this.getInvoiceFulldata();
          this.readMappingData();
        },
        (error) => {
          this.AlertService.errorObject.detail = error.statusText;
          this.messageService.add(this.AlertService.errorObject);
          this.displayErrorDialog = false;
        }
      );
  }

  readMappingData() {
    this.exceptionService.readMappedData().subscribe((data: any) => {
      this.mappedData = data.description;
    });
  }

  Reject() {
    let rejectionData = {
      documentdescription: this.rejectionComments,
      userAmount: 0,
    };

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

  onChangeGrn(id, val) {}

  onSave_submit(val, boolean, txt) {
    let emptyBoolean: boolean = false;
    let commentBoolean = false;
    this.GRNObject.forEach((ele) => {
      if (ele.Value == '') {
        emptyBoolean = true;
        this.AlertService.errorObject.detail = 'Fields should not be empty!';
      } else if (ele.Value != ele.old_value) {
        // console.log(parseFloat(ele.Value),parseFloat(ele.old_value))
        if (
          ele.ErrorDesc == null ||
          ele.ErrorDesc == '' ||
          ele.ErrorDesc == 'None' ||
          ele.ErrorDesc == 'none'
        ) {
          commentBoolean = true;
          this.AlertService.errorObject.detail =
            'Please add comments for the Line which you adjusted.';
        }
      }
    });
    if (emptyBoolean == false && commentBoolean == false) {
      if (
        boolean == true &&
        confirm('Are you sure you want to create GRN, Please confirm')
      ) {
        this.CreateGRNAPI(boolean, txt);
      } else {
        this.CreateGRNAPI(false, 'GRN data saved successfully');
      }
    } else {
      this.messageService.add(this.AlertService.errorObject);
    }
  }

  CreateGRNAPI(boolean, txt) {
    this.SharedService.saveGRNData(
      boolean,
      JSON.stringify(this.GRNObject)
    ).subscribe(
      (data: any) => {
        if(data?.result[1]== 0){
          this.AlertService.addObject.severity = 'info';
          this.AlertService.addObject.detail = data?.result[0];
        } else if(data?.result[1]== 1) {
          this.AlertService.addObject.detail = data?.result[0];
        } else if(data?.result[1]== 2) {
          this.AlertService.addObject.severity = 'warn';
          this.AlertService.addObject.detail = data?.result[0];
        }
        this.messageService.add(this.AlertService.addObject);
        
        if (boolean == true) {
          setTimeout(() => {
            this.router.navigate(['/customer/Create_GRN_inv_list']);
          }, 3000);
        }
      },
      (error) => {
        if (error.status == 403) {
          this.AlertService.errorObject.detail =
            'Invoice quantity beyond threshold';
        } else {
          this.AlertService.errorObject.detail = 'Server error';
        }
        this.messageService.add(this.AlertService.errorObject);
      }
    );
  }

  ngOnDestroy() {
    if( this.grnCreateBoolean == false){
      let sessionData = {
        session_status: false,
      };
      this.exceptionService
        .updateDocumentLockInfo(sessionData)
        .subscribe((data: any) => {});
      // clearInterval(this.timer);
      clearTimeout(this.callSession);
    }
    // this.timer = null;
    this.AlertService.addObject.severity = 'success';
    this.tagService.financeApprovePermission = false;
    this.tagService.approveBtnBoolean = false;
    this.tagService.submitBtnBoolean = false;
  }
}
