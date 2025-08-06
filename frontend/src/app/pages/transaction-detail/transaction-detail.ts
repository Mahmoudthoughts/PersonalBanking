import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { DataService } from '../../services/data.service';
import { TagService } from '../../services/tag.service';
import { TagTree } from '../../components/tag-tree/tag-tree';
import { Tag } from '../../models/tag';

@Component({
  selector: 'app-transaction-detail',
  standalone: true,
  imports: [CommonModule, FormsModule, TagTree],
  templateUrl: './transaction-detail.html',
  styleUrl: './transaction-detail.scss'
})
export class TransactionDetail implements OnInit {
  transaction: any;
  tags: Tag[] = [];
  selected: number[] = [];
  suggested: Tag[] = [];
  newTagName = '';

  constructor(
    private data: DataService,
    private tagService: TagService,
    private route: ActivatedRoute
  ) {}

  ngOnInit() {
    const id = Number(this.route.snapshot.params['id']);
    this.load(id);
  }

  load(id: number) {
    this.data.getTransaction(id).subscribe(tx => {
      this.transaction = tx;
      this.selected = tx.tags ? tx.tags.map((t: any) => t.id) : [];
      this.data.aiTags(id).subscribe(s => (this.suggested = s));
    });
    this.tagService.getTags().subscribe(t => (this.tags = t));
  }

  addTag() {
    if (!this.newTagName.trim()) return;
    this.tagService.createTag({ name: this.newTagName }).subscribe(() => {
      this.newTagName = '';
      this.tagService.getTags().subscribe(t => (this.tags = t));
    });
  }

  applySuggested(tag: Tag) {
    if (!this.selected.includes(tag.id)) {
      this.selected = [...this.selected, tag.id];
    }
  }

  ignoreSuggested(tag: Tag) {
    this.suggested = this.suggested.filter(t => t.id !== tag.id);
  }

  save() {
    if (!this.transaction) return;
    this.data
      .updateTransaction(this.transaction.id, { tags: this.selected })
      .subscribe(() => this.load(this.transaction.id));
  }
}
