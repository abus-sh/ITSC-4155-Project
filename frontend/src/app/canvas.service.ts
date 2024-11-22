import { Injectable } from '@angular/core';
import { getBackendURL, getCanvasCacheTime } from '../config';
import { HttpClient, HttpParams } from '@angular/common/http';
import { APICourse, Course } from './courses/courses.component';
import { firstValueFrom, Subject } from 'rxjs';
import { AddSubtaskBody, Assignment, Subtask, SubtasksDict } from './dashboard/dashboard.component';
import { CalendarEvent } from './calendar/calendar.component';

interface AddSubtaskResponse {
    success: boolean,
    message?: string,
    id?: number,
    todoist_id?: string
    author?: boolean
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
    private dueSoonUrl = getBackendURL() + '/api/v1/user/due_soon';
    private calendarEventsUrl = getBackendURL() + '/api/v1/user/calendar_events';
    private getSubTasksUrl = getBackendURL() + '/api/v1/tasks/get_subtasks';
    private addSubTaskUrl = getBackendURL() + '/api/v1/tasks/add_subtask';
    private subTaskUrl = getBackendURL() + '/api/v1/tasks';
    private downloadSubmissionUrl = getBackendURL() + '/api/v1/courses/ID/submissions';
    private undatedAssignmentsUrl = getBackendURL() + '/api/v1/courses/ID/undated_assignments';
    private customDueDateUrl = getBackendURL() +
        '/api/v1/courses/CID/assignments/AID/custom_due_date';

    courses$ = new Subject<Course[]>();
    private courses: Course[] = [];
    private coursesLastUpdated = 0; // Unix timestamp

    dueAssignments$ = new Subject<Assignment[]>();
    private dueAssignments: Assignment[] = [];
    private dueAssignmentsLastUpdated = 0;

    undatedAssignments$ = new Subject<Assignment[]>();
    private undatedAssignments: Assignment[] = [];
    private undatedAssignmentsLastUpdated = 0;

    constructor(private http: HttpClient) {}

    async getCourses(): Promise<void> {
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


    async getUndatedAssignments() {
        // Only fetch new data if enough time has passwed
        const now = new Date().getTime();
        if ((now - this.undatedAssignmentsLastUpdated) > getCanvasCacheTime()) {
            this.undatedAssignments$.next(this.undatedAssignments);
            this.undatedAssignments = await this.fetchUndatedAssignments();
            this.undatedAssignmentsLastUpdated = now;
        }

        this.undatedAssignments$.next(this.undatedAssignments);
    }

    async fetchUndatedAssignments() {
        const assignments = await this.courses.map(async course => {
            return await firstValueFrom(this.http.get<Assignment[]>(
                this.undatedAssignmentsUrl.replace('ID', course.id.toString()),
                { withCredentials: true }
            ));
        }).reduce(async (assignsP, aP) => {
            const assigns = await assignsP;
            const a = await aP;

            return assigns.concat(a);
        });

        return assignments;
    }

    async setCustomDueDate(assignment: Assignment, due_date: string) {
        if (assignment.course_id === undefined || assignment.id === undefined) {
            return;
        }

        const url = this.customDueDateUrl
            .replace('CID', assignment.course_id.toString())
            .replace('AID', assignment.id.toString());
        const body = {
            due_date
        };
        await firstValueFrom(this.http.post(url, body, { withCredentials: true }));
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

    async addFakeAssignment(assignment: Assignment) {
        if (assignment.due_at) {
            this.dueAssignments.push(assignment);
            this.dueAssignments.sort(this.compareAssignments);

            this.dueAssignments$.next(this.dueAssignments);
        } else {
            this.undatedAssignments.push(assignment);
            this.undatedAssignments.sort(this.compareAssignments);

            this.undatedAssignments$.next(this.undatedAssignments);
        }
    }

    private compareAssignments(a1: Assignment, a2: Assignment) {
        // See if sorting by due date works. An assignment w/ a due date is always above one that
        // doesn't have one
        if (a1.due_at && a2.due_at) {
            if (a1.due_at > a2.due_at) {
                return 1;
            } else if (a1.due_at < a2.due_at) {
                return -1;
            }
        }
        if (a1.due_at && !a2.due_at) {
            return 1;
        }
        if (!a1.due_at && a2.due_at) {
            return -1;
        }

        // Sort by title otherwise
        if (a1.title > a2.title) {
            return 1;
        } else if (a1.title < a2.title) {
            return -1;
        }

        return 0;
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
            todoist_id: resp.todoist_id,
            author: resp.author
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
        for (const due_assign of this.dueAssignments) {
            // Check if the Canvas IDs match or if the native database IDs match
            // Don't allow matching on undefined IDs though
            if ((due_assign.id !== undefined && due_assign.id === assignment.id) ||
                (due_assign.db_id !== undefined && due_assign.db_id === assignment.db_id)) {
                
                due_assign.user_description = description;
                break;
            }
        }
    }

    async downloadSubmissions(course: Course) {
        try {
            const submissions = await firstValueFrom(
                this.http.get(this.downloadSubmissionUrl.replace('ID', course.id.toString()),
                {
                    withCredentials: true,
                    responseType: 'blob',
                    observe: 'response'
                },
            ));
            
            // Get the file name for this file
            // Default to submissions.zip
            let fileName = 'submissions.zip';

            // If the Content-Disposition header was set, try to use that for the name
            const contentHeader = submissions.headers.get('Content-Disposition');
            if (contentHeader) {
                // The format should be "inline; filename=filename.zip", so extract "filename.zip"
                const splitHeader = contentHeader.split('=');
                if (splitHeader.length == 2) {
                    fileName = contentHeader.split('=')[1].replaceAll('"', '');
                }
            }
            
            if (submissions.body) {
                this.downloadFile(submissions.body, fileName);
            } else {
                throw Error('No file provided by server.');
            }
        } catch (error) {
            console.log(error);
            return false;
        }

        return true;
    }

    // Based on https://stackoverflow.com/a/46882407
    private downloadFile(blob: Blob, fileName: string) {
        const url = window.URL.createObjectURL(blob);

        // Hidden anchor to trigger the download
        const a = document.createElement('a');
        a.setAttribute('style', 'display:none;');
        document.body.appendChild(a);

        // Set the info for the download and trigger it
        a.href = url;
        a.download = fileName;
        a.click();

        // Remove the anchor element since it isn't needed anymore
        a.remove();
    }
}
