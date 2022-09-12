import { Router } from '@angular/router';
import { HttpClient, HttpEventType } from '@angular/common/http';
import { Component, ElementRef, OnInit, ViewChild } from '@angular/core';
import { MessageService } from 'primeng/api';
import { Subject, throwError } from 'rxjs';
import { catchError, map } from 'rxjs/operators';
import { ServiceInvoiceService } from 'src/app/services/serviceBased/service-invoice.service';
import { environment } from 'src/environments/environment.prod';
import * as XLSX from 'xlsx';
import * as fileSaver from 'file-saver';


@Component({
  selector: 'app-bulk-upload-service',
  templateUrl: './bulk-upload-service.component.html',
  styleUrls: ['./bulk-upload-service.component.scss']
})
export class BulkUploadServiceComponent implements OnInit {
  spinnerEnabled = false;
  btnEnabled = false;
  keys: string[];
  dataSheet = new Subject();
  dataSheet1 = new Subject();
  @ViewChild('inputFile') inputFile: ElementRef;
  isExcelFile: boolean;
  keys1: string[];
  erpSelectionBoolean: boolean;
  uploadSectionBoolean: boolean;
  displayErpBoolean;
  ERPList = [
    { erp: 'EBS' },
    { erp: 'EDP' },
  ]
  progress: number;
  UploadDetails: string | Blob;
  selectedERPType: any;
  fileChoosen = "No file chosen";

  constructor(private http: HttpClient,
    private router: Router,
    private spService: ServiceInvoiceService,
    private messageService: MessageService) { }


  onChange(evt) {
    this.UploadDetails = evt.target.files[0];
    this.fileChoosen = evt.target.files[0].name;
    let data, data1, header;
    const target: DataTransfer = <DataTransfer>(evt.target);
    this.isExcelFile = !!target.files[0].name.match(/(.xls|.xlsx)/);
    if (target.files.length > 1) {
      this.inputFile.nativeElement.value = '';
    }
    if (this.isExcelFile) {
      this.spinnerEnabled = true;
      this.btnEnabled = true;
      const reader: FileReader = new FileReader();
      reader.onload = (e: any) => {
        /* read workbook */
        const bstr: string = e.target.result;
        const wb: XLSX.WorkBook = XLSX.read(bstr, { type: 'binary' });

        /* grab first sheet */
        let index = wb.SheetNames.findIndex(ele => {
          return 'Master Template' == ele;
        });
        const wsname: string = wb.SheetNames[index];
        const ws: XLSX.WorkSheet = wb.Sheets[wsname];

        /* grab second sheet */
        let index1 = wb.SheetNames.findIndex(ele => {
          return 'Cost Category Template' == ele;
        });
        const wsname1: string = wb.SheetNames[index1];
        const ws1: XLSX.WorkSheet = wb.Sheets[wsname1];

        /* save data */
        data = XLSX.utils.sheet_to_json(ws);
        data1 = XLSX.utils.sheet_to_json(ws1);
      };

      reader.readAsBinaryString(target.files[0]);

      reader.onloadend = (e) => {
        this.spinnerEnabled = false;
        this.keys = Object.keys(data[0]);
        this.keys1 = Object.keys(data1[0]);
        this.dataSheet.next(data)
        this.dataSheet1.next(data1)
      }
    } else {
      this.inputFile.nativeElement.value = '';
    }
  }

  removeData() {
    this.btnEnabled = false;
    this.inputFile.nativeElement.value = '';
    this.dataSheet.next(null);
    this.dataSheet1.next(null);
    this.keys = null;
    this.keys1 = null;
  }

  selectedErp(val) {
    console.log(val)
    this.selectedERPType = val;
    this.erpSelectionBoolean = true;
  }
  downloadTemplate() {

    this.spService.downloadTemplate(this.selectedERPType).subscribe((data: any) => {
      this.excelDownload(data,'Bulkupload_template_serina');

      this.uploadSectionBoolean = true;
      this.displayErpBoolean = false;
      this.spService.displayErpBoolean = false;
      this.messageService.add({
        severity: "success",
        summary: "File Downloaded",
        detail: "File Downloaded Successfully"
      });
    }, error => {
      this.messageService.add({
        severity: "error",
        summary: "error",
        detail: "Download failed, please try again"
      });
    })
  }
  excelDownload(data,type){
    let blob: any = new Blob([data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet; charset=utf-8' });
    const url = window.URL.createObjectURL(blob);
    let d = new Date();
    let datestring = d.getDate() + "-" + (d.getMonth() + 1) + "-" + d.getFullYear() + " " +
      d.getHours() + ":" + d.getMinutes();
    fileSaver.saveAs(blob, `${type}-${this.selectedERPType}-(${datestring})`);
  }
  uploadXlFile() {
    this.progress = 1;
    const formData = new FormData();
    formData.append("file", this.UploadDetails);

    this.http
      .post(`${environment.apiUrl}/${environment.apiVersion}/SP/BulkUploadData`, formData, {
        reportProgress: true,
        observe: "events"
      })
      .pipe(
        map((event: any) => {
          if (event.type == HttpEventType.UploadProgress) {
            this.progress = Math.round((100 / event.total) * event.loaded);

          } else if (event.type == HttpEventType.Response) {
            this.progress = null;
            console.log(event.body.Result.result)
            let result = event.body.Result.result.split(" ");
            if(result[0] != "0"){
              this.messageService.add({
                severity: "success",
                summary: "File Uploaded",
                detail: event.body.Result.result
              });
              this.spService.downloadRejectRecords().subscribe(data => {
                this.excelDownload(data,'Rejected_accounts_serina');
              })
              setTimeout(() => {
                this.router.navigate([`/customer/serviceProvider`]);
              }, 4000);
            } else if(result[0] == result[result.length-1]){
              this.messageService.add({
                severity: "success",
                summary: "File Uploaded",
                detail: event.body.Result.result
              });
              setTimeout(() => {
                this.router.navigate([`/customer/serviceProvider`]);
              }, 4000);
            } else if(result[0] == "0") {
              this.spService.downloadRejectRecords().subscribe(data => {
                this.excelDownload(data,'Rejected_accounts_serina');
              })
              this.messageService.add({
                severity: "error",
                summary: "error",
                detail: "Accounts having some issue, please try again"
              });
            }

          }

        }),
        catchError((err: any) => {
          this.progress = null;
          this.messageService.add({
            severity: "error",
            summary: "error",
            detail: "Upload failed, please try again"
          });
          return throwError(err.message);
        })
      )
      .toPromise();
  }
  ngOnInit(): void {
    this.displayErpBoolean = this.spService.displayErpBoolean;
  }

}
