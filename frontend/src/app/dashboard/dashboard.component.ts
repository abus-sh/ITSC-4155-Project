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

export interface Subtask {
    id: number;
    canvas_id: number;
    name: string;
    description: string;
    due_date: string;
    status: number;
    todoist_id?: string;
}

export interface Assignment {
    title: string;
    description: string | null;
    user_description: string | null;
    type: string;
    submission_types: string[] | string;
    html_url?: string;
    context_name?: string;
    context_code?: string;
    id?: number;
    db_id?: number;
    points_possible?: number;
    graded_submissions_exist: boolean;
    due_at?: string;
    subtasks: Subtask[];
    user_submitted?: boolean;
    course_id?: number;
}

export type SubtasksDict = Record<number, Subtask[]>;

export interface AddSubtaskBody {
    name: string,
    description: string,
    due_date: string,
    status: number,
    canvas_id: number
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
    private cantToggle = false;

    assignmentFormDisplay = false;

    noteFormDisplay = false;
    noteAssignment?: Assignment;

    sendMessageFormDisplay = false;
    sendMessageAssignment?: Assignment;

    filterFormDisplay = false;
    filters: string[] = [];

    sectionCollapseUpcoming = false;
    sectionCollapseComplete = false;
    assignments: Assignment[] = [];

    sectionCollapseUndated = false;
    undatedAssignments: Assignment[] = [];

    constructor(private fb: FormBuilder, private canvasService: CanvasService,
        private renderer: Renderer2, private filterService: FilterService) {
        
        this.addSubtaskForm = this.fb.group({
            name: ['', Validators.required],
            description: [''],
            due_date: [this.getFormattedDueDate()],
            status: ['0']
        });

        this.filterService.filters$.subscribe(filters => this.filters = filters);
        this.filterService.getFilters();
    }

    ngOnInit() {
        this.canvasService.dueAssignments$.subscribe(assignments => {
            this.assignments = assignments;
        });

        this.canvasService.undatedAssignments$.subscribe(assignments => {
            this.undatedAssignments = assignments;
        })

        this.canvasService.getDueAssignments().then(() => {
            this.canvasService.getSubTasks(this.assignments);
        });

        this.canvasService.getCourses().then(() => {
            this.canvasService.getUndatedAssignments();
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
            this.sectionCollapseUndated = !this.sectionCollapseUndated;
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

        setTimeout(() => this.cantToggle = false, 1000); // Unlock status toggle
    }

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

        let element = event.target as HTMLElement;

        // Exclude custom date input box
        if (element.tagName === "INPUT") {
            const input = element as HTMLInputElement;
            if (input.name === "due-date") {
                return;
            }
        }

        // Find the closest div parent to this element
        // This allows us to determine if we are clicking a submenu that should not trigger the menu
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


    openFilterForm() {
        this.filterFormDisplay = true;
    }

    closeFilterForm() {
        this.filterFormDisplay = false;
    }

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

    setCustomDueDate(assignment: Assignment, event: MouseEvent | KeyboardEvent) {
        if (event.target === null || !(event.target instanceof HTMLElement)) {
            return;
        }

        let element: HTMLElement | null = event.target as HTMLElement;
        while (element !== null && !element.classList.contains('assignment-card')) {
            element = element.parentElement;
        }
        if (element === null) {
            return;
        }
        const due_date = (element.children[1].children[1] as HTMLInputElement).value;
        this.canvasService.setCustomDueDate(assignment, due_date);
    }
}
