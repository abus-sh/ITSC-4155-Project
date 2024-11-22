import { ComponentFixture, TestBed } from '@angular/core/testing';
import { CoursesComponent } from './courses.component';
import { provideHttpClient } from '@angular/common/http';
import { Subject } from 'rxjs';
import { CanvasService } from '../canvas.service';

describe('CoursesComponent', () => {
    let component: CoursesComponent;
    let fixture: ComponentFixture<CoursesComponent>;
    let canvasService: jasmine.SpyObj<CanvasService>;

    beforeEach(async () => {
        canvasService = jasmine.createSpyObj('CanvasService', ['getCourses', 'getGradedAssignments']);
        canvasService.courses$ = new Subject();

        await TestBed.configureTestingModule({
            imports: [CoursesComponent],
            providers: [
                provideHttpClient(),
                { provide: CanvasService, useValue: canvasService }
            ]
        }).compileComponents();


        fixture = TestBed.createComponent(CoursesComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('Creating the courses component', () => {
        expect(component).toBeTruthy();
    });
});
