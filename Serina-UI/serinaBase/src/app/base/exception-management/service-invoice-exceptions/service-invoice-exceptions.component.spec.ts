import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ServiceInvoiceExceptionsComponent } from './service-invoice-exceptions.component';

describe('ServiceInvoiceExceptionsComponent', () => {
  let component: ServiceInvoiceExceptionsComponent;
  let fixture: ComponentFixture<ServiceInvoiceExceptionsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ServiceInvoiceExceptionsComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ServiceInvoiceExceptionsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
