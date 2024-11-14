import { Component, EventEmitter, Input, Output } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Assignment } from '../dashboard/dashboard.component';
import { CommonModule } from '@angular/common';

@Component({
    selector: 'app-tasknote',
    standalone: true,
    imports: [CommonModule, ReactiveFormsModule],
    templateUrl: './tasknote.component.html',
    styleUrl: './tasknote.component.scss'
})
export class TasknoteComponent {
    @Input() assignment?: Assignment;
    @Output() closeFormAction = new EventEmitter();

    noteForm: FormGroup;
    formError = false;

    constructor(private fb: FormBuilder) {
        this.noteForm = this.fb.group({
            note: ['', {
                validators: [
                    Validators.maxLength(1000)
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
    }

    updateNote() {
        // TODO: make this save the note
        // For now, just do nothing
        this.closeForm();
    }

    closeForm() {
        this.closeFormAction.emit();
    }
}
