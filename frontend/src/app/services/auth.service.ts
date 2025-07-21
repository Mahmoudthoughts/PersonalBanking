import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { environment } from '../../environments/environment';
import { tap } from 'rxjs/operators';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private tokenKey = 'jwt_token';

  constructor(private http: HttpClient, private router: Router) {}

  login(email: string, password: string) {
    return this.http.post<{access_token: string}>(
      `${environment.apiUrl}/auth/login`,
      { email, password }
    ).pipe(
      tap(res => {
        localStorage.setItem(this.tokenKey, res.access_token);
      })
    );
  }

  register(data: { name?: string; username?: string; email: string; password: string }) {
    return this.http.post<{id: number}>(
      `${environment.apiUrl}/auth/register`,
      data
    );
  }

  logout(redirect: boolean = true): void {
    localStorage.removeItem(this.tokenKey);
    if (redirect) {
      this.router.navigate(['/login']);
    }
  }

  get token(): string | null {
    return localStorage.getItem(this.tokenKey);
  }

  logout(): void {
    localStorage.clear();
    this.router.navigate(['/login']);
  }
}
