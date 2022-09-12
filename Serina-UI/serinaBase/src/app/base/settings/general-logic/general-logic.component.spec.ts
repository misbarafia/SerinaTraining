import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GeneralLogicComponent } from './general-logic.component';

describe('GeneralLogicComponent', () => {
  let component: GeneralLogicComponent;
  let fixture: ComponentFixture<GeneralLogicComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ GeneralLogicComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(GeneralLogicComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
