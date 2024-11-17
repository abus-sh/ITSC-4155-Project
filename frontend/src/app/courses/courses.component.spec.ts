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

        canvasService.getCourses.and.returnValue(Promise.resolve());
        canvasService.getGradedAssignments.and.returnValue(Promise.resolve());

        canvasService.courses$.next([
            {
                id: 1,
                name: 'Course 1',
                image_download_url: 'url1',
                computed_current_score: 90,
                assignments: [
                    {
                        assignment_id: '1',
                        html_url: 'http://example.com/assignment1',
                        name: 'Assignment 1',
                        score: 95,
                        points_possible: 100
                    }
                ],
                showAssignments: false
            }
        ]);
        fixture.detectChanges();
    });

    it('Creating the courses component', () => {
        expect(component).toBeTruthy();
    });

    it('Check component for mock course with mock graded assignment', () => {
        expect(component.courses.length).toBe(1);
        expect(component.courses[0].name).toBe('Course 1');
        expect(component.courses[0].assignments.length).toBe(1);
        expect(component.courses[0].assignments[0].name).toBe('Assignment 1');
    });

    it('Toggle course assignments visibility', () => {
        const course = component.courses[0];
        expect(course.showAssignments).toBeFalse();
        component.toggleAssignments(course);
        expect(course.showAssignments).toBeTrue();
        component.toggleAssignments(course);
        expect(course.showAssignments).toBeFalse();
    });
});
