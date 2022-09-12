import { ComponentFixture, TestBed } from '@angular/core/testing';

import { NonPoComponent } from './non-po.component';

describe('NonPoComponent', () => {
  let component: NonPoComponent;
  let fixture: ComponentFixture<NonPoComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ NonPoComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(NonPoComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
