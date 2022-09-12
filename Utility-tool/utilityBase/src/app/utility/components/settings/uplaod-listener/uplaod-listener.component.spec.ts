import { ComponentFixture, TestBed } from '@angular/core/testing';

import { UplaodListenerComponent } from './uplaod-listener.component';

describe('UplaodListenerComponent', () => {
  let component: UplaodListenerComponent;
  let fixture: ComponentFixture<UplaodListenerComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ UplaodListenerComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(UplaodListenerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
