import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable } from 'rxjs';
import { map, take, tap } from 'rxjs/operators';
import { Router } from '@angular/router';


interface AuthStatus {
    authenticated: boolean;
    user?: {
        id: number;
        username: string;
    };
    picture?: string;
}

@Injectable({
    providedIn: 'root'
})
export class AuthService {
    // Default no picture image
    private noPicture = 'https://t4.ftcdn.net/jpg/05/49/98/39/360_F_549983970_bRCkYfk0P6PP5fKbMhZMIb07mCJ6esXL.jpg'

    private authStatusSubject = new BehaviorSubject<AuthStatus>({ authenticated: false, picture: this.noPicture });
    authStatus$ = this.authStatusSubject.asObservable();

    private backend = "http://localhost:5000"; // Backend for testing

    constructor(private http: HttpClient, private router: Router) {
        this.isLoggedIn().subscribe()
        this.getUserInfo();
    }

    // Request CSRF token from backend
    getCsrfToken(): Observable<any> {
        return this.http.get(`${this.backend}/api/auth/csrf-token`, { withCredentials: true });
    }

    // Login into the backend with username and password, return the user session
    // Does an extra login authentication with the session
    login(username: string, password: string): Observable<any> {
        return this.http.post(`${this.backend}/api/auth/login`, { username, password }, { withCredentials: true }).pipe(
            tap(() => this.isLoggedIn())
        );
    }

    // Logout of the session, reset the sessio cookie and set authenticated to false
    logout(): Observable<any> {
        return this.http.post(`${this.backend}/api/auth/logout`, {}, { withCredentials: true }).pipe(
            tap(() => {
                this.authStatusSubject.next({ authenticated: false, picture: this.noPicture });
                this.router.navigate(['/login']);
            })
        );
    }

    // Check the if the user session is logged in
    isLoggedIn(): Observable<boolean> {
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

    getUserInfo(): void {
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
