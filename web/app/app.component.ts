import { Component, inject } from '@angular/core';
import { HashLocationStrategy, LocationStrategy } from '@angular/common';
import { RouterOutlet } from '@angular/router';
import { TranslateService } from '@ngx-translate/core';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
  providers: [
    { provide: LocationStrategy, useClass: HashLocationStrategy },
    { provide: 'LOCALSTORAGE', useValue: window.localStorage }
  ],
})
export class AppComponent {
  private translate = inject(TranslateService);

  constructor() {
    this.translate.addLangs(['en_US', 'pt_BR']);
    this.translate.setFallbackLang('en_US');
    const browserLang = navigator.language.replace('-', '_');
    const defaultLang = browserLang.startsWith('pt') ? 'pt_BR' : 'en_US';
    this.translate.use(defaultLang);
  }
}