import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MobmainComponent } from './mobmain.component';

describe('MobmainComponent', () => {
  let component: MobmainComponent;
  let fixture: ComponentFixture<MobmainComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ MobmainComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(MobmainComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
