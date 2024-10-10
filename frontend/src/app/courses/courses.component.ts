import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { OnInit } from '@angular/core';
import { getBackendURL } from '../../config';
import { CommonModule } from '@angular/common';


interface Course {
    id: number;
    name: string;
    image_download_url: string;
    computed_current_score: string;
}

@Component({
    selector: 'app-courses',
    standalone: true,
    imports: [CommonModule],
    templateUrl: './courses.component.html',
    styleUrls: ['./courses.component.scss']
})
export class CoursesComponent implements OnInit {
  private coursesUrl = getBackendURL() + '/api/v1/courses/all';
  public courses: Course[] = [];

    constructor(private http: HttpClient) {
        this.fetchCourses();
    }

    ngOnInit(): void {}

    fetchCourses(): void {
        this.http.get<any[]>(this.coursesUrl, { withCredentials: true }).subscribe(
            (data: any[]) => { 

                const transformedCourses: Course[] = data.map(course => {
                    const finalScore = (course.enrollments && course.enrollments.length) > 0 
                        ? course.enrollments[0].computed_current_score : null;
    
                    return {
                        id: course.id,
                        name: course.name,
                        image_download_url: course.image_download_url,
                        computed_current_score: finalScore
                    };
                });
    
                this.courses = transformedCourses;
            },
            (error) => {
                console.error('Error fetching courses:', error);
            }
        );
    }
}