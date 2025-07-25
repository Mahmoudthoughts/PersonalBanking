import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClientModule } from '@angular/common/http';
import { Router } from '@angular/router';
import { DataService } from '../../services/data.service';
import { saveAs } from 'file-saver';

@Component({
  selector: 'app-upload',
  standalone: true,
  imports: [CommonModule, HttpClientModule],
  templateUrl: './upload.html',
  styleUrl: './upload.scss'
})
export class Upload {
  parsed: any[] = [];
  constructor(private data: DataService, private router: Router) {}

  onFileSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    if (!input.files || input.files.length === 0) {
      return;
    }

    const file = input.files[0];
    const formData = new FormData();
    formData.append('file', file);

    this.data.parsePdf(formData).subscribe(res => {
      this.parsed = res;
      const blob = new Blob([JSON.stringify(res, null, 2)], { type: 'application/json' });
      saveAs(blob, 'transactions.json');
    });
  }
}
