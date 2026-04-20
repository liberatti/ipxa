import { Routes } from '@angular/router';
import { LandingLayoutComponent } from './layouts/landing-layout/landing-layout.component';
import { LandingComponent } from './view/landing/landing.component';

export const routes: Routes = [

    {
        path: '',
        component: LandingLayoutComponent,
        children: [
            { path: '', component: LandingComponent }
        ]
    },
    {
        path: '**',
        redirectTo: '',
        pathMatch: 'full'
    }
];