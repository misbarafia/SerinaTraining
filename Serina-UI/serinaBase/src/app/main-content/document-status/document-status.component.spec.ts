import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DocumentStatusComponent } from './document-status.component';

describe('DocumentStatusComponent', () => {
  let component: DocumentStatusComponent;
  let fixture: ComponentFixture<DocumentStatusComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ DocumentStatusComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(DocumentStatusComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
