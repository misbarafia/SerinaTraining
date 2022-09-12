import { ComponentFixture, TestBed } from '@angular/core/testing';

import { BaseTypeComponent } from './base-type.component';

describe('BaseTypeComponent', () => {
  let component: BaseTypeComponent;
  let fixture: ComponentFixture<BaseTypeComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ BaseTypeComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(BaseTypeComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
