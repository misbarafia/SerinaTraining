import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FinanceApprovalSettingsComponent } from './finance-approval-settings.component';

describe('FinanceApprovalSettingsComponent', () => {
  let component: FinanceApprovalSettingsComponent;
  let fixture: ComponentFixture<FinanceApprovalSettingsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ FinanceApprovalSettingsComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(FinanceApprovalSettingsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
