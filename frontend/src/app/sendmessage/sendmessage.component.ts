import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Assignment } from '../dashboard/dashboard.component';



export interface Recipient {
    id: number;
    name: string;
}

@Component({
    selector: 'app-sendmessage',
    standalone: true,
    imports: [ReactiveFormsModule, CommonModule],
    templateUrl: './sendmessage.component.html',
    styleUrl: './sendmessage.component.scss'
})
export class SendmessageComponent implements OnInit {
    @Input() messageAssignment?: Assignment;
    @Output() closeFormAction = new EventEmitter();

    messageForm: FormGroup;
    recipientsList: Recipient[] = [
        { id: 1, name: 'John Doe' },
        { id: 2, name: 'Jane Smith' },
        { id: 3, name: 'Alice Johnson' },
    ];
    selectedRecipients: Recipient[] = [];
    recipientsIds: number[] = [];

    constructor(private fb: FormBuilder) {
        this.messageForm = this.fb.group({
            recipients: [this.recipientsIds, [Validators.required]],
            subject: ['', [Validators.required, Validators.maxLength(100)]],
            body: ['', [Validators.required, Validators.maxLength(1000)]],
        });
    }

    ngOnInit(): void {
        // Send request to get professor and TA's ids to send emails to
        if (this.messageAssignment !== null && this.messageAssignment !== undefined) {
            console.log('Getting professor for course:', this.messageAssignment.context_code);
        }
    }

    closeMessageForm() {
        this.closeFormAction.emit();
    }

    sendMessage() {
        console.log('Message sent to recipients:', this.selectedRecipients);
    }

    // Method to toggle recipient selection
    toggleRecipientSelection(event: any) {
        const selectedOptions = event.target.selectedOptions;
        const selectedValues = Array.from(selectedOptions).map((option: any) => parseInt(option.value, 10));
        console.log(selectedValues);

        selectedValues.forEach((recipientId) => {
            // Check if the recipient ID is already in the recipientsIds array
            if (!this.recipientsIds.includes(recipientId)) {
                this.recipientsIds.push(recipientId);

                // Add the recipient object to the selectedRecipients array
                const recipient = this.recipientsList.find(recipient => recipient.id === recipientId);
                if (recipient) {
                    this.selectedRecipients.push(recipient);
                }
            }
        });
        event.target.selectedIndex = -1;
    }

    // Remove recipient from selected list
    removeRecipient(id: number) {
        this.selectedRecipients = this.selectedRecipients.filter(recipient => recipient.id !== id);
        this.recipientsIds = this.recipientsIds.filter(recipientId => recipientId !== id);
    }
}

