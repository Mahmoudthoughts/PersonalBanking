import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';
import { Tag } from '../models/tag';

@Injectable({ providedIn: 'root' })
export class TagService {
  constructor(private http: HttpClient) {}

  getTags() {
    return this.http.get<Tag[]>(`${environment.apiUrl}/tags`);
  }

  createTag(payload: Partial<Tag>) {
    return this.http.post<{id: number}>(`${environment.apiUrl}/tags`, payload);
  }

  updateTag(id: number, payload: Partial<Tag>) {
    return this.http.patch(`${environment.apiUrl}/tags/${id}`, payload);
  }

  deleteTag(id: number) {
    return this.http.delete(`${environment.apiUrl}/tags/${id}`);
  }
}
