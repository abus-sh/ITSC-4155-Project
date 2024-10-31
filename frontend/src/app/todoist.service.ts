import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { getBackendURL } from '../config';
import { firstValueFrom } from 'rxjs';

@Injectable({
    providedIn: 'root'
})
export class TodoistService {
    private addAssignmentUrl = getBackendURL() + '/api/v1/tasks/add_task';

    constructor(private http: HttpClient) {}

    async addAssignment(name: string, due_at: string, description?: string) {
        const resp = await firstValueFrom(this.http.post(this.addAssignmentUrl, {
            name,
            due_at,
            description
        }, { withCredentials: true }));

        console.log(resp);
    }
}
