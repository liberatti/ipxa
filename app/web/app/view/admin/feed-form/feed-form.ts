import { Component, Inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatDialogModule, MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { Feed } from 'app/models/feed';

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
    MatSlideToggleModule
  ],
  templateUrl: './feed-form.html',
  styleUrls: ['./feed-form.css']
})
export class FeedFormComponent implements OnInit {
  form: FormGroup;
  formats = ['embedded', 'cdir_text', 'cdir_gz'];
  types = ['reputation', 'bypass'];
  intervals = ['hourly', 'daily'];

  constructor(
    private fb: FormBuilder,
    private dialogRef: MatDialogRef<FeedFormComponent>,
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
    this.form.get('format')?.valueChanges.subscribe(format => {
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
    });

    if (this.data) {
      const formData = { ...this.data } as any;
      if (this.data.data) {
        formData['data_raw'] = this.data.data.join('\n');
      }
      this.form.patchValue(formData);
    }

    // Trigger initial validation check
    this.form.get('format')?.updateValueAndValidity();
  }

  onSave() {
    if (this.form.valid) {
      const value = { ...this.form.value };
      if (value.data_raw) {
        value.data = value.data_raw.split('\n').map((s: string) => s.trim()).filter((s: string) => s.length > 0);
      }
      delete value.data_raw;
      this.dialogRef.close(value);
    }
  }

  onCancel() {
    this.dialogRef.close();
  }
}
