import { SharedService } from 'src/app/services/shared.service';
import { Component, OnInit } from '@angular/core';
import { NgxSpinnerService } from 'ngx-spinner';
import { MessageService } from 'primeng/api';
import { PermissionService } from 'src/app/services/permission.service';
import { DocumentService } from 'src/app/services/vendorPortal/document.service';

@Component({
  selector: 'app-vendor-contact',
  templateUrl: './vendor-contact.component.html',
  styleUrls: ['./vendor-contact.component.scss']
})
export class VendorContactComponent implements OnInit {
  readVendorDetails: any[];
  editable:boolean;
  savebooleanVendor:boolean
  editBtnBoolean:boolean = true;
  vendorName: any;
  constructor(private permissionService: PermissionService,
    private docService : DocumentService,
    private sharedService : SharedService,
    private messageService: MessageService,
    private SpinnerService: NgxSpinnerService) { }

  ngOnInit(): void {
    this.getVendorContactDetails();
  }

  getVendorContactDetails(){
    this.docService.readVendorContactData().subscribe((data:any)=>{
      console.log(data);
      this.readVendorDetails = data.result[0];
      this.sharedService.vendorID = data.result[0].idVendor;
      this.vendorName = data.result[0].VendorName
    })
  }
  editVendorDetails(){
    this.savebooleanVendor = true;
    this.editBtnBoolean = false;
    this.editable = true;
  }
  updatevendor(value){
    console.log(value)
    this.sharedService.updatevendor(JSON.stringify(value)).subscribe((data:any)=>{
      console.log(data)
    })
  }
  onCancel(){
    this.savebooleanVendor = false;
    this.editBtnBoolean = true;
    this.editable = false;
  }

}
