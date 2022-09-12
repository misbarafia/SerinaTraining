import { TestBed } from '@angular/core/testing';

import { AdminGaurdService } from './admin-gaurd.service';

describe('AdminGaurdService', () => {
  let service: AdminGaurdService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(AdminGaurdService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
