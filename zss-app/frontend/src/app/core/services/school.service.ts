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

  getGrades(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/grades`);
  }
  
  recordAbsence(data: { student_id: string, date_from: string, date_to: string, reason: string }): Observable<any> {
    return this.http.post(`${this.apiUrl}/absences`, data);
  }
}