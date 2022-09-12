import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SharepointListenerComponent } from './sharepoint-listener.component';

describe('SharepointListenerComponent', () => {
  let component: SharepointListenerComponent;
  let fixture: ComponentFixture<SharepointListenerComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ SharepointListenerComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(SharepointListenerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
