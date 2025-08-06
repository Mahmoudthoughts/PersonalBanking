import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { forkJoin } from 'rxjs';
import Chart from 'chart.js/auto';

import { DataService } from '../../services/data.service';
import { AuthService } from '../../services/auth.service';
import { TagService } from '../../services/tag.service';
import { Tag } from '../../models/tag';
import { CalendarHeatmapComponent } from '../../components/calendar-heatmap/calendar-heatmap';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterModule, CalendarHeatmapComponent],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.scss'
})
export class Dashboard implements OnInit {
  private categoryChart: Chart | null = null;
  private monthlyChart: Chart | null = null;

  private transactions: any[] = [];
  private tags: Tag[] = [];
  private tagMap: { [id: number]: Tag } = {};
  dailyTotals: { date: string; total: number }[] = [];

  constructor(
    private data: DataService,
    private router: Router,
    private auth: AuthService,
    private tagService: TagService
  ) {}

  ngOnInit(): void {
    if (!this.auth.token) {
      this.router.navigate(['/']);
      return;
    }

    forkJoin({
      transactions: this.data.getTransactions(),
      daily: this.data.getDailySummary(),
      tags: this.tagService.getTags()
    }).subscribe(({ transactions, daily, tags }) => {
      this.transactions = transactions as any[];
      this.dailyTotals = daily as any[];
      this.tags = tags;
      this.buildTagMap();

      const monthTotals = this.computeMonthTotals(this.transactions);
      this.renderTagChart(null);
      this.renderMonthChart(monthTotals);
    });
  }

  private buildTagMap() {
    for (const t of this.tags) {
      this.tagMap[t.id] = t;
    }
  }

  private computeMonthTotals(transactions: any[]): { [key: string]: number } {
    const monthTotals: { [key: string]: number } = {};
    for (const tx of transactions) {
      const month = (tx.transaction_date as string).slice(0, 7);
      monthTotals[month] = (monthTotals[month] || 0) + tx.total_amount;
    }
    return monthTotals;
  }

  private renderTagChart(parentId: number | null) {
    if (this.categoryChart) {
      this.categoryChart.destroy();
    }

    const relevant = this.tags.filter(t => t.parent_id === parentId);
    const totals: { [id: number]: number } = {};
    relevant.forEach(t => (totals[t.id] = 0));
    if (parentId === null) {
      totals[0] = 0; // Uncategorized
    }

    for (const tx of this.transactions) {
      if (tx.tags && tx.tags.length) {
        for (const tag of tx.tags) {
          let current = this.tagMap[tag.id];
          while (current && current.parent_id !== parentId && current.parent_id != null) {
            current = this.tagMap[current.parent_id];
          }
          if (current && current.parent_id === parentId) {
            totals[current.id] = (totals[current.id] || 0) + tx.total_amount;
          }
        }
      } else if (parentId === null) {
        totals[0] += tx.total_amount;
      }
    }

    const labels = relevant.map(t => t.name);
    const values = relevant.map(t => totals[t.id] || 0);
    if (parentId === null && totals[0]) {
      labels.push('Uncategorized');
      values.push(totals[0]);
    }

    this.categoryChart = new Chart('categoryChart', {
      type: 'pie',
      data: {
        labels,
        datasets: [{ data: values, backgroundColor: this.generateColors(labels.length) }]
      },
      options: {
        onClick: (_e, els) => {
          if (!els.length) return;
          const index = els[0].index;
          if (parentId === null && labels[index] === 'Uncategorized') {
            this.router.navigate(['/transactions'], { queryParams: { category: 'Uncategorized' } });
            return;
          }
          const tag = relevant[index];
          if (!tag) return;
          const children = this.tags.filter(t => t.parent_id === tag.id);
          if (children.length) {
            this.renderTagChart(tag.id);
          } else {
            this.router.navigate(['/transactions'], { queryParams: { tag: tag.id } });
          }
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

  goToDay(day: string) {
    this.router.navigate(['/transactions'], { queryParams: { day } });
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
