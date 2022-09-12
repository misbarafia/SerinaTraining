import { Location } from '@angular/common';
import { Injectable } from '@angular/core';
import { ActivatedRouteSnapshot, CanActivate, Router, RouterStateSnapshot } from '@angular/router';
import { AuthenticationService } from '../auth-service.service';

@Injectable({
  providedIn: 'root'
})
export class AdminGaurdService implements CanActivate {
  constructor(
      private router: Router,
      private Location: Location,
      private authenticationService: AuthenticationService
  ) { }

  canActivate(route: ActivatedRouteSnapshot, state: RouterStateSnapshot) {
      const currentUser = this.authenticationService.currentUserValue;
      if (currentUser) {
          if (currentUser['permissioninfo'].is_spa === 1) {
              // Admin so return true
              return true;
          }
      }

      // not logged in so redirect to login page with the return url
      alert("Sorry!, you do not have access")
      // this.Location.path();
      return false;
  }
}