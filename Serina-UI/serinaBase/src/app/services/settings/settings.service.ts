import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, Subject } from 'rxjs';
import { tap, retry } from 'rxjs/operators';
import { environment } from 'src/environments/environment.prod';

@Injectable({
  providedIn: 'root'
})
export class SettingsService {
  userId:number;
  userData:any;
  finaceApproveBoolean = false;
  generalSettingsData: any = new Subject<any>();

  constructor(private http : HttpClient) {
    // this.userData = JSON.parse(localStorage.getItem('currentLoginUser'));
   }

  financeApprovalSetting(data):Observable<any> {
    return this.http.post(`${environment.apiUrl}/${environment.apiVersion}/Customer/switchRoleBased/${this.userId}?isenabled=${data}`,'')
  }

  readGeneralSettings():Observable<any> {
    return this.http.get(`${environment.apiUrl}/${environment.apiVersion}/Customer/readGenSettings/${this.userId}`).pipe(
      tap((data:any)=>{
        this.generalSettingsData.next(data);
      })
    )
  }

  readServiceTriggerSettings():Observable<any> {
    return this.http.get(`${environment.apiUrl}/${environment.apiVersion}/Permission/readServiceSchedule/${this.userId}`)
  }

  serviceBatchTriggerUpdate(data):Observable<any> {
    return this.http.post(`${environment.apiUrl}/${environment.apiVersion}/Permission/updateServiceSchedule/${this.userId}`,data)
  }


  // Notification Settings
  readNotificationRecipientsData(nty_id,ent_id):Observable<any>{
    return this.http.get(`${environment.apiUrl}/${environment.apiVersion}/Notification/getNotificationsRecepients/${this.userId}/notificationTypeID/${nty_id}/entityID/${ent_id}`).pipe(retry(2))
  }
  saveNotificationRecipientsData(nty_id,ent_id,data):Observable<any>{
    return this.http.post(`${environment.apiUrl}/${environment.apiVersion}/Notification/updateNotificationRecipients/${this.userId}/notificationTypeID/${nty_id}/entityID/${ent_id}`,data).pipe(retry(2))
  }
  readRecipients(ent_id):Observable<any>{
    return this.http.get(`${environment.apiUrl}/${environment.apiVersion}/Notification/ReadRecipients/${this.userId}/entityID/${ent_id}`).pipe(retry(2))
  }

  changePassword(data):Observable<any>{
    return this.http.post(`${environment.apiUrl}/${environment.apiVersion}/Customer/PortalPasswordUpdate/${this.userId}`,data).pipe(retry(2))
  }

}
