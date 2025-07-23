import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup } from '@angular/forms';
import { Router } from '@angular/router';
import { DataService } from '../../services/data.service';

@Component({
  selector: 'app-add-transaction',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './add-transaction.html',
  styleUrl: './add-transaction.scss'
})
export class AddTransaction {
  form: FormGroup;

  constructor(private fb: FormBuilder, private data: DataService, private router: Router) {
    this.form = this.fb.nonNullable.group({
      transaction_date: '',
      description: '',
      total_amount: 0,
      card_number: '',
      cardholder_name: '',
      cardholder_id: '',
      source_file: ''
    });
  }

  submit() {
    const payload = this.form.getRawValue();
    this.data.createTransaction(payload).subscribe(() => {
      this.router.navigate(['/transactions']);
    });
  }
}
