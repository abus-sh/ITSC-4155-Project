import { ComponentFixture, fakeAsync, TestBed, tick } from '@angular/core/testing';
import { AppComponent } from './app.component';
import { provideHttpClient } from '@angular/common/http';
import { AuthService } from './auth.service';
import { of } from 'rxjs';


describe('AppComponent', () => {
    let authServiceSpy: jasmine.SpyObj<AuthService>;
    let fixture: ComponentFixture<AppComponent>;
    let component: AppComponent;

    beforeEach(async () => {
        const authSpy = jasmine.createSpyObj('AuthService', ['getCsrfToken', 'logout', 'authStatus$']);

        await TestBed.configureTestingModule({
            imports: [AppComponent],
            providers: [
                provideHttpClient(),
                { provide: AuthService, useValue: authSpy },
            ]
        }).compileComponents();

        authServiceSpy = TestBed.inject(AuthService) as jasmine.SpyObj<AuthService>;
        authServiceSpy.authStatus$ = of({ authenticated: true });

        fixture = TestBed.createComponent(AppComponent);
        component = fixture.componentInstance;
    });

    it('Creating the app component', () => {
        expect(component).toBeTruthy();
    });

    it(`Component has the 'frontend' title`, () => {
        expect(component.title).toEqual('frontend');
    });

    it('Toggle sidebar', () => {
        const sidebar = document.createElement('div');
        sidebar.classList.add('sidebar');
        document.body.appendChild(sidebar);
        const mainContent = document.createElement('div');
        mainContent.classList.add('main-content');
        document.body.appendChild(mainContent);

        component.toggleSidebar();

        expect(sidebar.classList.contains('active')).toBeTrue();
        expect(mainContent.classList.contains('active')).toBeTrue();

        component.toggleSidebar();

        expect(sidebar.classList.contains('active')).toBeFalse();
        expect(mainContent.classList.contains('active')).toBeFalse();

        document.body.removeChild(sidebar);
        document.body.removeChild(mainContent);
    });

    it('Call logout method from AuthService', fakeAsync(() => {
        const logoutResponse = { message: '', success: true };
        authServiceSpy.logout.and.returnValue(of(logoutResponse));

        component.logout();
        tick();

        expect(authServiceSpy.logout).toHaveBeenCalled();
    }));

    it('Fetch CSRF token on init', () => {
        const csrfTokenResponse = { csrf_token: 'test-csrf-token' };
        authServiceSpy.getCsrfToken.and.returnValue(of(csrfTokenResponse));

        component.ngOnInit();

        expect(authServiceSpy.getCsrfToken).toHaveBeenCalled();
        expect(document.cookie).toContain('XSRF-TOKEN=test-csrf-token');
    });
});
