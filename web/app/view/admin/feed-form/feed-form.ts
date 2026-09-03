import { Component, Inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatDialogModule, MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { TranslatePipe, TranslateDirective, TranslateService } from '@ngx-translate/core';
import { Feed } from 'app/models/feed';
import { FeedService } from 'app/services/feed.service';
import { NotificationService } from 'app/services/notification.service';

@Component({
  selector: 'app-feed-form',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatButtonModule,
    MatSlideToggleModule,
    MatProgressSpinnerModule,
    TranslatePipe,
    TranslateDirective
  ],
  templateUrl: './feed-form.html',
  styleUrls: ['./feed-form.css']
})
export class FeedFormComponent implements OnInit {
  form: FormGroup;
  formats = ['embedded', 'cdir_text', 'cdir_gz'];
  types = ['reputation', 'bypass'];
  intervals = ['hourly', 'daily'];
  isLoading = signal(false);

  constructor(
    private fb: FormBuilder,
    private dialogRef: MatDialogRef<FeedFormComponent>,
    private feedService: FeedService,
    private notificationService: NotificationService,
    private translate: TranslateService,
    @Inject(MAT_DIALOG_DATA) public data: Feed | null
  ) {
    this.form = this.fb.group({
      name: ['', Validators.required],
      slug: ['', Validators.required],
      provider: ['ipxa', Validators.required],
      type: ['reputation', Validators.required],
      source: [''],
      data_raw: [''],
      description: [''],
      format: ['cdir_text', Validators.required],
      update_interval: ['hourly'],
      risk_score: [0, [Validators.min(0), Validators.max(100)]]
    });
  }

  ngOnInit() {
    this.updateFormatValidators(this.form.get('format')?.value);

    this.form.get('format')?.valueChanges.subscribe(format => {
      this.updateFormatValidators(format);
    });

    this.form.get('name')?.valueChanges.subscribe(name => {
      if (!this.data && name) {
        const generatedSlug = name.toLowerCase().trim().replace(/[^a-z0-9_]+/g, '_').replace(/^_+|_+$/g, '');
        const slugCtrl = this.form.get('slug');
        if (slugCtrl && !slugCtrl.dirty) {
          slugCtrl.setValue(generatedSlug);
        }
      }
    });

    if (this.data) {
      const formData = { ...this.data } as any;
      if (this.data.data) {
        formData['data_raw'] = this.data.data.join('\n');
      }
      this.form.patchValue(formData);
      this.updateFormatValidators(this.data.format || 'cdir_text');
    }
  }

  private updateFormatValidators(format: string) {
    const dataRawControl = this.form.get('data_raw');
    const sourceControl = this.form.get('source');

    if (format === 'embedded') {
      dataRawControl?.setValidators([Validators.required]);
      sourceControl?.clearValidators();
    } else {
      dataRawControl?.clearValidators();
      sourceControl?.setValidators([Validators.required]);
    }
    dataRawControl?.updateValueAndValidity();
    sourceControl?.updateValueAndValidity();
  }

  onSave() {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    const value: any = {
      ...(this.data || {}),
      ...this.form.value
    };

    if (value.format === 'embedded') {
      value.data = (value.data_raw || '')
        .split('\n')
        .map((s: string) => s.trim())
        .filter((s: string) => s.length > 0);
      value.source = '';
    } else {
      delete value.data;
    }
    delete value.data_raw;

    this.isLoading.set(true);

    const request$ = this.data?._id
      ? this.feedService.update(this.data._id, value)
      : this.feedService.save(value);

    request$.subscribe({
      next: () => {
        this.isLoading.set(false);
        this.notificationService.openSnackBar(this.translate.instant('NOTIFICATIONS.SUCCESS_SAVE'));
        this.dialogRef.close(true);
      },
      error: (err) => {
        this.isLoading.set(false);
        this.notificationService.openSnackBar(err.error?.message || this.translate.instant('NOTIFICATIONS.ERROR_GENERIC'));
      }
    });
  }

  onCancel() {
    this.dialogRef.close();
  }
}
