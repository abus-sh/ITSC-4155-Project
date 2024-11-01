import { Component, EventEmitter, Output } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { TodoistService } from '../todoist.service';

@Component({
    selector: 'app-addtask',
    standalone: true,
    imports: [ReactiveFormsModule],
    templateUrl: './addtask.component.html',
    styleUrl: './addtask.component.scss'
})
export class AddtaskComponent {
    @Output() closeFormAction = new EventEmitter();

    addTaskForm: FormGroup;

    errorMsg?: string = undefined;

    constructor(private fb: FormBuilder, private todoistService: TodoistService) {
        this.addTaskForm = this.fb.group({
            name: ['', {
                validators: [
                    Validators.required,
                    Validators.maxLength(100)
                ]
            }],
            description: ['', Validators.maxLength(500)],
            due_at: [this.getFormattedDueDate(), Validators.required]
        })
    }

    addAssignment() {
        if (this.addTaskForm.valid) {
            // Clear any old error messages
            this.errorMsg = undefined;
            
            // Close the modal
            this.closeForm();

            // Add the assignment
            const name = this.addTaskForm.controls['name'].value;
            const description = this.addTaskForm.controls['description'].value;
            const due_at = this.addTaskForm.controls['due_at'].value;
            this.todoistService.addAssignment(name, due_at, description);
        } else {
            // Set an appropriate error message based on what is invalid
            if (!this.addTaskForm.controls['name'].valid) {
                console.log(this.addTaskForm.controls['name'].value);
                this.errorMsg = 'Please provide an assignment name.';
            } else if (!this.addTaskForm.controls['due_at'].valid) {
                this.errorMsg = 'Please provide a valid due date.';
            } else {
                this.errorMsg = 'Please verify that all information is correct.';
            }
        }
    }

    // Get end of current day date
    getFormattedDueDate(): string {
        const now = new Date();

        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, '0'); // Ensure two digits for the month
        const day = String(now.getDate()).padStart(2, '0'); // Ensure two digits for the day

        return `${year}-${month}-${day}T23:59`; // 'YYYY-MM-DDTHH:MM'
    }

    closeForm() {
        this.closeFormAction.emit();
    }
}
