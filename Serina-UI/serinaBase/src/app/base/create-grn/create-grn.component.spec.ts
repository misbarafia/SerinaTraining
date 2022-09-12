import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CreateGRNComponent } from './create-grn.component';

describe('CreateGRNComponent', () => {
  let component: CreateGRNComponent;
  let fixture: ComponentFixture<CreateGRNComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ CreateGRNComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(CreateGRNComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
