import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from 'src/app/core/services/auth.service';

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
    if (this.loginForm.invalid) {
      return;
    }

    this.errorMessage = null; 

    this.authService.login(this.loginForm.value).subscribe({
      next: () => {
        console.log('Login uspešan!');
        this.router.navigate(['/']); 
      },
      error: (err) => {
        console.error('Greška pri logovanju:', err);
        this.errorMessage = 'Neispravan email ili lozinka. Pokušajte ponovo.';
      }
    });
  }
}