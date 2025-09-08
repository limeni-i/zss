import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormsModule } from '@angular/forms';


import { DashboardRoutingModule } from './dashboard-routing.module';
import { PatientDashboardComponent } from './patient-dashboard/patient-dashboard.component';
import { DoctorDashboardComponent } from './doctor-dashboard/doctor-dashboard.component';
import { StudentDashboardComponent } from './student-dashboard/student-dashboard.component';
import { TeacherDashboardComponent } from './teacher-dashboard/teacher-dashboard.component';
import { ParentDashboardComponent } from './parent-dashboard/parent-dashboard.component';
import { AdminDashboardComponent } from './admin-dashboard/admin-dashboard.component';
import { CalendarModule } from 'angular-calendar';


@NgModule({
  declarations: [
    PatientDashboardComponent,
    DoctorDashboardComponent,
    StudentDashboardComponent,
    TeacherDashboardComponent,
    ParentDashboardComponent,
    AdminDashboardComponent
  ],

  imports: [
    CommonModule,
    DashboardRoutingModule,
    ReactiveFormsModule,
    FormsModule,
    CalendarModule
  ]
})

export class DashboardModule { }
