import { Component, OnInit } from '@angular/core';
import { AuthService } from 'src/app/core/services/auth.service';
import { HealthService } from 'src/app/core/services/health.service';
import { CalendarEvent } from 'angular-calendar';
import { map } from 'rxjs/operators';
import { isSameDay, isSameMonth } from 'date-fns';

@Component({
  selector: 'app-patient-dashboard',
  templateUrl: './patient-dashboard.component.html',
  styleUrls: ['./patient-dashboard.component.scss']
})
export class PatientDashboardComponent implements OnInit {
  myAppointments: any[] = [];
  doctors: any[] = [];
  selectedDoctorId: string = '';
  viewDate: Date = new Date();
  events: CalendarEvent[] = [];
  activeDayIsOpen: boolean = false;
  availableSlotsForSelectedDay: CalendarEvent[] = [];

  successMessage: string | null = null;
  errorMessage: string | null = null;

  constructor(
    private healthService: HealthService,
    private authService: AuthService
  ) {}

  ngOnInit(): void {
    this.loadMyInitialData();
    this.authService.getUsersByRole('LEKAR').subscribe(data => this.doctors = data);
  }

  loadMyInitialData(): void {
    this.healthService.getPatientAppointments().subscribe(data => this.myAppointments = data);
  }

  onDoctorSelected(): void {
    if (!this.selectedDoctorId) return;
    
    this.activeDayIsOpen = false;
    this.availableSlotsForSelectedDay = [];

    this.healthService.getDoctorTimeslots(this.selectedDoctorId).pipe(
      map(slots => slots.map(slot => {
        const startTime = new Date(slot.start_time.$date);
        const endTime = new Date(slot.end_time.$date);

        return {
          start: startTime,
          end: endTime,
          title: slot.status === 'SLOBODAN' ? `Slobodan` : `Zauzet`,
          color: { primary: slot.status === 'SLOBODAN' ? '#1e90ff' : '#ad2121', secondary: '#D1E8FF' },
          meta: {
            slot_id: slot._id.$oid,
            status: slot.status
          }
        };
      }))
    ).subscribe(events => {
        this.events = events;
    });
  }
  
  dayClicked({ date, events }: { date: Date; events: CalendarEvent[] }): void {
    if (isSameMonth(date, this.viewDate)) {
      if ((isSameDay(this.viewDate, date) && this.activeDayIsOpen) || events.length === 0) {
        this.activeDayIsOpen = false;
      } else {
        this.activeDayIsOpen = true;
        this.viewDate = date;
        this.availableSlotsForSelectedDay = events.filter(event => event.meta.status === 'SLOBODAN');
      }
    } else {
       this.viewDate = date;
       this.activeDayIsOpen = false;
       this.availableSlotsForSelectedDay = [];
    }
  }

  bookSlot(slotId: string): void {
    this.successMessage = null;
    this.errorMessage = null;

    this.healthService.bookTimeslot(slotId).subscribe({
      next: () => {
        this.successMessage = "Termin je uspešno rezervisan!";
        this.loadMyInitialData();
        this.onDoctorSelected();
        this.activeDayIsOpen = false;
        setTimeout(() => this.successMessage = null, 4000);
      },
      error: (err) => {
        this.errorMessage = "Došlo je do greške ili je termin u međuvremenu zauzet.";
        setTimeout(() => this.errorMessage = null, 4000);
      }
    });
  }
}