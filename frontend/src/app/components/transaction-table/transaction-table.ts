import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

interface TransactionComponent {
  label: string;
  amount: number;
  vat: number;
}

interface Transaction {
  transaction_date: string;
  description: string;
  cardholder_name: string;
  total_amount: number;
  components?: TransactionComponent[];
}

@Component({
  selector: 'app-transaction-table',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './transaction-table.html',
  styleUrl: './transaction-table.scss'
})
export class TransactionTable {
  transactions: Transaction[] = [
    {
      transaction_date: '2024-06-01',
      description: 'Online Purchase',
      cardholder_name: 'John',
      total_amount: 120,
      components: [
        { label: 'Item Total', amount: 100, vat: 20 },
        { label: 'Shipping', amount: 20, vat: 0 }
      ]
    },
    {
      transaction_date: '2024-06-03',
      description: 'Grocery Store',
      cardholder_name: 'Mary',
      total_amount: 45
    },
    {
      transaction_date: '2024-06-04',
      description: 'Restaurant',
      cardholder_name: 'John',
      total_amount: 75,
      components: [
        { label: 'Meals', amount: 60, vat: 10 },
        { label: 'Service', amount: 15, vat: 0 }
      ]
    }
  ];

  expanded: { [key: number]: boolean } = {};

  toggle(index: number) {
    this.expanded[index] = !this.expanded[index];
  }
}
