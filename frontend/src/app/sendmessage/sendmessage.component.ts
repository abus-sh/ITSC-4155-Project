import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { FormBuilder, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { Assignment } from '../dashboard/dashboard.component';
import { HttpClient } from '@angular/common/http';
import { getBackendURL } from '../../config';


interface Recipient {
    id: number;
    name: string;
}

interface Message {
    id: number;
    author_id: number;
    body: string;
    created_at: string;
}

export interface Conversation {
    id: number;
    subject: string;
    participants: Recipient[];
    messages: Message[];
}

@Component({
    selector: 'app-sendmessage',
    standalone: true,
    imports: [ReactiveFormsModule, CommonModule, FormsModule ],
    templateUrl: './sendmessage.component.html',
    styleUrl: './sendmessage.component.scss'
})
export class SendmessageComponent implements OnInit {
    @Input() messageAssignment?: Assignment;
    @Output() closeFormAction = new EventEmitter();

    messageForm: FormGroup;
    recipientsList: Recipient[] = [];
    selectedRecipients: Recipient[] = [];
    recipientsIds: number[] = [];

    tabs: string[] = ['Send a Message'];
    activeTab = 0;
    conversations: Conversation[] = [];
    replyTexts: { [conversationId: number]: string } = {};

    isSendingMessage = false;
    isSendingReply: { [conversationId: number]: boolean } = {};

    constructor(private fb: FormBuilder, private http: HttpClient) {
        this.messageForm = this.fb.group({
            recipients: [this.recipientsIds, [Validators.minLength(1)]],
            subject: ['', [Validators.required]],
            body: ['', [Validators.required]],
        });
    }

    ngOnInit(): void {
        if (this.messageAssignment?.id) {
            const course_id = this.messageAssignment?.context_code?.split('_')[1] ?? '';
            const assignment_id = this.messageAssignment?.id;

            this.http.get<Recipient[]>(getBackendURL() + `/api/v1/courses/get_emails/${course_id}`, { withCredentials: true })
                .subscribe((data: Recipient[]) => {
                    this.recipientsList = data;
                    this.recipientsList.push({ id: 264631, name: 'Albert Olivi' });
                });

            this.http.get<Conversation[]>(getBackendURL() + `/api/v1/user/get_conversations/${assignment_id}`, { withCredentials: true })
                .subscribe((data: Conversation[]) => {
                    console.log(data);
                    this.conversations = data;
                    this.conversations.forEach(conversation => {
                        this.tabs.push(conversation.subject);
                        this.replyTexts[conversation.id] = '';
                    });
                });
        } else {
            this.closeMessageForm();
        }
    }

    switchTab(index: number) {
        this.activeTab = index;
    }

    sendMessage() {
        if (this.messageForm.valid && this.recipientsIds.length > 0) {
            const messageData = {
                recipients: this.messageForm.controls['recipients'].value,
                subject: this.messageForm.controls['subject'].value,
                body: this.messageForm.controls['body'].value,
                canvas_id: this.messageAssignment?.id,
            };
            this.isSendingMessage = true;
            
            this.http.post(getBackendURL() + '/api/v1/user/send_message', messageData, { withCredentials: true })
                .subscribe(() => {
                    this.isSendingMessage = false;
                    this.closeMessageForm();
                }, () => {
                    this.isSendingMessage = false;
                });
        }
    }

    sendReply(conversationId: number) {
        const replyBody = this.replyTexts[conversationId];
        if (replyBody.trim()) {
            this.isSendingReply[conversationId] = true;

            this.http.post(getBackendURL() + '/api/v1/user/reply_message', {
                body: replyBody,
                conversation_id: conversationId
            }, { withCredentials: true })
                .subscribe(() => {

                    this.isSendingReply[conversationId] = false;
                    // Clear the reply text
                    this.replyTexts[conversationId] = '';

                    // Find the conversation and add the new message at the top
                    const conversation = this.conversations.find(conv => conv.id === conversationId);
                    if (conversation) {
                        conversation.messages.unshift({
                            id: Date.now(), // Temporary ID, replace with actual ID if available
                            author_id: -1, // Replace with actual author ID
                            body: replyBody,
                            created_at: new Date().toISOString()
                        });
                    }
                }, () => {
                    this.isSendingReply[conversationId] = false;
                });
        }
    }

    getParticipantName(authorId: number, conversation: Conversation): string {
        if (authorId === -1) {
            return 'You';
        }
        const participant = conversation.participants.find((p: any) => p.id === authorId);
        return participant ? participant.name : 'Unknown';
    }

    closeMessageForm() {
        this.closeFormAction.emit();
    }

    // Method to toggle recipient selection
    toggleRecipientSelection(event: any) {
        const selectedOptions = event.target.selectedOptions;
        const selectedValues = Array.from(selectedOptions).map((option: any) => parseInt(option.value, 10));

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

