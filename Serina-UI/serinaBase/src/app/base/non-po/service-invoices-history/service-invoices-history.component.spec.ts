import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ServiceInvoicesHistoryComponent } from './service-invoices-history.component';

describe('ServiceInvoicesHistoryComponent', () => {
  let component: ServiceInvoicesHistoryComponent;
  let fixture: ComponentFixture<ServiceInvoicesHistoryComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ServiceInvoicesHistoryComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ServiceInvoicesHistoryComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
