import { ComponentFixture, fakeAsync, TestBed } from '@angular/core/testing';

import { TasknoteComponent } from './tasknote.component';
import { provideHttpClient } from '@angular/common/http';
import { Assignment } from '../dashboard/dashboard.component';
import { IdType } from '../todoist.service';

describe('TasknoteComponent Canvas, No Desc', () => {
    let component: TasknoteComponent;
    let fixture: ComponentFixture<TasknoteComponent>;

    const assignment: Assignment = {
        title: 'title',
        description: 'desc',
        type: 'assignment',
        submission_types: [],
        id: 1,
        graded_submissions_exist: false,
        due_at: 'now',
        subtasks: []
    };

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [TasknoteComponent],
            providers: [provideHttpClient()]
        }).compileComponents();

        fixture = TestBed.createComponent(TasknoteComponent);
        component = fixture.componentInstance;
        component.assignment = assignment;
        fixture.detectChanges();
    });

    it('Create the component', () => {
        expect(component).toBeTruthy();
    });

    it('Initialize the form', () => {
        expect(component.noteForm.value).toEqual({
            note: ''
        });
    });

    it('Test the form validation', () => {
        component.noteForm.setValue({
            note: ''
        });
        expect(component.noteForm.valid).toBeTruthy();

        component.noteForm.setValue({
            note: 'a'.repeat(500)
        });
        expect(component.noteForm.valid).toBeTruthy();

        component.noteForm.setValue({
            note: 'a'.repeat(501)
        });
        expect(component.noteForm.valid).toBeFalsy();
    });

    it('Test the form submission', fakeAsync(() => {
        spyOn(component['todoistService'], 'updateAssignmentDescription').and.resolveTo(true);
        const closeFormSpy = spyOn(component, 'closeForm');
        component.noteForm.setValue({
            note: 'note'
        });
        component.noteForm.controls['note'].markAsDirty();

        component.updateNote();
        
        expect(component['todoistService'].updateAssignmentDescription)
            .toHaveBeenCalledWith(1, IdType.Canvas, 'note');
    }));
});

describe('TasknoteComponent Canvas, Desc', () => {
    let component: TasknoteComponent;
    let fixture: ComponentFixture<TasknoteComponent>;

    const assignment: Assignment = {
        title: 'title',
        description: 'desc',
        user_description: 'user',
        type: 'assignment',
        submission_types: [],
        id: 1,
        graded_submissions_exist: false,
        due_at: 'now',
        subtasks: []
    };

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [TasknoteComponent],
            providers: [provideHttpClient()]
        }).compileComponents();

        fixture = TestBed.createComponent(TasknoteComponent);
        component = fixture.componentInstance;
        component.assignment = assignment;
        fixture.detectChanges();
    });

    it('Initialize the form', () => {
        expect(component.noteForm.value).toEqual({
            note: 'user'
        });
    });

    it('Test the form submission', fakeAsync(() => {
        spyOn(component['todoistService'], 'updateAssignmentDescription').and.resolveTo(true);
        const closeFormSpy = spyOn(component, 'closeForm');
        component.noteForm.setValue({
            note: 'note'
        });
        component.noteForm.controls['note'].markAsDirty();

        component.updateNote();
        
        expect(component['todoistService'].updateAssignmentDescription)
            .toHaveBeenCalledWith(1, IdType.Canvas, 'note');
    }));
});

describe('TasknoteComponent Native, No Desc', () => {
    let component: TasknoteComponent;
    let fixture: ComponentFixture<TasknoteComponent>;

    const assignment: Assignment = {
        title: 'title',
        description: 'desc',
        type: 'assignment',
        submission_types: [],
        db_id: 2,
        graded_submissions_exist: false,
        due_at: 'now',
        subtasks: []
    };

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [TasknoteComponent],
            providers: [provideHttpClient()]
        }).compileComponents();

        fixture = TestBed.createComponent(TasknoteComponent);
        component = fixture.componentInstance;
        component.assignment = assignment;
        fixture.detectChanges();
    });

    it('Initialize the form', () => {
        expect(component.noteForm.value).toEqual({
            note: ''
        });
    });

    it('Test the form submission', fakeAsync(() => {
        spyOn(component['todoistService'], 'updateAssignmentDescription').and.resolveTo(true);
        const closeFormSpy = spyOn(component, 'closeForm');
        component.noteForm.setValue({
            note: 'note'
        });
        component.noteForm.controls['note'].markAsDirty();

        component.updateNote();
        
        expect(component['todoistService'].updateAssignmentDescription)
            .toHaveBeenCalledWith(2, IdType.Native, 'note');
    }));
});

describe('TasknoteComponent Native, Desc', () => {
    let component: TasknoteComponent;
    let fixture: ComponentFixture<TasknoteComponent>;

    const assignment: Assignment = {
        title: 'title',
        description: 'desc',
        user_description: 'user',
        type: 'assignment',
        submission_types: [],
        db_id: 2,
        graded_submissions_exist: false,
        due_at: 'now',
        subtasks: []
    };

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [TasknoteComponent],
            providers: [provideHttpClient()]
        }).compileComponents();

        fixture = TestBed.createComponent(TasknoteComponent);
        component = fixture.componentInstance;
        component.assignment = assignment;
        fixture.detectChanges();
    });

    it('Initialize the form', () => {
        expect(component.noteForm.value).toEqual({
            note: 'user'
        });
    });

    it('Test the form submission', fakeAsync(() => {
        spyOn(component['todoistService'], 'updateAssignmentDescription').and.resolveTo(true);
        const closeFormSpy = spyOn(component, 'closeForm');
        component.noteForm.setValue({
            note: 'note'
        });
        component.noteForm.controls['note'].markAsDirty();

        component.updateNote();
        
        expect(component['todoistService'].updateAssignmentDescription)
            .toHaveBeenCalledWith(2, IdType.Native, 'note');
    }));
});
