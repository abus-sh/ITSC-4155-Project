import { Component, OnInit } from '@angular/core';
import { Course } from '../courses/courses.component';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { CanvasService } from '../canvas.service';
import { CommonModule } from '@angular/common';
import { OrderByPipe } from '../pipes/date.pipe';

interface ReadableCourse {
    course: Course,
    readableName: string
}

@Component({
    selector: 'app-submissiondownload',
    standalone: true,
    imports: [ReactiveFormsModule, CommonModule, OrderByPipe],
    templateUrl: './submissiondownload.component.html',
    styleUrl: './submissiondownload.component.scss'
})
export class SubmissiondownloadComponent implements OnInit {
    courses: ReadableCourse[] = [];
    courseForm: FormGroup;

    // Flag to determine if a ZIP download is pending
    fileDownloading = false;

    // Error message for file download
    errorMsg = '';

    constructor(private fb: FormBuilder, private canvasService: CanvasService) {
        this.courseForm = this.fb.group({
            classselect: ['', {
                validators: [
                    Validators.required
                ]
            }]
        });

        this.courseForm.valueChanges.subscribe(() => {
            this.errorMsg = '';
        })

        this.canvasService.courses$.subscribe(courses => {
            this.courses = courses.map(course => {
                return {
                    course: course,
                    readableName: this.parseCourseName(course.name)
                };
            });
        });
    }

    ngOnInit(): void {
        this.canvasService.getCourses();
    }

    async downloadSubmissions() {
        if (!this.courseForm.valid) {
            this.errorMsg = 'Please select a class to download submissions.';
            return;
        }

        // Convert the human-readable name back into a course
        const courseName = this.courseForm.controls['classselect'].value;
        const course = this.courses.filter(course => {
            return course.readableName === courseName;
        }).map(course => {
            return course.course;
        })[0];
        
        this.fileDownloading = true;
        
        if (await this.canvasService.downloadSubmissions(course)) {
            this.errorMsg = '';
        } else {
            this.errorMsg = 'An error occurred while downloading your submissions. Please try ' + 
                'again later.';
        }

        this.fileDownloading = false;
    }

    private parseCourseName(name: string) {
        const readableName = name
            .split('-').slice(2).join('-')  // Strip the semester information
            .replace('_Combined', '');      // Strip combined info

        return readableName;
    }
}
