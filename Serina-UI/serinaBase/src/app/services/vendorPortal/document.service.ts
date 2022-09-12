import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';
import { Observable } from 'rxjs/internal/Observable';
import { tap } from 'rxjs/operators';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root'
})
export class DocumentService {
  private subject = new Subject<any>();
  loginVendorfullData = new Subject<any>()
  public isLogin: boolean = false;
  keepLogin: boolean = false;
  vendorID: number;
  cuserID: number;
  spID: number;
  spAccountID:number;

  invoiceID: number;

  notificationId: number;
  NTtempalteId: number
  public currentUser: Observable<any>;
  userId: number;
  ap_id:number;

  selectedEntityId: number;
  selectedEntityBodyId: number;
  selectedEntityDeptId: number;
  activeMenuSetting = 'ocr';
  sidebarBoolean:boolean;


  initialViewSpBoolean:boolean =true;
  spListBoolean:boolean= true;
  spDetailsArray:any;

  initialViewVendorBoolean:boolean = true
  vendorFullDetails: any;
  
  apiVersion = environment.apiVersion;
  apiUrl = environment.apiUrl;
  url ="https://3dcf9b30604d.ngrok.io/"
  constructor(private http: HttpClient) { }

  sendMessage(isLogin: boolean) {
    this.subject.next({ boolean: isLogin });
  }
  sendCounterData(CounterDetails: []) {
    this.subject.next({ CounterDetails });
  }
  sendNotificationNumber(Arraylength) {
    this.subject.next({ Arraylength });
  }

  getNotifyArraylength(): Observable<any> {
    return this.subject.asObservable();
  }
  getData(): Observable<any> {
    return this.subject.asObservable();
  }
  getMessage(): Observable<any> {
    return this.subject.asObservable();
  }






  // To display customer user details 
  readcustomeruser() {
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/Customer/userlist/${this.userId}`)
  }
  // readEntityUserData(value){
  //   console.log(value)
  //   return this.http.get(`${this.apiUrl}/${this.apiVersion}/Permission/readUserAccess/${this.userId}/?ua_id=${value}&skip=0`)
  // }
  updatecustomeruser(data: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/${this.apiVersion}/Customer/updateCustomer/${this.userId}/idUser` + this.cuserID, data)
  }
  createNewUser(data: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/${this.apiVersion}/Customer/newCustomer/${this.userId}`, data)
  }
  
  // getRoleinfo(): Observable<any> {
  //   return this.http.get(`${this.apiUrl}/${this.apiVersion}/Permission/readAccessPermission/${this.userId}/`)
  // }
  displayRolesData(){
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/Permission/readPermissionRolesVendor/${this.userId}`)
  }
  displayRoleInfo(){
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/Permission/readPermissionRoleInfo/${this.userId}/AccessPermissionDefID${this.ap_id}`)
  }
  createRole(data:any): Observable<any>{
    return this.http.post(`/${this.apiVersion}/Permission/newAccessPermissionVendor/${this.userId}`,data)
  }
  updateRoleData(data:any): Observable<any>{
    return this.http.put(`${this.apiUrl}/${this.apiVersion}/Permission/updateAccessPermission/${this.userId}/idAccessPermission/{ap_id}?apd_id=${this.ap_id}`,data)
  }
  deleteRole(){
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/Permission/deletePermissionRole/${this.userId}/AccessPermissionDefID${this.ap_id}`)
  }
  editRole(data:any): Observable<any>{
    return this.http.post(`${this.apiUrl}/${this.apiVersion}/Permission/applyAccessPermission/${this.userId}`,data)
  }
  newAmountApproval(data:any): Observable<any>{
    return this.http.post(`${this.apiUrl}/${this.apiVersion}/Permission/newAmountApproval/${this.userId}`,data)
  }

  /* invoice Related */
  getAllInvoice() {
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/Invoice/readInvoiceListtempven/${this.userId}`)
  }
  // view Invoice
  getInvoiceInfo() {
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/Invoice/readServiceInvoiceData/${this.userId}/idInvoice${this.invoiceID}`)
  }
  updateInvoiceDetails(data: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/${this.apiVersion}/Invoice/updateServiceInvoiceData/${this.userId}/idInvoice${this.invoiceID}`, data)
  }
  readColumnInvoice(value){
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/Invoice/readColumnPosAllInvoices/${this.userId}/tabname/${value}`)
  }
  updateColumnPOs(data: any,value): Observable<any>{
    return this.http.post(`${this.apiUrl}/${this.apiVersion}/Invoice/updateColumnPosAllInvoices/${this.userId}/tabname/{tabname}?tabtype=${value}`,data)
  }
  readEditedInvoiceData(){
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/Invoice/readInvoiceList/${this.userId}/edited`)
  }
  assignInvoiceTo(inv_id){
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/Invoice/assignInvoice/${this.userId}/idInvoice/${inv_id}`)
  }
  approveInvoiceChanges(){
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/Invoice/approveEditInvoice/${this.userId}/idInvoice/${this.invoiceID}`)
  }



  // GRN Related
  getGRNdata(){
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/Invoice/readDocumentGRNList/${this.userId}`)
  }

  // OCR
  uploadInvoice(data: any,poNumber): Observable<any>{
    return this.http.post(`${this.apiUrl}/${this.apiVersion}/VendorPortal/uploadfile/${poNumber}`,data)
  }
  OcrProcess(OCRInput): Observable<any>{
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/ocr/status/stream?file_path=${OCRInput}`,{responseType: 'text',observe: "events"})
  }

  // vendor users
  readVendorUsers():Observable<any>{
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/Vendor/vendorUserList/${this.userId}`);
  }
  addVendorUser(data:any):Observable<any>{
    return this.http.post(`${this.apiUrl}/${this.apiVersion}/Vendor/newVendorUser/${this.userId}`,data);
  }
  updateVendorUser(data: any): Observable<any> {
    return this.http.put(`${this.apiUrl}/${this.apiVersion}/Vendor/updateVendorUser/updateVendorUserID/${this.userId}?vu_id=${this.cuserID}`, data);
  }
  readVendorAccountsData(ent_id){
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/Vendor/vendorAccount/${this.userId}?ent_id=${ent_id}`);
  }

  // vendor contact detalis
  readVendorContactData(): Observable<any>{
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/Vendor/readVendorDetails/${this.userId}`).pipe(
      tap(user=>{
        this.loginVendorfullData.next(user)
      })
    )
  }

  // Action center page
  getRejectedInvoices(): Observable<any>{
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/Invoice/readVendorRejectedInvoice/${this.userId}`)
  }

  getPendingInvoices(): Observable<any>{
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/Invoice/readVendorPendingInvoice/${this.userId}`)
  }

  getApprovedInvoices(): Observable<any>{
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/Invoice/readVendorApprovedInvoice/${this.userId}`)
  }


  
}
