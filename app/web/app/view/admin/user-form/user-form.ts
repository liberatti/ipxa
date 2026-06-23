import { Component, Inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatDialogModule, MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { User } from 'app/models/user';

@Component({
  selector: 'app-user-form',
  standalone: true,
  imports: [
    CommonModule, 
    ReactiveFormsModule, 
    MatDialogModule, 
    MatFormFieldModule, 
    MatInputModule, 
    MatSelectModule, 
    MatButtonModule,
    MatIconModule
  ],
  templateUrl: './user-form.html',
  styleUrls: ['./user-form.css']
})
export class UserFormComponent implements OnInit {
  form: FormGroup;
  roles = ['superuser', 'user'];

  constructor(
    private fb: FormBuilder,
    private dialogRef: MatDialogRef<UserFormComponent>,
    @Inject(MAT_DIALOG_DATA) public data: User | null
  ) {
    this.form = this.fb.group({
      name: ['', Validators.required],
      email: ['', [Validators.required, Validators.email]],
      password: [''],
      role: ['user', Validators.required],
      service_token: ['']
    });
  }

  ngOnInit() {
    if (this.data) {
      this.form.patchValue({
        name: this.data.name,
        email: this.data.email,
        role: this.data.role,
        service_token: this.data.service_token || ''
      });
      this.form.get('password')?.clearValidators();
    } else {
      this.form.get('password')?.setValidators([Validators.required]);
    }
    this.form.get('password')?.updateValueAndValidity();
  }

  generateToken() {
    const array = new Uint8Array(32);
    window.crypto.getRandomValues(array);
    const token = Array.from(array, dec => dec.toString(16).padStart(2, '0')).join('');
    this.form.get('service_token')?.setValue(token);
  }

  onSave() {
    if (this.form.valid) {
      const value = { ...this.form.value };
      if (!value.password) {
        delete value.password;
      }
      this.dialogRef.close(value);
    }
  }

  onCancel() {
    this.dialogRef.close();
  }
}
