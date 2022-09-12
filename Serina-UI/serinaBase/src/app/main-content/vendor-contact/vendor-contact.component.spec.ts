import { ComponentFixture, TestBed } from '@angular/core/testing';

import { VendorContactComponent } from './vendor-contact.component';

describe('VendorContactComponent', () => {
  let component: VendorContactComponent;
  let fixture: ComponentFixture<VendorContactComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ VendorContactComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(VendorContactComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
