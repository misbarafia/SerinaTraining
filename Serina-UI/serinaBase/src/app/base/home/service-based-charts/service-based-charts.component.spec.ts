import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ServiceBasedChartsComponent } from './service-based-charts.component';

describe('ServiceBasedChartsComponent', () => {
  let component: ServiceBasedChartsComponent;
  let fixture: ComponentFixture<ServiceBasedChartsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ServiceBasedChartsComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ServiceBasedChartsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
