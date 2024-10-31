import { Injectable } from '@angular/core';
import { getBackendURL, getCanvasCacheTime } from '../config';
import { HttpClient } from '@angular/common/http';
import { APIAssignment, APICourse, Course } from './courses/courses.component';
import { firstValueFrom, Subject } from 'rxjs';
import { AddSubtaskBody, Assignment, Subtask, SubtasksDict } from './dashboard/dashboard.component';


interface AddSubtaskResponse {
    success: boolean,
    message?: string,
    id?: number
}

interface ToggleSubtaskResponse {
    success: boolean,
    message: string
}

@Injectable({
  providedIn: 'root'
})
export class CanvasService {
    private coursesUrl = getBackendURL() + '/api/v1/courses/all';
    private courseGradedAssignmentsUrl = getBackendURL() + '/api/v1/courses/graded_assignments';
    private dueSoonUrl = getBackendURL() + '/api/v1/user/due_soon';
    private getSubTasksUrl = getBackendURL() + '/api/v1/tasks/get_subtasks';
    private addSubTaskUrl = getBackendURL() + '/api/v1/tasks/add_subtask';
    private subTaskUrl = getBackendURL() + '/api/v1/tasks';

    courses$ = new Subject<Course[]>();
    private courses: Course[] = [];
    private coursesLastUpdated = 0; // Unix timestamp

    dueAssignments$ = new Subject<Assignment[]>();
    private dueAssignments: Assignment[] = [];
    private dueAssignmentsLastUpdated = 0;

    constructor(private http: HttpClient) {}

    async getCourses() {
        // Only fetch new courses if enough time has passed
        const now = new Date().getTime();
        if ((now - this.coursesLastUpdated) > getCanvasCacheTime()) {
            // Send immediate update now w/ potentially old courses
            this.courses$.next(this.courses);

            // Get new courses
            this.courses = await this.fetchCourses();

            this.coursesLastUpdated = now;
        }

        // Send most recently received courses
        this.courses$.next(this.courses);
    }

    private async fetchCourses(): Promise<Course[]> {
        // Get the data from the backend, which fetches it from the Canvas API if not cached
        const data = await firstValueFrom(this.http.get<APICourse[]>(this.coursesUrl,
            { withCredentials: true}));

        const transformedCourses = data.map(course => {
            return {
                id: course.id,
                name: course.name,
                image_download_url: course.image_download_url,
                computed_current_score: course.enrollments[0].computed_current_score,
                assignments: []
            } as Course;
        });

        return transformedCourses;
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
        const assignments = await firstValueFrom(this.http
            .post<APIAssignment[]>(this.courseGradedAssignmentsUrl, body,
            { withCredentials: true }));
        
        this.courses[courseIndex].assignments = assignments;

        this.courses$.next(this.courses);
    }

    async getGradedAssignments() {
        for (const course of this.courses) {
            const body = { course_id: course.id };
            const assignments = await firstValueFrom(this.http
                .post<APIAssignment[]>(this.courseGradedAssignmentsUrl, body,
                { withCredentials: true }));

            course.assignments = assignments;
        }
        this.courses$.next(this.courses);
    }

    async getDueAssignments() {
        const now = new Date().getTime();
        if ((now - this.dueAssignmentsLastUpdated) > getCanvasCacheTime()) {
            // Send immediate update now w/ potentially old assignments
            this.courses$.next(this.courses);

            // Get new courses
            this.dueAssignments = await this.fetchDueAssignments();

            this.dueAssignmentsLastUpdated = now;
        }

        // Send most recently received assignments
        this.dueAssignments$.next(this.dueAssignments);
    }

    private async fetchDueAssignments(): Promise<Assignment[]> {
        const assignments = await firstValueFrom(this.http.get<Assignment[]>(this.dueSoonUrl,
            { withCredentials: true }));
        
        return assignments;
    }

    async getSubTasks(assignments: Assignment[]|undefined = undefined) {
        if (assignments === undefined) {
            assignments = this.dueAssignments;
        }

        const assignmentIds = assignments.map(assignment => Number(assignment.id))
            .filter(id => !isNaN(id));
        
        const subtasks = await firstValueFrom(this.http.post<SubtasksDict>(this.getSubTasksUrl,
            { task_ids: assignmentIds }, { withCredentials: true }));
        
        this.dueAssignments = this.dueAssignments.map(assignment => ({
            ...assignment,
            subtasks: subtasks[assignment.id] || []
        }));

        this.dueAssignments$.next(this.dueAssignments);
    }

    async addSubtask(subtaskData: AddSubtaskBody) {
        const resp = await firstValueFrom(this.http.post<AddSubtaskResponse>(this.addSubTaskUrl,
            subtaskData, { withCredentials: true }));
        console.log(resp);
        console.log(subtaskData);

        if (resp.id == undefined) {
            return;
        }

        const subtask: Subtask = {
            canvas_id: subtaskData.canvas_id,
            name: subtaskData.name,
            description: subtaskData.description,
            status: subtaskData.status,
            due_date: subtaskData.due_date,
            id: resp.id
        }

        this.dueAssignments.filter(assignment => {
            return assignment.id == subtaskData.canvas_id;
        }).forEach(assignment => {
            assignment.subtasks.push(subtask);
        });
        this.dueAssignments$.next(this.dueAssignments);
    }

    async toggleSubtaskStatus(subtask: Subtask) {
        const resp = await firstValueFrom(this.http.post<ToggleSubtaskResponse>(this.subTaskUrl +
            `/${subtask.todoist_id}/toggle`, {}, { withCredentials: true }));
        
        // Return true or false to check that the status was successfully changed on todoist
        if (!resp.success) {
            return false;
        }

        let target = this.dueAssignments.filter(assignment => assignment.subtasks.includes(subtask));
        console.log(target);
        return true;
    }
}
