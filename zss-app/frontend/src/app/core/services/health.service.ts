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
  
  scheduleAppointment(data: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/appointments`, data);
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
}