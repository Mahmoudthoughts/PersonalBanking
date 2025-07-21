import { Component, EventEmitter, Input, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Tag } from '../../models/tag';

@Component({
  selector: 'app-tag-tree',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './tag-tree.html',
  styleUrl: './tag-tree.scss'
})
export class TagTree {
  @Input() tags: Tag[] = [];
  @Input() selected: number[] = [];
  @Output() selectedChange = new EventEmitter<number[]>();
  @Output() edit = new EventEmitter<Tag>();
  @Output() remove = new EventEmitter<Tag>();

  toggle(id: number) {
    if (this.selected.includes(id)) {
      this.selected = this.selected.filter(t => t !== id);
    } else {
      this.selected = [...this.selected, id];
    }
    this.selectedChange.emit(this.selected);
  }
}
