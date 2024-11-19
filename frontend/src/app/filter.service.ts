import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';

@Injectable({
    providedIn: 'root'
})
export class FilterService {
    filters$ = new Subject<string[]>();
    private filters: string[] = [];

    async getFilters() {
        // TODO: replace with real fetching
        this.filters = [
            'Extra'
        ];

        this.filters$.next(this.filters);
    }

    addFilter(filter: string) {
        // Prevent duplicate filters
        if (!this.filters.includes(filter)) {
            // TODO: add the filter via the API
            this.filters.push(filter);

            this.filters$.next(this.filters);
        }
    }

    deleteFilter(filter: string) {
        this.filters = this.filters.filter(val => val !== filter);
        this.filters$.next(this.filters);
    }
}

