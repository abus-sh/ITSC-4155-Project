import { Pipe, PipeTransform } from '@angular/core';
import { Assignment } from '../dashboard/dashboard.component';

@Pipe({
    name: 'filter',
    standalone: true,
    pure: false
})
export class FilterPipe implements PipeTransform {
    // Removes assignments that contain any string in args[0]
    transform(value: Assignment[], ...args: unknown[]): Assignment[] {
        console.log('hi');

        // If no array was given to filter against, don't filter
        if (args.length === 0 || !Array.isArray(args[0])) {
            return value;
        }

        const filters = args[0];

        // Love some O(n^2) code
        return value.filter(assign => {
            for (let filter of filters) {
                if (assign.title.includes(filter)) {
                    return false;
                }
            }
            return true;
        });
    }

}
