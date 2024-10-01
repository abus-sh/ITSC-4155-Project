import { RouterOutlet } from '@angular/router';
import { RouterModule } from '@angular/router';
import { Component, OnInit } from '@angular/core';
import { AuthService } from './auth.service';
import { Observable } from 'rxjs';
import { CommonModule } from '@angular/common';
//import { HttpClientModule } from '@angular/common/http';


@Component({
    selector: 'app-root',
    standalone: true,
    imports: [CommonModule, RouterOutlet, RouterModule],
    templateUrl: './app.component.html',
    styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {
    title = 'frontend';             // Title of the application
    authStatus$: Observable<any>;   // Observable for tracking authentication status

    constructor(private authService: AuthService) {
        this.authStatus$ = this.authService.authStatus$;
    }

    ngOnInit() {
        // Fetch CSRF token on app load
        this.authService.getCsrfToken().subscribe({
            next: (response) => {
                // get CSRF token
                const csrfToken = response.csrf_token;
                // Set the CSRF token in the cookie, so that the interceptor 
                // can put it in the header for every request that requires it (CsrfInterceptor)
                document.cookie = `XSRF-TOKEN=${csrfToken}; path=/; SameSite=Strict;`;
            },
            error: (err) => {
                console.error('Failed to fetch CSRF token', err);
            }
        });
    }
    
    logout() {
        this.authService.logout().subscribe();
    }
}
