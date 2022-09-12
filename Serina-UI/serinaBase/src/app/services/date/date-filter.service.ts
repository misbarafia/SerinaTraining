import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class DateFilterService {
  lastYear: number;
  displayYear: string;
  minDate: Date;
  maxDate: Date;

  constructor() { }
  
  dateRange(){
    let today = new Date();
    let day = today.getDate()
    let month = today.getMonth();
    let year = today.getFullYear();
    this.lastYear = year - 5;
    this.displayYear = `${this.lastYear}:${year}`;
    let prevYear = year - 5;

    this.minDate = new Date();
    this.minDate.setDate(day)
    this.minDate.setMonth(month);
    this.minDate.setFullYear(prevYear);

    this.maxDate = new Date();
    this.maxDate.setMonth(month);
    this.maxDate.setFullYear(year);
  }
}
