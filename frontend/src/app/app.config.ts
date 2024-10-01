import { ApplicationConfig, provideZoneChangeDetection } from '@angular/core';
import { provideRouter } from '@angular/router';
import { routes } from './app.routes';
import { provideHttpClient, HTTP_INTERCEPTORS, withInterceptorsFromDi } from '@angular/common/http';
import { CsrfInterceptor } from './csrf.interceptor';

export const appConfig: ApplicationConfig = {
    providers: [
        provideHttpClient(withInterceptorsFromDi()),
        { 
            provide: HTTP_INTERCEPTORS, 
            useClass: CsrfInterceptor, 
            multi: true 
        },
        provideZoneChangeDetection({ eventCoalescing: true }),
        provideRouter(routes)
    ]
};
