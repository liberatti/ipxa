import { Injectable, Injector } from '@angular/core';
import { APIService } from './api.service';
import { Feed } from '../models/feed';

@Injectable({
  providedIn: 'root'
})
export class FeedService extends APIService<Feed, number> {

    constructor(
        protected override injector: Injector
    ) {
        super(injector, 'feed');
    }
}
