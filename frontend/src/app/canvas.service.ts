import { Injectable, OnInit } from '@angular/core';
import { getBackendURL } from '../config';
import { HttpClient } from '@angular/common/http';
import { APIAssignment, APICourse, Course } from './courses/courses.component';
import { firstValueFrom, Subject } from 'rxjs';



@Injectable({
  providedIn: 'root'
})
export class CanvasService implements OnInit {
    courses$ = new Subject<Course[]>();

    private coursesUrl = getBackendURL() + '/api/v1/courses/all';
    private courseGradedAssignments = getBackendURL() + '/api/v1/courses/graded_assignments';

    private courses: Course[] = [];

    constructor(private http: HttpClient) {}

    ngOnInit(): void {
        console.log("CanvasService init");
    }

    async getCourses() {
        console.log("CanvasService fetchCourses");

        // Get the data from the backend, which fetches it from the Canvas API if not cached
        const data = await firstValueFrom(this.http.get<APICourse[]>(this.coursesUrl,
            { withCredentials: true}));
        
        console.log(data.length);

        const transformedCourses = data.map(course => {
            return {
                id: course.id,
                name: course.name,
                image_download_url: course.image_download_url,
                computed_current_score: course.enrollments[0].computed_current_score,
                assignments: []
            } as Course;
        });

        this.courses = transformedCourses;

        this.courses$.next(this.courses);
    }

    async getGradedAssignmentsForCourse(courseId: number) {
        // Try to find the course that is being referenced
        let courseIndex = -1;
        for (let i = 0; i < this.courses.length; i++) {
            if (this.courses[i].id == courseId) {
                courseIndex = i;
                break;
            }
        }

        // If the course wasn't found, do nothing
        if (courseIndex === -1) {
            return;
        }

        const body = { course_id: courseId };
        let assignments = await firstValueFrom(this.http
            .post<APIAssignment[]>(this.courseGradedAssignments, body,
            { withCredentials: true }));
        
        this.courses[courseIndex].assignments = assignments;

        this.courses$.next(this.courses);
    }

    async getGradedAssignments() {
        for (let course of this.courses) {
            const body = { course_id: course.id };
            let assignments = await firstValueFrom(this.http
                .post<APIAssignment[]>(this.courseGradedAssignments, body,
                { withCredentials: true }));

            course.assignments = assignments;
        }
        this.courses$.next(this.courses);
    }
}
