import { ComponentFixture, TestBed } from '@angular/core/testing';
import { CalendarComponent, CalendarEvent } from './calendar.component';
import { provideHttpClient } from '@angular/common/http';


describe('CalendarComponent', () => {
    let component: CalendarComponent;
    let fixture: ComponentFixture<CalendarComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [CalendarComponent],
            providers: [provideHttpClient()]
        })
            .compileComponents();

        fixture = TestBed.createComponent(CalendarComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('Creating the calendar component', () => {
        expect(component).toBeTruthy();
    });

    it('Update the calendar when prevMonth is called', () => {
        const initialMonth = component.monthView.getMonth();
        component.prevMonth();
        expect(component.monthView.getMonth()).toBe(initialMonth - 1);
    });

    it('Update the calendar when nextMonth is called', () => {
        const initialMonth = component.monthView.getMonth();
        component.nextMonth();
        expect(component.monthView.getMonth()).toBe(initialMonth + 1);
    });

    it('Load events for the current month', async () => {
        const spy = spyOn(component['canvasService'], 'getCalendarEvents').and.returnValue(Promise.resolve([]));
        await component.loadEvents('2023-01-01', '2023-01-31');
        expect(spy).toHaveBeenCalled();
    });

    it('Format date correctly', () => {
        const date1 = new Date(2023, 0, 1);
        expect(component.formatDate(date1)).toBe('2023-01-01');

        const date2 = new Date(2023, 11, 31); 
        expect(component.formatDate(date2)).toBe('2023-12-31');

        const date3 = new Date(2024, 1, 29); // leap year
        expect(component.formatDate(date3)).toBe('2024-02-29');

        const date4 = new Date(2023, 6, 4); 
        expect(component.formatDate(date4)).toBe('2023-07-04');
    });

    it('Generate days in month correctly with overflow from previous month', () => {
        const days = component.generateDaysInMonth(2024, 0);
        expect(days.length).toBeGreaterThan(0);
        expect(days[0].date).toBeInstanceOf(Date);
        expect(days[0].date.getDay()).toBe(0);
        expect(days[0].date.toDateString()).toBe('Sun Dec 31 2023');
    });

    it('Give the class submitted to turned in assignments', () => {
        const event = { type: 'assignment', user_submitted: true } as CalendarEvent;
        expect(component.getClass(event)).toBe('assignment submitted');
    });
});
