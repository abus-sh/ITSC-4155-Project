import { Component, OnInit, Renderer2 } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { OrderByPipe } from '../pipes/date.pipe';
import { CanvasService } from '../canvas.service';
import { AddtaskComponent } from "../addtask/addtask.component";
import { TasknoteComponent } from '../tasknote/tasknote.component';
import { SendmessageComponent } from '../sendmessage/sendmessage.component';

import { AddfilterComponent } from '../addfilter/addfilter.component';
import { FilterService } from '../filter.service';
import { FilterPipe } from '../pipes/filter.pipe';
import { HttpClient } from '@angular/common/http';
import { getBackendURL } from '../../config';



interface NotificationBase {
    title: string;
    message?: string;
    type: string;
}

export interface InvitationNotification extends NotificationBase {
    type: 'invitation';
    invitation_id: number;
    author_name: string;
    subtask_name: string;
}

export interface SimpleNotification extends NotificationBase {
    type: 'simple';
    date: string;
    id?: number;
}

export interface Subtask {
    id: number;
    canvas_id: number;
    name: string;
    description: string;
    due_date: string;
    status: number;
    todoist_id?: string;
    author?: boolean;
}

export interface Assignment {
    title: string;
    description: string;
    user_description?: string | null;
    type: string;
    submission_types: string[] | string;
    html_url?: string;
    context_name?: string;
    context_code?: string;
    id?: number;
    db_id?: number;
    points_possible?: number;
    graded_submissions_exist: boolean;
    due_at: string;
    subtasks: Subtask[];
    user_submitted?: boolean;
}

export type SubtasksDict = Record<number, Subtask[]>;

export interface AddSubtaskBody {
    name: string,
    description: string,
    due_date: string,
    status: number,
    canvas_id: number,
    author?: boolean
}

@Component({
    selector: 'app-dashboard',
    standalone: true,
    imports: [CommonModule, ReactiveFormsModule, OrderByPipe, AddtaskComponent, TasknoteComponent,
        AddfilterComponent, FilterPipe, SendmessageComponent],
    templateUrl: './dashboard.component.html',
    styleUrl: './dashboard.component.scss',
})
export class DashboardComponent implements OnInit {
    private previousDropdown: HTMLElement | null = null;

    subtaskFormDisplay = false;
    subtaskAssignment: Assignment | null = null;
    addSubtaskForm: FormGroup;

    subtaskShareDisplay = false;
    subtaskShareAssignment: Subtask | null = null;

    shareSubtaskForm: FormGroup;

    private cantToggle = false;

    assignmentFormDisplay = false;

    noteFormDisplay = false;
    noteAssignment?: Assignment;

    sendMessageFormDisplay = false;
    sendMessageAssignment?: Assignment;

    filterFormDisplay = false;
    filters: string[] = [];

    sendInvitation = getBackendURL() + '/api/v1/user/send_invitation';
    notification_url = getBackendURL() + '/api/v1/user/get_notifications';
    respond_invitation = getBackendURL() + '/api/v1/user/invitation_response';
    notification_dismiss = getBackendURL() + '/api/v1/user/dismiss_notification';


    sectionCollapseUpcoming = false;
    sectionCollapseComplete = false;
    sectionCollapseNotifications = false;
    assignments: Assignment[] = [];
    notifications: { invitation: InvitationNotification[], simple: SimpleNotification[] } = { invitation: [], simple: [] };

    constructor(private fb: FormBuilder, private canvasService: CanvasService,
        private renderer: Renderer2, private filterService: FilterService,

        private http: HttpClient) {

        this.addSubtaskForm = this.fb.group({
            name: ['', Validators.required],
            description: [''],
            due_date: [this.getFormattedDueDate()],
            status: ['0']
        });

        this.shareSubtaskForm = this.fb.group({
            username: ['', Validators.required]
        });

        this.filterService.filters$.subscribe(filters => this.filters = filters);
        this.filterService.getFilters();
    }

    ngOnInit() {
        this.canvasService.dueAssignments$.subscribe(assignments => {
            this.assignments = assignments;
        });

        this.canvasService.getDueAssignments().then(() => {
            this.canvasService.getSubTasks(this.assignments);
        });
        this.fetchNotifications();
    }

    fetchNotifications() {
        this.http.get<{ invitation: InvitationNotification[], simple: SimpleNotification[] }>(this.notification_url, { withCredentials: true })
            .subscribe((data: { invitation: InvitationNotification[], simple: SimpleNotification[] }) => {
                this.notifications = data;
            });
    }


    /********************************************
    *
    *            REQUEST TO BACKEND
    *   
    *********************************************/

    // SEND POST REQUEST for creating a new Subtask
    addSubtask(assignment: Assignment | null) {
        if (this.addSubtaskForm.valid && assignment != null) {
            console.log(assignment.id);

            const formData: AddSubtaskBody = {
                ...this.addSubtaskForm.value,
                name: this.addSubtaskForm.value.name || '',
                description: this.addSubtaskForm.value.description || '',
                due_date: this.addSubtaskForm.value.due_date || '',
                status: Number(this.addSubtaskForm.value.status) || 0,
                canvas_id: assignment.id
            };

            this.canvasService.addSubtask(formData);

            this.addSubtaskForm.reset({
                name: '',
                description: '',
                due_date: this.getFormattedDueDate(),
                status: 0
            });
            this.closeForm();
        }
    }

    shareSubtask() {
        if (this.shareSubtaskForm.valid && this.subtaskShareAssignment) {
            const formData = {
                subtask_id: this.subtaskShareAssignment.id,
                username: this.shareSubtaskForm.value.username
            };

            this.http.post(this.sendInvitation, formData, { withCredentials: true })
                .subscribe(() => {
                    this.closeShareForm();
                    this.shareSubtaskForm.reset();
                });
        }
    }

    respondInvitation(notification: InvitationNotification, accept: boolean) {
        this.http.post(this.respond_invitation, { invitation_id: notification.invitation_id, accept: accept }, { withCredentials: true })
            .subscribe(() => {
                this.notifications.invitation = this.notifications.invitation.filter(n => n !== notification);
                this.canvasService.getSubTasks(this.assignments);
            });
    }

    dismissNotification(notification: SimpleNotification) {
        this.http.post(this.notification_dismiss, { notification_id: notification.id }, { withCredentials: true })
            .subscribe(() => {
                this.notifications.simple = this.notifications.simple.filter(n => n !== notification);
            });
    }


    /********************************************
    *
    *             VISUAL METHODS
    *   
    *********************************************/

    // Toggle for the sections: Upcoming and Completed Assignments
    toggleSection(section: number) {
        if (section == 0) {
            this.sectionCollapseUpcoming = !this.sectionCollapseUpcoming;
        } else if (section == 1) {
            this.sectionCollapseComplete = !this.sectionCollapseComplete;
        } else if (section == 2) {
            this.sectionCollapseNotifications = !this.sectionCollapseNotifications;
        }
    }

    // Toggle for the subtasks dropdown
    toggleDropdown(event: Event): void {
        const button = event.target as HTMLElement;
        const card = button.parentElement?.parentElement as HTMLElement;
        const dropdown = button.parentElement?.nextElementSibling as HTMLElement;

        // Hide the previously opened dropdown, if any
        if (this.previousDropdown && this.previousDropdown !== dropdown) {
            this.renderer.removeClass(this.previousDropdown, 'show');
            this.renderer.removeClass(this.previousDropdown.parentElement, 'show-dropdown');
        }

        // Toggle the clicked dropdown
        if (this.previousDropdown == dropdown) {
            this.renderer.removeClass(dropdown, 'show');
            this.renderer.removeClass(card, 'show-dropdown');
            this.previousDropdown = null;
        } else {
            this.renderer.addClass(dropdown, 'show');
            this.renderer.addClass(card, 'show-dropdown');
            this.previousDropdown = dropdown;
        }
    }

    // Toggle whether a subtask is completed
    async toggleSubtaskStatus(subtask: Subtask) {
        // If you send multiple toggle status rapidly to Todoist, 
        // they won't be processed in exact order, causing some to be ignored
        if (this.cantToggle) {
            return;
        }
        this.cantToggle = true;

        subtask.status = subtask.status ? 0 : 1;
        // Lie to the user and cause the visuals to update automatically
        const statusChanged = await this.canvasService.toggleSubtaskStatus(subtask);
        // If changing the status to todoist failed, turn the subtask.status back to before
        if (!statusChanged) {
            subtask.status = subtask.status ? 0 : 1;
        }

        setTimeout(() => this.cantToggle = false, 3000); // Unlock status toggle
    }

    /********************************************
    *
    *           OPEN CLOSE FORM
    *   
    *********************************************/


    /*      ADD SUBTASK FORM         */

    // Open the creation subtask form
    openForm(assignment: Assignment) {
        this.subtaskFormDisplay = true;
        this.subtaskAssignment = assignment;
    }

    // Closes the creation subtask form
    closeForm() {
        this.subtaskFormDisplay = false;
        this.subtaskAssignment = null;
    }

    /*      SHARE SUBTASK FORM      */

    openShareForm(subtask: Subtask) {
        this.subtaskShareDisplay = true;
        this.subtaskShareAssignment = subtask;
    }

    // Closes the creation subtask form
    closeShareForm() {
        this.subtaskShareDisplay = false;
        this.subtaskShareAssignment = null;
    }


    /*      ASSIGNMENT FORM         */

    openAssignmentForm() {
        this.assignmentFormDisplay = true;
    }

    closeAssignmentForm() {
        this.assignmentFormDisplay = false;
    }

    /*      NOTE FORM         */

    openNoteForm(assignment: Assignment, event: MouseEvent | KeyboardEvent) {
        if (event.target === null) {
            return;
        }

        // Find the closest div parent to this element
        // This allows us to determine if we are clicking a submenu that should not trigger the menu
        let element = event.target as HTMLElement;
        while (element.tagName !== "DIV") {
            if (element.parentElement === null) {
                return;
            }
            element = element.parentElement;
        }
        // If the div isn't the card itself (i.e., it is some submenu), do nothing
        if (!element.classList.contains("assignment-card") &&
            !element.classList.contains("title-holder")) {
            return;
        }

        this.noteAssignment = assignment;
        this.noteFormDisplay = true;
    }

    closeNoteForm() {
        this.noteFormDisplay = false;
    }

    /*      SEND MESSAGE FORM         */

    openSendMessageForm(assignment: Assignment) {
        if (assignment.id !== undefined) {
            this.sendMessageAssignment = assignment;
            this.sendMessageFormDisplay = true;
        }
    }

    closeSendMessageForm() {
        this.sendMessageFormDisplay = false;
    }


    /*      FILTER FORM         */

    openFilterForm() {
        this.filterFormDisplay = true;
    }

    closeFilterForm() {
        this.filterFormDisplay = false;
    }


    /********************************************
    *
    *             FORMATTERS
    *   
    *********************************************/


    // Get end of current day date
    getFormattedDueDate(): string {
        const now = new Date();

        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, '0'); // Ensure two digits for the month
        const day = String(now.getDate()).padStart(2, '0'); // Ensure two digits for the day

        return `${year}-${month}-${day}T23:59`; // 'YYYY-MM-DDTHH:MM'
    }

    // Get due date color depending on how far due date is from today
    getDueDateColor(dueDate: string): string {
        const daysDiff = this.dayDifference(dueDate)

        if (daysDiff <= 1) {
            return "#FF0000";  // Today or tomorrow is red
        } else if (daysDiff <= 3) {
            return "#DF6F00";  // 1 to 3 days is orange
        } else if (daysDiff <= 8) {
            return "#00B100";  // 4 to 8 days is green
        } else {
            return "#494A53";  // More than 8 days is gray
        }
    }

    // Get the day difference from today to due date
    dayDifference(dueDate: string): number {
        const today = new Date();
        const due = new Date(dueDate);
        today.setHours(0, 0, 0, 0);
        due.setHours(0, 0, 0, 0);

        const timeDifference = due.getTime() - today.getTime();
        // Convert the difference from milliseconds to days
        const daysDifference = timeDifference / (1000 * 3600 * 24);

        return Math.floor(daysDifference);
    }

    isAuthor(subtask: Subtask): boolean {
        return subtask.author === true;
    }
}
