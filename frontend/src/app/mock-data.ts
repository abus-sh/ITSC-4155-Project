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
        "id": 223560,
        "name": "202480-Fall 2024-ITIS-3300-092-Software Req & Project Mgmt",
        "image_download_url": null,
        "computed_current_score": 98.65,
        "assignments": []
    },
    {
        "id": 228876,
        "name": "202480-Fall 2024-ITIS-4221-091:ITIS-5221-091_Combined",
        "image_download_url": "https://inst-fs-iad-prod.inscloudgate.net/files/76dccf8c-da95-4f26-a0cc-34100b7c20ca/10961506.png?download=1&token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpYXQiOjE3MzE2MDM3MjUsInVzZXJfaWQiOm51bGwsInJlc291cmNlIjoiL2ZpbGVzLzc2ZGNjZjhjLWRhOTUtNGYyNi1hMGNjLTM0MTAwYjdjMjBjYS8xMDk2MTUwNi5wbmciLCJqdGkiOiI3OWFmYjIyMC01NzUyLTQwNTAtOTRlZi1jMGM2Y2ZmOTc4ZWEiLCJob3N0IjpudWxsLCJleHAiOjE3MzIyMDg1MjV9.DWk2f40NHaMTNsMA8fNmLP3E414JCrlYbhRjESxmsLBbaPSPsiuQcBA2XJWplDlQYLvvahYuLh6a9ddR8DyijA",
        "computed_current_score": null,
        "assignments": []
    },
    {
        "id": 222949,
        "name": "202480-Fall 2024-ITSC-4155-001-Software Development Projects",
        "image_download_url": null,
        "computed_current_score": 99.96,
        "assignments": []
    }
];

export const mockAssignments: APIAssignment[] = [
    // ...mock assignment data...
];

export const mockDueAssignments: Assignment[] = [
    // ...mock due assignment data...
];

export const mockCalendarEvents: CalendarEvent[] = [
    // ...mock calendar event data...
];

export const mockSubtaskResponse = {
    success: true,
    id: 1,
    todoist_id: '123'
};

export const mockToggleSubtaskResponse = {
    success: true
};