import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatTableDataSource, MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { TranslatePipe, TranslateDirective, TranslateService } from '@ngx-translate/core';
import { FeedService } from '../../../services/feed.service';
import { Feed } from '../../../models/feed';
import { FeedFormComponent } from '../feed-form/feed-form';
import { DefaultPageMeta, PageMeta } from 'app/models/shared';
import { MatPaginatorModule, PageEvent } from '@angular/material/paginator';
import { NotificationService } from 'app/services/notification.service';
import { ConfirmDialogComponent } from 'app/components/confirm-dialog/confirm-dialog.component';

@Component({
  selector: 'app-feed-list',
  standalone: true,
  imports: [
    CommonModule, 
    MatTableModule, 
    MatButtonModule, 
    MatIconModule, 
    MatCardModule, 
    MatDialogModule, 
    MatPaginatorModule,
    MatFormFieldModule,
    MatInputModule,
    TranslatePipe,
    TranslateDirective
  ],
  templateUrl: './feed-list.html',
  styleUrls: ['./feed-list.css']
})
export class FeedListComponent implements OnInit {
  feedDC: string[] = ['name', 'provider', 'type', 'format', 'risk_score', 'updated_on', 'actions'];
  feedDS: MatTableDataSource<Feed>;
  feedPA: PageMeta;
  searchQuery = signal<string>('');

  constructor(
    private feedService: FeedService,
    private dialog: MatDialog,
    private translate: TranslateService,
    private notificationService: NotificationService
  ) {
    this.feedDS = new MatTableDataSource<Feed>();
    this.feedPA = new DefaultPageMeta();
    this.setupFilterPredicate();
  }

  private setupFilterPredicate() {
    this.feedDS.filterPredicate = (data: Feed, filter: string) => {
      const normalizedFilter = filter.trim().toLowerCase();
      if (!normalizedFilter) return true;
      const name = (data.name || '').toLowerCase();
      const provider = (data.provider || '').toLowerCase();
      const source = (data.source || '').toLowerCase();
      return name.includes(normalizedFilter) || provider.includes(normalizedFilter) || source.includes(normalizedFilter);
    };
  }

  applyFilter(event: Event) {
    const filterValue = (event.target as HTMLInputElement).value;
    this.searchQuery.set(filterValue);
    this.feedDS.filter = filterValue.trim().toLowerCase();
  }

  clearFilter() {
    this.searchQuery.set('');
    this.feedDS.filter = '';
  }

  ngOnInit() {
    this.updateGridTable();
  }

  updateGridTable() {
    this.feedService.get(this.feedPA).subscribe(res => {
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

    dialogRef.afterClosed().subscribe(saved => {
      if (saved) {
        this.updateGridTable();
      }
    });
  }

  onRemove(id: number) {
    const dialogRef = this.dialog.open(ConfirmDialogComponent, {
      data: {
        titleKey: 'DIALOGS.CONFIRM_DELETE.TITLE',
        messageKey: 'DIALOGS.CONFIRM_DELETE.MESSAGE',
        confirmTextKey: 'ACTIONS.DELETE',
        cancelTextKey: 'ACTIONS.CANCEL',
        confirmColor: 'warn',
        icon: 'delete_outline'
      },
      panelClass: 'custom-dialog-container'
    });

    dialogRef.afterClosed().subscribe(confirmed => {
      if (confirmed) {
        this.feedService.removeById(id).subscribe({
          next: () => {
            this.notificationService.openSnackBar(this.translate.instant('NOTIFICATIONS.SUCCESS_DELETE'));
            this.updateGridTable();
          },
          error: (err) => {
            this.notificationService.openSnackBar(err.error?.message || this.translate.instant('NOTIFICATIONS.ERROR_GENERIC'));
          }
        });
      }
    });
  }
  nextPage(event: PageEvent) {
    this.feedPA.page = event.pageIndex + 1;
    this.feedPA.per_page = event.pageSize;
    this.updateGridTable();
  }

}
