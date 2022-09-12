import { TestBed } from '@angular/core/testing';

import { CanLeaveService } from './can-leave.service';

describe('CanLeaveService', () => {
  let service: CanLeaveService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(CanLeaveService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
