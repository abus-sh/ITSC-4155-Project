import { Injectable } from '@angular/core';
import { CanActivate, ActivatedRouteSnapshot, RouterStateSnapshot, Router } from '@angular/router';
import { Observable, of } from 'rxjs';
import { AuthService } from './auth.service';
import { map, catchError } from 'rxjs/operators';

@Injectable({
    providedIn: 'root',
})
export class AuthGuard implements CanActivate {
    constructor(private loginService: AuthService, private router: Router) {}

    // Protect routes/pages that require login to access
    /* eslint-disable  @typescript-eslint/no-unused-vars */
    canActivate(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<boolean> {
        // Send a request to the server if the user is logged in
        return this.loginService.isLoggedIn().pipe(
            map(isLoggedIn => {
                if (isLoggedIn) {
                    return true; // Allow access
                } else {
                    this.router.navigate(['/login']); // Redirect to login
                    return false; // Deny access
                }
            }),
            // * No error should happen unless the backend can't respond to the request
            catchError(err => {
                console.error('Error checking login status:', err); // Log error for debugging
                this.router.navigate(['/login']); // Redirect to login on error
                return of(false); // Deny access
            })
        );
    }
}
