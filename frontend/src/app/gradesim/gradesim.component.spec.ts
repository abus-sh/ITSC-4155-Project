import { ComponentFixture, TestBed } from '@angular/core/testing';
import { GradesimComponent } from './gradesim.component';
import { CourseLog } from '../courses/courses.component';


describe('GradesimComponent', () => {
    let component: GradesimComponent;
    let fixture: ComponentFixture<GradesimComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [GradesimComponent]
        })
            .compileComponents();

        fixture = TestBed.createComponent(GradesimComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('Creating the Gradesim component', () => {
        expect(component).toBeTruthy();
    });

    it('Calculate final grade correctly', () => {
        const gradeScale: CourseLog[] = [
            {
                name: 'Category 1',
                weight: 0.5,
                assignments: [
                    { name: 'Assignment 1', score: 90, max_score: 100, omit_from_final_grade: false },
                    { name: 'Assignment 2', score: 80, max_score: 100, omit_from_final_grade: false }
                ]
            },
            {
                name: 'Category 2',
                weight: 0.5,
                assignments: [
                    { name: 'Assignment 3', score: 70, max_score: 100, omit_from_final_grade: false },
                    { name: 'Assignment 4', score: 60, max_score: 100, omit_from_final_grade: false }
                ]
            }
        ];
        const finalGrade = component.calculateFinalGrade(gradeScale);
        expect(finalGrade).toBeCloseTo(75, 1);
    });

    it('Update assignment score and recalculate final grade', () => {
        component.log_course = {
            id: 1,
            name: 'Course 1',
            image_download_url: 'http://example.com/image.png',
            computed_current_score: 0,
            gradelog: [
                {
                    name: 'Category 1',
                    weight: 1,
                    assignments: [
                        { name: 'Assignment 1', score: 50, max_score: 100, omit_from_final_grade: false }
                    ]
                }
            ]
        };
        if (component.log_course.gradelog === undefined) {
            return;
        }
        const assignment = component.log_course.gradelog[0].assignments[0];
        const event = { target: { value: '80' } } as unknown as Event;
        component.onScoreChange(assignment, event);
        expect(assignment.score).toBe(80);
        const finalGrade = component.calculateFinalGrade(component.log_course.gradelog);
        expect(finalGrade).toBeCloseTo(80, 1);
    });
});
