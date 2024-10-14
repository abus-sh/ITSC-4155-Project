import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable } from 'rxjs';
import { map, tap } from 'rxjs/operators';
import { Router } from '@angular/router';
import { getBackendURL } from '../config';

export interface AuthStatus {
    authenticated: boolean;
    user?: {
        id: number;
        username: string;
    };
    picture?: string;
}

interface CSRFResponse {
    csrf_token: string
}

interface AuthResponse {
    message: string,
    success: boolean
}

@Injectable({
    providedIn: 'root'
})
export class AuthService {
    // Default no picture image
    private noPicture = 'https://t4.ftcdn.net/jpg/05/49/98/39/360_F_549983970_bRCkYfk0P6PP5fKbMhZMIb07mCJ6esXL.jpg'

    private authStatusSubject = new BehaviorSubject<AuthStatus>({ authenticated: false, picture: this.noPicture });
    authStatus$ = this.authStatusSubject.asObservable();

    private backend = getBackendURL();

    constructor(private http: HttpClient, private router: Router) {
        console.log('Auth Service - Launched')
        this.isLoggedIn().subscribe(isAuthenticated => {
            if (isAuthenticated) {
                this.getUserInfo();
                this.syncTodoist();
            }
        });
    }

    // Request CSRF token from backend
    getCsrfToken() {
        console.log('Getting CSRF Token')
        return this.http.get<CSRFResponse>(`${this.backend}/api/auth/csrf-token`,
            { withCredentials: true });
    }

    // Login into the backend with username and password, return the user session
    // Does an extra login authentication with the session
    login(username: string, password: string): Observable<AuthResponse> {
        console.log('Logging in..')
        return this.http.post<AuthResponse>(`${this.backend}/api/auth/login`,
            { username, password }, { withCredentials: true }).pipe(
                tap(() => this.isLoggedIn())
            );
    }

    // Logout of the session, reset the sessio cookie and set authenticated to false
    logout(): Observable<AuthResponse> {
        console.log('Logging out..')
        return this.http.post<AuthResponse>(`${this.backend}/api/auth/logout`, {},
            { withCredentials: true }).pipe(
            tap(() => {
                this.authStatusSubject.next({ authenticated: false, picture: this.noPicture });
                this.router.navigate(['/login']);
            })
        );
    }

    // Check the if the user session is logged in
    isLoggedIn(): Observable<boolean> {
        console.log('Checking Authentication Status')
        return this.http.get<AuthStatus>(`${this.backend}/api/auth/status`, { withCredentials: true }).pipe(
            map(response => {
                this.authStatusSubject.next({
                    ...this.authStatusSubject.value,        // Spread existing values
                    authenticated: response.authenticated,  // Update authenticated
                    user: response.user,                    // Update user details
                });
                return response.authenticated;
            })
        );
    }

    // Sync assignments/tasks with Todoist
    syncTodoist() {
        console.log('Syncing tasks with Todoist');
        this.http.post(`${this.backend}/api/v1/tasks/update`, null).subscribe({
            next: (response) => {
                console.log(' * Tasks synced with Todoist', response);
            },
            error: (err) => {
                console.error(' * TODOIST: FAILED TO SYNC', err);
            }
        });
    }

    // Get user profile image to display in sidebar
    getUserInfo(): void {
        console.log('Get user profile image')
        this.http.get<{ canvas: { canvas_pic: string } }>(`${this.backend}/api/v1/user/profile`, { withCredentials: true }).pipe(
            tap((userProfile) => {
                const canvasPic = userProfile.canvas.canvas_pic;
                this.authStatusSubject.next({
                    ...this.authStatusSubject.value,
                    picture: canvasPic,
                })
            })
        ).subscribe();
    }
}
