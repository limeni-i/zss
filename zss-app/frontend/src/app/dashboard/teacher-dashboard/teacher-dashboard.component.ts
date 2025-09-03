import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { AuthService } from 'src/app/core/services/auth.service';
import { SchoolService } from 'src/app/core/services/school.service';
import { map } from 'rxjs/operators';

@Component({
  selector: 'app-teacher-dashboard',
  templateUrl: './teacher-dashboard.component.html',
  styleUrls: ['./teacher-dashboard.component.scss']
})
export class TeacherDashboardComponent implements OnInit {
  students: any[] = [];
  absenceForm!: FormGroup;
  successMessage: string | null = null;
  errorMessage: string | null = null;

  constructor(
    private schoolService: SchoolService,
    private authService: AuthService,
    private fb: FormBuilder
  ) {}

  ngOnInit(): void {
    this.authService.getUsers().pipe(
      map(users => users.filter(user => user.role === 'UCENIK'))
    ).subscribe(data => this.students = data);

    this.absenceForm = this.fb.group({
      student_id: ['', Validators.required],
      date_from: ['', Validators.required],
      date_to: ['', Validators.required],
      reason: ['']
    });
  }

  onSubmit(): void {
    if (this.absenceForm.invalid) return;
    this.successMessage = null;
    this.errorMessage = null;

    this.schoolService.recordAbsence(this.absenceForm.value).subscribe({
      next: (res) => {
        this.successMessage = res.message;
        this.absenceForm.reset();
      },
      error: (err) => this.errorMessage = "Greška pri evidenciji izostanka."
    });
  }
}