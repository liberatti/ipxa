export interface IpDetails {
    address: string;
    broadcast: string;
    network: string;
    prefix: number;
    version: number;
}

export interface LocationDetails {
    continent: string;
    country_code: string;
    country_name: string;
}

export interface OrgDetails {
    asn_description: string;
    asn_name: string;
    asn_number: number;
}

export interface SecurityDetails {
    action: string;
    is_permitted: boolean;
    reasons: string[];
    risk_score: number;
}

export interface IpInfo {
    ip: IpDetails;
    location: LocationDetails;
    organization: OrgDetails;
    security: SecurityDetails;
}

// Keeping GeoIPData for backward compatibility or search results
export interface GeoIPData {
    organization: string;
    ans_number: number;
    ans_description: string;
    source: string;
    country: string;
    country_code: string;
    network: string;
    prefix: number;
    broadcast?: string;
    version: number;
}