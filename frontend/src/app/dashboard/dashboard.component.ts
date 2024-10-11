import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { getBackendURL } from '../../config';
import { HttpClient } from '@angular/common/http';
import { OrderByPipe } from '../pipes/date.pipe';



interface Assignment {
    title: string;
    description: string;
    type: string;
    submission_types: string[];
    html_url: string;
    context_name: string;
    id: string | number;
    points_possible: number;
    graded_submissions_exist: boolean;
    due_at: string;
}

@Component({
    selector: 'app-dashboard',
    standalone: true,
    imports: [CommonModule, OrderByPipe],
    templateUrl: './dashboard.component.html',
    styleUrl: './dashboard.component.scss',
})
export class DashboardComponent {
    private dueSoonUrl = getBackendURL() + '/api/v1/user/due_soon';
    assignments: Assignment[] = [];

    constructor(private http: HttpClient) { }

    ngOnInit() {
        this.dueSoonAssignments();
    }

    dueSoonAssignments(): void {
        this.http.get<Assignment[]>(this.dueSoonUrl, { withCredentials: true }).subscribe(
            (data: Assignment[]) => {
                this.assignments = data;
            },
            (error) => {
                console.error('Error fetching courses:', error);
            }
        );
    }

    getDueDateColor(dueDate: string): string {
        const daysDiff = this.dayDifference(dueDate)
    
        if (daysDiff <= 1) {
            return "#FF0000";  // Today or tomorrow is red
        } else if (daysDiff <= 3) {
            return "#DF6F00";  // 1 to 3 days is orange
        } else if (daysDiff <= 8) {
            return "#00B100";  // 4 to 7 days is green
        } else {
            return "#494A53";  // More than 7 days is gray
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
