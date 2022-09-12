import { ComponentFixture, TestBed } from '@angular/core/testing';

import { VendorItemListComponent } from './vendor-item-list.component';

describe('VendorItemListComponent', () => {
  let component: VendorItemListComponent;
  let fixture: ComponentFixture<VendorItemListComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ VendorItemListComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(VendorItemListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
