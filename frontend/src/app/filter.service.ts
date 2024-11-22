import { Injectable } from '@angular/core';
import { firstValueFrom, Subject } from 'rxjs';
import { getBackendURL } from '../config';
import { HttpClient } from '@angular/common/http';

interface FilterApiResponse {
    filters: string[];
};

@Injectable({
    providedIn: 'root'
})
export class FilterService {
    filters$ = new Subject<string[]>();
    private filters: string[] = [];

    private getFiltersUrl = getBackendURL() + '/api/v1/filters';
    private createFilterUrl = getBackendURL() + '/api/v1/filters/new';
    private deleteFilterUrl = getBackendURL() + '/api/v1/filters';

    constructor(private http: HttpClient) {}

    async getFilters() {
        try {
            const filters = await firstValueFrom(this.http.get<FilterApiResponse>(
                this.getFiltersUrl,
                { withCredentials: true })
            );

            this.filters = filters.filters;
            this.filters$.next(this.filters);
        } catch {
            return false;
        }
        
        return true;
    }

    async addFilter(filter: string) {
        // Prevent duplicate filters
        if (!this.filters.includes(filter)) {
            // Send an immediate update to make things feel faster
            this.filters.push(filter);
            this.filters$.next(this.filters);

            try {
                await firstValueFrom(this.http.post(this.createFilterUrl, {
                    'filter': filter
                }, { withCredentials: true }));
            } catch {
                // Remove it from the list on error
                // Don't bother making an API call since the filter wasn't created
                this.deleteFilter(filter, false);
                return false;
            }
        }

        return true;
    }

    async deleteFilter(filter: string, skipApiCall=false) {
        // Send an update assuming the delete API call will succeed
        this.filters = this.filters.filter(val => val !== filter);
        this.filters$.next(this.filters);

        if (!skipApiCall) {
            try {
                await firstValueFrom(this.http.delete(this.deleteFilterUrl, {
                    withCredentials: true,
                    body: {
                        'filter': filter
                    }
                }));
            } catch {
                // In case of failure, un-delete the filter
                this.filters.push(filter);
                this.filters$.next(this.filters);

                return false;
            }
        }

        return true;
    }
}

