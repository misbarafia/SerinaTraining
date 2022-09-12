import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ModalOnBoardComponent } from './modal-on-board.component';

describe('ModalOnBoardComponent', () => {
  let component: ModalOnBoardComponent;
  let fixture: ComponentFixture<ModalOnBoardComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ModalOnBoardComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ModalOnBoardComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
