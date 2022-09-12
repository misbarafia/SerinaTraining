import { AuthenticationService } from 'src/app/services/auth/auth.service';
import { BehaviorSubject, Observable, Subject } from 'rxjs';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { environment } from 'src/environments/environment';
import { take, tap } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class SharedService {
  userId: any;
  url = environment.apiUrl;
  private apiUrl = environment.apiUrl
  private apiVersion = environment.apiVersion
  headers_object;
  httpOptions;
  storeVendorsList = new BehaviorSubject<any>([]);
  storeServiceProviderList = new BehaviorSubject<any>([]);
  storeEntityList = new Subject();
  vendorDetails: any;
  SPDetails:any;
  private vendorDataSubject: BehaviorSubject<any>;
  private SPDataSubject: BehaviorSubject<any>;
  private vendorData: Observable<any>;
  private SPData: Observable<any>;
  finalJsonData = new Subject();

  modelData: any;
  modelObsevable: Observable<any>
  configDataSubject: BehaviorSubject<any>;
  frData: any;

  errorObject = {
    severity: "error",
    summary: "error",
    detail: "Something went wrong"
  }
  isAdmin: boolean;
  vendorList = [];
  selectedEntityId: any = 'ALL';
  onboard_status: any = 'ALL';
  vendorNameForSearch: any;
  spNameForSearch:any;
  constructor(private http: HttpClient) {
    if (sessionStorage.getItem('vendorData')) {
      this.vendorDataSubject = new BehaviorSubject<any>(JSON.parse(sessionStorage.getItem('vendorData')));
      this.vendorData = this.vendorDataSubject.asObservable();
    }
    if(sessionStorage.getItem('spData')){
      this.SPDataSubject = new BehaviorSubject<any>(JSON.parse(sessionStorage.getItem('spData')));
      this.SPData = this.SPDataSubject.asObservable();
    }
    if (sessionStorage.getItem('configData')) {
      this.configDataSubject = new BehaviorSubject<any>(JSON.parse(sessionStorage.getItem('configData')));
      this.modelObsevable = this.configDataSubject.asObservable();
    }

  }
  // sendModelData(){
  //   this.modelStatusData.next(this.modelData);
  // }
  // getModalData(): Observable<any> {
  //   return this.modelStatusData.asObservable();
  // }

  readVendorData():Observable<any>{
    return this.storeVendorsList.asObservable();
  }

  readSPData():Observable<any>{
    return this.storeServiceProviderList.asObservable();
  }
  sendMail(email: any): Observable<any> {
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/resetPassword/?email=${email}`);
  }
  updatepass(data: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/${this.apiVersion}/setPassword/`,data);
  }

  public get currentSPData(): any{
    return this.SPDataSubject.value;
  }
  public get currentVendorData(): any {
    return this.vendorDataSubject.value;
  }

  public get configData(): any {
    return this.configDataSubject.value;
  }

  getVendors(data): Observable<any> {
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/Vendor/vendorlist/${this.userId}${data}`);
  }

  getServiceProviders(data): Observable<any>{
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/ServiceProvider/serviceproviderlist1/${this.userId}${data}`);
  }

  getOnboardedData():Observable<any>{
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/Vendor/check_onboarded/${this.userId}`);
  }

  getVendorAccounts(v_id): Observable<any> {
    return this.http.get(`${this.url}/${this.apiVersion}/fr/vendoraccount/${v_id}`);
  }
  getSPAccounts(v_id): Observable<any> {
    return this.http.get(`${this.url}/${this.apiVersion}/fr/serviceaccount/${v_id}`);
  }
  getSummaryEntity() {
    return this.http
      .get(
        `${environment.apiUrl}/apiv1.1/Summary/apiv1.1/EntityFilter/${this.userId}`
      );
  }
  getFrConfig(): Observable<any> {
    return this.http.get(`${this.url}/${this.apiVersion}/fr/getfrconfig/${this.userId}`).pipe(
      take(1)
    );
  }

  getMetaData(documentId): Observable<any> {
    return this.http.get(`${this.url}/${this.apiVersion}/fr/getfrmetadata/${documentId}`);
  }
  downloadDoc(tagtype){
    return this.http.get(`${this.apiUrl}/${this.apiVersion}/fr/entityTaggedInfo?tagtype=${tagtype}`,{responseType: 'blob'});
  }
  getAccuracyScore(type,name){
    return this.http.get(`${this.url}/${this.apiVersion}/fr/getActualAccuracy/${type}/${name}`);
  }
  getAllTags(tagtype):Observable<any> {
    return this.http.get(`${this.url}/${this.apiVersion}/fr/getalltags?tagtype=${tagtype}`);
  }
  updateFrConfig(data): Observable<any> {
    return this.http.post(`${this.url}/${this.apiVersion}/fr/updatefrconfig/${this.userId}`, data);
  }
  getRules(): Observable<any> {
    return this.http.get(`${this.url}/${this.apiVersion}/fr/documentrules`);
  }
  getAmountRules(): Observable<any> {
    return this.http.get(`${this.url}/${this.apiVersion}/fr/documentrulesnew`);
  }
  updateFrMetaData(documentId,data): Observable<any> {
    return this.http.put(`${this.url}/${this.apiVersion}/fr/update_metadata/${documentId}`,data);
  }
  getModalList(v_id): Observable<any> {
    return this.http.get(`${this.url}/${this.apiVersion}/fr/getmodellist/${v_id}`);
  }
  getModalListSP(s_id): Observable<any> {
    return this.http.get(`${this.url}/${this.apiVersion}/fr/getmodellistsp/${s_id}`);
  }

  createNewTemplate(data): Observable<any> {
    return this.http.post(`${this.url}/${this.apiVersion}/fr/createmodel/${this.userId}`, data);
  }

  uploadFolder(data): Observable<any> {
    return this.http.post(`${this.url}/${this.apiVersion}/fr/uploadfolder`, data);
  }

  uploadBlob(data): Observable<any> {
    return this.http.post(`${this.url}/${this.apiVersion}/fr/upload_blob`, data);
  }

  uploadFileblob(data): Observable<any> {
    return this.http.post(`${this.url}/${this.apiVersion}/fr/uploadfile`, data);
  }

  modelValidate(data): Observable<any> {
    return this.http.post(`${this.url}/${this.apiVersion}/fr/model_validate`, data);
  }
  saveLabelsFile(frobj): Observable<any>{
    return this.http.post(`${this.url}/${this.apiVersion}/ModelOnBoard/save_labels_file`,frobj);
  }
  checkModelStatus(modelId): Observable<any>{
    return this.http.get(`${this.url}/${this.apiVersion}/ModelOnBoard/check_model_status/${modelId}`);
  }
  saveFieldsFile(frobj): Observable<any>{
    return this.http.post(`${this.url}/${this.apiVersion}/ModelOnBoard/save_fields_file`,frobj)
  }
  getFinalData(modal_id): Observable<any> {
    return this.http.get(`${this.url}/${this.apiVersion}/fr/getfinaldata/${modal_id}`).pipe(
      tap((data: any) => {
        this.finalJsonData.next(data);
      })
    );
  }
  getModelsByVendor(modeltype:any,Id:any): Observable<any>{
    return this.http.get(`${this.url}/${this.apiVersion}/ModelOnBoard/get_training_result_vendor/${modeltype}/${Id}`);
  }
  reupload_blob(data): Observable<any> {
    return this.http.post(`${this.url}/${this.apiVersion}/fr/reupload_blob`, data);
  }

  updateModel(data, modal_id): Observable<any> {
    return this.http.post(`${this.url}/${this.apiVersion}/fr/updatemodel/${modal_id}`, data);
  }
  checkSameVendors(vendoraccount,modelname): Observable<any> {
    return this.http.get(`${this.url}/${this.apiVersion}/fr/checkduplicatevendors/${vendoraccount}/${modelname}`);
  }
  checkSameSP(serviceaccount,modelname): Observable<any> {
    return this.http.get(`${this.url}/${this.apiVersion}/fr/checkduplicatesp/${serviceaccount}/${modelname}`);
  }
  copymodels(vendoraccount,modelname): Observable<any> {
    return this.http.get(`${this.url}/${this.apiVersion}/fr/copymodels/${vendoraccount}/${modelname}`);
  }
  copymodelsSP(serviceaccount,modelname): Observable<any> {
    return this.http.get(`${this.url}/${this.apiVersion}/fr/copymodelsSP/${serviceaccount}/${modelname}`);
  }
  getallEntities(): Observable<any>{
    return this.http.get(`${this.url}/${this.apiVersion}/fr/get_all_entities/${this.userId}`);
  }
  updateEntity(ent,obj):Observable<any>{
    return this.http.put(`${this.url}/${this.apiVersion}/fr/update_entity/${ent}`,obj);
  }
  uploadDb(data, modal_id):Observable<any>{
    return  this.http.post(`${this.url}/${this.apiVersion}/ModelOnBoard/newModel/${modal_id}/${this.userId}`, data);
  }
  getTrainingTestRes(modal_id):Observable<any>{
    return this.http.get(`${this.url}/${this.apiVersion}/fr/getTrainTestResults/${modal_id}`);
  }
  getTaggingInfo(container,folderpath,connstr,documentId): Observable<any>{
    return this.http.get(`${this.url}/${this.apiVersion}/ModelOnBoard/get_tagging_info/${documentId}`,{headers:new HttpHeaders({'container':container,'connection_string':connstr,"path":folderpath})});
  }
  getAnalyzeResult(frobj):Observable<any>{
    return this.http.get(`${this.url}/${this.apiVersion}/ModelOnBoard/get_analyze_result/${frobj['container']}`,{headers:new HttpHeaders({'filename':frobj['filename'],'connstr':frobj['connstr'],'fr_endpoint':frobj['fr_endpoint'],'fr_key':frobj['fr_key'],'account':frobj['account']})});
  }
  getTrainingResult(documentId): Observable<any>{
    return this.http.get(`${this.url}/${this.apiVersion}/ModelOnBoard/get_training_result/${documentId}`);
  }
  trainModel(frobj): Observable<any>{
    return this.http.post(`${this.url}/${this.apiVersion}/ModelOnBoard/train-model`,frobj);
  }
  updateTrainingResult(resultobj): Observable<any>{
    return this.http.post(`${this.url}/${this.apiVersion}/ModelOnBoard/create_training_result`,resultobj);
  }
  composeModels(modelsobj): Observable<any>{
    return this.http.post(`${this.url}/${this.apiVersion}/ModelOnBoard/compose_model`,modelsobj);
  }
  saveComposedModel(modelobj): Observable<any>{
    return this.http.post(`${this.url}/${this.apiVersion}/ModelOnBoard/create_compose_result`,modelobj);
  }
  testModel(modelobj): Observable<any>{
    return this.http.post(`${this.url}/${this.apiVersion}/ModelOnBoard/test_analyze_result/${modelobj['modelid']}`,modelobj['formData'],{headers:new HttpHeaders({'fr_endpoint':modelobj['fr_endpoint'],'fr_key':modelobj['fr_key']})})
  }
  addVendor(vendorobj,vu_id): Observable<any>{
    return this.http.post(`${this.url}/${this.apiVersion}/Vendor/newVendor/${vu_id}`,vendorobj);
  }
  addSP(spobj,vu_id): Observable<any>{
    return this.http.post(`${this.url}/${this.apiVersion}/Vendor/newVendor/${vu_id}`,spobj); 
  }
  addVendorAccount(vendoraccobj,vu_id,v_id): Observable<any>{
    return this.http.post(`${this.url}/${this.apiVersion}/Vendor/newVendorAccount/${vu_id}/idVendor/${v_id}`,vendoraccobj);
  }
  addSPAccount(vendoraccobj,vu_id,v_id): Observable<any>{
    return this.http.post(`${this.url}/${this.apiVersion}/Vendor/newVendorAccount/${vu_id}/idVendor/${v_id}`,vendoraccobj);
  }
  getemailconfig(): Observable<any>{
    return this.http.get(`${this.url}/${this.apiVersion}/emailconfig/getemailconfig/1`);
  }
  saveemailconfig(emailconfig): Observable<any>{
    return this.http.post(`${this.url}/${this.apiVersion}/emailconfig/saveemailconfig`,emailconfig);
  }

  getSharepointconfig(): Observable<any>{
    return this.http.get(`${this.url}/${this.apiVersion}/sharepoint/getsharepointconfig`);
  }
  saveSharePointConfig(shareConfig): Observable<any>{
    return this.http.post(`${this.url}/${this.apiVersion}/sharepoint/savesharepointconfig`,shareConfig);
  }
  resetTagging(resetObj): Observable<any>{
    return this.http.post(`${this.url}/${this.apiVersion}/ModelOnBoard/reset_tagging`,resetObj);
  }
  getLabelsInfo(folderPath,filename): Observable<any>{
    return this.http.get(`${this.url}/${this.apiVersion}/ModelOnBoard/get_labels_info/${filename}`,{headers:new HttpHeaders({'folderpath':folderPath})});
  }
}