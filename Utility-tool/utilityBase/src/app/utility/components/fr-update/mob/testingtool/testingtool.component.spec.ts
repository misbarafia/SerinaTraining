import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TestingtoolComponent } from './testingtool.component';

describe('TestingtoolComponent', () => {
  let component: TestingtoolComponent;
  let fixture: ComponentFixture<TestingtoolComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ TestingtoolComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(TestingtoolComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
