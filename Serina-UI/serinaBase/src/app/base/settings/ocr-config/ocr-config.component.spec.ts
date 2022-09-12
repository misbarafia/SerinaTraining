import { ComponentFixture, TestBed } from '@angular/core/testing';

import { OcrConfigComponent } from './ocr-config.component';

describe('OcrConfigComponent', () => {
  let component: OcrConfigComponent;
  let fixture: ComponentFixture<OcrConfigComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ OcrConfigComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(OcrConfigComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
