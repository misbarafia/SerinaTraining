import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ActionCenterVendorComponent } from './action-center-vendor.component';

describe('ActionCenterVendorComponent', () => {
  let component: ActionCenterVendorComponent;
  let fixture: ComponentFixture<ActionCenterVendorComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ActionCenterVendorComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ActionCenterVendorComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
