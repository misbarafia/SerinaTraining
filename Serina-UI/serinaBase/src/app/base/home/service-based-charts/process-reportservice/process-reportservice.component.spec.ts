import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ProcessReportserviceComponent } from './process-reportservice.component';

describe('ProcessReportserviceComponent', () => {
  let component: ProcessReportserviceComponent;
  let fixture: ComponentFixture<ProcessReportserviceComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ProcessReportserviceComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ProcessReportserviceComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
