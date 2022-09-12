import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ServiceDocStatusComponent } from './service-doc-status.component';

describe('ServiceDocStatusComponent', () => {
  let component: ServiceDocStatusComponent;
  let fixture: ComponentFixture<ServiceDocStatusComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ServiceDocStatusComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ServiceDocStatusComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
