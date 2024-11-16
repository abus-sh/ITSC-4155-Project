import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AddtaskComponent } from './addtask.component';
import { provideHttpClient } from '@angular/common/http';

describe('AddtaskComponent', () => {
  let component: AddtaskComponent;
  let fixture: ComponentFixture<AddtaskComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AddtaskComponent],
      providers: [provideHttpClient()]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AddtaskComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('Creating the component', () => {
    expect(component).toBeTruthy();
  });

  it('Form is valid form when all fields are filled correctly', () => {
    component.addTaskForm.controls['name'].setValue('Test Task');
    component.addTaskForm.controls['description'].setValue('Test Description');
    component.addTaskForm.controls['due_at'].setValue('2023-12-31T23:59');
    expect(component.addTaskForm.valid).toBeTruthy();
  });

  it('Form is invalid form when name is missing', () => {
    component.addTaskForm.controls['name'].setValue('');
    component.addTaskForm.controls['description'].setValue('Test Description');
    component.addTaskForm.controls['due_at'].setValue('2023-12-31T23:59');
    expect(component.addTaskForm.invalid).toBeTruthy();
  });

  it('Form is invalid when due date is missing', () => {
    component.addTaskForm.controls['name'].setValue('Test Task');
    component.addTaskForm.controls['description'].setValue('Test Description');
    component.addTaskForm.controls['due_at'].setValue('');
    expect(component.addTaskForm.invalid).toBeTruthy();
  });
});
