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
}
