import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable } from 'rxjs';
import { map, tap } from 'rxjs/operators';

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
    
    private backend = "http://localhost:5000";

    constructor(private http: HttpClient) {
        this.isLoggedIn().subscribe();
    }


    getCsrfToken(): Observable<any> {
        return this.http.get(`${this.backend}/auth/csrf-token`, { withCredentials: true });
    }

    login(username: string, password: string): Observable<any> {
        return this.http.post(`${this.backend}/auth/login`, { username, password }, { withCredentials: true }).pipe(
            tap(() => this.isLoggedIn())
        );
    }

    logout(): Observable<any> {
        return this.http.post(`${this.backend}/auth/logout`, {}, { withCredentials: true }).pipe(
            tap(() => this.authStatusSubject.next({ authenticated: false }))
        );
    }

    // checkAuthStatus(): void {
    //     console.log("Check being done!");
    //     this.http.get<AuthStatus>(`${this.backend}/auth/status`, { withCredentials: true }).subscribe(
    //         status => {
    //             this.authStatusSubject.next(status);
    //             console.log("Auth Status Updated:", status); // Check status
    //         },
    //         error => {
    //             this.authStatusSubject.next({ authenticated: false });
    //             console.error("Failed to check auth status:", error); // Log errors
    //         }
    //     );
    // }

    isLoggedIn(): Observable<boolean> {
        console.log("Sending request..");
        return this.http.get<AuthStatus>(`${this.backend}/auth/status`, { withCredentials: true }).pipe(
            map(response => {
                console.log("Request received!")
                this.authStatusSubject.next(response);
                return response.authenticated;
            })
        );
    }
}
