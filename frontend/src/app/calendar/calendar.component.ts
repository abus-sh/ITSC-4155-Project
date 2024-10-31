import { Component } from '@angular/core';
import { CanvasService } from '../canvas.service';
import { CommonModule } from '@angular/common';



// Not just assignment, but zoom meeting and other calendar events
export interface CalendarEvent {
    title: string;
    description: string;
    type: string;
    html_url: string;
    context_name: string;
    start_at: Date;
    end_at: Date;
    user_submitted?: boolean;
}

interface CalendarDay {
    date: Date;
    items: CalendarEvent[];
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

    /***********************************      
    * 
    *       Calendar Set Events
    * 
    ***********************************/

    loadEvents(start_date: string, end_date: string) {
        this.canvasService.getCalendarEvents(start_date, end_date).then((events: CalendarEvent[]) => {
            const dayMap = new Map<string, CalendarDay>();

            this.days.forEach(day => {
                dayMap.set(day.date.toDateString(), day);
            });

            events.forEach(event => {
                const eventDateString = new Date(event.start_at).toDateString()

                const correspondingDay = dayMap.get(eventDateString);

                // If a corresponding day is found, add the event to its CalendarEvent list
                if (correspondingDay) {
                    correspondingDay.items.push(event);
                }
            });
        });
    }


    /***********************************      
    * 
    *       Calendar Set up
    * 
    ***********************************/

    // Updates the month name, year, and days for the current calendar
    updateCalendar() {
        // Load CalendarDays
        this.monthName = this.monthView.toLocaleString('default', { month: 'long' });
        this.year = this.monthView.getFullYear();
        this.days = this.generateDaysInMonth(this.monthView.getFullYear(), this.monthView.getMonth());

        const firstDate = this.formatDate(this.days[0].date); 
        const lastDate = this.formatDate(this.days[this.days.length - 1].date);

        // Load CalendarEvents
        this.loadEvents(firstDate, lastDate);
    }

    // Creates an array of days for the current month, with days from the previous month if needed
    generateDaysInMonth(year: number, month: number): CalendarDay[] {
        const daysInMonth = new Date(year, month + 1, 0).getDate();
        const days: CalendarDay[] = [];

        const firstDateOfMonth = new Date(year, month, 1);
        const firstDay = firstDateOfMonth.getDay();

        // Days that overflow into this month from the previous
        for (let i = firstDay - 1; i >= 0; i--) {
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
        this.monthView.setMonth(this.monthView.getMonth() - 1, 1);
        this.updateCalendar();
    }

    // Go to the next month and update the calendar
    nextMonth() {
        this.monthView.setMonth(this.monthView.getMonth() + 1, 1);
        this.updateCalendar();
    }

    formatDate(date: Date): string {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    }
}
