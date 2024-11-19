import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AddfilterComponent } from './addfilter.component';

describe('AddfilterComponent', () => {
  let component: AddfilterComponent;
  let fixture: ComponentFixture<AddfilterComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AddfilterComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AddfilterComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
