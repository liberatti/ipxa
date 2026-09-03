import { ApplicationConfig, provideZoneChangeDetection, InjectionToken } from '@angular/core';
import { APP_BASE_HREF } from '@angular/common';
import { provideRouter } from '@angular/router';
import { routes } from './app.routes';
import { environment } from 'environments/environment';
import { provideHttpClient, withFetch, withInterceptors } from '@angular/common/http';
import { provideMomentDateAdapter } from '@angular/material-moment-adapter';
import { MatPaginatorIntl } from '@angular/material/paginator';
import { provideTranslateService } from '@ngx-translate/core';
import { provideTranslateHttpLoader } from '@ngx-translate/http-loader';
import { JwtInterceptor } from './interceptors/jwt.interceptor';
import { CustomMatPaginatorIntl } from './services/custom-paginator-intl';

export const REST_API_URL = new InjectionToken<string>('REST_API_URL');
export const API_DATA_FORMAT = new InjectionToken<string>('API_DATA_FORMAT');

export const appConfig: ApplicationConfig = {
  providers: [
    provideZoneChangeDetection({ eventCoalescing: true }),
    provideMomentDateAdapter(undefined, { useUtc: true }),
    { provide: REST_API_URL, useValue: environment.apiUrl },
    { provide: API_DATA_FORMAT, useValue: environment.apiDateFormat },
    { provide: APP_BASE_HREF, useValue: environment.appContext },
    { provide: MatPaginatorIntl, useClass: CustomMatPaginatorIntl },

    provideRouter(routes),
    provideHttpClient(
      withFetch(), withInterceptors([JwtInterceptor])
    ),
    provideTranslateService({
      fallbackLang: 'en_US',
      lang: 'en_US'
    }),
    provideTranslateHttpLoader({
      prefix: './assets/i18n/',
      suffix: '.json'
    })
  ]
};