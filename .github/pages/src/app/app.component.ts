import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatTabsModule } from '@angular/material/tabs';
import { MatDividerModule } from '@angular/material/divider';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatMenuModule } from '@angular/material/menu';
import { TranslateDirective, TranslatePipe, TranslateService } from '@ngx-translate/core';
import packageJson from '../../package.json';

interface FeatureItem {
  icon: string;
  titleKey: string;
  badgeKey: string;
  descriptionKey: string;
}

interface ScreenshotItem {
  id: string;
  icon: string;
  titleKey: string;
  subtitleKey: string;
  urlKey: string;
  image: string;
  descriptionKey: string;
  tagKeys: string[];
}

interface MetricItem {
  labelKey: string;
  value: string;
  captionKey: string;
}

interface FeedItem {
  name: string;
  description: string;
  type: string;
}

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatToolbarModule,
    MatButtonModule,
    MatIconModule,
    MatCardModule,
    MatChipsModule,
    MatTabsModule,
    MatDividerModule,
    MatTooltipModule,
    MatSelectModule,
    MatFormFieldModule,
    MatMenuModule,
    TranslateDirective,
    TranslatePipe
  ],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent {
  private translate = inject(TranslateService);

  readonly title = 'IPXA';
  readonly version = packageJson.version;

  readonly currentLang = signal<string>('en_US');

  readonly languages = [
    { code: 'en_US', labelKey: 'NAVBAR.LANG_EN' },
    { code: 'pt_BR', labelKey: 'NAVBAR.LANG_PT' }
  ];

  constructor() {
    this.translate.addLangs(['en_US', 'pt_BR']);
    this.translate.setFallbackLang('en_US');
    const savedLang = typeof localStorage !== 'undefined' ? localStorage.getItem('ipxa_pages_lang') : null;
    let initialLang = 'en_US';
    if (savedLang && (savedLang === 'en_US' || savedLang === 'pt_BR')) {
      initialLang = savedLang;
    } else if (typeof navigator !== 'undefined') {
      const browserLang = navigator.language.replace('-', '_');
      initialLang = browserLang.startsWith('pt') ? 'pt_BR' : 'en_US';
    }
    this.currentLang.set(initialLang);
    this.translate.use(initialLang);
  }

  setLanguage(lang: string): void {
    this.currentLang.set(lang);
    this.translate.use(lang);
    if (typeof localStorage !== 'undefined') {
      localStorage.setItem('ipxa_pages_lang', lang);
    }
  }

  readonly metrics: MetricItem[] = [
    { labelKey: 'METRICS.LATENCY.LABEL', value: '< 5ms', captionKey: 'METRICS.LATENCY.CAPTION' },
    { labelKey: 'METRICS.FEEDS.LABEL', value: '20+ Feeds', captionKey: 'METRICS.FEEDS.CAPTION' },
    { labelKey: 'METRICS.PRIVATE.LABEL', value: '100% Private', captionKey: 'METRICS.PRIVATE.CAPTION' },
    { labelKey: 'METRICS.HOOKS.LABEL', value: 'Apache & Nginx', captionKey: 'METRICS.HOOKS.CAPTION' }
  ];

  readonly features: FeatureItem[] = [
    {
      icon: 'public',
      titleKey: 'FEATURES.GEOIP.TITLE',
      badgeKey: 'FEATURES.GEOIP.BADGE',
      descriptionKey: 'FEATURES.GEOIP.DESCRIPTION'
    },
    {
      icon: 'security',
      titleKey: 'FEATURES.RBL.TITLE',
      badgeKey: 'FEATURES.RBL.BADGE',
      descriptionKey: 'FEATURES.RBL.DESCRIPTION'
    },
    {
      icon: 'bolt',
      titleKey: 'FEATURES.API_FLAVORS.TITLE',
      badgeKey: 'FEATURES.API_FLAVORS.BADGE',
      descriptionKey: 'FEATURES.API_FLAVORS.DESCRIPTION'
    },
    {
      icon: 'domain',
      titleKey: 'FEATURES.WORKSPACE.TITLE',
      badgeKey: 'FEATURES.WORKSPACE.BADGE',
      descriptionKey: 'FEATURES.WORKSPACE.DESCRIPTION'
    },
    {
      icon: 'integration_instructions',
      titleKey: 'FEATURES.HOOKS.TITLE',
      badgeKey: 'FEATURES.HOOKS.BADGE',
      descriptionKey: 'FEATURES.HOOKS.DESCRIPTION'
    },
    {
      icon: 'dashboard',
      titleKey: 'FEATURES.DASHBOARD.TITLE',
      badgeKey: 'FEATURES.DASHBOARD.BADGE',
      descriptionKey: 'FEATURES.DASHBOARD.DESCRIPTION'
    }
  ];

  readonly screenshots: ScreenshotItem[] = [
    {
      id: 'admin-dashboard',
      icon: 'dashboard',
      titleKey: 'SCREENSHOTS.ADMIN_DASHBOARD.TITLE',
      subtitleKey: 'SCREENSHOTS.ADMIN_DASHBOARD.SUBTITLE',
      urlKey: 'SCREENSHOTS.ADMIN_DASHBOARD.URL',
      image: 'assets/screenshot-01.png',
      descriptionKey: 'SCREENSHOTS.ADMIN_DASHBOARD.DESCRIPTION',
      tagKeys: [
        'SCREENSHOTS.ADMIN_DASHBOARD.TAG_1',
        'SCREENSHOTS.ADMIN_DASHBOARD.TAG_2',
        'SCREENSHOTS.ADMIN_DASHBOARD.TAG_3'
      ]
    },
    {
      id: 'ip-info',
      icon: 'travel_explore',
      titleKey: 'SCREENSHOTS.IP_INFO.TITLE',
      subtitleKey: 'SCREENSHOTS.IP_INFO.SUBTITLE',
      urlKey: 'SCREENSHOTS.IP_INFO.URL',
      image: 'assets/screenshot-02.png',
      descriptionKey: 'SCREENSHOTS.IP_INFO.DESCRIPTION',
      tagKeys: [
        'SCREENSHOTS.IP_INFO.TAG_1',
        'SCREENSHOTS.IP_INFO.TAG_2',
        'SCREENSHOTS.IP_INFO.TAG_3'
      ]
    }
  ];

  readonly feeds: FeedItem[] = [
    { name: 'FireHOL Level 1', description: 'Highly curated threat aggregation lists', type: 'Reputation' },
    { name: 'Cisco Talos & DShield', description: 'Global IP blacklists and attack telemetry', type: 'Reputation' },
    { name: 'Abuse.ch Feodo & SSLBL', description: 'Active botnet C2 servers and malicious SSL IPs', type: 'Reputation' },
    { name: 'Spamhaus DROP', description: 'Don\'t Route Or Peer advisory blocks', type: 'Reputation' },
    { name: 'Emerging Threats & CI Army', description: 'Known compromised hosts and malicious scanners', type: 'Reputation' },
    { name: 'Blocklist.de & GreenSnow', description: 'SSH, mail, and brute-force attacker IPs', type: 'Reputation' },
    { name: 'Binary Defense & BruteForce', description: 'Honeypot attackers and SSH brute-force lists', type: 'Reputation' },
    { name: 'Tor Project & Cymru Bogons', description: 'Tor exit nodes and unallocated IP ranges', type: 'Reputation' }
  ];

  readonly composeCode = `volumes:
  data:

services:
  ipxa:
    image: liberatti/ipxa:latest
    container_name: ipxa
    environment:
      - API_KEY=dev
      # - SECURITY_ENABLED=false
      # - IPINFO_TOKEN=
      # - IBLOCKLIST_USERNAME=
      # - IBLOCKLIST_PASSWORD=
      # - MAXMIND_ACCOUNT_ID=
      # - MAXMIND_LICENSE_KEY=
    volumes:
      - data:/data
    ports:
      - "5001:5000"
    deploy:
      resources:
        limits:
          memory: 256M
    restart: unless-stopped`;

  readonly apacheHookCode = `<VirtualHost *:80>
    ServerName example.com
    DocumentRoot /var/www/html

    # IPXA Access Control Hook
    LuaHookAccessChecker /etc/httpd/lua/ipxa.lua ip_info_check

    # IPXA JSON Error Handler
    Alias /errors /etc/httpd/lua/errors.lua
    <Location /errors>
        SetHandler lua-script
    </Location>
    ErrorDocument 403 /errors
</VirtualHost>`;

  readonly nginxHookCode = `http {
    lua_package_path "/usr/local/openresty/lualib/ipxa/?.lua;;";
    lua_shared_dict ip_cache 10m; # In-memory caching

    server {
        listen 80;
        error_page 403 /lua-error;

        location / {
            access_by_lua_file /usr/local/openresty/lualib/ipxa/ip_info_check.lua;
        }

        location = /lua-error {
            internal;
            content_by_lua_file /usr/local/openresty/lualib/ipxa/errors.lua;
        }
    }
}`;

  readonly errorResponseCode = `{
  "error": "Forbidden",
  "status": 403,
  "request_id": "b10ed3a6f76ad62a75a956ce3e922336",
  "message": "ipxa [block/risk-score]: 172.20.0.1 risk_score=14"
}`;

  readonly apiInfoCode = `GET /ipxa/api/ip/info/14.152.94.1
x-api-key: dev

# Response (HTTP 200 OK)
{
  "ip": {
    "address": "14.152.94.1",
    "network": "14.152.80.0",
    "prefix": 20,
    "version": 4
  },
  "location": {
    "continent": "Asia",
    "country_name": "China",
    "country_code": "CN"
  },
  "organization": {
    "asn_name": "CT-DONGGUAN-IDC CHINANET Guangdong province network",
    "asn_number": 134763
  },
  "security": {
    "reasons": [
      "rbl:firehol_level1"
    ],
    "risk_score": 9,
    "trusted": false
  }
}`;

  readonly apiCheckCode = `GET /ipxa/api/ip/check/14.152.94.1

# Response (HTTP 200 OK)
{
  "ip": "14.152.94.1",
  "risk_score": 9,
  "reasons": [
    "rbl:firehol_level1"
  ]
}`;

  readonly apiQuickCode = `GET /ipxa/api/ip/quick/14.152.94.1

# Response Headers:
# x-risk-score: 9
# x-country-code: CN
# x-trusted: False

# Response Body (HTTP 200 OK)
{
  "risk_score": 9
}`;

  copiedCompose = false;
  copiedApache = false;
  copiedNginx = false;
  copiedApi = false;

  copyCompose(): void {
    navigator.clipboard.writeText(this.composeCode).then(() => {
      this.copiedCompose = true;
      setTimeout(() => (this.copiedCompose = false), 2000);
    });
  }

  copyApache(): void {
    navigator.clipboard.writeText(this.apacheHookCode).then(() => {
      this.copiedApache = true;
      setTimeout(() => (this.copiedApache = false), 2000);
    });
  }

  copyNginx(): void {
    navigator.clipboard.writeText(this.nginxHookCode).then(() => {
      this.copiedNginx = true;
      setTimeout(() => (this.copiedNginx = false), 2000);
    });
  }

  copyApi(code: string): void {
    navigator.clipboard.writeText(code).then(() => {
      this.copiedApi = true;
      setTimeout(() => (this.copiedApi = false), 2000);
    });
  }
}
