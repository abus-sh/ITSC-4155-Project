import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CanvasService } from '../canvas.service';

interface Assignment {
    assignment_id: string;
    name: string;
    score: number;
    points_possible: number;
}

export interface Course {
    id: number;
    name: string;
    assignments: Assignment[];
    showAssignments?: boolean;
}

@Component({
    selector: 'app-gradesim',
    standalone: true,
    imports: [CommonModule],
    templateUrl: './gradesim.component.html',
    styleUrls: ['./gradesim.component.scss']
})
export class GradesimComponent {
    public gradeSim: Course[] = [];
    public potentialScores: { [courseId: number]: number } = {};

    toggleAssignments(course: Course): void {
        course.showAssignments = !course.showAssignments;
    }

    editScore(course: Course, assignment: Assignment, newScore: number): void {
        assignment.score = newScore;
        this.calculatePotentialScore(course);
    }

    calculatePotentialScore(course: Course): void {
        const totalScore = course.assignments.reduce((sum, a) => sum + (a.score || 0), 0);
        const totalPoints = course.assignments.reduce((sum, a) => sum + (a.points_possible || 0), 0);
        const potentialScore = (totalPoints > 0) ? (totalScore / totalPoints) * 100 : 0;

        this.potentialScores[course.id] = parseFloat(potentialScore.toFixed(2));
    }

    calculatePotentialScores(): void {
        this.gradeSim.forEach((course) => this.calculatePotentialScore(course));
    }
}
