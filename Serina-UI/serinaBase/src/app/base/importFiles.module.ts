import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';

import { DatePipe } from '@angular/common';

import {DemoMaterialModule} from './material-module';
import {MatSelectModule} from '@angular/material/select';

import { FileUploadModule } from 'ng2-file-upload';
import {DropdownModule} from 'primeng/dropdown';
import { ClickOutsideModule } from 'ng-click-outside';
import { ConfirmPopupModule } from "primeng/confirmpopup";
import { ButtonModule } from "primeng/button";
import {AccordionModule} from 'primeng/accordion';
import {ToggleButtonModule} from 'primeng/togglebutton';
import { ConfirmationService, MessageService } from "primeng/api";
import {ToastModule} from 'primeng/toast';
import {TimelineModule} from 'primeng/timeline';
import {AutoCompleteModule} from 'primeng/autocomplete';
import {MultiSelectModule} from 'primeng/multiselect';
import {SidebarModule} from 'primeng/sidebar';
import {TableModule} from 'primeng/table';
import {TabViewModule} from 'primeng/tabview';
import {TooltipModule} from 'primeng/tooltip';
import {DialogModule} from 'primeng/dialog';
import {OrderListModule} from 'primeng/orderlist';
import {MatExpansionModule} from '@angular/material/expansion';
import {BadgeModule} from 'primeng/badge';
import {PaginatorModule} from 'primeng/paginator';
import {ConfirmDialogModule} from 'primeng/confirmdialog';
import {CalendarModule} from 'primeng/calendar';
import {ChipsModule} from 'primeng/chips';
import { NgxSpinnerModule } from "ngx-spinner"; 

import { TextMaskModule } from 'angular2-text-mask';

import { NgbModule } from '@ng-bootstrap/ng-bootstrap';



@NgModule({ 
    declarations:[],
    imports: [
        CommonModule,
        FormsModule,
        ReactiveFormsModule,
        DemoMaterialModule,
        FileUploadModule,
        MatSelectModule,
        ConfirmPopupModule,
        TimelineModule,
        ButtonModule,
        ConfirmDialogModule,
        DropdownModule,
        DialogModule,
        MultiSelectModule,
        AutoCompleteModule,
        SidebarModule,
        TooltipModule,
        ClickOutsideModule,
        TableModule,
        TabViewModule,
        MatExpansionModule,
        BadgeModule,
        NgxSpinnerModule,
        AccordionModule,
        ToggleButtonModule,
        OrderListModule,
        PaginatorModule,
        ToastModule,
        CalendarModule,
        TextMaskModule,
        NgbModule,
        ChipsModule
      ],
      exports:[
        CommonModule,
        DemoMaterialModule,
        FileUploadModule,
        MatSelectModule,
        ConfirmPopupModule,
        ConfirmDialogModule,
        TimelineModule,
        ButtonModule,
        DropdownModule,
        DialogModule,
        MultiSelectModule,
        AutoCompleteModule,
        SidebarModule,
        TooltipModule,
        ClickOutsideModule,
        TableModule,
        TabViewModule,
        MatExpansionModule,
        BadgeModule,
        NgxSpinnerModule,
        AccordionModule,
        ToggleButtonModule,
        OrderListModule,
        PaginatorModule,
        ToastModule,
        CalendarModule,
        TextMaskModule,
        NgbModule,
        ChipsModule
      ],
      providers:[DatePipe,ConfirmationService, MessageService ]
})
export class importFilesModule { }
