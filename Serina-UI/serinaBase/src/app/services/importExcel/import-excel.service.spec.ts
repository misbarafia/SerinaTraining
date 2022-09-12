import { TestBed } from '@angular/core/testing';

import { ImportExcelService } from './import-excel.service';

describe('ImportExcelService', () => {
  let service: ImportExcelService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(ImportExcelService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
