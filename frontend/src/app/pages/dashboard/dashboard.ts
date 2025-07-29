import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { DataService } from '../../services/data.service';
import { AuthService } from '../../services/auth.service';
import Chart from 'chart.js/auto';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.scss'
})
export class Dashboard implements OnInit {
  private categoryChart: Chart | null = null;
  private monthlyChart: Chart | null = null;

  private readonly allCategories: string[] = [
    'Home supplies',
    'Groceries',
    'Fuel',
    'Dining',
    'Entertainment',
    'Transport',
    'Utilities',
    'Visa/Travel',
    'Medical',
    'Government Services',
    'Shopping',
    'Food Delivery',
    'Uncategorized'
  ];


  constructor(
    private data: DataService,
    private router: Router,
    private auth: AuthService
  ) {}

  ngOnInit(): void {
    if (!this.auth.token) {
      this.router.navigate(['/']);
      return;
    }
    this.data.getTransactions().subscribe(transactions => {
      const categoryTotals: { [key: string]: number } = {};
      const monthTotals: { [key: string]: number } = {};

      // Initialize all known categories to 0
      for (const cat of this.allCategories) {
        categoryTotals[cat] = 0;
      }

      for (const tx of transactions as any[]) {
        const month = (tx.transaction_date as string).slice(0, 7);
        monthTotals[month] = (monthTotals[month] || 0) + tx.total_amount;

        const cat = (tx.tags && tx.tags.length)
          ? tx.tags[0].name
          : this.inferCategory(tx.description || '');

        if (!categoryTotals.hasOwnProperty(cat)) {
          categoryTotals[cat] = 0; // support for dynamic categories
        }

        categoryTotals[cat] += tx.total_amount;
      }

      // Sort alphabetically before rendering
      const sortedCategoryTotals: { [key: string]: number } = {};
      for (const cat of Object.keys(categoryTotals).sort()) {
        sortedCategoryTotals[cat] = categoryTotals[cat];
      }

      this.renderCategoryChart(sortedCategoryTotals);
      this.renderMonthChart(monthTotals);
    });
  }

  private inferCategory(description: string): string {
    const desc = description.toLowerCase();

    if (desc.includes('carrefour')) return 'Groceries';
    if (desc.includes('careem')) return 'Transport';
    if (desc.includes('talabat')) return 'Food Delivery';
    if (desc.includes('noon')) return 'Shopping';
    if (desc.includes('amazon')) return 'Shopping';
    if (desc.includes('disney') || desc.includes('sephora') || desc.includes('boots')) return 'Entertainment';
    if (desc.includes('hospital')) return 'Medical';
    if (desc.includes('vfs')) return 'Visa/Travel';
    if (desc.includes('government') || desc.includes('smartdxbgov') || desc.includes('dxb')) return 'Government Services';
    if (desc.includes('tesla')) return 'Utilities';
    if (desc.includes('fuel') || desc.includes('adnoc')) return 'Fuel';

    return 'Uncategorized';
  }

  private renderCategoryChart(totals: { [key: string]: number }) {
    if (this.categoryChart) {
      this.categoryChart.destroy();
    }

    const labels = Object.keys(totals);
    const values = Object.values(totals);

    this.categoryChart = new Chart('categoryChart', {
      type: 'pie',
      data: {
        labels,
        datasets: [{
          data: values,
          backgroundColor: this.generateColors(labels.length)
        }]
      },
      options: {
        onClick: (_e, els) => {
          if (!els.length) return;
          const index = els[0].index;
          const label = labels[index];
          this.router.navigate(['/transactions'], {
            queryParams: { category: label }
          });
        }
      }
    });
  }

  private renderMonthChart(totals: { [key: string]: number }) {
    if (this.monthlyChart) {
      this.monthlyChart.destroy();
    }

    const labels = Object.keys(totals).sort();
    const data = labels.map(label => totals[label]);

    this.monthlyChart = new Chart('monthlyChart', {
      type: 'line',
      data: {
        labels,
        datasets: [{
          data,
          label: 'Total Spend',
          borderColor: 'blue',
          backgroundColor: 'lightblue',
          fill: false,
          tension: 0.3
        }]
      },
      options: {
        responsive: true,
        onClick: (_e, els) => {
          if (!els.length) return;
          const index = els[0].index;
          const label = labels[index];
          this.router.navigate(['/transactions'], {
            queryParams: { month: label }
          });
        }
      }
    });
  }

  private generateColors(count: number): string[] {
    const baseColors = [
      '#3366CC', '#DC3912', '#FF9900', '#109618',
      '#990099', '#3B3EAC', '#0099C6', '#DD4477',
      '#66AA00', '#B82E2E', '#316395', '#994499',
      '#22B14C', '#FF6347', '#4682B4', '#D2691E'
    ];
    return Array.from({ length: count }, (_, i) => baseColors[i % baseColors.length]);
  }
}
