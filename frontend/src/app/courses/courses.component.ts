import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { OnInit } from '@angular/core';
import { getBackendURL } from '../../config';


interface Course {
  id: number;
  name: string;
  course_image: string;
}

@Component({
  selector: 'app-courses',
  templateUrl: './courses.component.html',
  styleUrls: ['./courses.component.scss']
})
export class CoursesComponent implements OnInit {
  private coursesUrl = getBackendURL() + '/api/v1/courses/all';

  courses: Course[] = [];

  constructor(private http: HttpClient) {
  }

  ngOnInit(): void {
    this.fetchCourses();
  }

  fetchCourses(): void {
    this.http.get<Course[]>(this.coursesUrl, {withCredentials: true}).subscribe(
      (data: Course[]) => {
        this.courses = data;  
      },
      (error) => {
        console.error('Error fetching courses:', error);
      }
    );
  }
}