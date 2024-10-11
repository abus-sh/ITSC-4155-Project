import { Injectable } from '@angular/core';
import { HttpRequest, HttpHandler, HttpEvent, HttpInterceptor } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable()
export class CsrfInterceptor implements HttpInterceptor {

    /* eslint-disable  @typescript-eslint/no-explicit-any */
    // Intercept method to modify HTTP requests to add the X-CSRFToken in header
    intercept(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
        const csrfToken = this.getCsrfTokenFromCookie();

        if (['POST', 'PUT', 'DELETE', 'PATCH'].includes(request.method) && csrfToken) {
            request = request.clone({
                headers: request.headers.set('X-CSRFToken', csrfToken),
                withCredentials: true // Keep the other credentials
            });
        }
        return next.handle(request);
    }

    // Function to retrieve the CSRF token from cookies
    getCsrfTokenFromCookie(): string | null {
        const name = 'XSRF-TOKEN=';
        const decodedCookie = decodeURIComponent(document.cookie);
        const ca = decodedCookie.split(';');
        for (let c of ca) {
            c = c.trim();
            if (c.indexOf(name) === 0) {
                return c.substring(name.length, c.length);
            }
        }
        return null;
    }
}