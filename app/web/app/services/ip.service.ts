import { Injectable, Injector } from "@angular/core";
import { APIService } from "./api.service";
import { IpInfo } from "../models/ipinfo";

@Injectable({
    providedIn: 'root'
})
export class IpInfoService extends APIService<IpInfo, string> {


    constructor(
        protected override injector: Injector
    ) {
        super(injector, '')
    }

    getIpInfo(ip: string) {
        return this.httpClient.get<IpInfo>(this.END_POINT + "ip/info/" + ip);
    }
    getIpInfoByASN(searchTerm: string) {
        return this.httpClient.get<IpInfo>(this.END_POINT + "asn/" + searchTerm);
    }

    getIpInfoByNetwork(searchTerm: string) {
        return this.httpClient.get<IpInfo>(this.END_POINT + "network/" + searchTerm);
    }
}
