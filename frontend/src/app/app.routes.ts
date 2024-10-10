import { Routes } from '@angular/router';
import { AuthGuard } from './auth.guard';
import { LoginComponent } from './login/login.component';
import { RegisterComponent } from './register/register.component';
import { DashboardComponent } from './dashboard/dashboard.component';
import { ProfileComponent } from './profile/profile.component';
import { ProfileResolver } from './resolver/profile.resolver';
import { CoursesComponent } from './courses/courses.component';

export const routes: Routes = [
    { path: 'login', component: LoginComponent },       // Route for login page
    { path: 'register', component: RegisterComponent }, // Route for register page

    {
        path: 'dashboard', component: DashboardComponent,
        canActivate: [AuthGuard]
    },

    { path: 'courses', component: CoursesComponent, 
        canActivate: [AuthGuard] },

    { path: 'profile', component: ProfileComponent, 
        canActivate: [AuthGuard] }, // resolve: {profileData: ProfileResolver} RESOLVE MAY NOT BE NEEDED

    // Redirect to dashboard, if user is not logged in, dashboard will redirect to login
    { path: '**', redirectTo: 'dashboard' }

];
