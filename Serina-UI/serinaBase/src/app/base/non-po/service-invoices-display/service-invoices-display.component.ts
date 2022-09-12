import { Component, Input, OnInit, ViewChild } from '@angular/core';
import { FormGroup } from '@angular/forms';
import { NgxSpinnerService } from 'ngx-spinner';
import { MessageService } from 'primeng/api';
import { ServiceInvoiceService } from 'src/app/services/serviceBased/service-invoice.service';
import { SharedService } from 'src/app/services/shared.service';
import { TaggingService } from 'src/app/services/tagging.service';

@Component({
  selector: 'app-service-invoices-display',
  templateUrl: './service-invoices-display.component.html',
  styleUrls: ['./service-invoices-display.component.scss']
})
export class ServiceInvoicesDisplayComponent implements OnInit {

    @ViewChild("canvas") canvas;
    @Input() filename;
    @Input() erpVoucherStatus;
    @ViewChild('inputv') inputv;
  
    keyrequired:any={};
  
    keyRequiredboolean:boolean =true;
  
    isEditable: boolean;
    editable: boolean;
    rect: any;
    rectCoords: any;
    inputData = [];
    vendorDetails: FormGroup;
  
    page: number = 1;
    totalPages: number;
    isLoaded: boolean = false;
  
    isRect: boolean;
    mergedArray: any;
    inputDisplayArray = [];
    updateInvoiceData = [];
    showInvoice: any;
    mergedLineData: any;
    lineDisaplyarray = [];
    lineDisplayData: any;
  
    zoomdata: number = 1;
    requiredBoolen: boolean;
    constructor( private tagService: TaggingService,
      private sharedService: SharedService,
      private messageService: MessageService,
      private serviceInvoice : ServiceInvoiceService,
      private SpinnerService: NgxSpinnerService,) {

    }
  
    ngOnInit(): void {
  
      this.editable = this.tagService.editable;
      this.showInvoice = this.serviceInvoice.invoiceDetals;
      this.requiredBoolen = this.serviceInvoice.requiredBoolean
      console.log(this.showInvoice)
      this.displayInvoiceDataDetails();
    }
  
  
    zoomIn() {
      this.zoomdata = this.zoomdata + 0.1
    }
    zoomOut() {
      this.zoomdata = this.zoomdata - 0.1
    }

    drawrectangleonHighlight() {
      // var rect, isDown, origX, origY;
      // this.removeEvents();
  
      // isDown = true;
  
      // origX = 30;
      // origY = 200;
  
      // rect = new fabric.Rect({
      //   left: 100,
      //   top: 30,
      //   originX: 'left',
      //   originY: 'top',
      //   angle: 0,
      //   fill: 'rgba(255,0,0,0.5)',
      //   selectable: false,
      //   transparentCorners: false
      // });
      // this.canvas.add(rect);
      // let rectObj = {
      //   xl: rect.aCoords.bl.x,
      //   yt: rect.aCoords.tr.y,
      //   xr: rect.aCoords.tr.x,
      //   yb: rect.aCoords.bl.y,
      //   width: rect.width,
      //   height: rect.height
      // }
      // console.log(rect);
      // console.log(rectObj);
      // this.ngAfterViewInit();
  
    }

    addVendorDetails() {
      console.log(this.vendorDetails.value);
    }
    onChangeValue(key, value, data) {
      let count = 0;
      let requiredFieldArray = this.inputData.filter((element)=>{
        return element.highlight
      })
      this.keyrequired[key]=value;
  
      this.inputData.forEach((element)=>{
        if(element.highlight && this.keyrequired[element.TagLabel]  && this.keyrequired[element.TagLabel].length > 0){
          count= count+1;
        }
      })
      if(requiredFieldArray.length == count){
        this.keyRequiredboolean = false;
      } else{
        this.keyRequiredboolean = true;
      }
      let updateValue = {
        "invoiceDataID": data.idInvoiceData,
        "invoiceTagDefID": data.idInvoiceTagDef,
        "OldValue": data.Value,
        "NewValue": value
      }
      if(key == 'invoice_date'){
        if(value.match(/\d{4}-(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)-\d{2}/gi)){
  
          this.updateInvoiceData.push(updateValue)
        }else{
          this.inputv.value ='';
          alert("please enter YYYY-MMM-DD in this format");
  
        }
      }
      else if(key == 'Invoice Date'){
        if(value.match(/^\d{2}[/]\d{2}[/]\d{4}$/)){
  
          this.updateInvoiceData.push(updateValue)
        }else{
          value =''
          alert("please enter DD/MM/YYYY in this format");
  
        }
      }
      else if(key == 'Issue Date'){
        if(value.match(/^\d{2}[/]\d{2}[/]\d{4}$/)){
  
          this.updateInvoiceData.push(updateValue)
        }else{
          value =''
          alert("please enter DD/MM/YYYY in this format");
  
        }
      }
      else if(key == 'bill_date'){
        if(value.match(/\d{2} (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d{4}/gi)){
  
          this.updateInvoiceData.push(updateValue)
        }else{
          value =''
          alert("please enter DD MMM YYYY in this format");
  
        }
      }
       else{
        this.updateInvoiceData.push(updateValue)
      }
    }
    onChangeValueLine(oldV, newV, InId, tagId) {
      let updateValue = {
        "invoiceDataID": InId,
        "invoiceTagDefID": tagId,
        "OldValue": oldV,
        "NewValue": newV
      }
      this.updateInvoiceData.push(updateValue)
    }
  
    onSubmitData() {
      this.SpinnerService.show();
      console.log(this.updateInvoiceData);
      this.sharedService.updateInvoiceDetails(JSON.stringify(this.updateInvoiceData)).subscribe((data: any) => {
        if (data.result == 'success') {
          this.messageService.add({
            severity: "info",
            summary: "Updated",
            detail: "Updated Successfully"
          });
          this.displayInvoiceDataDetails()
  
        } else {
          this.messageService.add({
            severity: "error",
            summary: "error",
            detail: "Something went wrong"
          });
        }
        this.updateInvoiceData = [];
        this.SpinnerService.hide();
      })
    }

    displayInvoiceDataDetails() {
      // this.SpinnerService.show();
      // this.inputDisplayArray = [];
      // this.lineDisaplyarray = [];
      // this.sharedService.displayInvoiceDetails().subscribe((data: any) => {
      //   console.log(data)
      //   data.invoicedata.forEach(element => {
      //     this.mergedArray = { ...element.InvoiceData, ...element.InvoiceTagDef }
  
      //     this.inputDisplayArray.push(this.mergedArray)
  
      //   });
      //   this.inputData = this.inputDisplayArray
      //   this.inputData.forEach((e)=>{
      //     this.keyrequired[e.TagLabel]=e.Value;
      //   })
      //   this.lineDisplayData = data.lineitems;
      //   this.SpinnerService.hide();
      // })
    }
    viewDownload() {
      // this.sharedService.downloadInvoiceData().subscribe((response: any) => {
      //   let blob: any = new Blob([response], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet; charset=utf-8' });
      //   const url = window.URL.createObjectURL(blob);
      //   // window.open(url);
      //   //window.location.href = response.url;
      //   // fileSaver.saveAs(blob, this.filename);
      //   //}), error => console.log('Error downloading the file'),
      // }), (error: any) => console.log('Error downloading the file'),
      //   () => console.info('File downloaded successfully');
    }
    downloadXL(data) {
      const blob = new Blob([data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
      const url = window.URL.createObjectURL(blob);
      window.open(url);
    }
    afterLoadComplete(pdfData: any) {
      this.totalPages = pdfData.numPages;
      this.isLoaded = true;
    }
  
    nextPage() {
      this.page++;
    }
  
    prevPage() {
      this.page--;
    }
  

}
