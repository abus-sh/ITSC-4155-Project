import { Routes } from '@angular/router';
import { AuthGuard } from './auth.guard';
import { LoginComponent } from './login/login.component';
import { RegisterComponent } from './register/register.component';
import { DashboardComponent } from './dashboard/dashboard.component';
import { ProfileComponent } from './profile/profile.component';
import { CoursesComponent } from './courses/courses.component';
import { CalendarComponent } from './calendar/calendar.component';
import { GradesimComponent } from './gradesim/gradesim.component';

export const routes: Routes = [
    { path: 'login', component: LoginComponent },       // Route for login page
    { path: 'register', component: RegisterComponent }, // Route for register page

    {
        path: 'dashboard', component: DashboardComponent,
        canActivate: [AuthGuard]
    },

    {
        path: 'courses', component: CoursesComponent,
        canActivate: [AuthGuard]
    },

    {
        path: 'profile', component: ProfileComponent,
        canActivate: [AuthGuard]
    },

    {
        path: 'calendar', component: CalendarComponent,
        canActivate: [AuthGuard]
    },

    {
        path: 'gradesim', component: GradesimComponent,
        canActivate: [AuthGuard]
    },

    // Redirect to dashboard, if user is not logged in, dashboard will redirect to login
    { path: '**', redirectTo: 'dashboard' }

];
