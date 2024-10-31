import { Component } from '@angular/core';
import { CanvasService } from '../canvas.service';
import { CommonModule } from '@angular/common';



// Not just assignment and subtasks, but zoom meeting and other calendar events
export interface Events {
    name: string;
    date: string;
    url: string;
}

interface CalendarDay {
    date: Date;
    items: Events[];
    isCurrentMonth: boolean;
    isToday: boolean;
}

@Component({
    selector: 'app-calendar',
    standalone: true,
    imports: [CommonModule],
    templateUrl: './calendar.component.html',
    styleUrls: ['./calendar.component.scss']
})
export class CalendarComponent {
    monthName: string = '';
    year: number = 0;
    days: CalendarDay[] = [];


    private todayString: string;
    private monthView: Date;

    constructor(private canvasService: CanvasService) {
        this.monthView = new Date(new Date().toLocaleString("en-US", { timeZone: "America/New_York" }));
        this.todayString = this.monthView.toDateString();
        this.updateCalendar();
    }

    // Updates the month name, year, and days for the current calendar
    updateCalendar() {
        this.monthName = this.monthView.toLocaleString('default', { month: 'long' });
        this.year = this.monthView.getFullYear();
        this.days = this.generateDaysInMonth(this.monthView.getFullYear(), this.monthView.getMonth());
    }

    // Creates an array of days for the current month, with days from the previous month if needed
    generateDaysInMonth(year: number, month: number): CalendarDay[] {
        const daysInMonth = new Date(year, month + 1, 0).getDate();
        const days: CalendarDay[] = [];

        const firstDateOfMonth = new Date(year, month, 1);
        const firstDay = firstDateOfMonth.getDay();

        // Days that overflow into this month from the previous
        for (let i = firstDay; i > 0; i--) {
            const date = new Date(year, month, 0);
            date.setDate(date.getDate() - i);
            days.push({ date, items: [], isCurrentMonth: false, isToday: date.toDateString() === this.todayString });
        }

        // This month's days
        for (let i = 1; i <= daysInMonth; i++) {
            const date = new Date(year, month, i);
            days.push({ date, items: [], isCurrentMonth: true, isToday: date.toDateString() === this.todayString });
        }

        return days;
    }

    // Go to the previous month and update the calendar
    prevMonth() {
        this.monthView.setMonth(this.monthView.getMonth() - 1);
        this.updateCalendar();
    }

    // Go to the next month and update the calendar
    nextMonth() {
        this.monthView.setMonth(this.monthView.getMonth() + 1);
        this.updateCalendar();
    }
}
