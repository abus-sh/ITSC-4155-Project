import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Assignment } from '../dashboard/dashboard.component';
import { CommonModule } from '@angular/common';
import { IdType, TodoistService } from '../todoist.service';
import { CanvasService } from '../canvas.service';

@Component({
    selector: 'app-tasknote',
    standalone: true,
    imports: [CommonModule, ReactiveFormsModule],
    templateUrl: './tasknote.component.html',
    styleUrl: './tasknote.component.scss'
})
export class TasknoteComponent implements OnInit {
    @Input() assignment?: Assignment;
    @Output() closeFormAction = new EventEmitter();

    noteForm: FormGroup;
    formError = false;
    charCount = 0;

    apiError = '';

    constructor(private fb: FormBuilder, private todoistService: TodoistService,
        private canvasService: CanvasService) {
        this.noteForm = this.fb.group({
            note: ['', {
                validators: [
                    Validators.maxLength(500)
                ]
            }]
        });

        this.noteForm.statusChanges.subscribe(status => {
            if (status === 'VALID') {
                this.formError = false;
            } else {
                this.formError = true;
            }
        });

        this.noteForm.valueChanges.subscribe(data => {
            this.charCount = data.note.length;
        });
    }

    ngOnInit(): void {
        if (this.assignment && this.assignment.user_description) {
            this.noteForm.patchValue({
                note: this.assignment.user_description
            });
        }
    }

    async updateNote() {
        if (!this.assignment || !this.noteForm.valid) {
            return;
        }

        // Don't do anything if the value hasn't changed
        if (!this.noteForm.controls['note'].dirty) {
            this.closeForm();
            return;
        }

        const desc = this.noteForm.controls['note'].value;
        let id = undefined;
        let id_type = undefined;

        if (this.assignment.db_id) {
            id = this.assignment.db_id;
            id_type = IdType.Native;
        } else if (this.assignment.id) {
            id = this.assignment.id;
            id_type = IdType.Canvas;
        } else {
            this.closeForm();
            return;
        }

        const assignment = this.assignment;
        const result = await this.todoistService.updateAssignmentDescription(id, id_type, desc);
        if (result) {
            this.apiError = '';
            this.canvasService.updateAssignmentDescription(assignment, desc);
            this.closeForm();
        } else {
            // Something went wrong, show an error message
            this.apiError = 'An API error has occurred. Please try again.';
        }
    }

    closeForm() {
        this.closeFormAction.emit();
    }
}
