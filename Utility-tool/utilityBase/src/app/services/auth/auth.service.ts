
import { Router } from '@angular/router';
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { environment } from 'src/environments/environment';
import { SharedService } from '../shared/shared.service';

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
    private apiUrl = environment.apiUrl
    private apiVersion = environment.apiVersion

    constructor(private http: HttpClient,
        private router:Router,
        private sharedService: SharedService) {
        this.currentUserSubject = new BehaviorSubject<User>(JSON.parse(sessionStorage.getItem('currentLoginUser')));
        this.currentUser = this.currentUserSubject.asObservable();
    }

    public get currentUserValue(): User {
        return this.currentUserSubject.value;
    }

    login(data) {
        return this.http.post<any>(`${environment.apiUrl}/apiv1.1/login`, data)
            .pipe(map(user => {
                // store user details and jwt token in session storage to keep user logged in between page refreshes
                if(user.permissioninfo.isConfigPortal === 1){
                    const userData = sessionStorage.setItem('currentLoginUser', JSON.stringify(user));
                    this.sharedService.userId = user.userdetails.idUser;
                    this.currentUserSubject.next(user);
                }
                return user;
            }));
    }

    logout() {
        // remove user from local storage to log user out
        sessionStorage.removeItem('currentLoginUser');
        this.router.navigate(['/login'])
        this.currentUserSubject.next(null);
    }
}