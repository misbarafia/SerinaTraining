import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ExceptionManagementComponent } from './exception-management.component';

describe('ExceptionManagementComponent', () => {
  let component: ExceptionManagementComponent;
  let fixture: ComponentFixture<ExceptionManagementComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ExceptionManagementComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ExceptionManagementComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
