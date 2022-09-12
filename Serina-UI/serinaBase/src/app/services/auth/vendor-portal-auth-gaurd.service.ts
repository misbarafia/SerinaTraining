import { Injectable } from '@angular/core';
import { ActivatedRouteSnapshot, CanActivate, Router, RouterStateSnapshot } from '@angular/router';
import { AuthenticationService } from './auth-service.service';

@Injectable({
  providedIn: 'root'
})
export class VendorPortalAuthGaurd implements CanActivate {
  constructor(
      private router: Router,
      private authenticationService: AuthenticationService
  ) { }

  canActivate(route: ActivatedRouteSnapshot, state: RouterStateSnapshot) {
      const currentUser = this.authenticationService.currentUserValue;
      if (currentUser) {
        if (currentUser.user_type === 'vendor_portal') {
          // logged in so return true
          return true;
      }
      }

      // not logged in so redirect to login page with the return url
      this.router.navigate(['/login'], { queryParams: { returnUrl: state.url } });
      return false;
  }
}
