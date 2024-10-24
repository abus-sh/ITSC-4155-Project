import { Component, OnInit, Renderer2 } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { getBackendURL } from '../../config';
import { HttpClient } from '@angular/common/http';
import { OrderByPipe } from '../pipes/date.pipe';

interface Subtask {
    id: number,
    canvas_id: number;
    name: string;
    description: string;
    due_date: string;
    status: boolean;
}

interface Assignment {
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

@Component({
    selector: 'app-dashboard',
    standalone: true,
    imports: [CommonModule, ReactiveFormsModule, OrderByPipe],
    templateUrl: './dashboard.component.html',
    styleUrl: './dashboard.component.scss',
})
export class DashboardComponent implements OnInit {
    private dueSoonUrl = getBackendURL() + '/api/v1/user/due_soon';
    private subTasks = getBackendURL() + '/api/v1/tasks/get_subtasks';
    private previousDropdown: HTMLElement | null = null;

    subtaskFormDisplay = false;
    subtaskAssignment: Assignment | null = null;
    addSubtaskForm: FormGroup;

    sectionCollapseUpcoming = false;
    sectionCollapseComplete = false;
    assignments: Assignment[] = [];

    constructor(private fb: FormBuilder, private http: HttpClient, private renderer: Renderer2) {
        this.addSubtaskForm = this.fb.group({
            name: ['', Validators.required],
            description: [''],
            due_date: [this.getFormattedDueDate()],
            status: ['0']
        });
    }

    ngOnInit() {
        this.dueSoonAssignments();
    }


    /********************************************
    *
    *            REQUEST TO BACKEND
    *   
    *********************************************/

    // GET ASSIGNMENTS FOR DASHBOARD
    dueSoonAssignments(): void {
        this.http.get<Assignment[]>(this.dueSoonUrl, { withCredentials: true }).subscribe(
            (data: Assignment[]) => {
                this.assignments = data;
                this.getSubTasks(data);
            },
            (error) => {
                console.error('Error fetching courses:', error);
            }
        );
    }

    // GET SUBTASKS FOR ASSIGNMENTS IN DASHBOARD
    getSubTasks(data: Assignment[]) {
        const assignmentIds = data.map((assignment: Assignment) => Number(assignment.id)).filter(id => !isNaN(id))
        type SubtasksDict = { [canvas_id: number]: Subtask[] };

        this.http.post<SubtasksDict>(this.subTasks, { task_ids: assignmentIds }, { withCredentials: true }).subscribe(
            (subtasksDict: SubtasksDict) => {

                this.assignments = this.assignments.map(assignment => ({
                    ...assignment,
                    subtasks: subtasksDict[assignment.id] || []
                }));
            },
            (error) => {
                console.error('Error fetching subtasks:', error);
            }
        );
    }

    // SEND POST REQUEST for creating a new Subtask
    addSubtask(assignment: Assignment | null) {
        if (this.addSubtaskForm.valid && assignment != null) {
            console.log(assignment.id);

            const formData = {
                ...this.addSubtaskForm.value,
                name: this.addSubtaskForm.value.name || '',
                description: this.addSubtaskForm.value.description || '',
                due_date: this.addSubtaskForm.value.due_date || '',
                status: Number(this.addSubtaskForm.value.status) || 0,
                canvas_id: assignment.id
            };

            this.http.post(getBackendURL() + '/api/v1/tasks/add_subtask', formData, { withCredentials: true }).subscribe({
                next: (response) => {
                    console.log(" * Subtask added to Assignment: ", assignment.id)
                },
                error: (error) => {
                    console.error('Error:', error);
                }
            });

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
