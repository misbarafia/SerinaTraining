import { ComponentFixture, TestBed } from '@angular/core/testing';

import { UtilityHomeComponent } from './utility-home.component';

describe('UtilityHomeComponent', () => {
  let component: UtilityHomeComponent;
  let fixture: ComponentFixture<UtilityHomeComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ UtilityHomeComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(UtilityHomeComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
