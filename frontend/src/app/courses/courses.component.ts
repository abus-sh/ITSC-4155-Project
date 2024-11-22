import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CanvasService } from '../canvas.service';
import { GradesimComponent } from '../gradesim/gradesim.component';
import { getBackendURL } from '../../config';
import { HttpClient } from '@angular/common/http';



export interface GradeAssignment {
    name: string;
    max_score: number;
    score: number;
    omit_from_final_grade: boolean;
}

export interface CourseLog {
    name: string;
    weight: number;
    assignments: GradeAssignment[];
}

export interface Course {
    id: number;
    name: string;
    image_download_url: string | null;
    computed_current_score: string | number | null;
    gradelog?: CourseLog[];
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
    imports: [CommonModule, GradesimComponent],
    templateUrl: './courses.component.html',
    styleUrls: ['./courses.component.scss']
})
export class CoursesComponent {
    public courses: Course[] = [];
    simulationFormDisplay = false;
    simulationCourse?: Course;

    constructor(private canvasService: CanvasService, private http: HttpClient) {
        this.canvasService.courses$.subscribe((courses) => {
            this.courses = courses;
        });

        this.initializeCourses();
    }

    async initializeCourses() {
        await this.canvasService.getCourses();
        for (const course of this.courses) {
            this.fetchGradeSimulation(course);
        }
    }

    private fetchGradeSimulation(course: Course) {
        this.http.get<CourseLog[]>(`${getBackendURL()}/api/v1/courses/get_grade_simulation/${course.id}`, {
            withCredentials: true
        }).subscribe({
            next: (gradeLog) => {
                course.gradelog = gradeLog;
            },
            error: (error) => {
                console.error(`Failed to fetch grade simulation for course ${course.id}`, error);
            }
        });
    }

    
    /*      GRADE SIMULATION FORM         */

    // Open the grade simulation form
    openSimulationForm(course: Course) {
        if (course.gradelog !== undefined) {
            this.simulationFormDisplay = true;
            this.simulationCourse = course;
        }
    }

    // Closes the grade simulation form
    closeSimulationForm() {
        this.simulationFormDisplay = false;
    }
}