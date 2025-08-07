import { Routes } from '@angular/router';
import { Login } from './pages/login/login';
import { Dashboard } from './pages/dashboard/dashboard';
import { Upload } from './pages/upload/upload';
import { ImportJson } from './pages/import-json/import-json';
import { ImportExport } from './pages/import-export/import-export';
import { Transactions } from './pages/transactions/transactions';
import { AddTransaction } from './pages/add-transaction/add-transaction';
import { TransactionDetail } from './pages/transaction-detail/transaction-detail';
import { Tags } from './pages/tags/tags';
import { Report } from './pages/report/report';
import { Home } from './pages/home/home';
import { Register } from './pages/register/register';

export const routes: Routes = [
  { path: 'login', component: Login },
  { path: 'register', component: Register },
  { path: 'dashboard', component: Dashboard },
  { path: 'upload', component: Upload },
  { path: 'import-json', component: ImportJson },
  { path: 'import-export', component: ImportExport },
  { path: 'transactions/new', component: AddTransaction },
  { path: 'transactions', component: Transactions },
  { path: 'transactions/:id', component: TransactionDetail },
  { path: 'tags', component: Tags },
  { path: 'report/:month', component: Report },
  { path: '', component: Home }
];
