import { Component } from '@angular/core';
import { CanvasService } from '../canvas.service';
import { CommonModule } from '@angular/common';


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
    days: { date: Date; items: string[]; isCurrentMonth: boolean; isToday: boolean }[] = [];

    private currentDate: Date;

    constructor(private canvasService: CanvasService) {
        this.currentDate = new Date(new Date().toLocaleString("en-US", { timeZone: "America/New_York" }));
        this.updateCalendar();
    }

    // Updates the month name, year, and days for the current calendar
    updateCalendar() {
        this.monthName = this.currentDate.toLocaleString('default', { month: 'long' });
        this.year = this.currentDate.getFullYear();
        this.days = this.generateDaysInMonth(this.currentDate.getFullYear(), this.currentDate.getMonth());
    }

    // Creates an array of days for the current month, with days from the previous month if needed
    generateDaysInMonth(year: number, month: number): { date: Date; items: string[]; isCurrentMonth: boolean; isToday: boolean }[] {
        const daysInMonth = new Date(year, month + 1, 0).getDate();
        const days: { date: Date; items: string[]; isCurrentMonth: boolean; isToday: boolean }[] = [];
        const todayString = this.currentDate.toDateString();

        const firstDateOfMonth = new Date(year, month, 1);
        const firstDay = firstDateOfMonth.getDay();

        for (let i = firstDay; i > 0; i--) {
            const date = new Date(year, month, 0); // Last day of the previous month
            date.setDate(date.getDate() - i);
            days.push({ date, items: [], isCurrentMonth: false, isToday: date.toDateString() === todayString });
        }

        for (let i = 1; i <= daysInMonth; i++) {
            const date = new Date(year, month, i);
            days.push({ date, items: [], isCurrentMonth: true, isToday: date.toDateString() === todayString });
        }

        return days;
    }

    // Go to the previous month and update the calendar
    prevMonth() {
        this.currentDate.setMonth(this.currentDate.getMonth() - 1);
        this.updateCalendar();
    }

    // Go to the next month and update the calendar
    nextMonth() {
        this.currentDate.setMonth(this.currentDate.getMonth() + 1);
        this.updateCalendar();
    }
}
