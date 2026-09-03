import { CommonModule } from '@angular/common';
import { Component, Inject } from '@angular/core';
import { MAT_SNACK_BAR_DATA, MatSnackBarRef } from '@angular/material/snack-bar';

@Component({
  selector: 'app-multi-snackbar',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './multi-snackbar.component.html',
  styleUrls: ['./multi-snackbar.component.css']
})
export class MultiSnackbarComponent {
  constructor(
    public snackBarRef: MatSnackBarRef<MultiSnackbarComponent>,
    @Inject(MAT_SNACK_BAR_DATA) public data: { messages: string[] }
  ) {}
} 