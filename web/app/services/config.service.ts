import { Injectable, Inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { REST_API_URL } from '../app.config';

export interface ConfigStats {
  cache_size: number;
  feeds_reputation: number;
  feeds_bypass: number;
  rbl_size: number;
  geoip_entries: number;
}

@Injectable({
  providedIn: 'root'
})
export class ConfigService {
  constructor(
    private httpClient: HttpClient,
    @Inject(REST_API_URL) private apiUrl: string
  ) {}

  getStats(): Observable<ConfigStats> {
    return this.httpClient.get<ConfigStats>(`${this.apiUrl}/api/config/stats`);
  }
}
