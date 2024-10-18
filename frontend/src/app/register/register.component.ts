import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { getBackendURL } from '../../config';


@Component({
    selector: 'app-register',
    standalone: true,
    imports: [ReactiveFormsModule, CommonModule, RouterModule],
    templateUrl: './register.component.html',
    styleUrls: ['./register.component.scss']
})
export class RegisterComponent {
    registerForm: FormGroup;

    canOpenTodoist: boolean;
    tokenRetrieved: boolean;
    todoistAuthString: string;
    authCode: string;
    authState: string;

    constructor(private fb: FormBuilder, private http: HttpClient, private router: Router) {
        // Initialize the form with validators
        this.canOpenTodoist = true;
        this.tokenRetrieved = false;
        this.todoistAuthString = "";
        this.authCode = '';
        this.authState = '';

        this.registerForm = this.fb.group({
            username: ['', Validators.required],
            password: ['', Validators.required],
            confirmPassword: ['', Validators.required],
            canvasToken: ['', Validators.required],
        });
    }

    ngOnInit(): void {
        window.addEventListener('message', (event) => {
            // Retrieve code and state from backend
            if (event.origin === getBackendURL()) {
                this.handleOAuthResponse(event.data);
            }
        });
    }

    onSubmit() {
        if (this.registerForm.valid) {
            if (!this.tokenRetrieved) {
                console.error('Please, give authorization to Todoist to register an account');
                return;
            }

            const { username, password, confirmPassword, canvasToken } = this.registerForm.value;

            // Check if password and confirmPassword match
            if (password !== confirmPassword) {
                console.error('Passwords do not match');
                return;
            }

            const body = {
                username,
                password,
                canvasToken,
                todoist: {
                    code: this.authCode,
                    state: this.authState,
                }
            };

            // Make HTTP POST request to the registration endpoint
            this.http.post(getBackendURL() + '/api/auth/signup', body, { withCredentials: true })
                .subscribe(
                    response => {
                        console.log('Registration successful', response);
                        // Redirect to login or another page after successful registration
                        this.router.navigate(['/login']);
                    },
                    error => {
                        console.error('Registration failed', error);
                        // Handle registration errors (e.g., show error messages)
                    }
                );
        } else {
            console.error('Form is invalid');
            // Handle form validation errors
        }
    }

    openTodoistAuth() {
        if (this.canOpenTodoist) {
            const popup = window.open(getBackendURL() + '/api/auth/todoist/redirect', 'Todoist OAuth', 'width=600,height=400');
            if (popup) {
                // Make popup the focus
                popup.focus();
            } else {
                console.error('Popup blocked or failed to open');

            }
        }
    }

    handleOAuthResponse(data: { result: string, code: string, state: string }) {
        // Authorization retrieval process has ended, allow for registration
        if (data.result == 'success') {
            console.log('Token info retrieval result: ', data.result);
            this.authCode = data.code;
            this.authState = data.state;
            this.tokenRetrieved = true;
            this.todoistAuthString = "Authorization completed - ✔️"
        } else {
            console.log("Error authorizing Todoist: ", data)
            this.todoistAuthString = "Error while authorizing Todoist - ❌"
        }
    }
}