import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Comparision3WayComponent } from './comparision3-way.component';

describe('Comparision3WayComponent', () => {
  let component: Comparision3WayComponent;
  let fixture: ComponentFixture<Comparision3WayComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ Comparision3WayComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(Comparision3WayComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
