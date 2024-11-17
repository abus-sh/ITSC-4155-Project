import { TestBed } from '@angular/core/testing';

import { CanvasService } from './canvas.service';
import { provideHttpClient } from '@angular/common/http';

describe('CanvasService', () => {
    let service: CanvasService;

    beforeEach(() => {
        TestBed.configureTestingModule({
            providers: [provideHttpClient()]
        });
        TestBed.configureTestingModule({});
        service = TestBed.inject(CanvasService);
    });

    it('should be created', () => {
        expect(service).toBeTruthy();
    });
});
