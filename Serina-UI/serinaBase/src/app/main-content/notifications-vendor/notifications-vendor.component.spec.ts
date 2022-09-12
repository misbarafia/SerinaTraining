import { ComponentFixture, TestBed } from '@angular/core/testing';

import { NotificationsVendorComponent } from './notifications-vendor.component';

describe('NotificationsVendorComponent', () => {
  let component: NotificationsVendorComponent;
  let fixture: ComponentFixture<NotificationsVendorComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ NotificationsVendorComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(NotificationsVendorComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
