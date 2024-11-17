import { fakeAsync, flush, TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { CanvasService } from './canvas.service';
import { getBackendURL } from '../config';
import { mockCourses, mockCoursesProcessed } from './mock-data';


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

});
