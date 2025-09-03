import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { AuthService } from 'src/app/core/services/auth.service';
import { SchoolService } from 'src/app/core/services/school.service';

@Component({
  selector: 'app-parent-dashboard',
  templateUrl: './parent-dashboard.component.html',
  styleUrls: ['./parent-dashboard.component.scss']
})
export class ParentDashboardComponent implements OnInit {
  teachers: any[] = [];
  messageForm!: FormGroup;
  selectedTeacherId: string = '';
  conversation: any[] = [];
  successMessage: string | null = null;
  
  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private schoolService: SchoolService
  ) {}

  ngOnInit(): void {
    this.authService.getUsersByRole('NASTAVNIK').subscribe(data => this.teachers = data);
    this.messageForm = this.fb.group({
      content: ['', Validators.required],
      receiver_id: ['', Validators.required],
      receiver_role: ['NASTAVNIK']
    });
  }

  loadConversation() {
    if (!this.selectedTeacherId) return;
    this.messageForm.patchValue({ receiver_id: this.selectedTeacherId });
    this.schoolService.getConversation(this.selectedTeacherId).subscribe(data => {
      this.conversation = data;
    });
  }

  onMessageSubmit() {
    if (this.messageForm.invalid) return;
    this.schoolService.sendMessage(this.messageForm.value).subscribe(() => {
      this.successMessage = "Poruka poslata!";
      this.loadConversation();
      this.messageForm.get('content')?.reset();
      setTimeout(() => this.successMessage = null, 3000);
    });
  }
}