import { OrderByPipe } from './date.pipe';

describe('OrderByPipe', () => {
    let pipe: OrderByPipe;

    beforeEach(() => {
        pipe = new OrderByPipe();
    });

    it('Create an OrderByPipe instance', () => {
        expect(pipe).toBeTruthy();
    });

    it('Sort array by dueDate field', () => {
        const array = [
            { dueDate: '2023-10-10' },
            { dueDate: '2023-10-08' },
            { dueDate: '2023-10-09' }
        ];
        const sortedArray = pipe.transform(array, 'dueDate');
        expect(sortedArray).toEqual([
            { dueDate: '2023-10-08' },
            { dueDate: '2023-10-09' },
            { dueDate: '2023-10-10' }
        ]);
    });

    it('Return the same array if field to sort by is not provided', () => {
        const array = [
            { dueDate: '2023-10-10' },
            { dueDate: '2023-10-08' },
            { dueDate: '2023-10-09' }
        ];
        const result = pipe.transform(array, '');
        expect(result).toEqual(array);
    });

    it("Return the empty array if it's empty", () => {
        const result = pipe.transform([], 'dueDate');
        expect(result).toEqual([]);
    });
});
