import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TaggingtoolComponent } from './taggingtool.component';

describe('TaggingtoolComponent', () => {
  let component: TaggingtoolComponent;
  let fixture: ComponentFixture<TaggingtoolComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ TaggingtoolComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(TaggingtoolComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
