import { Injectable, inject } from '@angular/core';
import { MatPaginatorIntl } from '@angular/material/paginator';
import { TranslateService } from '@ngx-translate/core';

@Injectable()
export class CustomMatPaginatorIntl extends MatPaginatorIntl {
  private translate = inject(TranslateService);

  constructor() {
    super();
    this.translate.onLangChange.subscribe(() => this.getTranslations());
    this.getTranslations();
  }

  getTranslations() {
    this.itemsPerPageLabel = this.translate.instant('PAGINATOR.ITEMS_PER_PAGE') || 'Items per page:';
    this.nextPageLabel = this.translate.instant('PAGINATOR.NEXT_PAGE') || 'Next page';
    this.previousPageLabel = this.translate.instant('PAGINATOR.PREVIOUS_PAGE') || 'Previous page';
    this.firstPageLabel = this.translate.instant('PAGINATOR.FIRST_PAGE') || 'First page';
    this.lastPageLabel = this.translate.instant('PAGINATOR.LAST_PAGE') || 'Last page';
    this.changes.next();
  }

  override getRangeLabel = (page: number, pageSize: number, length: number): string => {
    if (length === 0 || pageSize === 0) {
      return `0 / ${length}`;
    }
    const safeLength = Math.max(length, 0);
    const startIndex = page * pageSize;
    const endIndex = startIndex < safeLength ? Math.min(startIndex + pageSize, safeLength) : startIndex + pageSize;
    return `${startIndex + 1} – ${endIndex} / ${safeLength}`;
  };
}
