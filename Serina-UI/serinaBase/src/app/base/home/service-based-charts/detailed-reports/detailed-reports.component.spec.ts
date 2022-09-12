import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DetailedReportsComponent } from './detailed-reports.component';

describe('DetailedReportsComponent', () => {
  let component: DetailedReportsComponent;
  let fixture: ComponentFixture<DetailedReportsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ DetailedReportsComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(DetailedReportsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
