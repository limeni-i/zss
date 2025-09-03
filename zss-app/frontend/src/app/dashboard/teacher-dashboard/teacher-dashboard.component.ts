import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { AuthService } from 'src/app/core/services/auth.service';
import { SchoolService } from 'src/app/core/services/school.service';

@Component({
  selector: 'app-teacher-dashboard',
  templateUrl: './teacher-dashboard.component.html',
  styleUrls: ['./teacher-dashboard.component.scss']
})

export class TeacherDashboardComponent implements OnInit {
  gradeForm!: FormGroup;
  absenceForm!: FormGroup;
  students: any[] = [];
  parents: any[] = [];
  myAbsences: any[] = [];
  myGrades: any[] = [];
  successMessage: string | null = null;
  currentTab: 'grades' | 'absences' | 'messages' = 'grades';

  messageForm!: FormGroup;
  selectedParentId: string = '';
  conversation: any[] = [];

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private schoolService: SchoolService
  ) {}

  ngOnInit(): void {
    this.loadInitialData();
    this.buildForms();
  }

  loadInitialData() {
    this.authService.getUsersByRole('UCENIK').subscribe(data => this.students = data);
    this.authService.getUsersByRole('RODITELJ').subscribe(data => this.parents = data);
    this.loadMyTeacherData();
  }

  loadMyTeacherData() {
    this.schoolService.getGrades().subscribe(data => this.myGrades = data);
    this.schoolService.getAbsences().subscribe(data => this.myAbsences = data);
  }
  
  buildForms() {
    this.gradeForm = this.fb.group({
      student_id: ['', Validators.required],
      subject: ['', Validators.required],
      value: ['', [Validators.required, Validators.min(1), Validators.max(5)]],
      date: [new Date().toISOString().slice(0, 10), Validators.required]
    });

    this.absenceForm = this.fb.group({
      student_id: ['', Validators.required],
      date_from: ['', Validators.required],
      date_to: ['', Validators.required],
      reason: ['']
    });

    this.messageForm = this.fb.group({
      content: ['', Validators.required],
      receiver_id: ['', Validators.required],
      receiver_role: ['RODITELJ']
    });
  }

  onGradeSubmit() {
    if (this.gradeForm.invalid) return;
    this.schoolService.createGrade(this.gradeForm.value).subscribe(() => {
      this.handleSuccess("Ocena uspešno uneta!", this.gradeForm);
    });
  }

  onAbsenceSubmit() {
    if (this.absenceForm.invalid) return;
    this.schoolService.recordAbsence(this.absenceForm.value).subscribe(() => {
      this.handleSuccess("Izostanak uspešno evidentiran!", this.absenceForm);
    });
  }

  onMessageSubmit() {
    if(this.messageForm.invalid) return;
    this.schoolService.sendMessage(this.messageForm.value).subscribe(() => {
      this.handleSuccess("Poruka poslata!", this.messageForm);
      this.loadConversation();
    });
  }
  
  handleSuccess(message: string, form: FormGroup) {
    this.successMessage = message;
    this.loadMyTeacherData();
    form.reset();
    setTimeout(() => this.successMessage = null, 3000);
  }

  loadConversation() {
    if (!this.selectedParentId) return;
    this.messageForm.patchValue({ receiver_id: this.selectedParentId });
    this.schoolService.getConversation(this.selectedParentId).subscribe(data => {
      this.conversation = data;
    });
  }
}