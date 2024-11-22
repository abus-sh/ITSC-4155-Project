import { fakeAsync, TestBed } from '@angular/core/testing';

import { FilterService } from './filter.service';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';

describe('FilterService', () => {
    let service: FilterService;
    let httpTesting: HttpTestingController;

    const mockFilters = [
        'abc',
        '123',
        'testing'
    ];

    beforeEach(() => {
        TestBed.configureTestingModule({
            providers: [provideHttpClient(), provideHttpClientTesting()]
        });
        service = TestBed.inject(FilterService);
        httpTesting = TestBed.inject(HttpTestingController);
    });

    afterEach(() => {
        httpTesting.verify();
    });

    it('Creating the service', () => {
        expect(service).toBeTruthy();
    });

    it('Test getting filters', fakeAsync(async () => {
        // Make sure the subject sends the right values
        service.filters$.subscribe(filters => {
            expect(filters).toEqual(mockFilters);
        });

        // Start the HTTP request
        const filterPromise = service.getFilters();

        // Mock a response
        const req = httpTesting.expectOne('http://localhost:9876/api/v1/filters');
        expect(req.request.method).toBe('GET');
        req.flush({
            filters: mockFilters
        });

        // Confirm that it completed successfully
        expect(await filterPromise).toEqual(true);
    }));

    it('Test creating filters', fakeAsync(async () => {
        // Set up test data
        service['filters'] = mockFilters.slice();

        // Make sure the subject sends the right values
        service.filters$.subscribe(filters => {
            expect(filters).toEqual(mockFilters.concat('hello'));
        });

        const filterPromise = service.addFilter('hello');

        const req = httpTesting.expectOne('http://localhost:9876/api/v1/filters/new');
        expect(req.request.method).toBe('POST');
        req.flush({
            'success': true,
            'message': 'Created filter.'
        });

        expect(await filterPromise).toEqual(true);
    }));

    it('Test deleting filters', fakeAsync(async () => {
        // Set up test data
        service['filters'] = mockFilters.slice();

        // Make sure the subject sends the right values
        service.filters$.subscribe(filters => {
            expect(filters).toEqual(mockFilters.filter(value => value !== 'testing'));
        });

        const filterPromise = service.deleteFilter('testing');

        const req = httpTesting.expectOne('http://localhost:9876/api/v1/filters');
        expect(req.request.method).toBe('DELETE');
        req.flush({
            'success': true,
            'message': 'Created filter.'
        });

        expect(await filterPromise).toEqual(true);
    }));
});
