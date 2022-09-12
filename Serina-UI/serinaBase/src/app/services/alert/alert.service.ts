import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AlertService {
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

  currentUserMsg = new BehaviorSubject<any>([]);
  currentUser: Observable<any>;

  constructor() {
    this.currentUser = this.currentUserMsg.asObservable();
   }

  public get currentUserMsgBox(){
    return this.currentUserMsg.value;
}
}
