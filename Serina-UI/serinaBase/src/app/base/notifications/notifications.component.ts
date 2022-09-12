import { Subscription } from 'rxjs';
import { AlertService } from './../../services/alert/alert.service';
import { SharedService } from 'src/app/services/shared.service';
import { Component, OnInit } from '@angular/core';
import { IMqttMessage, MqttService } from 'ngx-mqtt';

@Component({
  selector: 'app-notifications',
  templateUrl: './notifications.component.html',
  styleUrls: ['./notifications.component.scss'],
})
export class NotificationsComponent implements OnInit {
  notifyArray: any[];
  arrayLengthNotify: number;
  lengthBoolean: boolean;
  subscription: Subscription;
  messageBox: any;
  numberOfNotify: number;
  notificationType = [
    { id: 1, name: 'System Notification' },
    { id: 2, name: 'OCR Notifications' },
    { id: 3, name: 'ERP Notification' },
    { id: 4, name: 'Batch Process Notification' },
    { id: 5, name: 'Role/User Management Notification' },
    { id: 6, name: 'Exceptions Notification' },
    { id: 7, name: 'Settings Notification' },
  ];
  constructor(
    private SharedService: SharedService,
    private _mqttService: MqttService,
    private alertService: AlertService
  ) {
    // this.messageData = this.alertService.currentUserMsgBox;
  }

  ngOnInit(): void {
    this.subscribeNewTopic();
    this.notification_logic();
    if (this.arrayLengthNotify === 0) {
      this.lengthBoolean = false;
    } else {
      this.lengthBoolean = true;
    }
  }

  notification_logic() {
    this.notifyArray = JSON.parse(localStorage.getItem('messageBox'));

    if (this.notifyArray == null) {
      this.notifyArray = [];
    } else {
      this.notifyArray = this.notifyArray.reduce((unique, o) => {
        if (
          !unique.some((obj) => obj.idPullNotification === o.idPullNotification)
        ) {
          unique.push(o);
        }
        return unique;
      }, []);
      this.numberOfNotify = this.notifyArray.length;
      this.SharedService.sendNotificationNumber(this.notifyArray.length);
      this.numberOfNotify = this.notifyArray.length;
    }
  }

  getNotification() {
    // this.SharedService.getNotification().subscribe((data: any) => {
    //   console.log(data)
    //   this.notifyArray = data;
    //   this.arrayLengthNotify = this.notifyArray.length
    //   this.SharedService.sendNotificationNumber(this.notifyArray.length);
    // })
    this.notifyArray = this.alertService.currentUserMsgBox;
  }

  subscribeNewTopic(): void {
    let name = JSON.parse(localStorage.getItem('username'));
    this.subscription = this._mqttService.observe(name + 'queue').subscribe(
      (message: IMqttMessage) => {
        this.messageBox = JSON.parse(message.payload.toString());
        if (!localStorage.getItem('messageBox') || message.retain != true) {
          let pushArray = JSON.parse(message.payload.toString());
          pushArray.forEach((element) => {
            this.notifyArray.push(element);
          });
          if (pushArray.length > 1) {
            this.notifyArray = pushArray.reduce((unique, o) => {
              if (
                !unique.some(
                  (obj) => obj.idPullNotification === o.idPullNotification
                )
              ) {
                unique.push(o);
              }
              return unique;
            }, []);
          }
          localStorage.setItem(
            'messageBox',
            JSON.stringify(this.notifyArray)
          );
          // this.arrayLengthNotify = this.notifyArray.length
          this.notification_logic();

          // this.playAudio();
        }
      },
      (error) => {
        console.log(error);
        this._mqttService.disconnect();
        this.subscription.unsubscribe();
      }
    );
  }

  // for sound
  playAudio() {
    let audio = new Audio();
    audio.src = 'assets/when-604.mp3';
    audio.load();
    audio.play();
  }

  removeNotify(value, i) {
    this.SharedService.notificationId = value;
    let id = `?nt_id=${value}`;
    this.SharedService.removeNotification(id).subscribe((data: any) => {
      this.notifyArray.splice(i, 1);
      localStorage.messageBox = JSON.stringify(this.notifyArray);
      this.SharedService.sendNotificationNumber(this.notifyArray.length);
    });
  }

  clearAll() {
    if (confirm('Are you sure you want clear all notifications?')) {
      this.SharedService.removeNotification('').subscribe((data: any) => {
        this.notifyArray = [];
        localStorage.messageBox = JSON.stringify(this.notifyArray);
        this.SharedService.sendNotificationNumber(this.notifyArray.length);
      });
    }
  }
  ngOnDestroy(): void {
    // this.subscription.unsubscribe();
  }
}
