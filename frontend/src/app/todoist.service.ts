import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { getBackendURL } from '../config';
import { firstValueFrom } from 'rxjs';

export enum IdType {
    Canvas = 'canvas',
    Native = 'native'
}

@Injectable({
    providedIn: 'root'
})
export class TodoistService {
    private addAssignmentUrl = getBackendURL() + '/api/v1/tasks/add_task';
    private updateDescUrl = getBackendURL() + '/api/v1/tasks/ID/description';

    constructor(private http: HttpClient) {}

    async addAssignment(name: string, due_at: string, description?: string) {
        await firstValueFrom(this.http.post(this.addAssignmentUrl, {
            name,
            due_at,
            description
        }, { withCredentials: true }));
    }

    async updateAssignmentDescription(id: number, id_type: IdType, description: string) {
        try {
            const resp = await firstValueFrom(
                this.http.patch(this.updateDescUrl.replace('ID', id.toString()), {
                    'description': description,
                    'task_type': id_type
                },
                { withCredentials: true }
            ));
        } catch (error) {
            console.log(error);
            return false;
        }

        return true;
    }
}
