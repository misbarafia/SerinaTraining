import { SharedService } from './../../../services/shared.service';
import { DatePipe } from '@angular/common';
import { HttpClient, HttpEventType } from '@angular/common/http';
import { Component, ElementRef, OnInit, ViewChild } from '@angular/core';
import { MessageService } from 'primeng/api';
import { throwError } from 'rxjs';
import { catchError, map } from 'rxjs/operators';
import { AlertService } from 'src/app/services/alert/alert.service';
import { environment } from 'src/environments/environment.prod';

@Component({
  selector: 'app-vendor-item-list',
  templateUrl: './vendor-item-list.component.html',
  styleUrls: ['./vendor-item-list.component.scss']
})
export class VendorItemListComponent implements OnInit {
  totalTableData = [];
  columnsForTotal = [];
  totalColumnHeader = [];
  totalColumnField = [];
  ColumnLengthtotal: any;
  showPaginatortotal: boolean;

  /*calender variables*/
  selectDate: Date;
  displayYear;
  minDate: Date;
  maxDate: Date;
  lastYear: number;

  spinnerEnabled = false;
  btnEnabled = false;
  keys: string[];
  @ViewChild('inputFile') inputFile: ElementRef;
  isExcelFile: boolean;
  keys1: string[];
  uploadSectionBoolean: boolean;
  progress: number;
  UploadDetails: string | Blob;
  fileChoosen = "No file chosen";

  userId:number;
  filterData: any[];
  constructor(
    private alertService : AlertService,
    private messageService : MessageService,
    private datePipe : DatePipe,
    private sharedService : SharedService,
    private http :HttpClient) { }

  ngOnInit(): void {
    this.prepareColumns();
    this.getDate();
    this.readItemStatus();
    this.userId = this.sharedService.userId;
  }

    // to prepare display columns array
    prepareColumns() {
      this.columnsForTotal = [
        { field: 'uploaded_file', header: 'File name' },
        { field: 'uploaded_datetime', header: 'Uploaded time' },
        { field: 'firstName', header: 'Uploaded By' },
        { field: 'status', header: 'Status' },
      ];
  
      this.columnsForTotal.forEach((e) => {
        this.totalColumnHeader.push(e.header);
        this.totalColumnField.push(e.field);
      });
  
      this.ColumnLengthtotal = this.columnsForTotal.length + 1;
    }

    getDate() {
      let today = new Date();
      let month = today.getMonth();
      let year = today.getFullYear();
      this.lastYear = year - 5;
      this.displayYear = `${this.lastYear}:${year}`;
      let prevYear = year - 5;
  
      this.minDate = new Date();
      this.minDate.setMonth(month);
      this.minDate.setFullYear(prevYear);
  
      this.maxDate = new Date();
      this.maxDate.setMonth(month);
      this.maxDate.setFullYear(year);
    }

    onChange(evt) {
      this.UploadDetails = evt.target.files[0];
      this.fileChoosen = evt.target.files[0].name;
      console.log(evt.target.files[0])
      const target: DataTransfer = <DataTransfer>(evt.target);
      this.isExcelFile = !!target.files[0].name.match(/(.xls|.xlsx)/);
      if(this.isExcelFile === true) {
        this.btnEnabled = true;
      } else {
        this.btnEnabled = false;
      }
      if (target.files.length > 1) {
        this.inputFile.nativeElement.value = '';
      }
      if (this.isExcelFile) {
      } else {
        this.inputFile.nativeElement.value = '';
      }
    }



    uploadFile_item(){
      this.progress = 1;
      const formData = new FormData();
      formData.append("file", this.UploadDetails);
  
      this.http
        .post(`${environment.apiUrl}/${environment.apiVersion}/Invoice/uploadMasterItemMapping/${this.userId}`, formData, {
          reportProgress: true,
          observe: "events"
        })
        .pipe(
          map((event: any) => {
            if (event.type == HttpEventType.UploadProgress) {
              this.progress = Math.round((100 / event.total) * event.loaded);
  
            } else if (event.type == HttpEventType.Response) {
              this.progress = null;
              console.log(event.body)
              this.alertService.addObject.detail = "File is Uploaded Successfully";
              this.messageService.add(this.alertService.addObject);
              this.fileChoosen = '';
              this.btnEnabled = false;
              setTimeout(() => {
                this.readItemStatus();
              }, 5000);
            }
  
          }),
          catchError((err: any) => {
            this.progress = null;
            this.alertService.errorObject.detail = "Server error";
            this.messageService.add(this.alertService.errorObject);
            return throwError(err.message);
          })
        )
        .toPromise();
    }

    readItemStatus(){
      this.sharedService.getItemFileStatus().subscribe((data:any)=>{

        let dataArray = [];
        data.result.forEach(val=>{
          let mergeData = {...val.ItemMapUploadHistory,...val.User};
          dataArray.push(mergeData)
        })
        this.totalTableData = dataArray;

        this.filterData = this.totalTableData;
        if(this.totalTableData.length >10){
          this.showPaginatortotal = true;
        }
      })
    }

    filterMonthData(val){
      let month = val.getMonth();
      let filterArray = [];
      this.totalTableData = this.filterData;
      this.totalTableData.forEach(ele=>{
        let uploadDataMonth:any = new Date(ele.uploadeddate).getMonth();
        if(month == uploadDataMonth){
          filterArray.push(ele);
        }
      });
      this.totalTableData = filterArray;
    }

    clearDates(){
      this.totalTableData = this.filterData;
    }

}
