import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClientModule } from '@angular/common/http';
import { ReactiveFormsModule, FormBuilder, FormGroup } from '@angular/forms';
import { TagService } from '../../services/tag.service';
import { Tag } from '../../models/tag';
import { TagTree } from '../../components/tag-tree/tag-tree';

@Component({
  selector: 'app-tags',
  standalone: true,
  imports: [CommonModule, HttpClientModule, ReactiveFormsModule, TagTree],
  templateUrl: './tags.html',
  styleUrl: './tags.scss'
})
export class Tags implements OnInit {
  tags: Tag[] = [];
  flatTags: Tag[] = [];
  selected: number[] = [];

  showModal = false;
  editTag?: Tag;
  form: FormGroup;

  constructor(private service: TagService, private fb: FormBuilder) {
    this.form = this.fb.nonNullable.group({
      name: '',
      parent_id: '' as any
    });
  }

  ngOnInit() {
    this.load();
  }

  load() {
    this.service.getTags().subscribe(res => {
      this.flatTags = res;
      this.tags = this.buildTree(res);
    });
  }

  buildTree(list: Tag[]): Tag[] {
    const map: Record<number, Tag & {children: Tag[]}> = {};
    for (const t of list) {
      map[t.id] = { ...t, children: [] };
    }
    const roots: Tag[] = [];
    for (const t of Object.values(map)) {
      if (t.parent_id && map[t.parent_id]) {
        map[t.parent_id].children.push(t);
      } else {
        roots.push(t);
      }
    }
    return roots;
  }

  open(tag?: Tag) {
    this.editTag = tag;
    this.form.setValue({
      name: tag?.name || '',
      parent_id: tag?.parent_id ?? ''
    });
    this.showModal = true;
  }

  save() {
    const data = this.form.getRawValue();
    if (this.editTag) {
      this.service.updateTag(this.editTag.id, data).subscribe(() => {
        this.showModal = false;
        this.load();
      });
    } else {
      this.service.createTag(data).subscribe(() => {
        this.showModal = false;
        this.load();
      });
    }
  }

  remove(tag: Tag) {
    if (confirm('Delete tag?')) {
      this.service.deleteTag(tag.id).subscribe(() => this.load());
    }
  }
}
