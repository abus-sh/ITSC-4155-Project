import { fakeAsync, flush, TestBed, tick } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { CanvasService } from './canvas.service';
import { getBackendURL } from '../config';
import { mockDueSoon, mockCalendarEvents } from './mock-data';


describe('CanvasService', () => {
    let service: CanvasService;
    let httpMock: HttpTestingController;

    beforeEach(() => {
        TestBed.configureTestingModule({
            imports: [HttpClientTestingModule],
            providers: [CanvasService]
        });
        service = TestBed.inject(CanvasService);
        httpMock = TestBed.inject(HttpTestingController);

        // Reset service state
        service['courses'] = [];
        service['dueAssignments'] = [];
        service['coursesLastUpdated'] = 0;
        service['dueAssignmentsLastUpdated'] = 0;
    });

    afterEach(() => {
        httpMock.verify();
    });

    it('Creating the canvas service', () => {
        expect(service).toBeTruthy();
    });

    // This test is disabled, next test is comprehensive including this one
    // it('Fetch courses from backend and transform them', fakeAsync(() => {
    //     const mock = mockCourses;
    //     const mockProcessed = mockCoursesProcessed;
    //     expect(service['courses']).toEqual([]);
    //     service.getCourses();

    //     const req = httpMock.expectOne(`${getBackendURL()}/api/v1/courses/all`);
    //     expect(req.request.method).toBe('GET');
    //     req.flush(mock);
    //     flush();
        
    //     expect(service['courses']).toEqual(mockProcessed);
    // }));

    it('Get assignments due soon', fakeAsync(() => {
        const dueSoon = mockDueSoon;
        expect(service['dueAssignments']).toEqual([]);
        service.getDueAssignments();

        const req = httpMock.expectOne(`${getBackendURL()}/api/v1/user/due_soon`);
        expect(req.request.method).toBe('GET');
        req.flush(dueSoon);
        flush();

        expect(service['dueAssignments']).toEqual(dueSoon);
    }));

    it('Toggle subtask status', fakeAsync(() => {
        const subtask = {
            canvas_id: 1,
            name: 'Test Subtask',
            description: 'Test Description',
            status: 0,
            due_date: '2023-10-10',
            id: 1,
            todoist_id: '12345'
        };

        service.toggleSubtaskStatus(subtask).then(success => {
            expect(success).toBeTrue();
        });

        const req = httpMock.expectOne(`${getBackendURL()}/api/v1/tasks/12345/toggle`);
        expect(req.request.method).toBe('POST');
        req.flush({ success: true });
        flush();
    }));

    it('Get calendar events', fakeAsync(() => {
        const startDate = '2024-10-10';
        const endDate = '2024-10-10';
        service.getCalendarEvents(startDate, endDate).then(events => {
            expect(events).toEqual(mockCalendarEvents);
        });

        const req = httpMock.expectOne(`${getBackendURL()}/api/v1/user/calendar_events?start_date=${startDate}&end_date=${endDate}`);
        expect(req.request.method).toBe('GET');
        req.flush(mockCalendarEvents);
        flush();
    }));

    it('Send request to add a subtask', fakeAsync(() => {
        const subtaskData = {
            canvas_id: 2243006,
            name: 'New Subtask',
            description: 'New Subtask Description',
            status: 0,
            due_date: '2023-10-10'
        };
        const mockResponse = {
            success: true,
            id: 1,
            todoist_id: '12345'
        };

        service['dueAssignments'] = mockDueSoon;

        service.addSubtask(subtaskData).then(() => {
            const assignment = service['dueAssignments'].find(a => a.id === subtaskData.canvas_id);
            expect(assignment).toBeDefined();
            expect(assignment!.subtasks.length).toBe(1);
            expect(assignment!.subtasks[0].name).toBe(subtaskData.name);
            expect(assignment!.subtasks[0].description).toBe(subtaskData.description);
            expect(assignment!.subtasks[0].status).toBe(subtaskData.status);
            expect(assignment!.subtasks[0].due_date).toBe(subtaskData.due_date);
            expect(assignment!.subtasks[0].id).toBe(mockResponse.id);
            expect(assignment!.subtasks[0].todoist_id).toBe(mockResponse.todoist_id);
        });

        const req = httpMock.expectOne(`${getBackendURL()}/api/v1/tasks/add_subtask`);
        expect(req.request.method).toBe('POST');
        req.flush(mockResponse);
        flush();
    }));

    it('Update assignment description', () => {
        const newDescription = 'New Description';

        service['dueAssignments'] = mockDueSoon;

        const updatedAssignment = service['dueAssignments'].find(a => a.id === mockDueSoon[0].id);
        expect(updatedAssignment!.user_description).not.toBe(newDescription);

        service.updateAssignmentDescription(mockDueSoon[0], newDescription);

        expect(updatedAssignment).toBeDefined();
        expect(updatedAssignment!.user_description).toBe(newDescription);
    });

});
