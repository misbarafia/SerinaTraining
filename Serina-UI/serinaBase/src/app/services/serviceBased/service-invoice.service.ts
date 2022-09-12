import { environment } from './../../../environments/environment.prod';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, Subject } from 'rxjs';
import { retry } from 'rxjs/operators';

@Injectable({
  providedIn: 'root',
})
export class ServiceInvoiceService {
  private subject = new Subject<any>();
  public isLogin = false;
  keepLogin = false;
  vendorID: number;
  cuserID: number;
  spID: number;
  invoiceId: number;
  invoiceDetals;
  vendorFullDetails: any;
  userId: number;
  requiredBoolean: boolean;
  entityIdSummary = '';
  displayErpBoolean: boolean = true;
  serviceIdSummary: any;

  constructor(private http: HttpClient) {}

  // Invoice display
  getInvoice(stringDate: any) {
    if (stringDate) {
      return this.http.get(
        `${environment.apiUrl}/apiv1.1/readServiceInvoiceList/${this.userId}/?p_date=${stringDate}`
      );
    } else {
      return this.http.get(
        `${environment.apiUrl}/apiv1.1/readServiceInvoiceList/${this.userId}`
      );
    }
    stringDate = null;
  }
  displayInvoiceDetails() {
    return this.http
      .get(
        `${environment.apiUrl}/apiv1.1/readServiceInvoiceData/${this.userId}/idInvoice${this.invoiceId}`
      )
      .pipe(retry(2));
  }

  updateInvoiceDetails(data: any): Observable<any> {
    return this.http.post(
      `${environment.apiUrl}/apiv1.1/updateServiceInvoiceData/${this.userId}/idInvoice${this.invoiceId}`,
      data
    );
  }
  getSummaryData(stringDate: any) {
    // tslint:disable-next-line:triple-equals
    if (!stringDate && !this.entityIdSummary && !this.serviceIdSummary) {
      this.entityIdSummary = '';
      this.serviceIdSummary = '';
    } else if (!stringDate && this.entityIdSummary && !this.serviceIdSummary) {
      this.entityIdSummary = '?fentity=' + this.entityIdSummary;
      this.serviceIdSummary = '';
    } else if (!stringDate && !this.entityIdSummary && this.serviceIdSummary) {
      this.entityIdSummary = '';
      this.serviceIdSummary = '?sp_id=' + this.serviceIdSummary;
    } else if (stringDate && this.entityIdSummary && !this.serviceIdSummary) {
      this.entityIdSummary = '&fentity=' + this.entityIdSummary;
      this.serviceIdSummary = '';
    } else if (!stringDate && this.entityIdSummary && this.serviceIdSummary) {
      this.entityIdSummary = '?fentity=' + this.entityIdSummary;
      this.serviceIdSummary = '&sp_id=' + this.serviceIdSummary;
    } else if (stringDate && !this.entityIdSummary && this.serviceIdSummary) {
      this.entityIdSummary = '';
      this.serviceIdSummary = '&sp_id=' + this.serviceIdSummary;
    } else if (stringDate && this.entityIdSummary && this.serviceIdSummary) {
      // this.entityIdSummary ='';
      this.entityIdSummary = '&fentity=' + this.entityIdSummary;
      this.serviceIdSummary = '&sp_id=' + this.serviceIdSummary;
    }
    return this.http
      .get(
        `${environment.apiUrl}/apiv1.1/Summary/apiv1.1/invoiceProcessSummary/${this.userId}` +
          stringDate +
          this.entityIdSummary +
          this.serviceIdSummary
      )
      .pipe(retry(2));
  }

  getSummaryEntity() {
    return this.http
      .get(
        `${environment.apiUrl}/apiv1.1/Summary/apiv1.1/EntityFilter/${this.userId}`
      )
      .pipe(retry(2));
  }

  getServiceProvider() {
    return this.http
      .get(
        `${environment.apiUrl}/apiv1.1/Summary/apiv1.1/ServiceFilter/${this.userId}`
      )
      .pipe(retry(2));
  }
  downloadInvoiceData() {
    return this.http.get(
      `${environment.apiUrl}/apiv1.1/DownloadServiceInvoiceExcel/${this.userId}/idInvoice${this.invoiceId}`,
      { responseType: 'blob' }
    );
  }

  // bulk upload
  downloadTemplate(data): Observable<any> {
    return this.http.post(
      `${environment.apiUrl}/${environment.apiVersion}/SP/Downloadstemplate?temp=${data}`,
      '',
      { responseType: 'blob' }
    );
  }
  downloadRejectRecords(): Observable<any> {
    return this.http.post(
      `${environment.apiUrl}/${environment.apiVersion}/SP/DownloadRejectedRecords`,
      '',
      { responseType: 'blob' }
    );
  }

  // customer Summary
  getCutomerSummary(data): Observable<any> {
    return this.http
      .get(
        `${environment.apiUrl}/apiv1.1/Summary/apiv1.1/pages/${this.userId}${data}`
      )
      .pipe(retry(2));
  }

  triggerBatch(data): Observable<any> {
    return this.http.post(
      `${environment.apiUrl}/${environment.apiVersion}/ServiceProvider/triggerServiceBatch/${this.userId}`,
      data
    );
  }
  triggerBatchHistory(): Observable<any> {
    return this.http
      .get(
        `${environment.apiUrl}/${environment.apiVersion}/ServiceProvider/ServiceBatchHistory/${this.userId}`
      )
      .pipe(retry(2));
  }

  readEtisaltCostFile(): Observable<any> {
    return this.http
      .get(
        `${environment.apiUrl}/${environment.apiVersion}/ServiceProvider/ServiceCostAllocationFileHistory/${this.userId}`
      )
      .pipe(retry(2));
  }

  uploadFileAllocation(data): Observable<any> {
    return this.http
      .post(
        `${environment.apiUrl}/${environment.apiVersion}/ServiceProvider/ServiceCostAllocationFileUpload/${this.userId}`,data
      )
      .pipe(retry(2));
  }

  downloadFileAllocation(filename): Observable<any> {
    const headers = new Headers({ 'Content-Type': 'text/xml' });
    return this.http
      .get(
        `${environment.apiUrl}/${environment.apiVersion}/ServiceProvider/ServiceCostAllocationFileDownload/${this.userId}/fileName/${filename}`,{ responseType: 'blob' }
      )
      .pipe(retry(2));
  }
}
