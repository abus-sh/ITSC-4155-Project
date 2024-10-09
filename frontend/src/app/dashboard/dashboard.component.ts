import { Component } from '@angular/core';
import { ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { AuthService } from '../auth.service';
import { Router } from '@angular/router';
import { Observable } from 'rxjs';

@Component({
    selector: 'app-dashboard',
    standalone: true,
    imports: [ReactiveFormsModule, CommonModule],
    templateUrl: './dashboard.component.html',
    styleUrl: './dashboard.component.scss'
})
export class DashboardComponent {
    authStatus$: Observable<any>;


    constructor(private authService: AuthService, private router: Router) {
        this.authStatus$ = this.authService.authStatus$;
    }
    
    ngOnInit()
    {
        let btn = document.querySelector('#btn') as HTMLElement;
        let sidebar = document.querySelector('.sidebar') as HTMLElement;
        let mainContent = document.querySelector('.main-content') as HTMLElement;

        btn.onclick = function(){
            sidebar?.classList.toggle('active');
            mainContent?.classList.toggle('active');
        };
    }
}
