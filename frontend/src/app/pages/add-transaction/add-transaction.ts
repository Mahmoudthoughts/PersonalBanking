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
      date: '',
      description: '',
      amount: 0,
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
