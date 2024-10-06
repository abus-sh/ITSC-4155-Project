import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';


@Component({
    selector: 'app-profile',
    standalone: true,
    imports: [CommonModule, FormsModule],
    templateUrl: './profile.component.html',
    styleUrls: ['./profile.component.scss']
})
export class ProfileComponent implements OnInit {
    profileData: any;
    oldPassword: string = '';
    newPassword: string = '';
    confirmPassword: string = '';

    message: string | null = null;
    messageClass: string = '';

    private passwordChangeUrl = 'http://localhost:5000/api/v1/user/change-password';


    constructor(private route: ActivatedRoute, private http: HttpClient) { }

    ngOnInit(): void {
        // Get the profile data from the route
        this.profileData = this.route.snapshot.data['profileData'];

        if (!this.profileData) {
            console.error('Profile data not found');
        }
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
