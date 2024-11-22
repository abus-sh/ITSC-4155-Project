import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CanvasService } from '../canvas.service';
import { GradesimComponent } from '../gradesim/gradesim.component';
import { getBackendURL } from '../../config';



interface GradeAssignment {
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
    gradelog?: CourseLog;
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
    simulationGradelog?: CourseLog;

    constructor(private canvasService: CanvasService) {
        this.canvasService.courses$.subscribe((courses) => {
            this.courses = courses;
        });

        this.initializeCourses();
    }

    async initializeCourses() {
        await this.canvasService.getCourses();
        for (const course of this.courses) {
            try {
                const gradeLog = await this.fetchGradeSimulation(course.id);
                course.gradelog = gradeLog;
            } catch (error) {
                console.error(`Failed to fetch grade simulation for course ${course.id}`, error);
            }
        }
    }

    private async fetchGradeSimulation(courseId: number): Promise<CourseLog> {
        const response = await fetch(`${getBackendURL()}/api/v1/courses/get_grade_simulation/${courseId}`, {
            credentials: 'include'
        });
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    }

    
    /*      GRADE SIMULATION FORM         */

    // Open the grade simulation form
    openSimulationForm(gradeLog: CourseLog | undefined) {
        if (gradeLog !== undefined) {
            this.simulationFormDisplay = true;
            this.simulationGradelog = gradeLog;
        }
    }

    // Closes the grade simulation form
    closeSimulationForm() {
        this.simulationFormDisplay = false;
    }
}