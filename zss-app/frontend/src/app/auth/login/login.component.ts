import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from 'src/app/core/services/auth.service';
import { jwtDecode } from 'jwt-decode';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})

export class LoginComponent implements OnInit {
  loginForm!: FormGroup; // '!' znači da ćemo je sigurno inicijalizovati kasnije
  errorMessage: string | null = null;

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required]]
    });
  }

  onSubmit(): void {
  if (this.loginForm.invalid) { return; }
  this.errorMessage = null;

  this.authService.login(this.loginForm.value).subscribe({
    next: (response) => {
      console.log('Login uspešan!');
      
      const token = response.token;
      const decodedToken: any = jwtDecode(token);
      const userRole = decodedToken.role;

      switch (userRole) {
        case 'PACIJENT':
          this.router.navigate(['/dashboard/patient']);
          break;
        case 'LEKAR':
          this.router.navigate(['/dashboard/doctor']);
          break;
        case 'UCENIK':
          this.router.navigate(['/dashboard/student']);
          break;
        case 'NASTAVNIK':
          this.router.navigate(['/dashboard/teacher']);
          break;
        case 'RODITELJ':
          this.router.navigate(['/dashboard/parent']);
          break;
        case 'ADMIN':
          this.router.navigate(['/dashboard/admin']);
          break;
        default:
          this.router.navigate(['/']);
      }
    },
    error: (err) => {
      this.errorMessage = 'Neispravan email ili lozinka.';
    }
  });
}
}