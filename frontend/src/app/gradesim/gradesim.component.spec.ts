import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GradesimComponent } from './gradesim.component';

describe('GradesimComponent', () => {
  let component: GradesimComponent;
  let fixture: ComponentFixture<GradesimComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [GradesimComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(GradesimComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
