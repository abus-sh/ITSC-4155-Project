import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { AuthService } from '../auth.service';
import { Router } from '@angular/router';
import { ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';


@Component({
    selector: 'app-login',
    standalone: true,
    imports: [ReactiveFormsModule, CommonModule, RouterModule],
    templateUrl: './login.component.html',
    styleUrls: ['./login.component.scss']
})
export class LoginComponent {
    loginForm: FormGroup;
    errorMessage: string = '';

    constructor(private fb: FormBuilder, private authService: AuthService, private router: Router) {
        this.loginForm = this.fb.group({
            username: ['', Validators.required],
            password: ['', Validators.required]
        });
    }

    onSubmit() {
        const { username, password } = this.loginForm.value;
        this.authService.login(username, password).subscribe(
            res => {
                if (res.success) {
                    window.location.replace('/dashboard');
                } else {
                    this.errorMessage = res.message;
                }
            },
            err => {
                this.errorMessage = err.error.message || 'Login failed';
            }
        );
    }
}
