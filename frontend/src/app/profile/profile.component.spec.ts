import { ComponentFixture, TestBed, fakeAsync, flush } from '@angular/core/testing';
import { ProfileComponent } from './profile.component';
import { provideHttpClient } from '@angular/common/http';
import { of, throwError } from 'rxjs';

describe('ProfileComponent', () => {
    let component: ProfileComponent;
    let fixture: ComponentFixture<ProfileComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [ProfileComponent],
            providers: [provideHttpClient()]
        }).compileComponents();

        fixture = TestBed.createComponent(ProfileComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('Creating the profile component', () => {
        expect(component).toBeTruthy();
    });

    it('Display an error if the passwords do not match for the changing passwords form', () => {
        component.oldPassword = 'oldPassword123';
        component.newPassword = 'newPassword123';
        component.confirmPassword = 'differentPassword123';
        component.onSubmit();
        expect(component.message).toBe('New passwords do not match!');
        expect(component.messageClass).toBe('error');
    });

    it('Display an error if new password is less than 15 characters for the changing passwords form', () => {
        component.oldPassword = 'oldPassword123';
        component.newPassword = 'short';
        component.confirmPassword = 'short';
        component.onSubmit();
        expect(component.message).toBe('New password must be at least 15 characters long!');
        expect(component.messageClass).toBe('error');
    });

    it('Display an error message if any field is empty for the changing passwords form', () => {
        component.oldPassword = '';
        component.newPassword = 'newPassword123';
        component.confirmPassword = 'newPassword123';
        component.onSubmit();
        expect(component.message).toBe('All fields are required!');
        expect(component.messageClass).toBe('error');
    });

    it('Submit request to change password and display success message', fakeAsync(() => {
        component.oldPassword = 'oldPassword123';
        component.newPassword = 'newPassword1234567890';
        component.confirmPassword = 'newPassword1234567890';

        const mockResponse = { success: true, message: 'Password changed successfully!' };
        spyOn(component, 'reloadPage');
        spyOn(component['http'], 'post').and.returnValue(of(mockResponse));

        component.onSubmit();
        flush();

        expect(component.message).toBe(mockResponse.message);
        expect(component.messageClass).toBe('success');
        expect(component.reloadPage).toHaveBeenCalled();
    }));

    it('Submit request to change password and handle error message', fakeAsync(() => {
        component.oldPassword = 'oldPassword123';
        component.newPassword = 'newPassword1234567890';
        component.confirmPassword = 'newPassword1234567890';

        const mockErrorResponse = { success: false, message: "Mock backend error message!" };
        spyOn(component, 'reloadPage');
        spyOn(component['http'], 'post').and.returnValue(throwError({ error: mockErrorResponse }));

        component.onSubmit();
        flush();

        expect(component.message).toBe(mockErrorResponse.message);
        expect(component.messageClass).toBe('error');
        expect(component.reloadPage).not.toHaveBeenCalled();
    }));
});
