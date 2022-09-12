import { environment } from './../../../environments/environment';
import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { retry } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class ExceptionsService {



  userId: any;
  poNumber: string;
  invoiceID:any;

  selectedRuleId:number;

  constructor(private http : HttpClient) { }

  readBatchInvoicesData():Observable<any> {
    return this.http.get(`${environment.apiUrl}/${environment.apiVersion}/Exception/batchprocesssummary/${this.userId}`).pipe(retry(3))
  }

  readApprovalBatchInvoicesData():Observable<any> {
    return this.http.get(`${environment.apiUrl}/${environment.apiVersion}/Exception/batchprocesssummaryAdmin/${this.userId}`).pipe(retry(3))
  }

  readBatchRules():Observable<any> {
    return this.http.get(`${environment.apiUrl}/${environment.apiVersion}/fr/documentrules`).pipe(retry(3))
  }

  updatePONumber(po_num):Observable<any> {
    return this.http.get(`${environment.apiUrl}/${environment.apiVersion}/Exception/Update_po_number/${this.invoiceID}/po_num/${po_num}`).pipe(retry(3))
  };

  readLineItems():Observable<any> {
    return this.http.get(`${environment.apiUrl}/${environment.apiVersion}/Exception/get_items/${this.invoiceID}`).pipe(retry(3))
  };

  readLineData():Observable<any> {
    return this.http.get(`${environment.apiUrl}/${environment.apiVersion}/Exception/lineitem_po_grn/${this.userId}/invoiceid/${this.invoiceID}`).pipe(retry(3))
  }

  readFilePath():Observable<any> {
    return this.http.get(`${environment.apiUrl}/${environment.apiVersion}/Exception/readfilepath/${this.userId}/invoiceid/${this.invoiceID}`).pipe(retry(3))
  }

  readErrorTypes():Observable<any> {
    return this.http.get(`${environment.apiUrl}/${environment.apiVersion}/Exception/get_errortypes`).pipe(retry(3))
  }

  updateLineItems(inv_itemcode,po_itemcode,errorId,vendorAcId):Observable<any> {
    return this.http.get(`${environment.apiUrl}/${environment.apiVersion}/Exception/update_line_mapping/${this.invoiceID}/${inv_itemcode}/${po_itemcode}/${errorId}/${vendorAcId}/${this.userId}`).pipe(retry(3))
  }

  readMappedData():Observable<any> {
    return this.http.get(`${environment.apiUrl}/${environment.apiVersion}/Exception/get_mappeditem/${this.invoiceID}`).pipe(retry(3))
  }

  getInvoiceInfo():Observable<any> {
    return this.http.get(`${environment.apiUrl}/${environment.apiVersion}/Exception/testlinedata/${this.userId}/invoiceid/${this.invoiceID}`).pipe(retry(3))
  }

  send_batch_approval_review(rule_id):Observable<any> {
    return this.http.get(`${environment.apiUrl}/${environment.apiVersion}/Exception/Send_to_batch_approval/${this.userId}/invoiceid/${this.invoiceID}?rule_id=${rule_id}`).pipe(retry(3))
  }

  send_review_manual():Observable<any> {
    return this.http.get(`${environment.apiUrl}/${environment.apiVersion}/Exception/Send_to_manual_approval/${this.userId}/invoiceid/${this.invoiceID}`).pipe(retry(3))
  }

  send_batch_approval():Observable<any> {
    return this.http.get(`${environment.apiUrl}/${environment.apiVersion}/Exception/Send_to_batch_approval_Admin/${this.userId}/invoiceid/${this.invoiceID}`).pipe(retry(3))
  }

  send_manual_approval():Observable<any> {
    return this.http.get(`${environment.apiUrl}/${environment.apiVersion}/Exception/Send_to_manual_approval_Admin/${this.userId}/invoiceid/${this.invoiceID}`).pipe(retry(3))
  }

  readInvokeBatchData():Observable<any> {
    return this.http.get(`${environment.apiUrl}/${environment.apiVersion}/Exception/Invokebatchprocesssummary/${this.userId}`).pipe(retry(3))
  }


  // lock feature
  getDocumentLockInfo():Observable<any> {
    return this.http.get(`${environment.apiUrl}/${environment.apiVersion}/Invoice/getDocumentLockInfo/${this.userId}/idDocument/${this.invoiceID}`)
  }
  updateDocumentLockInfo(data):Observable<any> {
    return this.http.post(`${environment.apiUrl}/${environment.apiVersion}/Invoice/updateDocumentLockInfo/${this.userId}/idDocument/${this.invoiceID}`,data)
  }

  // line related
  removeLineData(item_code):Observable<any> {
    return this.http.delete(`${environment.apiUrl}/${environment.apiVersion}/Invoice/deleteLineItem/${this.invoiceID}/${item_code}`)
  }
  checkItemCode(item_code):Observable<any> {
    return this.http.get(`${environment.apiUrl}/${environment.apiVersion}/Invoice/checkLineItemExists/${this.invoiceID}/${item_code}`)
  }
  addLineItem(data):Observable<any> {
    return this.http.post(`${environment.apiUrl}/${environment.apiVersion}/Invoice/createLineItem`,data)
  }
}
