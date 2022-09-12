import { SharedService } from 'src/app/services/shared/shared.service';
import { Component, EventEmitter, Input, OnChanges, OnInit, Output, SimpleChanges, ViewChild } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MessageService } from 'primeng/api';
import { Subscription } from 'rxjs';
import { error } from 'protractor';
import { FileUploader } from 'ng2-file-upload';
import { finalize, take } from 'rxjs/operators';
import { MobmainService } from './mobmain/mobmain.service';

@Component({
  selector: 'app-mob',
  templateUrl: './mob.component.html',
  styleUrls: ['./mob.component.scss']
})
export class MobComponent implements OnInit, OnChanges {
  @Input() modelData: any;
  @Input() frConfigData: any;
  @Output() public updateStatus : EventEmitter<boolean> = new EventEmitter<boolean>();
  @Output() public enableTab : EventEmitter<boolean> = new EventEmitter<boolean>();
  @ViewChild('fileInput') fileInput: any;
  public uploadTrainData: FormGroup;
  folderPaths: any;
  isuploadable: boolean = false;
  isuploadable1: Boolean = false;
  uploadFileName: any;
  uploading: boolean = false;
  folderPathBoolean: boolean = false;
  uploadingFileBoolean: boolean;
  public uploader: FileUploader = new FileUploader({
    isHTML5: true
  });
  public hasBaseDropZoneOver: boolean = false;
  jsonFinalData: any;
  successBoolean: boolean;
  errorBoolean: boolean;
  successFileBoolean: boolean;
  errorFileBoolean: boolean;
  
  modelStatus: any;
  status1Boolean: boolean;
  status2Boolean: boolean;
  status3Boolean: boolean;
  status4Boolean: boolean;
  status5Boolean: boolean;
  chooseFolderBoolean: boolean;
  model_validate_msg = "Model Uploaded Sucessfully";
  model_invalidate_msg = "This Model is Rejected, please re-upload train documents to continue..";
  uploadBtnBoolean: boolean;
  chooseFileBoolean: boolean;
  pathFolder: any;
  filePath: any;
  showtaggingtool: boolean = false;
  msg = "";
  msg1 = "";
  model_validate_boolean: boolean;
  reuploadBoolean: boolean;

  inputUploadFolder;
  invalidModelBoolean: boolean;

  constructor(private fb: FormBuilder,
    private mobservice:MobmainService,
    private messageService: MessageService,
    private sharedService: SharedService) {
    this.uploadTrainData = this.fb.group({
      uploadFolder: this.fb.control('', Validators.required)
    });

  }
  
  ngOnInit(): void {
    this.mobservice.getModelData().subscribe(data => {
      this.modelData = data;
    });
  }
 
  fileOverBase(event) {
    // this.isuploadable=false;
    this.hasBaseDropZoneOver = event;
  }
  onSelectFile(event) {

    this.isuploadable = false;
    this.isuploadable1 = false;
    
  }
  ngOnChanges(changes: SimpleChanges): void {
    this.mobservice.setFrConfig(this.frConfigData);
    if (changes) {
      this.modelStatus = this.modelData;
      if (this.modelStatus) {
        if (this.modelStatus.modelID) {
          this.getJson(this.modelStatus.modelID);
        }
        if (this.modelStatus.modelStatus == 0) {
          this.status1Boolean = false;
          this.status2Boolean = false;
          this.status3Boolean = false;
          this.status4Boolean = false;
          this.status5Boolean = false;
          this.enableTab.emit(false);
        } else if (this.modelStatus.modelStatus == 1) {
          this.status1Boolean = false;
          this.status2Boolean = false;
          this.status3Boolean = false;
          this.status4Boolean = false;
          this.status5Boolean = false;
          this.enableTab.emit(false);

        } else if(this.modelStatus.modelStatus == 2) {
          this.enableTab.emit(true);
          this.status1Boolean = true;
          this.status2Boolean = true;
          this.status3Boolean = true;
          this.status4Boolean = false;
          this.status5Boolean = false;
        } else if (this.modelStatus.modelStatus == 3) {
          this.status1Boolean = true;
          this.status2Boolean = true;
          this.status3Boolean = true;
          this.status4Boolean = false;
          this.status5Boolean = false;
          this.enableTab.emit(true);

        } else if (this.modelStatus.modelStatus == 4) {
          this.status1Boolean = true;
          this.status2Boolean = true;
          this.status4Boolean = true;
          this.status3Boolean = false;
          this.status5Boolean = false;
          this.enableTab.emit(true);


        } else if (this.modelStatus.modelStatus == 5) {
          this.status1Boolean = true;
          this.status2Boolean = true;
          this.status5Boolean = true;
          this.status4Boolean = true;
          this.status3Boolean = false;
          console.log(this.status2Boolean);
          this.enableTab.emit(true);

        }else{
          this.status1Boolean = false;
          this.status2Boolean = false;
          this.status3Boolean = false;
          this.status4Boolean = false;
          this.status5Boolean = false;
        }
        if(this.status1Boolean){
          this.msg = "Files are already uploaded successfully";
        }else{
          this.msg = "";
        }
      }
    }
  }


  uploadFolderEvent(event) {
    this.folderPaths = event.target.files;
    this.uploadFolderPath();
  }

  uploadFolderPath() {
    this.uploading = true;
    this.chooseFolderBoolean = true;
    const formData = new FormData();
    for (const file of this.folderPaths) {
      formData.append("files", file, file.name);
    }
    console.log(formData);
    this.folderPathBoolean = false;
    this.sharedService.uploadFolder(formData).subscribe((data: any) => {
      this.msg = "Uploaded to Blob successfully."
      this.msg1 = " Please click on start upload to validate the uploaded files."
      this.uploading = false;
      console.log(data);
      this.fileInput.nativeElement.value = '';
      this.pathFolder = data.filepath;
      this.folderPathBoolean = true;
      this.status1Boolean = true;
    }, error => {
      this.sharedService.errorObject.detail = error.statusText
      this.messageService.add(this.sharedService.errorObject);
    })
  }
  fileDrop(event) {
    console.log(event[0])
  }
  upload_Blob() {
    let blobData = {
      "min_no": 1,
      "max_no": 50,
      "file_size_accepted": 50,
      "accepted_file_type": "jpg,pdf",
      "cnx_str": this.frConfigData[0].ConnectionString,
      "cont_name": this.frConfigData[0].ContainerName,
      "local_path": this.pathFolder,
      "folderpath": this.modelData.folderPath
    }
    // if(this.modelStatus.modelStatus > 2){
    //   blobData.local_path = this.modelStatus.folderPath;
    // } else {
    //   blobData.local_path = this.pathFolder;
    // }
    this.isuploadable = true;
    this.isuploadable1 = false;
    this.msg1 = "";
    this.sharedService.uploadBlob(JSON.stringify(blobData)).subscribe((data: any) => {
      console.log(data);
      this.enableTab.emit(true);
      this.isuploadable = false;
      this.folderPathBoolean = false;
      this.messageService.add({
        severity: "success",
        summary: "Uploaded",
        detail: "Folder uploaded successfully"
      });
      if(data.nl_upload_status != 0){
        this.msg = data.fnl_upload_msg;
        this.modelUpdate(2);
        this.uploadBtnBoolean = true;
        this.successBoolean = true;
  
        this.status1Boolean = true;
        this.status2Boolean = true;
        this.status3Boolean = false;
        this.status4Boolean = false;
        this.status5Boolean = false;
      } else {
        this.messageService.add(this.sharedService.errorObject);
      }
    }, error => {
      this.sharedService.errorObject.detail = error.statusText
      this.messageService.add(this.sharedService.errorObject);
      this.uploadBtnBoolean = true;
      this.errorBoolean = true;


    });
  }

  uploadFileEvent(event) {
    this.uploadFileName = event;
    console.log(event[0].name);
    this.uploadFile();
  }
  
  uploadFile() {
    this.chooseFileBoolean = true;
    const formData = new FormData();
    formData.append("file", this.uploadFileName[0], this.uploadFileName[0].name);

    console.log(formData);
    this.sharedService.uploadFileblob(formData).subscribe((data: any) => {

      this.filePath = data.filepath;
      // this.modelUpdate(3);

      this.successFileBoolean = true;



    }, error => {
      this.sharedService.errorObject.detail = error.statusText
      this.messageService.add(this.sharedService.errorObject);
      this.errorFileBoolean = true;
      this.uploadingFileBoolean = false;
    })
  }

  model_validate() {
    this.uploadingFileBoolean = true;
    let validateModel = {
      "model_path": this.filePath,
      "model_id": Number(this.modelStatus.idDocumentModel),
      "req_fields_accuracy": 0,
      "req_model_accuracy": 10.0,
      "mand_fld_list": "PurchaseOrder,InvoiceDate,InvoiceId",
      "cnx_str": this.frConfigData[0].ConnectionString,
      "cont_name": this.frConfigData[0].ContainerName,
      "VendorAccount": this.modelStatus.idVendorAccount
    }
    console.log(validateModel);
    console.log(this.modelStatus)
    // if(this.modelStatus.modelStatus > 4){
    //   validateModel.model_path = this.modelStatus.folderPath
    // } else {
    //   validateModel.model_path = this.filePath
    // }


    console.log(validateModel);
    this.sharedService.modelValidate(JSON.stringify(validateModel)).pipe(take(1), finalize(() => {
      this.uploadingFileBoolean = false;
    })).subscribe((data: any) => {
      console.log(data);
      if(data.model_id == ""){
        this.modelUpdate(3);
        this.status1Boolean = true;
        this.status2Boolean = true;
        this.status3Boolean = true;
        this.status4Boolean = false;
        this.status5Boolean = false;
        this.model_validate_boolean = true;
        
      } else {

        if(data.model_validate_status == 1){
          this.modelUpdate(4);
          this.modelStatus.modelID = data.model_id;
          this.getJson(data.model_id);
          this.status1Boolean = true;
          this.status2Boolean = true;
          this.status3Boolean = false;
          this.status4Boolean = true;
          this.status5Boolean = false;
    
          this.model_validate_msg = data.model_validate_msg;
          this.messageService.add({
            severity: "success",
            summary: "Uploaded",
            detail: "Model Uploaded Sucessfully"
          });
        } else {
          this.invalidModelBoolean = true;
          this.model_invalidate_msg = data.model_validate_msg;
          this.sharedService.errorObject.detail = 'please retry again.'
          this.messageService.add(this.sharedService.errorObject);
        }

      }


    }, error=> {
      this.sharedService.errorObject.detail = error.statusText
      this.messageService.add(this.sharedService.errorObject);
    })
  }

  

  getJson(data) {
    this.sharedService.getFinalData(data).subscribe((data: any) => {
      this.jsonFinalData = data;
    })
  }

  activate_reupload(){
    this.status1Boolean = false;
    this.status2Boolean = false;
    this.status3Boolean = false;
    this.status4Boolean = false;
    this.status5Boolean = false;
    this.reuploadBoolean = true;
    this.msg = "";
  }

  reupload_Blob(uploadtype) {

    let reuplaodMeta = {
      "min_no": 1,
      "max_no": 50,
      "file_size_accepted": 50,
      "accepted_file_type": "jpg,pdf",
      "cnx_str": this.frConfigData[0].ConnectionString,
      "cont_name": this.frConfigData[0].ContainerName,
      "local_path": this.pathFolder,
      "old_folder": this.modelStatus.folderPath,
      "upload_type":uploadtype
    }
    if(uploadtype == 'Fresh'){
      this.isuploadable1 = true;
    }else{
      this.isuploadable = true;
    }
    this.sharedService.reupload_blob(JSON.stringify(reuplaodMeta)).subscribe((data: any) => {
      console.log(data);
      this.enableTab.emit(true);
      this.isuploadable = false;
      this.isuploadable1 = false;
      // this.modelStatus.folderPath = data.blob_fld_name
      this.modelUpdate(2);
      this.status1Boolean = true;
      this.status2Boolean = true;
      this.status3Boolean = false;
      this.status4Boolean = false;
      this.status5Boolean = false;
      this.reuploadBoolean = false;
      this.folderPathBoolean = false;
      this.msg = data.fnl_upload_msg;
      this.msg1 = "";
    },error=>{
      this.sharedService.errorObject.detail = error.statusText
      this.messageService.add(this.sharedService.errorObject);
    })
  }

  modelUpdate(id_status) {

    let updatedData = {
      "modelName": this.modelStatus.modelName,
      "idVendorAccount": this.modelStatus.idVendorAccount,
      "folderPath": this.modelStatus.folderPath,
      "modelStatus": id_status
    }
    console.log(this.modelStatus);
    // if(this.modelStatus.modelStatus != 1){
    //   console.log("hi 1")
    //   updatedData.folderPath = this.modelStatus.folderPath;
    // } else {
    //   console.log("hi else")
    //   updatedData.folderPath = this.pathFolder;
    // }
    console.log(updatedData);
    this.sharedService.updateModel(JSON.stringify(updatedData), this.modelStatus.idDocumentModel).subscribe((data: any) => {
      console.log(data);
      this.updateStatus.emit(true);
    },error=>{
      this.sharedService.errorObject.detail = error.statusText
      this.messageService.add(this.sharedService.errorObject);
    })
  }
  uploadToSerina(){
    this.sharedService.uploadDb(JSON.stringify(this.jsonFinalData.final_data),this.modelStatus.idDocumentModel).subscribe(data=>{
      console.log(data);
      this.messageService.add({
        severity: "success",
        summary: "Uploaded",
        detail: "Model Uploaded Sucessfully"
      });
      this.status1Boolean = true;
      this.status2Boolean = true;
      this.status3Boolean = false;
      this.status4Boolean = true;
      this.status5Boolean = true;
      this.modelUpdate(5);
    },error=>{
      this.sharedService.errorObject.detail = error.statusText
      this.messageService.add(this.sharedService.errorObject);
    })
  }

}

