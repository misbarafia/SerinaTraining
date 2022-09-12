import { Component } from '@angular/core';
import {DomSanitizer} from '@angular/platform-browser';
import {MatIconRegistry} from '@angular/material/icon';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  title = 'serinaBase';

  constructor(
    private iconRegistry: MatIconRegistry, 
    private sanitizer: DomSanitizer
  ) {
    this.iconRegistry.addSvgIcon(
      'back_arrow',
      sanitizer.bypassSecurityTrustResourceUrl('assets/Serina Assets/Assets/back_arrow_fill_ic.svg')
    );
    this.iconRegistry.addSvgIcon(
      'logout',
      sanitizer.bypassSecurityTrustResourceUrl('assets/Serina Assets/Assets/logout_ic.svg')
    );
    this.iconRegistry.addSvgIcon(
      'total_page',
      sanitizer.bypassSecurityTrustResourceUrl('assets/Serina Assets/Assets/total_page_ic.svg')
    );
    this.iconRegistry.addSvgIcon(
      'total_inv',
      sanitizer.bypassSecurityTrustResourceUrl('assets/Serina Assets/Assets/total_invoice_ic.svg')
    );
    this.iconRegistry.addSvgIcon(
      'total_success',
      sanitizer.bypassSecurityTrustResourceUrl('assets/Serina Assets/Assets/total_sucess_ic.svg')
    );
    this.iconRegistry.addSvgIcon(
      'total_fail',
      sanitizer.bypassSecurityTrustResourceUrl('assets/Serina Assets/Assets/total_failed_ic.svg')
    );
    this.iconRegistry.addSvgIcon(
      'total_active',
      sanitizer.bypassSecurityTrustResourceUrl('assets/Serina Assets/Assets/total_active_account_ic.svg')
    );
    this.iconRegistry.addSvgIcon(
      'total_pending',
      sanitizer.bypassSecurityTrustResourceUrl('assets/Serina Assets/Assets/total_pending_ic.svg')
    );
    this.iconRegistry.addSvgIcon(
      'total_download',
      sanitizer.bypassSecurityTrustResourceUrl('assets/Serina Assets/Assets/total_download_ic.svg')
    );
    this.iconRegistry.addSvgIcon(
      'close',
      sanitizer.bypassSecurityTrustResourceUrl('assets/Serina Assets/Assets/cancel_line_ic.svg')
    );
    this.iconRegistry.addSvgIcon(
      'vendor_up',
      sanitizer.bypassSecurityTrustResourceUrl('assets/Serina Assets/Assets/Vendor/uploaded_inv_ic.svg')
    );
    this.iconRegistry.addSvgIcon(
      'vendor_pr',
      sanitizer.bypassSecurityTrustResourceUrl('assets/Serina Assets/Assets/Vendor/processed_inv_ic.svg')
    );
    this.iconRegistry.addSvgIcon(
      'vendor_rm',
      sanitizer.bypassSecurityTrustResourceUrl('assets/Serina Assets/Assets/Vendor/remaining_inv_ic.svg')
    );
    this.iconRegistry.addSvgIcon(
      'vendor_rej',
      sanitizer.bypassSecurityTrustResourceUrl('assets/Serina Assets/Assets/Vendor/rejected_inv_ic.svg')
    );
    this.iconRegistry.addSvgIcon(
      'vendor_err',
      sanitizer.bypassSecurityTrustResourceUrl('assets/Serina Assets/Assets/Vendor/error_inv_ic.svg')
    );
    this.iconRegistry.addSvgIcon(
      'service_total',
      sanitizer.bypassSecurityTrustResourceUrl('assets/Serina Assets/Assets/Service/total_invoice_ic.svg')
    );
    this.iconRegistry.addSvgIcon(
      'service_dwn',
      sanitizer.bypassSecurityTrustResourceUrl('assets/Serina Assets/Assets/Service/downloaded_ic.svg')
    );
    this.iconRegistry.addSvgIcon(
      'service_pr',
      sanitizer.bypassSecurityTrustResourceUrl('assets/Serina Assets/Assets/Service/processed_ic.svg')
    );
    this.iconRegistry.addSvgIcon(
      'service_rm',
      sanitizer.bypassSecurityTrustResourceUrl('assets/Serina Assets/Assets/Service/remaining_ic.svg')
    );
    this.iconRegistry.addSvgIcon(
      'service_scn',
      sanitizer.bypassSecurityTrustResourceUrl('assets/Serina Assets/Assets/Service/total_scaned_ic.svg')
    );
  }
}
