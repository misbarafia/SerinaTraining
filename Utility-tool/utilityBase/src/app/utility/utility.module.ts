
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import {DialogModule} from 'primeng/dialog';
import {MultiSelectModule} from 'primeng/multiselect';
import {ChipsModule} from 'primeng/chips';
import {CdkStepperModule} from '@angular/cdk/stepper';
import {NgStepperModule} from 'angular-ng-stepper';
import { NgxJsonViewerModule } from 'ngx-json-viewer';
import { ToastModule } from 'primeng/toast';
import { FileUploadModule } from 'ng2-file-upload';
import { UtilityRoutingModule } from './utility-routing.module';
import { HomeComponent } from './components/home/home.component';
import { VendorsComponent } from './components/vendors/vendors.component';
import { UtilityHomeComponent } from './components/utility-home/utility-home.component';
import { GuideComponent } from './components/guide/guide.component';
import { FrUpdateComponent } from './components/fr-update/fr-update.component';
import { ModalOnBoardComponent } from './components/modal-on-board/modal-on-board.component';
import { MessageService } from 'primeng/api';
import { MobComponent } from './components/fr-update/mob/mob.component';
import { TaggingtoolComponent } from './components/fr-update/mob/taggingtool/taggingtool.component';
import {DragDropModule} from '@angular/cdk/drag-drop';
import { TrainingtoolComponent } from './components/fr-update/mob/trainingtool/trainingtool.component';
import { ComposingtoolComponent } from './components/fr-update/mob/composingtool/composingtool.component';
import { TestingtoolComponent } from './components/fr-update/mob/testingtool/testingtool.component';
import { MobmainComponent } from './components/fr-update/mob/mobmain/mobmain.component';
import { InfiniteScrollModule } from 'ngx-infinite-scroll';
import { ServiceProvidersComponent } from './components/service-providers/service-providers.component';
import { FrUpdateSpComponent } from './components/fr-update-sp/fr-update-sp.component';

@NgModule({
  declarations: [HomeComponent, VendorsComponent, UtilityHomeComponent, GuideComponent, FrUpdateComponent, ModalOnBoardComponent, MobComponent, TaggingtoolComponent, TrainingtoolComponent, ComposingtoolComponent, TestingtoolComponent, MobmainComponent, ServiceProvidersComponent, FrUpdateSpComponent],
  imports: [
    CommonModule,
    UtilityRoutingModule,
    FormsModule,
    DialogModule,
    FileUploadModule,
    CdkStepperModule,
    NgStepperModule,
    ReactiveFormsModule,
    ToastModule,
    NgxJsonViewerModule,
    DragDropModule,
    ChipsModule,
    MultiSelectModule,
    InfiniteScrollModule
  ],
  providers:[MessageService]
})
export class UtilityModule { }
