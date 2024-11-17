import { fakeAsync, flush, TestBed, tick } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { CanvasService } from './canvas.service';
import { getBackendURL } from '../config';
import { mockCourses, mockCoursesProcessed, mockCoursesGradedAssignments, mockDueSoon, mockCalendarEvents } from './mock-data';


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

    it('Fetch courses from backend and transform them', fakeAsync(() => {
        const mock = mockCourses;
        const mockProcessed = mockCoursesProcessed;
        expect(service['courses']).toEqual([]);
        service.getCourses();

        const req = httpMock.expectOne(`${getBackendURL()}/api/v1/courses/all`);
        expect(req.request.method).toBe('GET');
        req.flush(mock);
        flush();
        
        expect(service['courses']).toEqual(mockProcessed);
    }));

    it('Getting the graded assignments from the backend', fakeAsync(() => {
        const mockProcessed = mockCoursesProcessed;
        const mockGraded = mockCoursesGradedAssignments;
        expect(service['courses']).toEqual([]);
        service['courses'] = mockProcessed;
        expect(service['courses']).toEqual(mockProcessed);

        service.getGradedAssignments(); 

        service['courses'].forEach(() => {
            const req = httpMock.expectOne(`${getBackendURL()}/api/v1/courses/graded_assignments`);
            expect(req.request.method).toBe('POST');
            req.flush(mockGraded);
            tick();
        });

        service['courses'].forEach(course => {
            expect(course.assignments).toEqual(mockGraded);
        });
    }));

    it('Get assignments due soon', fakeAsync(() => {
        expect(service['dueAssignments']).toEqual([]);
        service.getDueAssignments();

        const req = httpMock.expectOne(`${getBackendURL()}/api/v1/user/due_soon`);
        expect(req.request.method).toBe('GET');
        req.flush(mockDueSoon);
        flush();

        expect(service['dueAssignments']).toEqual(mockDueSoon);
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

});
