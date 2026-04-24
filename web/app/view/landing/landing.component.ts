import { Component, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { IpInputComponent } from 'app/components/ip-input/ip-input.component';

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
  selector: 'app-landing',
  standalone: true,
  imports: [CommonModule, IpInputComponent, MatIconModule],
  templateUrl: './landing.component.html',
  styleUrls: ['./landing.component.css']
})
export class LandingComponent {
  activeTab = signal<'info' | 'check' | 'quick'>('info');
  langTab = signal<'bash' | 'python'>('bash');
  mockResult = signal<MockResult | null>(null);
  isQuerying = signal(false);
  mobileMenuOpen = signal(false);
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

  constructor(private router: Router) {}

  onIpSearch(ip: string): void {
    this.isQuerying.set(true);
    // Simulate API response
    setTimeout(() => {
      const isClean = Math.random() > 0.4;
      this.mockResult.set({
        ip,
        country: 'United States',
        country_code: 'US',
        city: 'Mountain View',
        asn: 'AS15169',
        org: 'Google LLC',
        rbl_clean: isClean,
        rbl_lists: isClean ? [] : ['firehol_level1', 'spamhaus_sbl'],
        risk_score: isClean ? 0 : 65
      });
      this.isQuerying.set(false);
    }, 1200);
  }

  goToApp(): void {
    this.router.navigate(['/ip-info']);
  }

  setTab(tab: 'info' | 'check' | 'quick'): void {
    this.activeTab.set(tab);
  }

  riskClass = computed(() => {
    const score = this.mockResult()?.risk_score ?? 0;
    if (score === 0) return 'clean';
    if (score < 40) return 'low';
    if (score < 70) return 'medium';
    return 'high';
  });

  riskLabel = computed(() => {
    const r = this.mockResult();
    if (!r) return '';
    if (r.risk_score === 0) return 'Clean';
    if (r.risk_score < 40) return 'Low Risk';
    if (r.risk_score < 70) return 'Medium Risk';
    return 'High Risk';
  });

  apiSnippet = computed(() => {
    const tab = this.activeTab();
    if (tab === 'info') return `{
  "ip": { "address": "14.152.94.1", "version": 4 },
  "location": {
    "continent": "Asia",
    "country_code": "CN",
    "country_name": "China"
  },
  "organization": {
    "asn_number": 134763,
    "asn_name": "CT-DONGGUAN-IDC"
  },
  "security": {
    "action": "allow",
    "risk_score": 0,
    "is_permitted": true,
    "reasons": []
  }
}`;
    if (tab === 'check') return `{
  "action": "allow",
  "confidence": 1.0,
  "ip": "14.152.94.1",
  "risk_score": 0,
  "reasons": []
}`;
    return `{
  "action": "allow"
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
