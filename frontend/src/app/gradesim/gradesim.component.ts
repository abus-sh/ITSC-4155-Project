import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Course, CourseLog, GradeAssignment } from '../courses/courses.component';
import { ChangeDetectorRef } from '@angular/core';

@Component({
    selector: 'app-gradesim',
    standalone: true,
    imports: [CommonModule],
    templateUrl: './gradesim.component.html',
    styleUrls: ['./gradesim.component.scss']
})
export class GradesimComponent implements OnInit {
    @Input() full_course?: Course;
    @Output() closeGradeSimAction = new EventEmitter();
    log_course?: Course;

    constructor(private cdr: ChangeDetectorRef) {
    }

    ngOnInit(): void {
        this.log_course = this.full_course;
    }

    closeGradeSimForm() {
        this.closeGradeSimAction.emit();
    }

    calculateFinalGrade(gradeScale: CourseLog[]): number {
        /*
        * This function calculates the final grade of a course based on the grade scale.
        */
        let topCalc = 0.0;
        let bottomCalc = 0.0;

        for (const category of gradeScale) {
            const weight = category.weight;
            const assignments = category.assignments;

            if (!assignments.length) {
                continue;
            }

            const totalMaxScore = assignments
                .filter(a => !a.omit_from_final_grade && a.score !== null)
                .reduce((sum, a) => sum + a.max_score, 0);

            const totalScore = assignments
                .filter(a => !a.omit_from_final_grade && a.score !== null)
                .reduce((sum, a) => sum + a.score, 0);

            if (totalMaxScore > 0) {
                topCalc += Math.round(((totalScore * 100) / totalMaxScore) * 100) / 100 * weight;
                bottomCalc += weight;
            }
        }

        return bottomCalc > 0 ? topCalc / bottomCalc : 0;
    }

    onScoreChange(assignment: GradeAssignment, event: any) {
        /*
        * This function is called whenever the user changes the score of an assignment.
        */
        let newScore = +event.target.value;
        if (newScore < 0) {
            newScore = 0;
            event.target.value = 0;
        }
        assignment.score = newScore;
        if (this.log_course && this.log_course.gradelog) {
            const finalGrade = this.calculateFinalGrade(this.log_course.gradelog);
            console.log(`Final Grade: ${finalGrade.toFixed(2)}%`);
            document.getElementById('potentialScore')!.innerText = `Final Grade: ${finalGrade.toFixed(2)}%`;
        }
        console.log('Score changed');
    }
}
