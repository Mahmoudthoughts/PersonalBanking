import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router,RouterModule } from '@angular/router';
import { DataService } from '../../services/data.service';
import Chart from 'chart.js/auto';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.scss'
})
export class Dashboard implements OnInit {
  constructor(private data: DataService, private router: Router) {}

  ngOnInit(): void {
    this.data.getTransactions().subscribe(transactions => {
      const categoryTotals: { [key: string]: number } = {};
      const monthTotals: { [key: string]: number } = {};

      for (const tx of transactions as any[]) {
        const month = (tx.transaction_date as string).slice(0, 7);
        monthTotals[month] = (monthTotals[month] || 0) + tx.total_amount;

        const cat = (tx.tags && tx.tags.length)
          ? tx.tags[0].name
          : 'Uncategorized';
        categoryTotals[cat] = (categoryTotals[cat] || 0) + tx.total_amount;
      }

      this.renderCategoryChart(categoryTotals);
      this.renderMonthChart(monthTotals);
    });
  }

  private renderCategoryChart(totals: { [key: string]: number }) {
    const chart = new Chart('categoryChart', {
      type: 'pie',
      data: {
        labels: Object.keys(totals),
        datasets: [{ data: Object.values(totals) }]
      },
      options: {
        onClick: (_e, els) => {
          if (!els.length) return;
          const index = els[0].index;
          const label = Object.keys(totals)[index];
          this.router.navigate(['/transactions'], {
            queryParams: { category: label }
          });
        }
      }
    });
  }

  private renderMonthChart(totals: { [key: string]: number }) {
    const labels = Object.keys(totals).sort();
    const data = labels.map(l => totals[l]);

    new Chart('monthlyChart', {
      type: 'line',
      data: {
        labels,
        datasets: [{ data, label: 'Total Spend' }]
      },
      options: {
        onClick: (_e, els) => {
          if (!els.length) return;
          const index = els[0].index;
          this.router.navigate(['/transactions'], {
            queryParams: { month: labels[index] }
          });
        }
      }
    });
  }
}
