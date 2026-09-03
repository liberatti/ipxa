import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatTabsModule } from '@angular/material/tabs';
import { MatDividerModule } from '@angular/material/divider';
import { MatTooltipModule } from '@angular/material/tooltip';

interface FeatureItem {
  icon: string;
  title: string;
  badge: string;
  description: string;
}

interface ScreenshotItem {
  id: string;
  title: string;
  subtitle: string;
  image: string;
  description: string;
}

interface MetricItem {
  label: string;
  value: string;
  caption: string;
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
    MatToolbarModule,
    MatButtonModule,
    MatIconModule,
    MatCardModule,
    MatChipsModule,
    MatTabsModule,
    MatDividerModule,
    MatTooltipModule
  ],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent {
  readonly title = 'IPXA';
  readonly version = 'v1.0.10';

  readonly metrics: MetricItem[] = [
    { label: 'Ultra-low Latency', value: '< 5ms', caption: 'Sub-5ms local reputation lookups' },
    { label: 'Threat Feeds', value: '15+ RBLs', caption: 'Curated reputation & bypass lists' },
    { label: 'Private & Secure', value: '100% Private', caption: 'On-premise threat intelligence' },
    { label: 'Server Hooks', value: 'Apache & Nginx', caption: 'Edge blocking with native Lua' }
  ];

  readonly features: FeatureItem[] = [
    {
      icon: 'public',
      title: 'Intelligent GeoIP',
      badge: 'MaxMind & ip2asn',
      description: 'Local integration with MaxMind and ip2asn datasets for lightning-fast geographical, country code, and ASN lookups without external rate limits.'
    },
    {
      icon: 'security',
      title: 'RBL Threat Orchestration',
      badge: '15+ Feed Sources',
      description: 'Dynamic management of threat intelligence feeds (FireHOL 1-4, Cisco Talos, DShield, Abuse.ch Feodo, Spamhaus DROP, Emerging Threats, and Blocklist.de).'
    },
    {
      icon: 'bolt',
      title: 'Multiple API Flavors',
      badge: 'Sub-5ms Response',
      description: 'Specialized endpoints: full metadata (/api/ip/info), security checks (/api/ip/check), and headless proxy scoring (/api/ip/quick) with x-risk-score headers.'
    },
    {
      icon: 'domain',
      title: 'Multi-Workspace Isolation',
      badge: 'Multi-Tenant',
      description: 'Isolate configuration, custom threat feeds, and API keys across different environments, organizations, or security perimeters.'
    },
    {
      icon: 'integration_instructions',
      title: 'Edge Server Integrations',
      badge: 'Apache & OpenResty',
      description: 'Native Lua hooks for Apache (mod_lua) and OpenResty / Nginx for high-speed edge enforcement and standardized JSON error responses.'
    },
    {
      icon: 'dashboard',
      title: 'Admin Management Dashboard',
      badge: 'Web UI',
      description: 'Dark-mode Administrative Dashboard on port 5001 for real-time feed curation, workspace configuration, and metrics.'
    }
  ];

  readonly screenshots: ScreenshotItem[] = [
    {
      id: 'ip-info',
      title: 'Multi-Workspace & IP Intelligence',
      subtitle: 'Comprehensive GeoIP and threat breakdown per workspace',
      image: 'assets/screenshot-02.png',
      description: 'Exhaustive data inspection covering continent, country, coordinates, organization, risk level, and matched RBL reasons.'
    },
    {
      id: 'admin-dashboard',
      title: 'Admin Management Dashboard',
      subtitle: 'Dynamic threat feed management and workspace configuration',
      image: 'assets/screenshot-03.png',
      description: 'High-contrast dark-mode administrative dashboard to manage RBL threat lists, API keys, CIDR lists, and system monitoring parameters.'
    },
    {
      id: 'develop-flow',
      title: 'Development & Release Flow',
      subtitle: 'Automated Git flow & release pipeline',
      image: 'assets/develop-flow.png',
      description: 'Continuous integration lifecycle with automated release candidate branch management, lint verification, and version tagging.'
    }
  ];

  readonly feeds: FeedItem[] = [
    { name: 'FireHOL Level 1-4', description: 'Highly curated threat aggregation lists', type: 'Reputation' },
    { name: 'Cisco Talos & DShield', description: 'Global IP blacklists and attack telemetry', type: 'Reputation' },
    { name: 'Abuse.ch Feodo Tracker', description: 'Active botnet Command & Control servers', type: 'Reputation' },
    { name: 'Spamhaus DROP', description: 'Don\'t Route Or Peer advisory blocks', type: 'Reputation' },
    { name: 'Emerging Threats', description: 'Known compromised hosts and bot scanners', type: 'Reputation' },
    { name: 'Blocklist.de & GreenSnow', description: 'SSH, mail, and brute-force attacker IPs', type: 'Reputation' }
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

  readonly apiInfoCode = `GET /api/ip/info/14.152.94.1
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

  readonly apiCheckCode = `GET /api/ip/check/14.152.94.1

# Response (HTTP 200 OK)
{
  "ip": "14.152.94.1",
  "risk_score": 9,
  "reasons": [
    "rbl:firehol_level1"
  ]
}`;

  readonly apiQuickCode = `GET /api/ip/quick/14.152.94.1

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
