import { Component, Inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatSelectModule } from '@angular/material/select';
import { MatMenuModule } from '@angular/material/menu';
import { MatTooltipModule } from '@angular/material/tooltip';
import { TranslatePipe, TranslateDirective, TranslateService } from '@ngx-translate/core';
import { OAuthService } from 'app/services/oauth.service';
import { ThemeService } from 'app/services/theme.service';
import { HttpClient } from '@angular/common/http';
import { REST_API_URL } from 'app/app.config';
import { environment } from 'environments/environment';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    RouterModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatButtonModule,
    MatIconModule,
    MatCardModule,
    MatProgressBarModule,
    MatSlideToggleModule,
    MatMenuModule,
    MatTooltipModule,
    TranslatePipe,
    TranslateDirective
  ],
  templateUrl: './login.html',
  styleUrls: ['./login.css']
})
export class LoginComponent {
  form: FormGroup;
  isLoading = signal(false);
  errorMessage = signal<string | null>(null);
  showPassword = signal(false);
  currentYear = new Date().getFullYear();
  version = environment.version;
  security_enabled = signal(false);
  currentLang = signal<string>('en_US');

  languages = [
    { code: 'en_US', labelKey: 'AUTH.LOGIN.LANG_EN' },
    { code: 'pt_BR', labelKey: 'AUTH.LOGIN.LANG_PT' }
  ];

  constructor(
    private fb: FormBuilder,
    private authService: OAuthService,
    private themeService: ThemeService,
    private router: Router,
    private httpClient: HttpClient,
    private translate: TranslateService,
    @Inject(REST_API_URL) private apiUrl: string
  ) {
    this.form = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', Validators.required]
    });
    this.currentLang.set(this.translate.getCurrentLang() || this.translate.getFallbackLang() || 'en_US');
  }

  setLanguage(lang: string) {
    this.translate.use(lang);
    this.currentLang.set(lang);
  }

  isDarkTheme(): boolean {
    return this.themeService.isDark();
  }

  toggleTheme(): void {
    this.themeService.toggleTheme();
  }

  ngOnInit() {
    this.httpClient.get<any>(`${this.apiUrl}/api/config`, { responseType: "json" }).subscribe({
      next: (data: any) => {
        if (!data.security_enabled) {
          this.router.navigate(['/admin/feeds']);
        }
      }
    });
  }

  togglePassword() {
    this.showPassword.update(v => !v);
  }

  onSubmit() {
    if (this.form.valid) {
      this.isLoading.set(true);
      this.errorMessage.set(null);

      this.authService.login(this.form.value).subscribe({
        next: (data: any) => {
          this.authService.storeTokens(data);
          this.router.navigate(['/admin/feeds']);
        },
        error: (err: any) => {
          this.isLoading.set(false);
          this.errorMessage.set(err.error?.message || 'Authentication failed. Please check your credentials.');
        }
      });
    }
  }
}
