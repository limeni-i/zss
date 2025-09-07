import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root'
})
export class SchoolService {
  private apiUrl = environment.schoolApiUrl;

  constructor(private http: HttpClient) { }

  // Ocene
  createGrade(data: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/grades`, data);
  }
  getGrades(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/grades`);
  }

  // Izostanci
  recordAbsence(data: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/absences`, data);
  }
  getAbsences(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/absences`);
  }
  requestJustification(absenceId: string, data: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/absences/${absenceId}/request-justification`, data);
  }

  sendMessage(data: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/messages`, data);
  }
  getConversation(otherUserId: string): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/messages/conversation/${otherUserId}`);
  }

  getGradesPdf(): Observable<Blob> {
  return this.http.get(`${this.apiUrl}/grades/export-pdf`, {
    responseType: 'blob'
  });
  }

  downloadJustificationPdf(absenceId: string): Observable<Blob> {
    return this.http.get(`${this.apiUrl}/absences/${absenceId}/download-justification`, {
      responseType: 'blob'
    });
  }

}