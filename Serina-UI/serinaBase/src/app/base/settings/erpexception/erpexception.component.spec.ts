import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ERPExceptionComponent } from './erpexception.component';

describe('ERPExceptionComponent', () => {
  let component: ERPExceptionComponent;
  let fixture: ComponentFixture<ERPExceptionComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ERPExceptionComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ERPExceptionComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
