import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ReactiveFormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http'; 
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

@Component({
    selector: 'app-register',
    standalone: true,
    imports: [ReactiveFormsModule, CommonModule, RouterModule],
    templateUrl: './register.component.html',
    styleUrls: ['./register.component.scss']
})
export class RegisterComponent {
    registerForm: FormGroup;

    constructor(private fb: FormBuilder, private http: HttpClient, private router: Router) {
        // Initialize the form with validators
        this.registerForm = this.fb.group({
            username: ['', Validators.required], 
            password: ['', Validators.required], 
            confirmPassword: ['', Validators.required],
            canvasToken: ['', Validators.required] ,
            todoistToken: ['', Validators.required]  
        });
    }

    onSubmit() {
        if (this.registerForm.valid) {
            const { username, password, confirmPassword, canvasToken, todoistToken } = this.registerForm.value;

            // Check if password and confirmPassword match
            if (password !== confirmPassword) {
                console.error('Passwords do not match');
                return; 
            }

            // Make HTTP POST request to the registration endpoint
            this.http.post('http://localhost:5000/auth/signup', { username, password, canvasToken, todoistToken }, { withCredentials: true })
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
}