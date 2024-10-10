import { Pipe, PipeTransform } from "@angular/core";


// Sort array by due date
@Pipe({
    name: 'orderBy',
    standalone: true,
})
export class OrderByPipe implements PipeTransform {
    transform(array: any[], field: string): any[] {
        if (!array || !field) return array;
        return array.sort((a, b) => new Date(a[field]).getTime() - new Date(b[field]).getTime());
    }
}