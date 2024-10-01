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

    canActivate(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<boolean> {
        return this.loginService.isLoggedIn().pipe(
            map(isLoggedIn => {
                if (isLoggedIn) {
                    return true; // Allow access
                } else {
                    this.router.navigate(['/login']); // Redirect to login
                    return false; // Deny access
                }
            }),
            catchError(err => {
                console.error('Error checking login status:', err); // Log error for debugging
                this.router.navigate(['/login']); // Redirect to login on error
                return of(false); // Deny access
            })
        );
    }
}
