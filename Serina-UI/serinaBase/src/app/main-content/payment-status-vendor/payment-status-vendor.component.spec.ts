import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PaymentStatusVendorComponent } from './payment-status-vendor.component';

describe('PaymentStatusVendorComponent', () => {
  let component: PaymentStatusVendorComponent;
  let fixture: ComponentFixture<PaymentStatusVendorComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ PaymentStatusVendorComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(PaymentStatusVendorComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
