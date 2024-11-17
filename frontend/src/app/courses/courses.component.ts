import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CanvasService } from '../canvas.service';

interface Assignment {
    assignment_id: string;
    html_url: string;
    name: string;
    score: string | number;
    points_possible?: number;
}

export interface Course {
    id: number;
    name: string;
    image_download_url: string | null;
    computed_current_score: string | number | null;
    assignments: Assignment[];
    showAssignments?: boolean;
}

interface Enrollment {
    computed_current_score: string | number | null;
}

export interface APICourse extends Course {
    enrollments: Enrollment[];
}

export interface APIAssignment {
    assignment_id: string;
    html_url: string;
    name: string;
    score: number;
    points_possible: number;
}

@Component({
    selector: 'app-courses',
    standalone: true,
    imports: [CommonModule],
    templateUrl: './courses.component.html',
    styleUrls: ['./courses.component.scss']
})
export class CoursesComponent {
    public courses: Course[] = [];

    constructor(private canvasService: CanvasService) {
        this.canvasService.courses$.subscribe((courses) => {
            this.courses = courses;
        });

        this.initializeCourses();
    }

    async initializeCourses() {
        await this.canvasService.getCourses();
        await this.canvasService.getGradedAssignments();
    }

    toggleAssignments(course: Course): void {
        course.showAssignments = !course.showAssignments;
    }
}