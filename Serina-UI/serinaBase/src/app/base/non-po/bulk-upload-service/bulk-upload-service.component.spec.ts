import { ComponentFixture, TestBed } from '@angular/core/testing';

import { BulkUploadServiceComponent } from './bulk-upload-service.component';

describe('BulkUploadServiceComponent', () => {
  let component: BulkUploadServiceComponent;
  let fixture: ComponentFixture<BulkUploadServiceComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ BulkUploadServiceComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(BulkUploadServiceComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
