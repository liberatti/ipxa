import {Component} from '@angular/core';
import {HashLocationStrategy, LocationStrategy} from '@angular/common';
import {RouterOutlet} from '@angular/router';

@Component({
    selector: 'app-root',
    standalone: true,
    imports: [RouterOutlet],
    templateUrl: './app.component.html',
    styleUrls: ['./app.component.css'],
    providers: [
        {provide: LocationStrategy, useClass: HashLocationStrategy},
        {provide: 'LOCALSTORAGE', useValue: window.localStorage}
    ],
})
export class AppComponent {


}