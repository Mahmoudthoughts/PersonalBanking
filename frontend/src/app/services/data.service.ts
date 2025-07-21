import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { AuthService } from './auth.service';
import { environment } from '../../environments/environment';

@Injectable({ providedIn: 'root' })
export class DataService {
  constructor(private http: HttpClient, private auth: AuthService) {}

  private get headers() {
    return this.auth.authHeaders;
  }

  getTransactions() {
    return this.http.get<any[]>(`${environment.apiUrl}/transactions`, this.headers);
  }

  createTransaction(payload: any) {
    return this.http.post(`${environment.apiUrl}/transactions`, payload, this.headers);
  }

  getReport(month: string) {
    return this.http.get(`${environment.apiUrl}/reports/${month}`, {
      responseType: 'text',
      ...this.headers
    });
  }
}
