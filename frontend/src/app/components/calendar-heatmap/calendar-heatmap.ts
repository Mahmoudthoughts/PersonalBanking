import { Component, Input, Output, EventEmitter, OnChanges, ElementRef, ViewChild, AfterViewInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import * as d3 from 'd3';

@Component({
  selector: 'app-calendar-heatmap',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './calendar-heatmap.html',
  styleUrl: './calendar-heatmap.scss'
})
export class CalendarHeatmapComponent implements OnChanges, AfterViewInit {
  @Input() data: { date: string; total: number }[] = [];
  @Output() selectDay = new EventEmitter<string>();
  @ViewChild('svg', { static: true }) svgRef!: ElementRef<SVGSVGElement>;
  private initialized = false;

  ngAfterViewInit() {
    this.initialized = true;
    this.render();
  }

  ngOnChanges() {
    this.render();
  }

  private render() {
    if (!this.initialized) return;
    const svg = d3.select(this.svgRef.nativeElement);
    svg.selectAll('*').remove();

    const cellSize = 14;
    const width = 53 * cellSize;
    const height = 7 * cellSize;
    const year = new Date().getFullYear();
    const start = new Date(year, 0, 1);
    const end = new Date(year, 11, 31);

    svg.attr('viewBox', `0 0 ${width + 40} ${height + 20}`);

    const dataMap = new Map(this.data.map(d => [d.date, d.total]));
    const max = d3.max(this.data, d => d.total) || 0;
    const color = d3.scaleSequential(d3.interpolateBlues).domain([0, max || 1]);

    const g = svg.append('g').attr('transform', 'translate(20,20)');

    const days = d3.timeDays(start, end);
    g.selectAll('rect')
      .data(days)
      .join('rect')
      .attr('width', cellSize - 2)
      .attr('height', cellSize - 2)
      .attr('x', d => d3.timeWeek.count(d3.timeYear(d), d) * cellSize)
      .attr('y', d => d.getDay() * cellSize)
      .attr('fill', d => color(dataMap.get(d3.timeFormat('%Y-%m-%d')(d)) || 0))
      .on('click', (_e, d) => {
        this.selectDay.emit(d3.timeFormat('%Y-%m-%d')(d));
      });

    g.selectAll('text')
      .data(d3.timeMonths(start, end))
      .join('text')
      .attr('x', d => d3.timeWeek.count(start, d) * cellSize)
      .attr('y', -5)
      .text(d3.timeFormat('%b'));
  }
}
