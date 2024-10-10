import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../auth.service';
import { Observable } from 'rxjs';
import { getBackendURL } from '../../config';

interface UserProfile {
    username?: string;
    canvas?: {
        canvas_id: string;
        canvas_name: string;
        canvas_title: string;
        canvas_bio: string;
        canvas_pic: string;
    };
}

@Component({
    selector: 'app-profile',
    standalone: true,
    imports: [CommonModule, FormsModule],
    templateUrl: './profile.component.html',
    styleUrls: ['./profile.component.scss']
})
export class ProfileComponent implements OnInit {
    private profileUrl = getBackendURL() + '/api/v1/user/profile';
    private passwordChangeUrl = getBackendURL() + '/api/auth/change-password';
    authStatus$: Observable<any>;

    profileData: UserProfile = {};
    oldPassword: string = '';
    newPassword: string = '';
    confirmPassword: string = '';

    message: string | null = null;
    messageClass: string = '';

    constructor(private authService: AuthService, private http: HttpClient) { 
        this.authStatus$ = this.authService.authStatus$;
    }

    ngOnInit(): void {
        // Get the profile data from the route
        this.http.get<any>(this.profileUrl, { withCredentials: true }).subscribe(
            (data: UserProfile) => {
                this.profileData = data; // Profile data is loaded here
            },
            (error) => {
                console.error('Error fetching profile data:', error);  // Couldn;t get profile data
            }
        );
    }

    onSubmit() {

        if (!this.oldPassword?.trim() || !this.newPassword?.trim() || !this.confirmPassword?.trim()) {
            this.messageBox(true, "All fields are required!");
            return;
        }
        
        if (this.newPassword !== this.confirmPassword) {
            this.messageBox(true, "New passwords do not match!");
            return;
        }

        if (this.newPassword.length < 15) {
            this.messageBox(true, "New password must be at least 15 characters long!");
            return;
        }

        const payload = {
            oldPassword: this.oldPassword,
            newPassword: this.newPassword,
        };

        this.http.post<{ message: string }>(this.passwordChangeUrl, payload, { withCredentials: true }).subscribe(
            response => {
                console.log(response)
                this.messageBox(false, response.message);
                this.clearForm();
            },
            error => {
                if (error.error?.message) {
                    this.messageBox(true, error.error.message);
                }
                console.error('Error updating password:', error);
            }
        );
    }

    clearForm() {
        this.oldPassword = '';
        this.newPassword = '';
        this.confirmPassword = '';
        this.message = '';
    }

    messageBox(error: boolean, message: string) {
        this.message = message;
        this.messageClass = error ? 'error' : 'success';
    }
}
