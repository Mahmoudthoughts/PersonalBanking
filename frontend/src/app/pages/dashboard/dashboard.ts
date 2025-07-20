import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DataService } from '../../services/data.service';
import Chart from 'chart.js/auto';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.scss'
})
export class Dashboard implements OnInit {
  constructor(private data: DataService) {}

  ngOnInit(): void {
    this.data.getTransactions().subscribe(trans => {
      const totals: { [key: string]: number } = {};
      for (const t of trans as any[]) {
        const key = t.cardholder_id ?? 'other';
        totals[key] = (totals[key] || 0) + t.amount;
      }
      new Chart('summaryChart', {
        type: 'bar',
        data: {
          labels: Object.keys(totals),
          datasets: [{ data: Object.values(totals), label: 'Spend' }]
        }
      });
    });
  }
}
