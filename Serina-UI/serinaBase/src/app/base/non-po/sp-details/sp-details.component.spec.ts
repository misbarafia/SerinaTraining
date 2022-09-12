import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SpDetailsComponent } from './sp-details.component';

describe('SpDetailsComponent', () => {
  let component: SpDetailsComponent;
  let fixture: ComponentFixture<SpDetailsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ SpDetailsComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(SpDetailsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
