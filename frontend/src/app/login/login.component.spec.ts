import { ComponentFixture, fakeAsync, TestBed, tick } from '@angular/core/testing';
import { LoginComponent } from './login.component';
import { provideHttpClient } from '@angular/common/http';
import { RouterModule } from '@angular/router';
import { ReactiveFormsModule } from '@angular/forms';
import { AuthService } from '../auth.service';
import { of, throwError } from 'rxjs';


describe('LoginComponent', () => {
    let component: LoginComponent;
    let fixture: ComponentFixture<LoginComponent>;
    let authService: AuthService;

    beforeEach(async () => {

        await TestBed.configureTestingModule({
            imports: [LoginComponent, RouterModule.forRoot([]), ReactiveFormsModule],
            providers: [provideHttpClient(), AuthService]
        }).compileComponents();

        fixture = TestBed.createComponent(LoginComponent);
        component = fixture.componentInstance;
        authService = TestBed.inject(AuthService);
        fixture.detectChanges();
    });

    it('Creating the login component', () => {
        expect(component).toBeTruthy();
    });

    it('Create the form with username and password controls', () => {
        expect(component.loginForm.contains('username')).toBeTruthy();
        expect(component.loginForm.contains('password')).toBeTruthy();
    });

    it('Make the username and password controls required', () => {
        let usernameControl = component.loginForm.get('username');
        let passwordControl = component.loginForm.get('password');

        if (usernameControl && passwordControl) {
            usernameControl.setValue('');
            passwordControl.setValue('');

            expect(usernameControl.valid).toBeFalsy();
            expect(passwordControl.valid).toBeFalsy();
        }
    });

    it('Display error message on failed login', () => {
        spyOn(authService, 'login').and.returnValue(throwError({ error: { message: 'Login failed' } }));
        component.loginForm.setValue({ username: 'test', password: 'test' });
        component.onSubmit();

        expect(component.errorMessage).toBe('Login failed');
    });

    it('Navigate to dashboard on successful login', fakeAsync(() => {
        spyOn(authService, 'login').and.returnValue(of({ success: true, message: "Logged in" }));
        const goToDashboardSpy = spyOn(component, 'goToDashboard');
        component.loginForm.setValue({ username: 'test', password: 'test' });
        component.onSubmit();
        tick();

        expect(goToDashboardSpy).toHaveBeenCalled();
    }));
});
