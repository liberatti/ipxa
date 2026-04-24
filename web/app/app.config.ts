import { ApplicationConfig, provideZoneChangeDetection, importProvidersFrom, InjectionToken } from '@angular/core';
import { APP_BASE_HREF } from '@angular/common';
import { provideRouter } from '@angular/router';
import { routes } from './app.routes';
import { provideHttpClient, withFetch, withInterceptors } from '@angular/common/http';
import { environment } from 'environments/environment';
import { provideMomentDateAdapter } from "@angular/material-moment-adapter";

export const REST_API_URL = new InjectionToken<string>('REST_API_URL');
export const API_DATA_FORMAT = new InjectionToken<string>('API_DATA_FORMAT');

export const appConfig: ApplicationConfig = {
  providers: [

    provideZoneChangeDetection({ eventCoalescing: true }),
    provideMomentDateAdapter(undefined, { useUtc: true }),
    { provide: REST_API_URL, useValue: environment.apiUrl },
    { provide: API_DATA_FORMAT, useValue: environment.apiDateFormat },
    { provide: APP_BASE_HREF, useValue: environment.appContext },

    provideRouter(routes),
    provideHttpClient(
      withFetch(), withInterceptors([])
    )
  ]
};