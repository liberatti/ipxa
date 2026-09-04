import { Injectable, signal, effect, inject } from '@angular/core';
import { LocalStorageService } from './localstorage.service';

export type AppTheme = 'dark' | 'light';

@Injectable({
  providedIn: 'root'
})
export class ThemeService {
  private readonly THEME_KEY = 'ipxa_theme';
  private storage = inject(LocalStorageService);

  readonly currentTheme = signal<AppTheme>(this.getInitialTheme());

  constructor() {
    // Initial sync
    this.applyTheme(this.currentTheme());

    effect(() => {
      const theme = this.currentTheme();
      this.applyTheme(theme);
      this.storage.set(this.THEME_KEY, theme);
    });
  }

  toggleTheme(): void {
    this.currentTheme.update(theme => (theme === 'dark' ? 'light' : 'dark'));
  }

  setTheme(theme: AppTheme): void {
    this.currentTheme.set(theme);
  }

  isDark(): boolean {
    return this.currentTheme() === 'dark';
  }

  private getInitialTheme(): AppTheme {
    const saved = this.storage.get(this.THEME_KEY);
    if (saved === 'light' || saved === 'dark') {
      return saved;
    }
    return 'light';
  }

  private applyTheme(theme: AppTheme): void {
    const body = document.body;
    if (theme === 'light') {
      body.classList.remove('dark-theme');
      body.classList.add('light-theme');
    } else {
      body.classList.remove('light-theme');
      body.classList.add('dark-theme');
    }
  }
}
