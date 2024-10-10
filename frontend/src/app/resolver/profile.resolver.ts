import { Injectable } from '@angular/core';
import { Resolve } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { getBackendURL } from '../../config';


@Injectable({
    providedIn: 'root'
})
export class ProfileResolver implements Resolve<any> {
    private profileUrl = getBackendURL() + '/api/v1/user/profile';

    constructor(private http: HttpClient) { }

    // Only start render the page after the profile info was received from the backend
    resolve(): Observable<any> {
        return this.http.get<any>(this.profileUrl, { withCredentials: true });
    }
}
