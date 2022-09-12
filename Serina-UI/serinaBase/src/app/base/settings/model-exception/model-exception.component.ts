import { Component, Input, OnInit } from '@angular/core';

@Component({
  selector: 'app-model-exception',
  templateUrl: './model-exception.component.html',
  styleUrls: ['./model-exception.component.scss']
})
export class ModelExceptionComponent implements OnInit {
  avengers = [];  
  @Input() action:any;
  constructor() { }

  ngOnInit(): void {
    this.avengers = 
[{ id: 1, naming: 'Captain America', city:'US' }, 
{ id: 2, naming: 'Thor' , city:'Asgard'}, 
{ id: 3, naming: 'Iron Man' , city:'New York'}, 
{ id: 4, naming: 'Spider Man' , city:'Spiderverse'}, 
{ id: 5, naming: 'Doctor Strange', city:'Nepal' }, 
{ id: 6, naming: 'Black Panther' , city:'Wakanda'}, 
{ id: 7, naming: 'Hulk' , city:'US'}]; 
console.log(this.action)
  }

}
