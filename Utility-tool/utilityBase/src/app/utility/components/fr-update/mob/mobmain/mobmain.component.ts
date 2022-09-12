import { Component, Input, OnInit } from '@angular/core';
import { MobmainService } from './mobmain.service';

@Component({
  selector: 'app-mobmain',
  templateUrl: './mobmain.component.html',
  styleUrls: ['./mobmain.component.scss']
})
export class MobmainComponent implements OnInit {
  modelData: any;
  frConfigData: any;
  filePath:any;
  ready: boolean = false;
  showtab={"show1":true,"show2":false,"show3":false,"show4":false};
  constructor(private mobservice:MobmainService) { }

  ngOnInit(): void {
    this.mobservice.getModelData().subscribe(data => this.modelData = data);
    this.mobservice.getFrConfig().subscribe(data => this.frConfigData = data);
    this.ready = true;
  }
  getTab($eve){
    this.showtab = $eve;
  }
}
