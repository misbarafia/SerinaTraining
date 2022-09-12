import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ProcessMetricsComponent } from './process-metrics.component';

describe('ProcessMetricsComponent', () => {
  let component: ProcessMetricsComponent;
  let fixture: ComponentFixture<ProcessMetricsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ProcessMetricsComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ProcessMetricsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
