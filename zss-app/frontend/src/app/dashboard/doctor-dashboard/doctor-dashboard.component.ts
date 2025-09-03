import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { AuthService } from 'src/app/core/services/auth.service';
import { HealthService } from 'src/app/core/services/health.service';
import { map } from 'rxjs/operators';

@Component({
  selector: 'app-doctor-dashboard',
  templateUrl: './doctor-dashboard.component.html',
  styleUrls: ['./doctor-dashboard.component.scss']
})
export class DoctorDashboardComponent implements OnInit {
  appointments: any[] = [];
  students: any[] = [];
  certificateForm!: FormGroup;
  successMessage: string | null = null;
  errorMessage: string | null = null;

  constructor(
    private healthService: HealthService,
    private authService: AuthService,
    private fb: FormBuilder
  ) {}

  ngOnInit(): void {
    this.healthService.getAppointments().subscribe(data => this.appointments = data);
    
    this.authService.getUsers().pipe(
      map(users => users.filter(user => user.role === 'UCENIK'))
    ).subscribe(data => this.students = data);

    this.certificateForm = this.fb.group({
      student_id: ['', Validators.required],
      date_from: ['', Validators.required],
      date_to: ['', Validators.required],
      reason: ['Lekarsko opravdanje', Validators.required]
    });
  }

  onSubmit(): void {
    if (this.certificateForm.invalid) return;
    this.successMessage = null;
    this.errorMessage = null;

    this.healthService.issueCertificate(this.certificateForm.value).subscribe({
      next: (res) => this.successMessage = res.message,
      error: (err) => this.errorMessage = "Greška pri izdavanju potvrde.",
    });
  }
}