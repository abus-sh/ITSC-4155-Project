import { Routes, Resolve } from '@angular/router';
import { AuthGuard } from './auth.guard';
import { LoginComponent } from './login/login.component';
import { RegisterComponent } from './register/register.component';
import { DashboardComponent } from './dashboard/dashboard.component';
import { ProfileComponent } from './profile/profile.component';
import { ProfileResolver } from './resolver/profile.resolver';

export const routes: Routes = [
    { path: 'login', component: LoginComponent },       // Route for login page
    { path: 'register', component: RegisterComponent }, // Route for register page
    
    { path: 'dashboard', component: DashboardComponent, 
        canActivate: [AuthGuard] },

    { path: 'profile', component: ProfileComponent, 
        canActivate: [AuthGuard], 
        resolve: {profileData: ProfileResolver}},

        
    { path: '**', redirectTo: 'home' }
];
