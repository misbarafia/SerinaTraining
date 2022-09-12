import { Router } from '@angular/router';
import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-password-settings',
  templateUrl: './password-settings.component.html',
  styleUrls: ['./password-settings.component.scss']
})
export class PasswordSettingsComponent implements OnInit {

  constructor(private router : Router) { }

  ngOnInit(): void {
  }

  backToSettings() {
    this.router.navigate(['/customer/settings/generalSettings'])
  }
}
