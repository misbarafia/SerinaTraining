import { ComponentFixture, TestBed } from '@angular/core/testing';

import { VendorSitesComponent } from './vendor-sites.component';

describe('VendorSitesComponent', () => {
  let component: VendorSitesComponent;
  let fixture: ComponentFixture<VendorSitesComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ VendorSitesComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(VendorSitesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
