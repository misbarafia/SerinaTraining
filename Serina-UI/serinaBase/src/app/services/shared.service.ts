import { environment } from './../../environments/environment.prod';
import { HttpClient, HttpErrorResponse, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, Subject, of, BehaviorSubject, throwError } from 'rxjs';
import { catchError, map, retry, tap } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class SharedService {
  private subject = new Subject<any>();
  public isLogin: boolean = false;
  keepLogin: boolean = false;
  vendorID: number;
  cuserID: number;
  spID: number;
  spAccountID:number;

  invoiceID: any;

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
  editedUserData: any;
  VendorsReadData: any = new BehaviorSubject<any>([]);
  entityIdSummary: string;
  vendorReadID: any;

  errorObject = {
    severity: "error",
    summary: "error",
    detail: "Something went wrong"
  }
  addObject = {
    severity: "success",
    summary: "Success",
    detail: "Created Successfully"
  }
  updateObject = {
    severity: "info",
    summary: "Updated",
    detail: "Updated Successfully"
  }
  isCustomerPortal: boolean;

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

  // login

  login(data: any): Observable<any> {
    return this.http.post('/apiv1.1/login', data)
  }


  // email template
  displayTemplate() {
    return this.http.get('v1.0/get_templates/33')
  }
  updateTemplate(data: any): Observable<any> {
    return this.http.post('v1.0/update_template/33', data)
  }
  sendMail(email: any): Observable<any> {
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/resetPassword/?email=${email}`);
  }
  updatepass(data: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/${this.apiVersion}/setPassword/`,data);
  }

  // notifications
  getNotification() {
    return this.http.get(`/${this.apiVersion}/Notification/getNotifications/${this.userId}`)
  }
  removeNotification(id) {
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/Notification/markNotification/${this.userId}${id}`)
  }

  displayNTtemplate() {
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/Notification/getNotificationsTemplate/${this.userId}`)
  }
  updateNTtemplate(data: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/${this.apiVersion}/Notification/updateNotification/${this.userId}/idPullNotificationTemplate` + this.NTtempalteId, data);
  }


  // To display customer user details 
  readcustomeruser() {
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/Customer/userList/${this.userId}`)
  }
  readEntityUserData(value){
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/Permission/readUserAccess/${this.userId}/?ua_id=${value}&skip=0`,{headers:new HttpHeaders({'X-Forwarded-Proto':'https'})});
  }
  updatecustomeruser(data: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/${this.apiVersion}/Customer/updateCustomer/${this.userId}/idUser/` + this.cuserID, data);
  }
  createNewUser(data: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/${this.apiVersion}/Customer/newCustomer/${this.userId}`, data);
  }
  
  // getRoleinfo(): Observable<any> {
  //   return this.http.get(`/${this.apiVersion}/Permission/readAccessPermission${this.userId}/`);
  // }
  displayRolesData(){
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/Permission/readPermissionRolesUser/${this.userId}`);
  }
  displayRoleInfo(){
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/Permission/readPermissionRoleInfo/${this.userId}/accessPermissionDefID/${this.ap_id}`);
  }
  createRole(data:any): Observable<any>{
    return this.http.post(`${this.apiUrl}/${this.apiVersion}/Permission/newAccessPermissionUser/${this.userId}`,data);
  }
  updateRoleData(data:any): Observable<any>{
    return this.http.put(`${this.apiUrl}/${this.apiVersion}/Permission/updateAccessPermission/${this.userId}/idAccessPermission/${this.ap_id}`,data);
  }
  deleteRole(){
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/Permission/deletePermissionRole/${this.userId}/accessPermissionDefID/${this.ap_id}`);
  }
  editRole(data:any): Observable<any>{
    return this.http.post(`${this.apiUrl}/${this.apiVersion}/Permission/applyAccessPermission/${this.userId}`,data);
  }
  newAmountApproval(data:any): Observable<any>{
    return this.http.post(`${this.apiUrl}/${this.apiVersion}/Permission/newAmountApproval/${this.userId}`,data);
  }
  userCheck(name){
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/Customer/userName?name=${name}`);
  }
  resetPassword(email){
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/resetPassword/?email=${email}`);
  }

  getVendorsListToCreateNewlogin(id){
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/Customer/vendorNameList/${this.userId}`+id);
  }
  getVendorsCodesToCreateNewlogin(id){
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/Customer/vendorEntityCodes/${this.userId}?ven_code=${id}`);
  }
  createVendorSuperUser(data):Observable<any>{
    return this.http.post(`${this.apiUrl}/${this.apiVersion}/Customer/newVendorAdminUser/${this.userId}`,data);
  }
  readVendorSuperUsersList(){
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/Customer/vendorUserlist/${this.userId}`);
  }
  activate_deactivate(id){
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/Customer/changeUserAccountStatus/${this.userId}?deactivate_uid=${id}`);
  }

  // To display vendor list,create vendor,display vendor account and to update vendor apis
  readvendors(data) {
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/Vendor/vendorlist/${this.userId}${data}`).pipe(retry(2));
  }
  getVendorUniqueData(data):Observable<any>{
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/Vendor/vendorNameCode/${this.userId}${data}`)
  }

  readvendorbyid() {
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/Vendor/vendordetails/` + this.vendorID)
  }
  createvendor(data: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/${this.apiVersion}/Vendor/NewVendor/${this.userId}`, data)
  }
  updatevendor(data: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/${this.apiVersion}/Vendor/updateVendor/${this.userId}/idVendor/` + this.vendorID, data)
  }
  readvendoraccount() {
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/Vendor/vendorAccount/` + this.vendorID)
  }
  readvendoraccountSite() {
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/Vendor/vendorSite/${this.userId}/idVendor/` + this.vendorID);
  }
  readVendorInvoices(){
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/Invoice/readInvoiceList/${this.userId}/vendor/${this.vendorID}`)
  }
  readVendorInvoiceColumns(): Observable<object>{
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/Invoice/readVendorColumnPos/${this.userId}/tabname/{tabtype}`)
  }
  updateVendorInvoiceColumns(data){
    return this.http.post(`${this.apiUrl}/${this.apiVersion}/Invoice/updateVendorColumnPos/${this.userId}`,data)
  }
  getItemFileStatus():Observable<any>{
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/Invoice/readItemMetaStatus/${this.userId}`)
  }
  downloadErrFile(item_id):Observable<any>{
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/Invoice/downloadItemMasterErrorRecords/${this.userId}?item_history_id=${item_id}`,{ responseType: 'blob' })
  }
  readItemListData(ven_acc_id):Observable<any>{
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/Invoice/readItemMetaData/${this.userId}?ven_acc_id=${ven_acc_id}`)
  }


  // To display serviceprovider list,create serviceprovider,display serviceprovider account and to update serviceprovider apis

  readserviceprovider() {
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/ServiceProvider/serviceproviderlist/${this.userId}`)
  }
  createserviceprovider(data: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/${this.apiVersion}/ServiceProvider/newServiceProvider/${this.userId}`, data)
  }
  updateserviceprovider(data: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/${this.apiVersion}/ServiceProvider/updateServiceProvider/` + this.spID, data)
  }
  readserviceproviderbyid() {
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/ServiceProvider/serviceprovider/` + this.spID)
  }
  readserviceprovideraccount() {
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/ServiceProvider/serviceprovideraccount/${this.userId}/idService/${this.spID}`)
  }
  createserviceprovideraccount(data: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/${this.apiVersion}/ServiceProvider/newSPAccount/${this.userId}/serviceId/` + this.spID, data)
  }
  updateSpAccount(data: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/${this.apiVersion}/ServiceProvider/updateSPAccount/${this.userId}/idServiceAccount/${this.spAccountID}`, data)
  }
  readserviceproviderinvoice() {
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/InvoicePush/readServiceInvoiceList/${this.userId}?sp_id=` + this.spID)
  }
  readServiceInvoice() : Observable<any>{
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/Invoice/readInvoiceList/${this.userId}/serviceprovider/${this.spID}`)
  }
  readSPInvoicecolumns(): Observable<object>{
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/Invoice/readServiceProviderPos/${this.userId}/tabname/{tabtype}`)
  }
  updateSpInvoiceColumns(data){
    return this.http.post(`${this.apiUrl}/${this.apiVersion}/Invoice/updateServiceProviderColumnPos/${this.userId}`,data)
  }

  readOPUnits(): Observable<object>{
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/ServiceProvider/getoperationalUnits`)
  }

  // entity

  getEntitybody() {
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/Customer/readEntity_Body_Dept/${this.userId}?ent_id=${this.selectedEntityId}`).pipe(retry(2));
  }
  getEntityDept() {
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/Customer/readEntity_Dept/${this.userId}`).pipe(retry(2));
  }


  /* invoice Related */
  getAllInvoice() {
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/Invoice/readDocumentINVList/${this.userId}`).pipe(retry(2))
  }
  getPOData(data) {
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/Invoice/readDocumentPOList/${this.userId}${data}`).pipe(retry(2));
  }
  getServiceInvoices() {
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/Invoice/readDocumentINVListService/${this.userId}`).pipe(retry(2));
  }
  checkInvStatus(id,string) {
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/Invoice/${string}/${id}`).pipe(retry(2));
  }

  
  readReadyGRNData():Observable<any> {
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/Invoice/readGRNReadyInvoiceList/${this.userId}`).pipe(retry(2))
  }
  readReadyGRNInvData():Observable<any> {
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/Invoice/readGRNReadyInvoiceData/${this.userId}?inv_id=${this.invoiceID}`).pipe(retry(2))
  }
  saveGRNData(boolean_value,value):Observable<any> {
    return this.http.post(`${this.apiUrl}/${this.apiVersion}/Invoice/saveCustomGRNData/${this.userId}?inv_id=${this.invoiceID}&submit_type=${boolean_value}`,value).pipe(retry(2))
  }

  // view Invoice
  getInvoiceInfo() {
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/Invoice/readInvoiceData/${this.userId}/idInvoice/${this.invoiceID}`).pipe(retry(2),catchError(this.handleError))
  }
  getInvoiceFilePath() {
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/Invoice/readInvoiceFile/${this.userId}/idInvoice/${this.invoiceID}`).pipe(retry(2),catchError(this.handleError))
  }
  updateInvoiceDetails(data: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/${this.apiVersion}/Invoice/updateInvoiceData/${this.userId}/idInvoice/${this.invoiceID}`, data)
  }
  readColumnInvoice(value){
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/Invoice/readColumnPos/${this.userId}/tabname/${value}`).pipe(retry(3));
  }
  updateColumnPOs(data: any,value): Observable<any>{
    return this.http.post(`${this.apiUrl}/${this.apiVersion}/Invoice/updateColumnPos/${this.userId}/tabname/${value}`,data)
  }
  readEditedInvoiceData(){
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/Invoice/readInvoiceList/${this.userId}/edited`)
  }
  readEditedServiceInvoiceData() {
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/Invoice/readInvoiceListService/${this.userId}/edited`)
  }
  assignInvoiceTo(inv_id){
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/Invoice/assignInvoice/${this.userId}/idInvoice/${inv_id}`)
  }
  submitChangesInvoice(data:any):Observable<any>{
    return this.http.post(`${this.apiUrl}/${this.apiVersion}/Invoice/submitInvoice/${this.userId}/idInvoice/${this.invoiceID}`,data)
  }
  approveInvoiceChanges(data:any){
    return this.http.post(`${this.apiUrl}/${this.apiVersion}/Invoice/approveEditInvoice/${this.userId}/idInvoice/${this.invoiceID}`,data)
  }
  readApprovedInvoiceData(){
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/Invoice/readInvoiceList/${this.userId}/approved`).pipe(retry(2));
  }
  readApprovedSPInvoiceData() {
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/Invoice/readInvoiceListService/${this.userId}/approved`).pipe(retry(2))
  }
  financeApprovalPermission(): Observable<any>{
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/Permission/financiallapproval/${this.userId}/idInvoice/${this.invoiceID}`).pipe(retry(2)); 
  }
  ITRejectInvoice(data: any): Observable<any>{
    return this.http.post(`${this.apiUrl}/${this.apiVersion}/Invoice/rejectIT/${this.userId}/idInvoice/${this.invoiceID}`,data).pipe(retry(2)); 
  }
  vendorRejectInvoice(data: any): Observable<any>{
    return this.http.post(`${this.apiUrl}/${this.apiVersion}/Invoice/rejectVendor/${this.userId}/idInvoice/${this.invoiceID}`,data) 
  }
  vendorSubmit(query): Observable<any> {
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/Vendor/submitVendorInvoice/${this.userId}?re_upload=${query}&inv_id=${this.invoiceID}`)
  }
  triggerBatch(query):Observable<any> {
    return this.http.post(`${this.apiUrl}/${this.apiVersion}/fr/triggerbatch/${this.invoiceID}${query}`,'')
  }

  // invoiceStatusHistory

  getInvoiceLogs(){
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/Invoice/readInvoiceStatusHistory/${this.userId}/idInvoice/${this.invoiceID}`).pipe(retry(2));
  }
  downloadDoc(){
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/Invoice/journeydoc/docid/${this.invoiceID}`,{responseType: 'blob'});
  }

  // payment status
  getPaymentStatusData(){
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/Invoice/readInvoicePaymentStatus/${this.userId}`).pipe(retry(2));
  }

  // // GRN Related
  // getGRNdata(){
  //   return this.http.get(`/${this.apiVersion}/Invoice/apiv1.1/readDocumentGRNList/${this.userId}`)
  // }

    // PO Related
    getPoNumbers(vac_id,ent_id): Observable<any>{
      return this.http.get(`${this.apiUrl}/${this.apiVersion}/VendorPortal/getponumbers/${vac_id}?ent_id=${ent_id}`)
    }
  
    // GRN Related
    getGRNdata(data){
      return this.http.get(`${this.apiUrl}/${this.apiVersion}/Invoice/readDocumentGRNList/${this.userId}${data}`).pipe(retry(2));
    }
    getARCdata(data){
      return this.http.get(`${this.apiUrl}/${this.apiVersion}/Invoice/readDocumentARCList/${this.userId}${data}`).pipe(retry(2));
    }
    getRejecteddata(data){
      return this.http.get(`${this.apiUrl}/${this.apiVersion}/Invoice/readDocumentRejectList/${this.userId}${data}`).pipe(retry(2));
    }

    getGRNExceptionData(data){
      return this.http.get(`${this.apiUrl}/${this.apiVersion}/Invoice/readDocumentGRNException/${this.userId}${data}`);
    }

    // vendorAccounts
    readCustomerVendorAccountsData(vId) {
      return this.http.get(`${this.apiUrl}/${this.apiVersion}/Customer/vendorAccount/${this.userId}/idVendor/${vId}`).pipe(retry(2));
    }

    readUploadPOData(poNumber) {
      return this.http.get(`${this.apiUrl}/${this.apiVersion}/Invoice/readPOData/${this.userId}/idInvoice/${poNumber}`).pipe(retry(2));
    }
  
    // OCR
    uploadInvoice(data: any,poNumber): Observable<any>{
      return this.http.post(`${this.apiUrl}/${this.apiVersion}/VendorPortal/uploadfile/${poNumber}`,data)
    }
    OcrProcess(OCRInput): Observable<any>{
      return this.http.get(`${this.apiUrl}/${this.apiVersion}/ocr/status/stream?file_path=${OCRInput}`,{responseType: 'text',observe: "events"})
    }
  
    private handleError(error: HttpErrorResponse) {
      if (error.status === 0) {
        // A client-side or network error occurred. Handle it accordingly.
        console.error('An error occurred:', error.error);
      } else {
        // The backend returned an unsuccessful response code.
        // The response body may contain clues as to what went wrong.
        console.error(
          `Backend returned code ${error.status}, body was: `, error.error);
      }
      // Return an observable with a user-facing error message.
      return throwError(() => new Error('Something bad happened; please try again later.'));
    }

}
