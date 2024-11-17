import { ComponentFixture, TestBed, fakeAsync, tick } from '@angular/core/testing';
import { DashboardComponent, Subtask } from './dashboard.component';
import { provideHttpClient } from '@angular/common/http';
import { CanvasService } from '../canvas.service';


describe('DashboardComponent', () => {
    let component: DashboardComponent;
    let fixture: ComponentFixture<DashboardComponent>;
    let canvasService: CanvasService;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [DashboardComponent],
            providers: [provideHttpClient()]
        })
            .compileComponents();

        fixture = TestBed.createComponent(DashboardComponent);
        component = fixture.componentInstance;
        canvasService = TestBed.inject(CanvasService)
        fixture.detectChanges();
    });

    it('Creating the dashboard component', () => {
        expect(component).toBeTruthy();
    });

    it('Toggle section collapse for upcoming assignments', () => {
        component.sectionCollapseUpcoming = false;
        component.toggleSection(0);
        expect(component.sectionCollapseUpcoming).toBeTrue();
        component.toggleSection(0);
        expect(component.sectionCollapseUpcoming).toBeFalse();
    });

    it('Toggle section collapse for completed assignments', () => {
        component.sectionCollapseComplete = false;
        component.toggleSection(1);
        expect(component.sectionCollapseComplete).toBeTrue();
        component.toggleSection(1);
        expect(component.sectionCollapseComplete).toBeFalse();
    });

    it('Open and close subtask form', () => {
        const assignment = { id: 1, title: 'Test Assignment', description: '', type: '', submission_types: [], graded_submissions_exist: false, due_at: '', subtasks: [], user_submitted: false };
        component.openForm(assignment);
        expect(component.subtaskFormDisplay).toBeTrue();
        expect(component.subtaskAssignment).toEqual(assignment);

        component.closeForm();
        expect(component.subtaskFormDisplay).toBeFalse();
        expect(component.subtaskAssignment).toBeNull();
    });

    it('Open and close the assignment form', () => {
        component.openAssignmentForm();
        expect(component.assignmentFormDisplay).toBeTrue();

        component.closeAssignmentForm();
        expect(component.assignmentFormDisplay).toBeFalse();
    });

    it('Adding a new subtask', () => {
        const assignment = { id: 1, title: 'Test Assignment', description: '', type: '', submission_types: [], graded_submissions_exist: false, due_at: '', subtasks: [], user_submitted: false  };
        component.openForm(assignment);
        component.addSubtaskForm.setValue({
            name: 'Test Subtask',
            description: 'Test Description',
            due_date: '2023-12-31T23:59',
            status: '0'
        });

        spyOn(canvasService, 'addSubtask').and.callThrough();
        spyOn(component, 'closeForm').and.callThrough();
        
        component.addSubtask(assignment);
        expect(canvasService.addSubtask).toHaveBeenCalled();
        expect(component.addSubtaskForm.value.name).toBe('');
        expect(component.closeForm).toHaveBeenCalled();
        expect(component.subtaskFormDisplay).toBeFalse();
    });

    it('Toggle a subtask status', fakeAsync(() => {
        const subtask: Subtask = { id: 1, canvas_id: 1, name: 'Test Subtask', description: '', due_date: '', status: 0 };
        spyOn(canvasService, 'toggleSubtaskStatus').and.returnValue(Promise.resolve(true));

        component.toggleSubtaskStatus(subtask);
        tick(1010);
        expect(subtask.status).toBe(1);

        component.toggleSubtaskStatus(subtask);
        tick(1010);
        expect(subtask.status).toBe(0);
    }));
});
