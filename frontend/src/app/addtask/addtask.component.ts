import { Component, EventEmitter, Output } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { TodoistService } from '../todoist.service';
import { CanvasService } from '../canvas.service';
import { Assignment } from '../dashboard/dashboard.component';

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

    constructor(private fb: FormBuilder, private todoistService: TodoistService,
        private canvasService: CanvasService) {
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

    async addAssignment() {
        if (this.addTaskForm.valid) {
            // Clear any old error messages
            this.errorMsg = undefined;
            
            // Close the modal
            this.closeForm();

            // Add the assignment
            const name = this.addTaskForm.controls['name'].value;
            const description = this.addTaskForm.controls['description'].value;
            const due_at = this.addTaskForm.controls['due_at'].value;
            const db_id = await this.todoistService.addAssignment(name, due_at, description);
            const assignment: Assignment = {
                title: name,
                description: null,
                user_description: description,
                type: 'assignment',
                submission_types: [],
                db_id,
                graded_submissions_exist: false,
                due_at: this.getUserFormattedDueDate(due_at),
                subtasks: []
            }
            this.canvasService.addFakeAssignment(assignment);
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

        return `${year}-${month}-${day}T23:59`; // 'YYYY-MM-DDThh:mm'
    }

    closeForm() {
        this.closeFormAction.emit();
    }

    // Convert a date string into YYYY-MM-DD hh:mm:ss
    private getUserFormattedDueDate(dateStr: string) {
        const date = new Date(dateStr);
        
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const hour = String(date.getHours()).padStart(2, '0');
        const min = String(date.getMinutes()).padStart(2, '0');
        const sec = String(date.getSeconds()).padStart(2, '0');

        return `${year}-${month}-${day} ${hour}:${min}:${sec}`;
    }
}
