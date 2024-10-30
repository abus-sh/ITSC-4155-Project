import { Component, OnInit, Renderer2 } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { OrderByPipe } from '../pipes/date.pipe';
import { CanvasService } from '../canvas.service';

export interface Subtask {
    id: number,
    canvas_id: number;
    name: string;
    description: string;
    due_date: string;
    status: number;
}

export interface Assignment {
    title: string;
    description: string;
    type: string;
    submission_types: string[];
    html_url: string;
    context_name: string;
    id: number;
    points_possible: number;
    graded_submissions_exist: boolean;
    due_at: string;
    subtasks: Subtask[];
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
    imports: [CommonModule, ReactiveFormsModule, OrderByPipe],
    templateUrl: './dashboard.component.html',
    styleUrl: './dashboard.component.scss',
})
export class DashboardComponent implements OnInit {
    private previousDropdown: HTMLElement | null = null;

    subtaskFormDisplay = false;
    subtaskAssignment: Assignment | null = null;
    addSubtaskForm: FormGroup;

    sectionCollapseUpcoming = false;
    sectionCollapseComplete = false;
    assignments: Assignment[] = [];

    constructor(private fb: FormBuilder, private canvasService: CanvasService,
        private renderer: Renderer2) {
        
        this.addSubtaskForm = this.fb.group({
            name: ['', Validators.required],
            description: [''],
            due_date: [this.getFormattedDueDate()],
            status: ['0']
        });
    }

    ngOnInit() {
        this.canvasService.dueAssignments$.subscribe(assignments => {
            this.assignments = assignments;
        });

        this.canvasService.getDueAssignments().then(() => {
            this.canvasService.getSubTasks(this.assignments);
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
        } else {
            this.sectionCollapseComplete = !this.sectionCollapseComplete;
        }
    }

    // Toggle for the subtasks dropdown
    toggleDropdown(id: number, event: Event): void {
        const button = event.target as HTMLElement;
        const card = button.parentElement as HTMLElement;
        const dropdown = button.nextElementSibling as HTMLElement;
    
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
}
