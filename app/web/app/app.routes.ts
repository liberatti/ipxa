import { Routes } from '@angular/router';
import { AdminLayoutComponent } from './layouts/admin-layout/admin-layout';
import { FeedListComponent } from './view/admin/feed-list/feed-list';
import { UserListComponent } from './view/admin/user-list/user-list';
import { LoginComponent } from './view/login/login';

export const routes: Routes = [
    { path: 'login', component: LoginComponent },
    {
        path: 'admin',
        component: AdminLayoutComponent,
        children: [
            { path: 'feeds', component: FeedListComponent },
            { path: 'users', component: UserListComponent },
            { path: '', redirectTo: 'feeds', pathMatch: 'full' }
        ]
    },
    {
        path: '**',
        redirectTo: 'login',
        pathMatch: 'full'
    }
];