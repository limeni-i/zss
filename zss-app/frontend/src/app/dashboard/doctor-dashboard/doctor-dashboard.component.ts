import { Component, OnInit } from '@angular/core';
import { HealthService } from 'src/app/core/services/health.service';
import { CalendarEvent } from 'angular-calendar';
import { map } from 'rxjs/operators';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import {jwtDecode} from 'jwt-decode';

@Component({
  selector: 'app-doctor-dashboard',
  templateUrl: './doctor-dashboard.component.html',
  styleUrls: ['./doctor-dashboard.component.scss']
})
export class DoctorDashboardComponent implements OnInit {
  viewDate: Date = new Date();
  events: CalendarEvent[] = [];
  dayForm!: FormGroup;
  requests: any[] = [];
  consultationRequests: any[] = [];

  constructor(private healthService: HealthService, private fb: FormBuilder) {}

  ngOnInit(): void {
    this.loadMyCalendar();
    this.dayForm = this.fb.group({
      date: ['', Validators.required],
      start_hour: ['9', Validators.required],
      end_hour: ['17', Validators.required]
    });
    this.loadRequests();
    this.loadConsultationRequests();
  }

  loadMyCalendar() {
    const token = localStorage.getItem('authToken');
    if (!token) return;
    const decodedToken: any = jwtDecode(token);
    const doctorId = decodedToken.user_id;

    this.healthService.getDoctorTimeslots(doctorId).pipe(
      map(slots => slots.map(slot => {
        const startTime = new Date(slot.start_time.$date);
        const endTime = new Date(slot.end_time.$date);
        
        let title = slot.status === 'SLOBODAN' ? 'Slobodan' : `Rezervisano (Pacijent: ${slot.patient_id})`;
        
        return {
          start: startTime,
          end: endTime,
          title: title,
          color: { 
            primary: slot.status === 'SLOBODAN' ? '#1e90ff' : '#ad2121',
            secondary: '#D1E8FF' 
          }
        };
      }))
    ).subscribe(events => this.events = events);
  }

  createDay() {
    if(this.dayForm.invalid) return;
    this.healthService.createTimeslotsForDay(this.dayForm.value).subscribe(() => {
      this.loadMyCalendar();
    });
  }

  loadRequests() {
    this.healthService.getJustificationRequests().subscribe(data => this.requests = data);
  }

  approve(requestId: string) {
    this.healthService.approveRequest(requestId).subscribe(() => this.loadRequests());
  }

  reject(requestId: string) {
    this.healthService.rejectRequest(requestId).subscribe(() => this.loadRequests());
  }

  loadConsultationRequests() {
  this.healthService.getConsultationRequests().subscribe(data => this.consultationRequests = data);
}
}