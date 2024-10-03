import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable } from 'rxjs';
import { map, tap } from 'rxjs/operators';
import { Router } from '@angular/router';


interface AuthStatus {
    authenticated: boolean;
    user?: {
        id: number;
        username: string;
    };
}

@Injectable({
    providedIn: 'root'
})
export class AuthService {
    private authStatusSubject = new BehaviorSubject<AuthStatus>({ authenticated: false });
    authStatus$ = this.authStatusSubject.asObservable();
    
    private backend = "http://localhost:5000"; // Backend for testing

    constructor(private http: HttpClient, private router: Router) {
        this.isLoggedIn().subscribe();
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
                this.authStatusSubject.next({ authenticated: false });
                this.router.navigate(['/login']);
            })
        );
    }

    // Check the if the user session is logged in
    isLoggedIn(): Observable<boolean> {
        console.log("Sending request..");
        return this.http.get<AuthStatus>(`${this.backend}/api/auth/status`, { withCredentials: true }).pipe(
            map(response => {
                console.log("Request received!")
                this.authStatusSubject.next(response);
                return response.authenticated;
            })
        );
    }
}
