import { Routes } from '@angular/router';
import { LandingLayoutComponent } from './layouts/landing-layout/landing-layout.component';
import { LandingComponent } from './view/landing/landing.component';
import { AdminLayoutComponent } from './layouts/admin-layout/admin-layout';
import { WorkspaceListComponent } from './view/admin/workspace-list/workspace-list';
import { FeedListComponent } from './view/admin/feed-list/feed-list';
import { LoginComponent } from './view/login/login';

export const routes: Routes = [
    { path: 'login', component: LoginComponent },

    {
        path: '',
        component: LandingLayoutComponent,
        children: [
            { path: '', component: LandingComponent }
        ]
    },
    {
        path: 'admin',
        component: AdminLayoutComponent,
        children: [
            { path: 'workspaces', component: WorkspaceListComponent },
            { path: 'feeds', component: FeedListComponent },
            { path: '', redirectTo: 'feeds', pathMatch: 'full' }
        ]
    },
    {
        path: '**',
        redirectTo: '',
        pathMatch: 'full'
    }
];