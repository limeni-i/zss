import { Component, OnInit } from '@angular/core';
import { HealthService } from 'src/app/core/services/health.service';

@Component({
  selector: 'app-doctor-dashboard',
  templateUrl: './doctor-dashboard.component.html',
  styleUrls: ['./doctor-dashboard.component.scss']
})
export class DoctorDashboardComponent implements OnInit {
  requests: any[] = [];

  constructor(private healthService: HealthService) {}

  ngOnInit(): void {
    this.loadRequests();
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

}