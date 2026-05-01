import { Injectable, Injector } from '@angular/core';
import { APIService } from './api.service';
import { Workspace } from '../models/workspace';

@Injectable({
  providedIn: 'root'
})
export class WorkspaceService extends APIService<Workspace, number> {
  constructor(injector: Injector) {
    super(injector, 'workspace');
  }
}
