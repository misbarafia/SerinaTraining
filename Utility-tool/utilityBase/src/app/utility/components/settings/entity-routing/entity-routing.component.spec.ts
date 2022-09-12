import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EntityRoutingComponent } from './entity-routing.component';

describe('EntityRoutingComponent', () => {
  let component: EntityRoutingComponent;
  let fixture: ComponentFixture<EntityRoutingComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ EntityRoutingComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(EntityRoutingComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
