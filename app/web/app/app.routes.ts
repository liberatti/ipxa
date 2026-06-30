import { Routes } from '@angular/router';
import { AdminLayoutComponent } from './layouts/admin-layout/admin-layout';
import { FeedListComponent } from './view/admin/feed-list/feed-list';
import { LoginComponent } from './view/login/login';

export const routes: Routes = [
    { path: 'login', component: LoginComponent },
    {
        path: 'admin',
        component: AdminLayoutComponent,
        children: [
            { path: 'feeds', component: FeedListComponent },
            { path: '', redirectTo: 'feeds', pathMatch: 'full' }
        ]
    },
    {
        path: '**',
        redirectTo: 'login',
        pathMatch: 'full'
    }
];