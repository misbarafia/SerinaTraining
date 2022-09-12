import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ModelExceptionComponent } from './model-exception.component';

describe('ModelExceptionComponent', () => {
  let component: ModelExceptionComponent;
  let fixture: ComponentFixture<ModelExceptionComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ModelExceptionComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ModelExceptionComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
