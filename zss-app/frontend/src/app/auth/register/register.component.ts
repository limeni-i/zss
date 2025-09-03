import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from 'src/app/core/services/auth.service';

@Component({
  selector: 'app-register',
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.scss']
})
export class RegisterComponent implements OnInit {
  registerForm!: FormGroup;
  errorMessage: string | null = null;

  roles = ['PACIJENT', 'LEKAR', 'UCENIK', 'NASTAVNIK', 'RODITELJ', 'ADMIN'];

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.registerForm = this.fb.group({
      name: ['', [Validators.required]],
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(6)]],
      role: ['', [Validators.required]] 
    });
  }

  onSubmit(): void {
    if (this.registerForm.invalid) {
      return;
    }

    this.errorMessage = null;

    this.authService.register(this.registerForm.value).subscribe({
      next: () => {
        console.log('Registracija uspešna!');
  
        this.router.navigate(['/auth/login']);
      },
      error: (err) => {
        console.error('Greška pri registraciji:', err);
        if (err.status === 409) { 
          this.errorMessage = 'Korisnik sa unetim email-om već postoji.';
        } else {
          this.errorMessage = 'Došlo je do greške. Molimo pokušajte ponovo.';
        }
      }
    });
  }
}