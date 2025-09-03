import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { AuthService } from 'src/app/core/services/auth.service';
import { HealthService } from 'src/app/core/services/health.service';
import { filter, map } from 'rxjs/operators';

@Component({
  selector: 'app-patient-dashboard',
  templateUrl: './patient-dashboard.component.html',
  styleUrls: ['./patient-dashboard.component.scss']
})
export class PatientDashboardComponent implements OnInit {
  appointments: any[] = [];
  doctors: any[] = [];
  appointmentForm!: FormGroup;
  successMessage: string | null = null;
  errorMessage: string | null = null;

  constructor(
    private healthService: HealthService,
    private authService: AuthService,
    private fb: FormBuilder
  ) {}

  ngOnInit(): void {
    this.loadAppointments();
    this.loadDoctors();

    this.appointmentForm = this.fb.group({
      doctor_id: ['', Validators.required],
      date: ['', Validators.required]
    });
  }

  loadAppointments(): void {
    this.healthService.getAppointments().subscribe(data => this.appointments = data);
  }

  loadDoctors(): void {
    this.authService.getUsers().pipe(
      map(users => users.filter(user => user.role === 'LEKAR'))
    ).subscribe(data => this.doctors = data);
  }

  onSubmit(): void {
    if (this.appointmentForm.invalid) return;
    this.successMessage = null;
    this.errorMessage = null;

    this.healthService.scheduleAppointment(this.appointmentForm.value).subscribe({
      next: () => {
        this.successMessage = "Pregled je uspešno zakazan!";
        this.loadAppointments();
        this.appointmentForm.reset();
      },
      error: (err) => this.errorMessage = "Došlo je do greške."
    });
  }
}