import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { OnInit } from '@angular/core';
import { getBackendURL } from '../../config';
import { CommonModule } from '@angular/common';

interface Assignment {
    assignment_id: number;
    html_url: string;
    name: string;
    score: string;
}

interface Course {
    id: number;
    name: string;
    image_download_url: string;
    computed_current_score: string;
    assignments: Assignment[];
    showAssignments?: boolean;
}

@Component({
    selector: 'app-courses',
    standalone: true,
    imports: [CommonModule],
    templateUrl: './courses.component.html',
    styleUrls: ['./courses.component.scss']
})
export class CoursesComponent implements OnInit {
    private coursesUrl = getBackendURL() + '/api/v1/courses/all';
    private courseGradedAssignments = getBackendURL() + '/api/v1/courses/graded_assignments';
    public courses: Course[] = [];

    constructor(private http: HttpClient) {
        this.fetchCourses();
    }

    ngOnInit(): void { }

    fetchCourses(): void {
        this.http.get<any[]>(this.coursesUrl, { withCredentials: true }).subscribe(
            (data: any[]) => {

                const transformedCourses: Course[] = data.map(course => {
                    const finalScore = (course.enrollments && course.enrollments.length) > 0
                        ? course.enrollments[0].computed_current_score : 'N/A';

                    return {
                        id: course.id,
                        name: course.name,
                        image_download_url: course.image_download_url,
                        computed_current_score: finalScore,
                        assignments: []
                    };
                });

                this.courses = transformedCourses;

                // Fetch data for each course by sending course.id in the request body
                transformedCourses.forEach(course => {
                    this.getGradedAssignments(course.id).subscribe(assignments => {
                        console.log(assignments)
                        // Assuming assignments contains assignment_id, name, and score 
                        course.assignments = assignments.map((assignment: any) => ({
                            assignment_id: assignment.assignment_id,
                            html_url: assignment.html_url,
                            name: assignment.name, 
                            score: this.calculatePercentage(assignment.score, assignment.points_possible)
                        }));
                    }, (error) => {
                        console.error('Error fetching graded assignments:', error);
                    });
                });
            },
            (error) => {
                console.error('Error fetching courses:', error);
            }
        );
    }

    getGradedAssignments(courseId: number)  {
        const body = { course_id: courseId };
        return this.http.post<any>(this.courseGradedAssignments, body, { withCredentials: true });
    }

    calculatePercentage(score: number, pointsPossible: number): string {
        if (score != null && pointsPossible != null) {
            const percentage = (score / pointsPossible) * 100;
            const gradeTwoDecimals = Math.round(percentage * 100) / 100;
    
            // Check if the percentage is a whole number or has one decimal
            if (gradeTwoDecimals % 1 === 0) {
                return `${gradeTwoDecimals.toFixed(0)}%`;  // No decimal places
            } else if (gradeTwoDecimals * 10 % 1 === 0) {
                return `${gradeTwoDecimals.toFixed(1)}%`;  // 1 decimal place
            } else {
                return `${gradeTwoDecimals.toFixed(2)}%`;  // 2 decimal places
            }
        }
        return 'N/A';
    }

    toggleAssignments(course: Course): void {
        course.showAssignments = !course.showAssignments;
    }
}