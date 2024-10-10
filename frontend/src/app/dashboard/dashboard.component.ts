import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { getBackendURL } from '../../config';
import { HttpClient } from '@angular/common/http';



interface Assignment {
    id: number;
    title: string;
    url: string;
}

@Component({
    selector: 'app-dashboard',
    standalone: true,
    imports: [CommonModule],
    templateUrl: './dashboard.component.html',
    styleUrl: './dashboard.component.scss'
})
export class DashboardComponent {
    private dueSoonUrl = getBackendURL() + '/api/v1/user/due_soon';
    courses: Assignment[] = [];

    constructor(private http: HttpClient) {}

    ngOnInit()
    {
        this.dueSoonAssignments();
    }

    dueSoonAssignments(): void {
        this.http.get<Assignment[]>(this.dueSoonUrl, { withCredentials: true }).subscribe(
            (data: Assignment[]) => {
                console.log(data)
                this.courses = data;
            },
            (error) => {
                console.error('Error fetching courses:', error);
            }
        );
    }
}
