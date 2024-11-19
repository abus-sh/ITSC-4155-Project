import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Output } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { FilterService } from '../filter.service';

@Component({
    selector: 'app-addfilter',
    standalone: true,
    imports: [ReactiveFormsModule, CommonModule],
    templateUrl: './addfilter.component.html',
    styleUrl: './addfilter.component.scss'
})
export class AddfilterComponent {
    @Output() closeFormAction = new EventEmitter();

    addFilterForm: FormGroup;

    errorMsg = '';

    private maxKeywordLen = 50;

    filters: string[] = [];

    constructor(private fb: FormBuilder, private filterService: FilterService) {
        this.addFilterForm = this.fb.group({
            keyword: ['', {
                validators: [
                    Validators.required,
                    Validators.maxLength(this.maxKeywordLen)
                ]
            }]
        });

        this.filterService.filters$.subscribe(filters => this.filters = filters);
        this.filterService.getFilters();
    }

    addFilter() {
        const keyword = this.addFilterForm.controls['keyword'].value;

        if (!this.addFilterForm.valid) {
            // Determine relevant error message
            if (keyword === '') {
                this.errorMsg = 'Please provide a filter.';
            } else if (keyword.length > this.maxKeywordLen) {
                this.errorMsg = `Filters may only be ${this.maxKeywordLen} characters long.`;
            } else {
                this.errorMsg = 'An unknown error has occurred. Please try again.';
            }
            return;
        }

        // Clear the error message
        this.errorMsg = '';
        
        if (!this.filterService.addFilter(keyword)) {
            this.errorMsg = 'An API error has occurred. Please try again.';
        }

        this.addFilterForm.reset();
    }

    deleteFilter(filter: string) {
        this.filterService.deleteFilter(filter);
    }

    closeForm() {
        this.closeFormAction.emit();
    }
}
