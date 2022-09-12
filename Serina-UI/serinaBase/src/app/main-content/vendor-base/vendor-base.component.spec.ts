import { ComponentFixture, TestBed } from '@angular/core/testing';

import { VendorBaseComponent } from './vendor-base.component';

describe('VendorBaseComponent', () => {
  let component: VendorBaseComponent;
  let fixture: ComponentFixture<VendorBaseComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ VendorBaseComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(VendorBaseComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
