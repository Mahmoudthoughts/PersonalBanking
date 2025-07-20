import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './register.html',
  styleUrl: './register.scss'
})
export class Register {
  form: FormGroup;

  constructor(private fb: FormBuilder, private auth: AuthService, private router: Router) {
    this.form = this.fb.nonNullable.group({
      name: '',
      username: '',
      email: '',
      password: ''
    });
  }

  submit() {
    const { name, username, email, password } = this.form.getRawValue();
    this.auth.register({ name, username, email, password }).subscribe({
      next: () => this.router.navigate(['/login'])
    });
  }
}
