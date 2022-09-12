import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TechExceptionComponent } from './tech-exception.component';

describe('TechExceptionComponent', () => {
  let component: TechExceptionComponent;
  let fixture: ComponentFixture<TechExceptionComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ TechExceptionComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(TechExceptionComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
