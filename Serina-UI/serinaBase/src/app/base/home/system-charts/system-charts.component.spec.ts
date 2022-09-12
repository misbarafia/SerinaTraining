import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SystemChartsComponent } from './system-charts.component';

describe('SystemChartsComponent', () => {
  let component: SystemChartsComponent;
  let fixture: ComponentFixture<SystemChartsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ SystemChartsComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(SystemChartsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
