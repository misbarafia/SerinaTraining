import { Router } from '@angular/router';
import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit {
  viewType ;
  processURL = '/vendorPortal/home/processMetrics';
  detailURL = '/vendorPortal/home/detailedReports';
  constructor(private router : Router) { }

  ngOnInit(): void {
    if (this.router.url == this.processURL ) {
      this.viewType = 'Process';
    } else if(this.router.url == this.detailURL){
      this.viewType = 'detailed';
    } 
  }

  choosepageTab(value) {
    this.viewType = value;
    if (value == 'Process') {
      this.router.navigate([this.processURL]);
    } else if(value == 'detailed') {
      this.router.navigate([this.detailURL]);
    } 
  }

}
