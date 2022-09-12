import { TestBed } from '@angular/core/testing';

import { MobmainService } from './mobmain.service';

describe('MobmainService', () => {
  let service: MobmainService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(MobmainService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
