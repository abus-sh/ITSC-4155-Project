import { Injectable } from '@angular/core';
import { Resolve } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { getBackendURL } from '../../config';
import { UserProfile } from '../profile/profile.component';

// CURRENTLY NOT IN USE: may need to be used in the future

@Injectable({
    providedIn: 'root'
})
export class ProfileResolver implements Resolve<UserProfile> {
    private profileUrl = getBackendURL() + '/api/v1/user/profile';

    constructor(private http: HttpClient) { }

    // Only start render the page after the profile info was received from the backend
    resolve(): Observable<UserProfile> {
        return this.http.get<UserProfile>(this.profileUrl, { withCredentials: true });
    }
}
