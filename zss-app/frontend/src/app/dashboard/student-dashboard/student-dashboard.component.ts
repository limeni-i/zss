import { Component, OnInit } from '@angular/core';
import { SchoolService } from 'src/app/core/services/school.service';

@Component({
  selector: 'app-student-dashboard',
  templateUrl: './student-dashboard.component.html',
  styleUrls: ['./student-dashboard.component.scss']
})
export class StudentDashboardComponent implements OnInit {
  grades: any[] = [];

  constructor(private schoolService: SchoolService) { }

  ngOnInit(): void {
    this.schoolService.getGrades().subscribe(data => {
      this.grades = data;
    });
  }
}