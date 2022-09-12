import { Component, OnInit } from '@angular/core';
import { SharedService } from 'src/app/services/shared/shared.service';

@Component({
  selector: 'app-entity-routing',
  templateUrl: './entity-routing.component.html',
  styleUrls: ['./entity-routing.component.scss']
})
export class EntityRoutingComponent implements OnInit {
  entities = [];
  entityList:any[];
  showsuccess:boolean=false;
  showfailure:boolean=false;
  constructor(private sharedService:SharedService) { }

  ngOnInit(): void {
    this.readEntityList(this.showfailure,this.showsuccess);
  }
  readEntityList(showfail,showsuccess){
    this.showfailure = showfail;
    this.showsuccess = showsuccess;
    this.sharedService.getallEntities().subscribe(data => {
      this.entities = data;
      this.sharedService.storeEntityList.next(data);
      setTimeout(() => {
        this.searchEntity('');
      }, 100);
    });
  }
  hideAlert(){
    this.showfailure = false;
    this.showsuccess = false;
  }
  checkSynonymExists(code,entlist){
    for(let ent of this.entities){
      if(ent['EntityCode'] != code){
        let smallentlist = entlist.map(function(v){
          return v.toLowerCase();
        })
        let mainlist = ent['SynonymList'].map(function(v){
          return v.toLowerCase();
        });
        var duplicates = mainlist.filter(function(val) {
          return smallentlist.indexOf(val) != -1;
        });
        if(duplicates.length > 0){
          alert(`Duplicate Routing Keyword : Entity Name - ${ent['EntityName']}, Keywords - ${duplicates.join(", ")}`)
          return true;
        }
      }
    }
    return false;
  }
  searchEntity(value){
    let filteredEntity = this.entities.filter((entity) => {
      return entity.EntityName.toLowerCase().includes(value.toLowerCase());
    });
    if(filteredEntity.length == 0){
      filteredEntity = this.entities.filter((entity) => {
        return entity.EntityCode.toLowerCase().includes(value.toLowerCase());
      });
    }
    this.entityList = filteredEntity;
    for(let i=0;i<this.entityList.length;i++){
      this.entityList[i]['SynonymList'] = this.entityList[i]['Synonyms'] ? this.entityList[i]['Synonyms'].split(",") : [];
    }
  }
  SaveKeyWord(ent){
    this.showfailure = false;
    this.showsuccess = false;
    let filteredEntity = this.entities.filter((entity) => {
      return entity.idEntity == ent;
    });
    if(filteredEntity[0]['SynonymList'].join(",") == filteredEntity[0]['Synonyms']){
      return;
    }
    let hasduplicate = this.checkSynonymExists(filteredEntity[0]['EntityCode'],filteredEntity[0]['SynonymList']);
    if(hasduplicate){
      return;
    }
    let obj = {'City':filteredEntity[0]['City'],'Country':filteredEntity[0]['Country'],'EntityAddress':filteredEntity[0]['EntityAddress'],'Synonyms':filteredEntity[0]['SynonymList'].join(",")}
    this.sharedService.updateEntity(ent,obj).subscribe(data=>{
      if(data['message'] == 'success'){
        this.showsuccess = true;
        this.showfailure = false;
      }else{
        this.showfailure = true;
        this.showsuccess = false;
      }  
      this.readEntityList(this.showfailure,this.showsuccess);  
    })
  }
}
