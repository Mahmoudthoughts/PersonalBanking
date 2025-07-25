import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { AuthService } from '../../services/auth.service';
import { ActivatedRoute } from '@angular/router';
import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-report',
  standalone: true,
  imports: [CommonModule, HttpClientModule],
  templateUrl: './report.html',
  styleUrl: './report.scss'
})
export class Report implements OnInit {
  html = '';
  pdfUrl = '';

  constructor(private http: HttpClient, private route: ActivatedRoute, private auth: AuthService) {}

  ngOnInit(): void {
    const month = this.route.snapshot.paramMap.get('month') ?? '';
    this.pdfUrl = `${environment.apiUrl}/reports/${month}?format=pdf`;
    this.http
      .get(`${environment.apiUrl}/reports/${month}`, { responseType: 'text', ...this.auth.authHeaders })
      .subscribe(res => (this.html = res));
  }
}
