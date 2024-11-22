import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SubmissiondownloadComponent } from './submissiondownload.component';
import { provideHttpClient } from '@angular/common/http';

describe('SubmissiondownloadComponent', () => {
    let component: SubmissiondownloadComponent;
    let fixture: ComponentFixture<SubmissiondownloadComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [SubmissiondownloadComponent],
            providers: [provideHttpClient()]
        })
        .compileComponents();

        fixture = TestBed.createComponent(SubmissiondownloadComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();

        component.courses = [
            {
                readableName: 'course1',
                course: {
                    id: 1,
                    name: 'course1',
                    image_download_url: null,
                    computed_current_score: null,
                    gradelog: [],
                }
            },
            {
                readableName: 'course2',
                course: {
                    id: 2,
                    name: 'course2',
                    image_download_url: null,
                    computed_current_score: null,
                    gradelog: [],
                }
            }
        ]
    });

    it('Create the component', () => {
        expect(component).toBeTruthy();
    });

    it('Initialize the form', () => {
        expect(component.courseForm.value).toEqual({
            classselect: ''
        });
    });

    it('Test the form submissions', () => {
        spyOn(component['canvasService'], 'downloadSubmissions').and.resolveTo(true);
        component.courseForm.setValue({
            classselect: component.courses[0].readableName
        });

        component.downloadSubmissions();

        expect(component['canvasService'].downloadSubmissions)
            .toHaveBeenCalledWith(component.courses[0].course);
    });
});
