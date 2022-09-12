import { TestBed } from '@angular/core/testing';

import { VendorPortalAuthGaurd } from './vendor-portal-auth-gaurd.service';

describe('VendorPortalAuthGaurdService', () => {
  let service: VendorPortalAuthGaurd;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(VendorPortalAuthGaurd);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
