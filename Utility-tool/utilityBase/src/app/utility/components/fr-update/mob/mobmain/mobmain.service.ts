import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class MobmainService {
  private _value: BehaviorSubject<any> = new BehaviorSubject(null);
  private _value1: BehaviorSubject<any> = new BehaviorSubject(null);
  constructor() { }
  setModelData(newValue: any): void{
    this._value.next(newValue);
  }

  getModelData(): Observable<any>{
    return this._value.asObservable();
  }
  setFrConfig(newValue: any): void{
    this._value1.next(newValue);
  }

  getFrConfig(): Observable<any>{
    return this._value1.asObservable();
  }

 
}
