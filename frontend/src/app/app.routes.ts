import { Routes } from '@angular/router';
import { Login } from './pages/login/login';
import { Dashboard } from './pages/dashboard/dashboard';
import { Upload } from './pages/upload/upload';
import { Transactions } from './pages/transactions/transactions';
import { Tags } from './pages/tags/tags';
import { Report } from './pages/report/report';
import { Home } from './pages/home/home';

export const routes: Routes = [
  { path: 'login', component: Login },
  { path: 'dashboard', component: Dashboard },
  { path: 'upload', component: Upload },
  { path: 'transactions', component: Transactions },
  { path: 'tags', component: Tags },
  { path: 'report/:month', component: Report },
  { path: '', component: Home }
];
