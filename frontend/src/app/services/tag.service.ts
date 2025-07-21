import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { AuthService } from './auth.service';
import { environment } from '../../environments/environment';
import { Tag } from '../models/tag';

@Injectable({ providedIn: 'root' })
export class TagService {
  constructor(private http: HttpClient, private auth: AuthService) {}

  private get headers() {
    return this.auth.authHeaders;
  }

  getTags() {
    return this.http.get<Tag[]>(`${environment.apiUrl}/tags`, this.headers);
  }

  createTag(payload: Partial<Tag>) {
    return this.http.post<{id: number}>(`${environment.apiUrl}/tags`, payload, this.headers);
  }

  updateTag(id: number, payload: Partial<Tag>) {
    return this.http.patch(`${environment.apiUrl}/tags/${id}`, payload, this.headers);
  }

  deleteTag(id: number) {
    return this.http.delete(`${environment.apiUrl}/tags/${id}`, this.headers);
  }
}
