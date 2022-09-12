import { ComponentFixture, TestBed } from '@angular/core/testing';

import { BusinessChartsComponent } from './business-charts.component';

describe('BusinessChartsComponent', () => {
  let component: BusinessChartsComponent;
  let fixture: ComponentFixture<BusinessChartsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ BusinessChartsComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(BusinessChartsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
