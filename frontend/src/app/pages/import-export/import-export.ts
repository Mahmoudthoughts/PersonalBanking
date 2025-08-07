import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DataService } from '../../services/data.service';
import { saveAs } from 'file-saver';

@Component({
  selector: 'app-import-export',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './import-export.html',
  styleUrl: './import-export.scss'
})
export class ImportExport {
  constructor(private data: DataService) {}

  onFile(event: Event) {
    const input = event.target as HTMLInputElement;
    if (!input.files || !input.files.length) return;
    const formData = new FormData();
    formData.append('file', input.files[0]);
    this.data.importTransactions(formData).subscribe();
  }

  export() {
    this.data.exportTransactions().subscribe(blob => {
      saveAs(blob, 'transactions.csv');
    });
  }
}
