import { ChartsService } from './../dashboard/charts.service';
import { DocumentService } from './../vendorPortal/document.service';
import { SharedService } from './../shared.service';
import { Router } from '@angular/router';
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { environment } from 'src/environments/environment';
import { environment1 } from 'src/environments/environment.prod';

export interface User{
    id?: number;
    username: string;
    password: string;
    firstName?: string;
    lastName?: string;
    token?: string;
    user_type? : string;
}

@Injectable({ providedIn: 'root' })
export class AuthenticationService {
    private currentUserSubject: BehaviorSubject<User>;
    public currentUser: Observable<User>;
    private apiUrl = environment.apiUrl;
    private apiVersion = environment.apiVersion;

    constructor(private http: HttpClient,
        private router:Router,
        private docService : DocumentService,
        private chartService : ChartsService,
        private sharedService: SharedService) {
        this.currentUserSubject = new BehaviorSubject<User>(JSON.parse(localStorage.getItem('currentLoginUser')));
        this.currentUser = this.currentUserSubject.asObservable();
    }

    public get currentUserValue(): User {
        return this.currentUserSubject.value;
    }

    login(data) {
        return this.http.post<any>(`${this.apiUrl}/${this.apiVersion}/login`, data)
            .pipe(map(user => {
                // store user details and jwt token in session storage to keep user logged in between page refreshes
                const userData = localStorage.setItem('currentLoginUser', JSON.stringify(user));
                this.sharedService.userId = user.userdetails.idUser;
                this.docService.userId = user.userdetails.idUser;
                this.chartService.userId = user.userdetails.idUser;
                this.currentUserSubject.next(user);
                environment1.password = user.token;
                // environment1.password = this.currentUserValue.password;
                return user;
            }));
    }

    logout() {
        // remove user from local storage to log user out
        localStorage.removeItem('currentLoginUser');
        localStorage.removeItem('username');
        localStorage.removeItem('messageBox');
        localStorage.clear();
        this.router.navigate(['/login']);
        setTimeout(() => {
        if(this.router.url.includes('login')){
            window.location.reload();
        }
        }, 500);
        this.currentUserSubject.next(null);
    }
}