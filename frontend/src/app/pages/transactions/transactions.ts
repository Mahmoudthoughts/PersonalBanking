import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient, HttpClientModule, HttpParams } from '@angular/common/http';
import { AuthService } from '../../services/auth.service';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
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
  allTransactions: any[] = [];


  constructor(private http: HttpClient, private route: ActivatedRoute, private auth: AuthService) {}

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
      .get<any[]>(`${environment.apiUrl}/transactions`, { params, ...this.auth.authHeaders })
      .subscribe(res => {
        this.transactions = res;
      });
    this.http.get<any[]>(`${environment.apiUrl}/transactions`, this.auth.authHeaders).subscribe(res => {
      this.allTransactions = res;
      this.applyFilters();
      this.route.queryParams.subscribe(() => this.applyFilters());
    });
  }

  private applyFilters() {
    const params = this.route.snapshot.queryParams;
    let filtered = [...this.allTransactions];

    if (params['category']) {
      filtered = filtered.filter(t => {
        const cat = (t.tags && t.tags.length) ? t.tags[0].name : 'Uncategorized';
        return cat === params['category'];
      });
    }

    if (params['month']) {
      filtered = filtered.filter(t => (t.date as string).startsWith(params['month']));
    }

    this.transactions = filtered;
  }
}
