import { ComponentFixture, fakeAsync, flush, TestBed, tick } from '@angular/core/testing';
import { RegisterComponent } from './register.component';
import { provideHttpClient } from '@angular/common/http';
import { Router, RouterModule } from '@angular/router';
import { of } from 'rxjs';


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

    it('should create the component', () => {
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
        spyOn(component['http'], 'post').and.returnValue(of({'success': 'Registration successfull'}));
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
});
