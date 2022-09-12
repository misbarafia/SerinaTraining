import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ProfileVendorComponent } from './profile-vendor.component';

describe('ProfileVendorComponent', () => {
  let component: ProfileVendorComponent;
  let fixture: ComponentFixture<ProfileVendorComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ProfileVendorComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ProfileVendorComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
