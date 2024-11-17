import { fakeAsync, flush, TestBed, tick } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { CanvasService } from './canvas.service';
import { getBackendURL } from '../config';
import { mockCourses, mockCoursesProcessed, mockCoursesGradedAssignments, mockDueSoon } from './mock-data';


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
    });

    afterEach(() => {
        httpMock.verify();
    });

    it('Creating the canvas service', () => {
        expect(service).toBeTruthy();
    });

    it('Fetch courses from backend and transform them', fakeAsync(() => {
        service.getCourses();

        const req = httpMock.expectOne(`${getBackendURL()}/api/v1/courses/all`);
        expect(req.request.method).toBe('GET');
        req.flush(mockCourses);
        flush();
        
        expect(service['courses']).toEqual(mockCoursesProcessed);
        expect(service['courses'].length).toEqual(3);
    }));

    it('Getting the graded assignments from the backend', fakeAsync(() => {
        service['courses'] = mockCoursesProcessed;
        expect(service['courses']).toEqual(mockCoursesProcessed);

        service.getGradedAssignments(); 

        service['courses'].forEach(() => {
            const req = httpMock.expectOne(`${getBackendURL()}/api/v1/courses/graded_assignments`);
            expect(req.request.method).toBe('POST');
            req.flush(mockCoursesGradedAssignments);
            tick();
        });

        service['courses'].forEach(course => {
            expect(course.assignments).toEqual(mockCoursesGradedAssignments);
        });
    }));

    it('Get assignments due soon', () => {
        expect(service['dueAssignments']).toEqual([]);
        service.getDueAssignments();

        const req = httpMock.expectOne(`${getBackendURL()}/api/v1/user/due_soon`);
        expect(req.request.method).toBe('GET');
        req.flush(mockDueSoon);
        flush();

        expect(service['dueAssignments']).toEqual(mockDueSoon);
    });

    // it('', () => {

    // });

});
