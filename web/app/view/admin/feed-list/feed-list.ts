import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatTableDataSource, MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { FeedService } from '../../../services/feed.service';
import { Feed } from '../../../models/feed';
import { FeedFormComponent } from '../feed-form/feed-form';
import { DefaultPageMeta, PageMeta } from 'app/models/shared';
import { MatPaginatorModule, PageEvent } from '@angular/material/paginator';
@Component({
  selector: 'app-feed-list',
  standalone: true,
  imports: [CommonModule, MatTableModule, MatButtonModule, MatIconModule, MatCardModule, MatDialogModule, MatPaginatorModule],
  templateUrl: './feed-list.html',
  styleUrls: ['./feed-list.css']
})
export class FeedListComponent implements OnInit {
  feedDC: string[] = ['name', 'provider', 'type', 'format', 'risk_score', 'actions'];
  feedDS: MatTableDataSource<Feed>;
  feedPA: PageMeta;

  constructor(
    private feedService: FeedService,
    private dialog: MatDialog
  ) {
    this.feedDS = new MatTableDataSource<Feed>;
    this.feedPA = new DefaultPageMeta()
  }

  ngOnInit() {
    this.updateGridTable();
  }

  updateGridTable() {
    this.feedService.get(this.feedPA).subscribe(res => {
      console.log('feedPA', res);
      if (res.metadata) {
        this.feedPA.total_elements = res.metadata.total_elements;
        this.feedDS.data = res.data;
      } else {
        this.feedDS.data = [];
        this.feedPA.total_elements = 0;
      }
    });
  }

  openForm(feed?: Feed) {
    const dialogRef = this.dialog.open(FeedFormComponent, {
      data: feed || null,
      width: '600px',
      panelClass: 'custom-dialog-container'
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        if (feed?._id) {
          this.feedService.update(feed._id, result).subscribe(() => this.updateGridTable());
        } else {
          this.feedService.save(result).subscribe(() => this.updateGridTable());
        }
      }
    });
  }

  onRemove(id: number) {
    if (confirm('Deseja realmente excluir este feed?')) {
      this.feedService.removeById(id).subscribe(() => this.updateGridTable());
    }
  }
  nextPage(event: PageEvent) {
    this.feedPA.page = event.pageIndex + 1;
    this.feedPA.per_page = event.pageSize;
    this.updateGridTable();
  }

}
