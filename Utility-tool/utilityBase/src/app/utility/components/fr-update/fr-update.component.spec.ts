import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FrUpdateComponent } from './fr-update.component';

describe('FrUpdateComponent', () => {
  let component: FrUpdateComponent;
  let fixture: ComponentFixture<FrUpdateComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ FrUpdateComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(FrUpdateComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
