import { MessageService } from 'primeng/api';
import { AlertService } from 'src/app/services/alert/alert.service';
import { AuthenticationService } from './../services/auth/auth-service.service';
import { SharedService } from 'src/app/services/shared.service';
import { Injectable } from '@angular/core';
import { HttpRequest, HttpHandler, HttpEvent, HttpInterceptor, HttpErrorResponse, HttpResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';


@Injectable()
export class ErrorInterceptor implements HttpInterceptor {
    constructor(private authService: AuthenticationService,
      private alertSrvice : AlertService,
      private messageService : MessageService) { }

    intercept(request: HttpRequest<any>, next: HttpHandler): Observable<any> {
        return next.handle(request).pipe( catchError((err:HttpErrorResponse) => {
          if(err.status === 401 && !(request.url.includes('login'))){
            alert("Session got expired!, please login again");
            setTimeout(() => {
              this.authService.logout();
            }, 1000);

          }else if(err.status == 502 || 0){
            // alert("System under maintenance");
            // this.alertSrvice.errorObject.detail = "System under maintenance";
            // this.messageService.add(this.alertSrvice.errorObject);
          } else{
            // const error = err.error.message || err.statusText;
            console.log(err)
            return throwError(err)
          }
        }))
    }
}



// new Observable((observer)=>{
//   next.handle(request).subscribe(
//     (res:HttpResponse<any>)=>{
//       if(res instanceof HttpResponse) {
//         observer.next(res);
//       }
//     }, 
//     (err: HttpErrorResponse)=>{
//         if(err.status === 401 && !(request.url.includes('login'))){
//             this.authService.logout();
//           }else if(err.status == 502){
//             alert("System under maintenance");
//             // this.alertSrvice.errorObject.detail = "System under maintenance";
//             // console.log(this.alertSrvice.errorObject.detail)
//             // this.messageService.add(this.alertSrvice.errorObject);
//           } else{
//             // const error = err.error.message || err.statusText;
//             console.log(err)
//             return throwError(err)
//           }
//     }
//   )
// })