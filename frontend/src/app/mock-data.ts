import { APIAssignment, APICourse, Course } from './courses/courses.component';
import { Assignment } from './dashboard/dashboard.component';
import { CalendarEvent } from './calendar/calendar.component';


export const mockCourses: APICourse[] = [
    {
        id: 223560,
        name: "202480-Fall 2024-ITIS-3300-092-Software Req & Project Mgmt",
        image_download_url: null,
        computed_current_score: 98.65,
        assignments: [],
        enrollments: [
            {
                computed_current_score: 98.65,
            }
        ]
    },
    {
        id: 228876,
        name: "202480-Fall 2024-ITIS-4221-091:ITIS-5221-091_Combined",
        image_download_url: "https://inst-fs-iad-prod.inscloudgate.net/files/76dccf8c-da95-4f26-a0cc-34100b7c20ca/10961506.png?download=1&token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpYXQiOjE3MzE2MDM3MjUsInVzZXJfaWQiOm51bGwsInJlc291cmNlIjoiL2ZpbGVzLzc2ZGNjZjhjLWRhOTUtNGYyNi1hMGNjLTM0MTAwYjdjMjBjYS8xMDk2MTUwNi5wbmciLCJqdGkiOiI3OWFmYjIyMC01NzUyLTQwNTAtOTRlZi1jMGM2Y2ZmOTc4ZWEiLCJob3N0IjpudWxsLCJleHAiOjE3MzIyMDg1MjV9.DWk2f40NHaMTNsMA8fNmLP3E414JCrlYbhRjESxmsLBbaPSPsiuQcBA2XJWplDlQYLvvahYuLh6a9ddR8DyijA",
        computed_current_score: null,
        assignments: [],
        enrollments: [
            {
                computed_current_score: null,
            }
        ]
    },
    {
        id: 222949,
        name: "202480-Fall 2024-ITSC-4155-001-Software Development Projects",
        image_download_url: null,
        computed_current_score: 99.96,
        assignments: [],
        enrollments: [
            {
                computed_current_score: 99.96,
            }
        ]
    }
];

export const mockCoursesProcessed: Course[] = [
    {
        id: 223560,
        name: "202480-Fall 2024-ITIS-3300-092-Software Req & Project Mgmt",
        image_download_url: null,
        computed_current_score: 98.65,
        assignments: []
    },
    {
        id: 228876,
        name: "202480-Fall 2024-ITIS-4221-091:ITIS-5221-091_Combined",
        image_download_url: "https://inst-fs-iad-prod.inscloudgate.net/files/76dccf8c-da95-4f26-a0cc-34100b7c20ca/10961506.png?download=1&token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpYXQiOjE3MzE2MDM3MjUsInVzZXJfaWQiOm51bGwsInJlc291cmNlIjoiL2ZpbGVzLzc2ZGNjZjhjLWRhOTUtNGYyNi1hMGNjLTM0MTAwYjdjMjBjYS8xMDk2MTUwNi5wbmciLCJqdGkiOiI3OWFmYjIyMC01NzUyLTQwNTAtOTRlZi1jMGM2Y2ZmOTc4ZWEiLCJob3N0IjpudWxsLCJleHAiOjE3MzIyMDg1MjV9.DWk2f40NHaMTNsMA8fNmLP3E414JCrlYbhRjESxmsLBbaPSPsiuQcBA2XJWplDlQYLvvahYuLh6a9ddR8DyijA",
        computed_current_score: null,
        assignments: []
    },
    {
        id: 222949,
        name: "202480-Fall 2024-ITSC-4155-001-Software Development Projects",
        image_download_url: null,
        computed_current_score: 99.96,
        assignments: []
    }
];

export const mockCoursesGradedAssignments: APIAssignment[] = [
    {
        assignment_id: "2179271",
        html_url: "https://uncc.instructure.com/courses/223560/assignments/2179271",
        name: "Roll Call Attendance",
        score: 100,
        points_possible: 100
    },
    {
        assignment_id: "2316220",
        html_url: "https://uncc.instructure.com/courses/223560/assignments/2316220",
        name: "Team Member List",
        score: 5,
        points_possible: 5
    },
    {
        assignment_id: "2338695",
        html_url: "https://uncc.instructure.com/courses/223560/assignments/2338695",
        name: "Midterm Exam",
        score: 95.5,
        points_possible: 104
    }
];

export const mockDueSoon: Assignment[] = [
    {
        "context_name": "202480-Fall 2024-ITIS-4221-091:ITIS-5221-091_Combined",
        "due_at": "2024-11-18 23:59:59",
        "description": "",
        "graded_submissions_exist": false,
        "html_url": "https://uncc.instructure.com/courses/228876/assignments/2243006",
        "id": 2243006,
        "points_possible": 100,
        "submission_types": "online_upload",
        "title": "Project 4: Program Analysis for Tunestore",
        "type": "assignment",
        "user_description": null,
        "user_submitted": false,
        "subtasks": []
    },
    {
        "context_name": "202480-Fall 2024-ITIS-3300-092-Software Req & Project Mgmt",
        "due_at": "2024-11-18 23:59:59",
        "description": "",
        "graded_submissions_exist": false,
        "html_url": "https://uncc.instructure.com/courses/223560/assignments/2322150",
        "id": 2322150,
        "points_possible": 10,
        "submission_types": "online_upload",
        "title": "1st Half-PowerPoint Submission (Team Deliverable 5)",
        "type": "assignment",
        "user_description": null,
        "user_submitted": false,
        "subtasks": []
    },
    {
        "context_name": "202480-Fall 2024-ITIS-3300-092-Software Req & Project Mgmt",
        "due_at": "2024-11-19 23:59:59",
        "description": "",
        "graded_submissions_exist": false,
        "html_url": "https://uncc.instructure.com/courses/223560/assignments/2322146",
        "id": 2322146,
        "points_possible": 100,
        "submission_types": "online_upload",
        "title": "Team Deliverable-4: Project Phase-II",
        "type": "assignment",
        "user_description": null,
        "user_submitted": false,
        "subtasks": []
    }
];

export const mockCalendarEvents: CalendarEvent[] = [
    {
        title: 'Event 1',
        description: 'Description 1',
        type: 'event',
        start_at: new Date(),
        end_at: new Date(),
        html_url: 'http://example.com/event1',
        context_name: 'Context 1',
        user_submitted: false

    },
    {
        title: 'Event 2',
        description: 'Description 2',
        type: 'event',
        start_at: new Date(),
        end_at: new Date(),
        html_url: 'http://example.com/event2',
        context_name: 'Context 2',
        user_submitted: false
    }
];