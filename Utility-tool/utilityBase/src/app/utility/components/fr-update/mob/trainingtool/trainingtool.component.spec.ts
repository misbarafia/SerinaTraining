import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TrainingtoolComponent } from './trainingtool.component';

describe('TrainingtoolComponent', () => {
  let component: TrainingtoolComponent;
  let fixture: ComponentFixture<TrainingtoolComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ TrainingtoolComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(TrainingtoolComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
