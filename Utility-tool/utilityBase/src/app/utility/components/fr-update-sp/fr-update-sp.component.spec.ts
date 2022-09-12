import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FrUpdateSpComponent } from './fr-update-sp.component';

describe('FrUpdateSpComponent', () => {
  let component: FrUpdateSpComponent;
  let fixture: ComponentFixture<FrUpdateSpComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ FrUpdateSpComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(FrUpdateSpComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
