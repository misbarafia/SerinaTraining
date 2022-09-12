import { SharedService } from 'src/app/services/shared/shared.service';
import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MessageService } from 'primeng/api';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-modal-on-board',
  templateUrl: './modal-on-board.component.html',
  styleUrls: ['./modal-on-board.component.scss']
})
export class ModalOnBoardComponent implements OnInit {
  public uploadTrainData: FormGroup;
  isuploadable: boolean = true;
  folderPath:any;
  uploadFileName:any;
  folderPathBoolean:boolean;
  uploadingFolderBoolean: boolean;
  uploadingFileBoolean: boolean;
  jsonFinalData: any;
  successBoolean: boolean;
  errorBoolean: boolean;
  successFileBoolean: boolean;
  errorFileBoolean: boolean;

  modelData:Subscription;
  modelStatus:any;

  constructor(private fb: FormBuilder,
    private messageService : MessageService,
    private sharedService : SharedService) {
    this.uploadTrainData = this.fb.group({
      uploadFolder: this.fb.control('', Validators.required)
    });
    // this.modelData = this.sharedService.getModalData().subscribe((data:any)=>{
    //   this.modelStatus = data;
    //   console.log(this.modelStatus);
    // });
  }
  ngOnInit(): void {
    // this.modelData = this.sharedService.currentModelData;
  
    this.sharedService.finalJsonData.subscribe((data:any)=>{
      console.log(data);
      this.jsonFinalData = data;
    })
  }

  onSelectFile(event) {

    this.isuploadable = false;
    
  }
  uploadFolderEvent(event){
    this.folderPath = event;
    console.log(event);
    this.uploadFolderPath();
  }
  
  uploadFolderPath(){
    this.uploadingFolderBoolean = true;
    const formData = new FormData();
    for (const file of this.folderPath) {
      formData.append("files", file, file.name);
    }
    console.log(formData);
    this.sharedService.uploadFolder(formData).subscribe((data:any)=>{
      console.log(data);
      this.messageService.add({
        severity:"success",
        summary:"Uploaded",
        detail:"Folder uploaded successfully"
      });
      this.successBoolean = true;
      this.uploadingFolderBoolean = false;
      this.folderPathBoolean = true;
    }, error =>{
      this.messageService.add({
        severity:"error",
        summary:"error",
        detail: error.statusText
      });
      this.errorBoolean = true;
    })
  }

  upload_Blob(){
    let blobData = {
      "min_no": 0,
      "max_no": 0,
      "file_size_accepted": 0,
      "accepted_file_type": "string",
      "cnx_str": "string",
      "cont_name": "string",
      "local_path": "string"
    }
    this.sharedService.uploadBlob(JSON.stringify(blobData)).subscribe((data:any)=>{
      console.log(data);
    })
  }

  uploadFileEvent(event){
    this.uploadFileName = event;
    console.log(event[0].name);
    this.uploadFile();
  }
  uploadFile(){
    this.uploadingFileBoolean = true;
    const formData = new FormData();
      formData.append("file", this.uploadFileName[0], this.uploadFileName[0].name);
    
    console.log(formData);
    this.sharedService.uploadFileblob(formData).subscribe((data:any)=>{
      console.log(data);
      this.messageService.add({
        severity:"success",
        summary:"Uploaded",
        detail:"File uploaded successfully"
      });
      this.successFileBoolean = true;
      this.uploadingFileBoolean = false;
    }, error=>{
      this.messageService.add({
        severity:"error",
        summary:"error",
        detail: error.statusText
      });
      this.errorFileBoolean = true;
      this.uploadingFileBoolean = false;
    })
  }

  model_validate(){
    let validateModel = {
      "model_path": "string",
      "model_id": 0,
      "req_fields_accuracy": 0,
      "req_model_accuracy": 0,
      "mand_fld_list": "string",
      "cnx_str": "string",
      "cont_name": "string",
      "VendorAccount": "string"
    }
    this.sharedService.modelValidate(JSON.stringify(validateModel)).subscribe((data:any)=>{
      console.log(data);
    })
  }

}
