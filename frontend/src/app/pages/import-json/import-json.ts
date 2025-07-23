import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { DataService } from '../../services/data.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-import-json',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './import-json.html',
  styleUrl: './import-json.scss'
})
export class ImportJson {
  jsonText = '';
  parsed: any[] = [];

  constructor(private data: DataService, private router: Router) {}

  onFile(event: Event) {
    const input = event.target as HTMLInputElement;
    if (!input.files || !input.files.length) return;
    const file = input.files[0];
    const reader = new FileReader();
    reader.onload = () => {
      this.jsonText = reader.result as string;
      this.parse();
    };
    reader.readAsText(file);
  }

  parse() {
    try {
      this.parsed = JSON.parse(this.jsonText || '[]');
    } catch {
      this.parsed = [];
    }
  }

  submit() {
    this.data.batchCreateTransactions(this.parsed).subscribe(() => {
      this.router.navigate(['/transactions']);
    });
  }
}
