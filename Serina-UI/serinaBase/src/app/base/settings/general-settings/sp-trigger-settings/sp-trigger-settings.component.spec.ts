import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SpTriggerSettingsComponent } from './sp-trigger-settings.component';

describe('SpTriggerSettingsComponent', () => {
  let component: SpTriggerSettingsComponent;
  let fixture: ComponentFixture<SpTriggerSettingsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ SpTriggerSettingsComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(SpTriggerSettingsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
