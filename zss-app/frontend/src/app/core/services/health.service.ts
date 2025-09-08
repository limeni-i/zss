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

  createTimeslotsForDay(data: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/timeslots/create-day`, data);
  }
  getDoctorTimeslots(doctorId: string): Observable<any[]> {
  return this.http.get<any[]>(`${this.apiUrl}/timeslots/doctor/${doctorId}`);
}
  
  getFreeTimeslots(doctorId: string): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/timeslots/free/${doctorId}`);
  }
  bookTimeslot(slotId: string): Observable<any> {
    return this.http.put(`${this.apiUrl}/timeslots/${slotId}/book`, {});
  }
  getPatientAppointments(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/timeslots/patient`);
  }

  getJustificationRequests(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/justifications`);
  }

  approveRequest(requestId: string): Observable<any> {
    return this.http.put(`${this.apiUrl}/justifications/${requestId}/approve`, {});
  }

  rejectRequest(requestId: string): Observable<any> {
    return this.http.put(`${this.apiUrl}/justifications/${requestId}/reject`, {});
  }

  getJustificationPdf(requestId: string): Observable<Blob> {
  return this.http.get(`${this.apiUrl}/justifications/${requestId}/export-pdf`, {
    responseType: 'blob'
    });
  }

  getConsultationRequests(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/consultations`);
  }


}