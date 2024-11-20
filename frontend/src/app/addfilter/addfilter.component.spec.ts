import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AddfilterComponent } from './addfilter.component';
import { provideHttpClient } from '@angular/common/http';

describe('AddfilterComponent', () => {
  let component: AddfilterComponent;
  let fixture: ComponentFixture<AddfilterComponent>;

  beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [AddfilterComponent],
            providers: [provideHttpClient()]
        })
        .compileComponents();

        fixture = TestBed.createComponent(AddfilterComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('Creating the component', () => {
        expect(component).toBeTruthy();
    });

    it('Test initial form value', () => {
        expect(component.addFilterForm.value).toEqual({
            keyword: ''
        });
    });

    it('Test filter creation', () => {
        spyOn(component['filterService'], 'addFilter').and.resolveTo(true);
        component.addFilterForm.setValue({
            keyword: 'testing'
        });

        component.addFilter();

        expect(component['filterService'].addFilter).toHaveBeenCalledWith('testing');
    });

    it('Test filter deletion', () => {
        spyOn(component['filterService'], 'deleteFilter').and.resolveTo(false);

        component.deleteFilter('testing');

        expect(component['filterService'].deleteFilter).toHaveBeenCalledWith('testing');
    });

    it('Test form closing', () => {
        spyOn(component.closeFormAction, 'emit');

        component.closeForm();

        expect(component.closeFormAction.emit).toHaveBeenCalled();
    });
});
