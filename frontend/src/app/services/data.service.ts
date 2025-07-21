import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';

@Injectable({ providedIn: 'root' })
export class DataService {
  constructor(private http: HttpClient) {}

  getTransactions() {
    return this.http.get<any[]>(`${environment.apiUrl}/transactions`);
  }

  createTransaction(payload: any) {
    return this.http.post(`${environment.apiUrl}/transactions`, payload);
  }

  getReport(month: string) {
    return this.http.get(`${environment.apiUrl}/reports/${month}`, {
      responseType: 'text'
    });
  }
}
