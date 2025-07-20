import { Component, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { AppRoutingModule } from './app-routing.module';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, AppRoutingModule],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App {
  protected readonly title = signal('frontend');
}
