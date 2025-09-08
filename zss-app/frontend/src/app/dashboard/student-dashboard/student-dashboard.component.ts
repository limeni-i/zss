import { Component, OnInit } from '@angular/core';
import { AuthService } from 'src/app/core/services/auth.service';
import { SchoolService } from 'src/app/core/services/school.service';

@Component({
  selector: 'app-student-dashboard',
  templateUrl: './student-dashboard.component.html',
  styleUrls: ['./student-dashboard.component.scss']
})
export class StudentDashboardComponent implements OnInit {
  grades: any[] = [];
  absences: any[] = [];
  doctors: any[] = [];
  selectedDoctorId: string = '';
  successMessage: string | null = null;
  errorMessage: string | null = null;

  constructor(
    private schoolService: SchoolService,
    private authService: AuthService
  ) {}

  ngOnInit(): void {
    this.loadData();
    this.authService.getUsersByRole('LEKAR').subscribe(data => this.doctors = data);
  }

  loadData() {
    this.schoolService.getGrades().subscribe(data => this.grades = data);
    this.schoolService.getAbsences().subscribe(data => this.absences = data);
  }

  requestJustification(absence: any) {
    if (!this.selectedDoctorId) {
      alert("Molimo izaberite lekara.");
      return;
    }
    const payload = { doctor_id: this.selectedDoctorId };
    this.schoolService.requestJustification(absence._id.$oid, payload).subscribe({
  next: () => {
    this.successMessage = "Zahtev uspešno poslat!";
    this.loadData();
    setTimeout(() => this.successMessage = null, 3000);
  },
  error: (err) => {
    this.errorMessage = err.error.message || 'Došlo je do nepoznate greške.';
    setTimeout(() => this.errorMessage = null, 5000);
  }
});

  }

  downloadGradesPdf() {
  this.schoolService.getGradesPdf().subscribe(blob => {
    const a = document.createElement('a');
    const objectUrl = URL.createObjectURL(blob);
    a.href = objectUrl;
    a.download = 'svedocanstvo.pdf';
    a.click();
    URL.revokeObjectURL(objectUrl);
  });
}

}