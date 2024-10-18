import { Component, OnInit, Renderer2 } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { getBackendURL } from '../../config';
import { HttpClient } from '@angular/common/http';
import { OrderByPipe } from '../pipes/date.pipe';

interface Subtask {
    assignment_id: number;
    name: string;
    desc: string;
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
    private currentDropdown: HTMLElement | null = null;

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
            due_date: [''],
            status: ['0']
        });
    }

    ngOnInit() {
        this.dueSoonAssignments();
    }

    toggleSection(section: number) {
        if (section == 0) {
            this.sectionCollapseUpcoming = !this.sectionCollapseUpcoming;
        } else {
            this.sectionCollapseComplete = !this.sectionCollapseComplete;
        }
    }

    dueSoonAssignments(): void {
        this.http.get<Assignment[]>(this.dueSoonUrl, { withCredentials: true }).subscribe(
            (data: Assignment[]) => {
                this.assignments = data;

                const assignmentIds = this.getAssignmentIds(data);
                this.getSubTasks(assignmentIds);
            },
            (error) => {
                console.error('Error fetching courses:', error);
            }
        );
    }

    getSubTasks(assignmentIds: number[]) {
        const idsParam = assignmentIds.join(',');
        const idsUrl = `${this.dueSoonUrl}?ids=${idsParam}`;
    }

    getAssignmentIds(data: Assignment[]): number[] {
        return data
            .map((assignment: Assignment) => Number(assignment.id))
            .filter(id => !isNaN(id));
    }

    toggleDropdown(id: number, event: Event): void {
        const button = event.target as HTMLElement;
        const card = button.parentElement as HTMLElement;
        const dropdown = button.nextElementSibling as HTMLElement;

        if (this.currentDropdown) { // If there is a previous selected subtask dropdown
            this.renderer.removeClass(this.currentDropdown, 'show');
            this.renderer.removeClass(this.currentDropdown.parentElement, 'show-dropdown');
        }
        if (this.currentDropdown !== dropdown) { // If the selected dropdown is not the same as the previous
            this.renderer.addClass(dropdown, 'show');
            this.renderer.addClass(card, 'show-dropdown');
        }
        this.currentDropdown = dropdown; // Save dropdown selected
    }

    openForm(assignment: Assignment) {
        this.subtaskFormDisplay = true;
        this.subtaskAssignment = assignment;
    }

    closeForm() {
        this.subtaskFormDisplay = false;
        this.subtaskAssignment = null;
    }

    addSubtask(assignment: Assignment | null) {
        if (this.addSubtaskForm.valid && assignment != null) {
            console.log(assignment.id);

            const formData = {
                ...this.addSubtaskForm.value,
                name: this.addSubtaskForm.value.name || '',
                description: this.addSubtaskForm.value.description || '',
                due_date: this.addSubtaskForm.value.due_date || '',
                status: Number(this.addSubtaskForm.value.status) || 0,
                task_id: assignment.id
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
                due_date: '',
                status: 0
            });
            this.closeForm();
        }
    }


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
