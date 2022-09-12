import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ServiceInvoicesDisplayComponent } from './service-invoices-display.component';

describe('ServiceInvoicesDisplayComponent', () => {
  let component: ServiceInvoicesDisplayComponent;
  let fixture: ComponentFixture<ServiceInvoicesDisplayComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ServiceInvoicesDisplayComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ServiceInvoicesDisplayComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
