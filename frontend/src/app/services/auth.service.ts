import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { tap } from 'rxjs/operators';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private tokenKey = 'jwt_token';

  constructor(private http: HttpClient) {}

  login(email: string, password: string) {
    return this.http.post<{access_token: string}>(
      '/auth/login',
      { email, password }
    ).pipe(
      tap(res => {
        localStorage.setItem(this.tokenKey, res.access_token);
      })
    );
  }

  get token(): string | null {
    return localStorage.getItem(this.tokenKey);
  }
}
