import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { AuthService, AuthStatus } from '../auth.service';
import { Observable } from 'rxjs';
import { getBackendURL } from '../../config';
import { CanvasService } from '../canvas.service';
import { SubmissiondownloadComponent } from '../submissiondownload/submissiondownload.component';

export interface UserProfile {
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
    imports: [CommonModule, FormsModule, SubmissiondownloadComponent],
    templateUrl: './profile.component.html',
    styleUrls: ['./profile.component.scss']
})
export class ProfileComponent implements OnInit {
    private backendUrl = getBackendURL();
    private profileUrl = this.backendUrl + '/api/v1/user/profile';
    private passwordChangeUrl = this.backendUrl + '/api/auth/change-password';
    authStatus$: Observable<AuthStatus>;

    profileData: UserProfile = {};
    oldPassword = '';
    newPassword = '';
    confirmPassword = '';

    message: string | null = null;
    messageClass = '';

    lastSyncDate = '~'

    constructor(private authService: AuthService, private http: HttpClient,
        private canvasService: CanvasService) { 
        
        this.authStatus$ = this.authService.authStatus$;
    }

    ngOnInit(): void {
        // Get the profile data from the route
        this.http.get<UserProfile>(this.profileUrl, { withCredentials: true }).subscribe(
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
                this.messageBox(false, response.message);
                this.clearForm();
                this.reloadPage()
            },
            error => {
                if (!error.error.success) {
                    this.messageBox(true, error.error.message);
                }
                console.error('Error updating password:', error);
            }
        );
    }

    syncTodoistManual() {
        this.lastSyncDate = 'Started, please wait..'
        this.http.post(`${this.backendUrl}/api/v1/tasks/update`, null).subscribe({
            next: () => {
                this.lastSyncDate = new Date().toLocaleString();
                this.canvasService.getDueAssignments().then(() => this.canvasService.getSubTasks());
            },
            error: () => {
                this.lastSyncDate = 'error'
            }
        });
    }

    clearForm() {
        this.oldPassword = '';
        this.newPassword = '';
        this.confirmPassword = '';
    }

    messageBox(error: boolean, message: string) {
        this.message = message;
        this.messageClass = error ? 'error' : 'success';
    }

    // For some reason window.location doesn't want to be mocked in the spec, and I hate it
    reloadPage() {
        window.location.reload();
    }
}
