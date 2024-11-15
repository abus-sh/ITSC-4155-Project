import { ComponentFixture, fakeAsync, TestBed, tick } from '@angular/core/testing';
import { RegisterComponent } from './register.component';
import { provideHttpClient } from '@angular/common/http';
import { RouterModule } from '@angular/router';
import { of, throwError } from 'rxjs';
import { getBackendURL } from '../../config';


describe('RegisterComponent', () => {
    let component: RegisterComponent;
    let fixture: ComponentFixture<RegisterComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [RegisterComponent, RouterModule.forRoot([])],
            providers: [provideHttpClient()]
        }).compileComponents();

        fixture = TestBed.createComponent(RegisterComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('Creating the component', () => {
        expect(component).toBeTruthy();
    });

    it('Initialize the form with empty values', () => {
        const form = component.registerForm;
        expect(form.value).toEqual({
            username: '',
            password: '',
            confirmPassword: '',
            canvasToken: ''
        });
    });

    it('Mark form as invalid if any required field is missing', () => {
        component.registerForm.setValue({
            username: '',
            password: '',
            confirmPassword: '',
            canvasToken: ''
        });
        expect(component.registerForm.valid).toBeFalsy();
    });

    it('Show an error if the token was not retrieved when submitting', () => {
        spyOn(console, 'error');
        component.tokenRetrieved = false;
        component.registerForm.setValue({
            username: 'testuser',
            password: 'password123',
            confirmPassword: 'password123',
            canvasToken: 'token123'
        });
        component.onSubmit();
        expect(console.error).toHaveBeenCalledWith('Please, give authorization to Todoist to register an account');
    });

    it('Show an error if the passwords do not match when submitting', () => {
        spyOn(console, 'error');
        component.tokenRetrieved = true;
        component.registerForm.setValue({
            username: 'testuser',
            password: 'password123',
            confirmPassword: 'password456',
            canvasToken: 'token123'
        });
        component.onSubmit();
        expect(console.error).toHaveBeenCalledWith('Passwords do not match');
    });

    it('Call the registration endpoint on valid form submission and redirect to login', fakeAsync(() => {
        spyOn(component['http'], 'post').and.returnValue(of({'success': true, 'message': "Account created for testuser"}));
        const navigateSpy = spyOn(component['router'], 'navigate');
        component.tokenRetrieved = true;
        component.authCode = 'code';
        component.authState = 'state';

        component.registerForm.setValue({
            username: 'testuser',
            password: 'password123',
            confirmPassword: 'password123',
            canvasToken: 'token123'
        });
        
        component.onSubmit();
        tick();

        expect(component['http'].post).toHaveBeenCalledWith(jasmine.any(String), jasmine.any(Object), jasmine.any(Object));
        expect(navigateSpy).toHaveBeenCalledWith(['/login']);
    }));

    it('Handle backend errors during registration', () => {
        spyOn(console, 'error');
        spyOn(component['http'], 'post').and.returnValue(throwError({ error: 'Registration error' }));

        component.tokenRetrieved = true;
        component.authCode = 'code';
        component.authState = 'state';

        component.registerForm.setValue({
            username: 'testuser',
            password: 'password123',
            confirmPassword: 'password123',
            canvasToken: 'token123'
        });

        component.onSubmit();
        expect(console.error).toHaveBeenCalledWith('Registration failed', { error: 'Registration error' });
    });

    it('Should open Todoist OAuth popup when called', () => {
        spyOn(window, 'open').and.returnValue(window);
    
        component.openTodoistAuth();
        expect(window.open).toHaveBeenCalledWith(
            getBackendURL() + '/api/auth/todoist/redirect', 'Todoist OAuth', 'width=600,height=400');
    });

    it('Should not open popup if canOpenTodoist is false', () => {
        spyOn(window, 'open');
        component.canOpenTodoist = false; 
    
        component.openTodoistAuth();
        expect(window.open).not.toHaveBeenCalled(); 
    });

    it('Popup should send message and be given to handleOAuthResponse', () => {
        spyOn(component, 'handleOAuthResponse');  
        const mockEventData = { result: 'success', code: 'authCode123', state: 'authState123' };
        
        window.dispatchEvent(new MessageEvent('message', {
            data: mockEventData,
            origin: getBackendURL(),  
        }));
    
        expect(component.handleOAuthResponse).toHaveBeenCalledWith(mockEventData);
    });

    it('Should update component variables on handleOAuthResponse success', () => {
        component.handleOAuthResponse({ result: 'success', code: 'authCode123', state: 'authState123' });
        expect(component.tokenRetrieved).toBeTrue();
        expect(component.authCode).toBe('authCode123');
        expect(component.authState).toBe('authState123');
        expect(component.todoistAuthString).toBe('Authorization completed - ✔️');
    });

    it('Show error on handleOAuthResponse failure', () => {
        spyOn(console, 'error');
        const errorOAuth = { result: 'failure', code: '', state: '' };
        component.handleOAuthResponse(errorOAuth);
        expect(component.tokenRetrieved).toBeFalse();
        expect(component.todoistAuthString).toBe('Error while authorizing Todoist - ❌');
        expect(console.error).toHaveBeenCalledWith('Error authorizing Todoist: ', errorOAuth);
    });
});
