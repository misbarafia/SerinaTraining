import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ComposingtoolComponent } from './composingtool.component';

describe('ComposingtoolComponent', () => {
  let component: ComposingtoolComponent;
  let fixture: ComponentFixture<ComposingtoolComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ComposingtoolComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ComposingtoolComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
