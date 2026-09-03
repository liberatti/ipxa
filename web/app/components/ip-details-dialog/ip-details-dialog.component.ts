import { Component, Inject, computed, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatDialogModule, MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { TranslatePipe, TranslateDirective } from '@ngx-translate/core';
import { IpInfo } from '../../models/ipinfo';

@Component({
  selector: 'app-ip-details-dialog',
  standalone: true,
  imports: [CommonModule, MatDialogModule, MatIconModule, MatButtonModule, TranslatePipe, TranslateDirective],
  templateUrl: './ip-details-dialog.component.html',
  styleUrls: ['./ip-details-dialog.component.css'],
})
export class IpDetailsDialogComponent {
  dataSignal = signal<IpInfo>(this.data);

  riskLevelClass = computed(() => {
    const score = this.dataSignal().security?.risk_score || 0;
    if (score === 0) return 'low';
    return score < 50 ? 'medium' : 'high';
  });

  riskLevelKey = computed(() => {
    const score = this.dataSignal().security?.risk_score || 0;
    if (score === 0) return 'IP_DETAILS.RISK_LOW';
    return score < 50 ? 'IP_DETAILS.RISK_MEDIUM' : 'IP_DETAILS.RISK_HIGH';
  });

  riskScore = computed(() => {
    return this.dataSignal().security?.risk_score || 0;
  });

  constructor(
    public dialogRef: MatDialogRef<IpDetailsDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: IpInfo
  ) {
    this.dataSignal.set(data);
  }

  getCountryName(code: string): string {
    if (!code || code.length > 3) return code;
    try {
      const displayNames = new Intl.DisplayNames(['en'], { type: 'region' });
      return displayNames.of(code.toUpperCase()) || code;
    } catch (e) {
      return code;
    }
  }

  close(): void {
    this.dialogRef.close();
  }
}
