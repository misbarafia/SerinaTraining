import { ComponentFixture, TestBed } from '@angular/core/testing';

import { InvokeBatchComponent } from './invoke-batch.component';

describe('InvokeBatchComponent', () => {
  let component: InvokeBatchComponent;
  let fixture: ComponentFixture<InvokeBatchComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ InvokeBatchComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(InvokeBatchComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
