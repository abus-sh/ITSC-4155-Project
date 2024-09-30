import { Injectable } from '@angular/core';
import { CanActivate, ActivatedRouteSnapshot, RouterStateSnapshot, Router } from '@angular/router';
import { Observable } from 'rxjs';
import { AuthService } from './auth.service';

@Injectable({
    providedIn: 'root'
})
export class AuthGuard implements CanActivate {

    constructor(private authService: AuthService, private router: Router) { }

    canActivate(
        next: ActivatedRouteSnapshot,
        state: RouterStateSnapshot
    ): Observable<boolean> | Promise<boolean> | boolean {
        let isAuthenticated = false;

        // Subscribe to the authentication status
        this.authService.authStatus$.subscribe(status => {
            isAuthenticated = status.authenticated;
        });

        // Redirect based on authentication status
        if (!isAuthenticated) {
            this.router.navigate(['/login']); // Redirect to the login page if not authenticated
            return false; // Prevent access to the route
        }
        return true; // Allow access to the route if authenticated
    }
}
