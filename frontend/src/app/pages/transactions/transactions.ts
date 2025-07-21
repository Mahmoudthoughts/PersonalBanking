import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient, HttpClientModule, HttpParams } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-transactions',
  standalone: true,
  imports: [CommonModule, HttpClientModule, FormsModule],
  templateUrl: './transactions.html',
  styleUrl: './transactions.scss'
})
export class Transactions implements OnInit {
  transactions: any[] = [];
  filters = {
    amount: '',
    tag: '',
    cardholder: '',
    desc: '',
    start: '',
    end: ''
  };

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.load();
  }

  load() {
    let params = new HttpParams();
    for (const [key, value] of Object.entries(this.filters)) {
      if (value) {
        params = params.set(key, value as string);
      }
    }
    this.http
      .get<any[]>(`${environment.apiUrl}/transactions`, { params })
      .subscribe(res => {
        this.transactions = res;
      });
  }
}
