import { ComponentFixture, TestBed } from '@angular/core/testing';

import { VendorBasedChartsComponent } from './vendor-based-charts.component';

describe('VendorBasedChartsComponent', () => {
  let component: VendorBasedChartsComponent;
  let fixture: ComponentFixture<VendorBasedChartsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ VendorBasedChartsComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(VendorBasedChartsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
