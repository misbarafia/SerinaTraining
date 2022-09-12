import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ExceptionReportsComponent } from './exception-reports.component';

describe('ExceptionReportsComponent', () => {
  let component: ExceptionReportsComponent;
  let fixture: ComponentFixture<ExceptionReportsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ExceptionReportsComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ExceptionReportsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
