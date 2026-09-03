import { Component, TemplateRef, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatDialog, MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatTooltipModule } from '@angular/material/tooltip';
import { TranslatePipe, TranslateDirective } from '@ngx-translate/core';
import { OAuthService } from '../../services/oauth.service';
import { LocalStorageService } from '../../services/localstorage.service';
import { ThemeService } from '../../services/theme.service';
import { Router } from '@angular/router';
import { IpInputComponent } from '../../components/ip-input/ip-input.component';

@Component({
  selector: 'app-admin-layout',
  standalone: true,
  imports: [
    CommonModule, 
    RouterModule, 
    MatToolbarModule, 
    MatIconModule,
    MatButtonModule,
    MatDialogModule,
    MatTooltipModule,
    TranslatePipe,
    TranslateDirective,
    IpInputComponent
  ],
  templateUrl: './admin-layout.html',
  styleUrls: ['./admin-layout.css']
})
export class AdminLayoutComponent {
  @ViewChild('ipLookupDialog') ipLookupDialog!: TemplateRef<any>;
  private dialogRef?: MatDialogRef<any>;

  constructor(
    private oauthService: OAuthService,
    private localStorageService: LocalStorageService,
    private themeService: ThemeService,
    private router: Router,
    private dialog: MatDialog
  ) {}

  isDarkTheme(): boolean {
    return this.themeService.isDark();
  }

  toggleTheme(): void {
    this.themeService.toggleTheme();
  }

  openIpLookupDialog() {
    this.dialogRef = this.dialog.open(this.ipLookupDialog, {
      width: '600px',
      maxWidth: '92vw',
      panelClass: 'custom-dialog-container',
      autoFocus: false
    });
  }

  onIpSearched() {
    this.dialogRef?.close();
  }

  logout() {
    this.oauthService.resetTokens();
    this.localStorageService.clear();
    this.router.navigate(['/login']);
  }
}

