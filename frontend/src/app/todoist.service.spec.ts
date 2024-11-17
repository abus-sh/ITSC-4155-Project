import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';

import { TodoistService } from './todoist.service';
import { provideHttpClient } from '@angular/common/http';
import { IdType } from './todoist.service';

describe('TodoistService', () => {
    let service: TodoistService;
    let httpMock: HttpTestingController;

    beforeEach(() => {
        TestBed.configureTestingModule({
            imports: [HttpClientTestingModule],
            providers: [TodoistService]
        });
        service = TestBed.inject(TodoistService);
        httpMock = TestBed.inject(HttpTestingController);
    });

    afterEach(() => {
        httpMock.verify();
    });

    it('Creating TodoistService', () => {
        expect(service).toBeTruthy();
    });

    it('Send request to add an assignment', async () => {
        const mockAssignment = { name: 'Test Assignment', due_at: '2023-10-10', description: 'Test Description' };

        service.addAssignment(mockAssignment.name, mockAssignment.due_at, mockAssignment.description);

        const req = httpMock.expectOne(service['addAssignmentUrl']);
        expect(req.request.method).toBe('POST');
        expect(req.request.body).toEqual(mockAssignment);
        req.flush({});
    });

    it('Send request to update assignment description', async () => {
        const mockId = 1;
        const mockDescription = 'Updated Description';
        const mockIdType = IdType.Canvas;

        service.updateAssignmentDescription(mockId, mockIdType, mockDescription);

        const req = httpMock.expectOne(service['updateDescUrl'].replace('ID', mockId.toString()));
        expect(req.request.method).toBe('PATCH');
        expect(req.request.body).toEqual({ description: mockDescription, task_type: mockIdType });
        req.flush({});
    });
});
