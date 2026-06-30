import { Component, signal, computed } from '@angular/core';
import { CommonModule, HashLocationStrategy, LocationStrategy } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { IpInputComponent } from 'app/components/ip-input/ip-input.component';
import { environment } from 'environments/environment';

interface MockResult {
  ip: string;
  country: string;
  country_code: string;
  city: string;
  asn: string;
  org: string;
  rbl_clean: boolean;
  rbl_lists: string[];
  risk_score: number;
}

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, IpInputComponent, MatIconModule, MatButtonModule],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
  providers: [
    { provide: LocationStrategy, useClass: HashLocationStrategy },
    { provide: 'LOCALSTORAGE', useValue: window.localStorage }
  ],
})
export class AppComponent {
  activeTab = signal<'info' | 'check' | 'quick'>('info');
  langTab = signal<'bash' | 'python'>('bash');
  mockResult = signal<MockResult | null>(null);
  isQuerying = signal(false);
  mobileMenuOpen = signal(false);
  version = signal(environment.version);
  currentYear = new Date().getFullYear();

  features = [
    {
      icon: 'geo',
      title: 'GeoIP Local',
      desc: 'Country, city, ASN, and organization resolved locally without external calls.',
      gradient: 'from-blue to-cyan'
    },
    {
      icon: 'shield',
      title: 'RBL Verification',
      desc: 'Simultaneous query across dozens of reputation blacklists in milliseconds.',
      gradient: 'from-purple to-pink'
    },
    {
      icon: 'bolt',
      title: 'High Performance',
      desc: 'No network latency. In-memory queries with response times < 5ms.',
      gradient: 'from-cyan to-green'
    },
    {
      icon: 'lock',
      title: 'Total Privacy',
      desc: 'No data leaves your infrastructure. LGPD/GDPR compliant.',
      gradient: 'from-green to-blue'
    },
    {
      icon: 'api',
      title: 'Local REST API',
      desc: 'Simple HTTP integration. Support for Python, Node, Go libraries, and more.',
      gradient: 'from-yellow to-orange'
    },
    {
      icon: 'cost',
      title: 'Zero Cost per Req.',
      desc: 'No plans, limits, or per-query charges. Run as many as you want.',
      gradient: 'from-orange to-red'
    }
  ];

  steps = [
    {
      number: '01',
      title: 'Install',
      desc: 'Configure via Docker or direct installation. Ready in less than 5 minutes.',
      code: 'docker run -d -p 5000:5000 ipxa/ipxa:latest'
    },
    {
      number: '02',
      title: 'Integrate',
      desc: 'Use the local REST API or the native library in your preferred language.',
      code: 'curl http://localhost:5000/api/ip/info/8.8.8.8'
    },
    {
      number: '03',
      title: 'Query',
      desc: 'Query IPs locally with real-time response: unified GeoIP + RBL.',
      code: '{ "action": "allow", "risk_score": 0 }'
    }
  ];

  comparison = [
    { feature: 'Average latency', external: '150–500ms', local: '< 5ms' },
    { feature: 'Cost per req.', external: '$0.001+', local: 'Zero' },
    { feature: 'Privacy', external: 'Exposed data', local: 'Total' },
    { feature: 'Availability', external: 'External SLA', local: '100% local' },
    { feature: 'LGPD/GDPR', external: 'Risk', local: 'Compliant' },
    { feature: 'Rate limiting', external: 'Yes', local: 'No' }
  ];

  setTab(tab: 'info' | 'check' | 'quick'): void {
    this.activeTab.set(tab);
  }

  apiSnippet = computed(() => {
    const tab = this.activeTab();
    if (tab === 'info') return `{
  "ip": {
    "address": "14.152.94.1",
    "broadcast": "14.152.95.255",
    "network": "14.152.80.0",
    "prefix": 20,
    "version": 4
  },
  "location": {
    "city": null,
    "continent": "Asia",
    "country": "China",
    "country_code": "CN",
    "country_name": "China",
    "latitude": 34.7732,
    "longitude": 113.722,
    "region": null
  },
  "organization": {
    "asn_description": "",
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
    if (tab === 'check') return `{
  "ip": "14.152.94.1",
  "reasons": [
    "rbl:firehol_level1"
  ],
  "risk_score": 9
}`;
    return `{
  "risk_score": 9
}`;
  });

  curlSnippet = computed(() => {
    const tab = this.activeTab();
    const endpoint = tab === 'info' ? 'info' : (tab === 'check' ? 'check' : 'quick');
    return `curl -X GET "http://localhost:5000/api/ip/${endpoint}/14.152.94.1" \\
     -H "Content-Type: application/json"`;
  });

  pythonSnippet = computed(() => {
    const tab = this.activeTab();
    const endpoint = tab === 'info' ? 'info' : (tab === 'check' ? 'check' : 'quick');
    return `import requests

response = requests.get("http://localhost:5000/api/ip/${endpoint}/14.152.94.1")
data = response.json()
print(data)`;
  });
}