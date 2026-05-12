import { Injectable, Injector } from '@angular/core';
import { APIService } from './api.service';
import { User } from '../models/user';

@Injectable({
  providedIn: 'root'
})
export class UserService extends APIService<User, number> {
  constructor(injector: Injector) {
    super(injector, 'user');
  }
}
