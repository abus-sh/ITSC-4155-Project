import { Injectable } from '@angular/core';
import { getBackendURL, getCanvasCacheTime } from '../config';
import { HttpClient, HttpParams } from '@angular/common/http';
import { APIAssignment, APICourse, Course } from './courses/courses.component';
import { firstValueFrom, Subject } from 'rxjs';
import { AddSubtaskBody, Assignment, Subtask, SubtasksDict } from './dashboard/dashboard.component';
import { CalendarEvent } from './calendar/calendar.component';

interface AddSubtaskResponse {
    success: boolean,
    message?: string,
    id?: number,
    todoist_id?: string
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
    private calendarEventsUrl = getBackendURL() + '/api/v1/user/calendar_events';
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
        let assignments = await firstValueFrom(this.http.get<Assignment[]>(this.dueSoonUrl,
            { withCredentials: true }));
        
        assignments = assignments.map(assignment => {
            if (assignment.subtasks === undefined) {
                return {
                    ...assignment,
                    subtasks: []
                };
            }
            return assignment;
        });

        return assignments;
    }

    // This may be better to not cache it, but I will leave it here if we change our mind
    async getCalendarEvents(start_date: string, end_date: string): Promise<CalendarEvent[]> {
        const params = new HttpParams().set('start_date', start_date).set('end_date', end_date);
    
        const events = await firstValueFrom(this.http.get<CalendarEvent[]>(this.calendarEventsUrl, {
            params: params,
            withCredentials: true
        }));
        
        return events;
    }

    async getSubTasks(assignments: Assignment[]|undefined = undefined) {
        if (assignments === undefined) {
            assignments = this.dueAssignments;
        }

        const assignmentIds = assignments.map(assignment => Number(assignment.id))
            .filter(id => !isNaN(id));
        
        if (assignmentIds.length !== 0) {
            const subtasks = await firstValueFrom(this.http.post<SubtasksDict>(this.getSubTasksUrl,
                { task_ids: assignmentIds }, { withCredentials: true }));
            
            this.dueAssignments = this.dueAssignments.map(assignment => {
                if (assignment.id) {
                    return {
                        ...assignment,
                        subtasks: subtasks[assignment.id]
                    };
                }
                return {
                    ...assignment,
                    subtasks: []
                };
            });
        }

        this.dueAssignments$.next(this.dueAssignments);
    }

    async addSubtask(subtaskData: AddSubtaskBody) {
        const resp = await firstValueFrom(this.http.post<AddSubtaskResponse>(this.addSubTaskUrl,
            subtaskData, { withCredentials: true }));
        console.log(resp);
        console.log(subtaskData);

        if (resp.id == undefined || resp.id == undefined) {
            return;
        }

        const subtask: Subtask = {
            canvas_id: subtaskData.canvas_id,
            name: subtaskData.name,
            description: subtaskData.description,
            status: subtaskData.status,
            due_date: subtaskData.due_date,
            id: resp.id,
            todoist_id: resp.todoist_id
        }

        this.dueAssignments.filter(assignment => {
            return assignment.id == subtaskData.canvas_id;
        }).forEach(assignment => {
            if (assignment.subtasks === undefined) {
                assignment.subtasks = [];
            }

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

        return true;
    }

    updateAssignmentDescription(assignment: Assignment, description: string) {
        for (let due_assign of this.dueAssignments) {
            // Check if the Canvas IDs match or if the native database IDs match
            // Don't allow matching on undefined IDs though
            if ((due_assign.id !== undefined && due_assign.id === assignment.id) ||
                (due_assign.db_id !== undefined && due_assign.db_id === assignment.db_id)) {
                
                due_assign.user_description = description;
                break;
            }
        }
    }
}
