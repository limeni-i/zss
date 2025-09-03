import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root'
})
export class HealthService {
  private apiUrl = environment.healthApiUrl;

  constructor(private http: HttpClient) { }

  getAppointments(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/appointments`);
  }
  
  scheduleAppointment(data: { doctor_id: string, date: string }): Observable<any> {
    return this.http.post(`${this.apiUrl}/appointments`, data);
  }

  issueCertificate(data: { student_id: string, date_from: string, date_to: string, reason: string }): Observable<any> {
    return this.http.post(`${this.apiUrl}/reports/certificate`, data);
  }
}