import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RolesVendorComponent } from './roles-vendor.component';

describe('RolesVendorComponent', () => {
  let component: RolesVendorComponent;
  let fixture: ComponentFixture<RolesVendorComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ RolesVendorComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(RolesVendorComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
