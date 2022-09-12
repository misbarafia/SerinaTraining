import os
from azure.cosmosdb.table.tableservice import TableService
def getopunits():
    table_service = TableService(account_name=os.getenv('STORAGE_ACC',default="rovest001"), account_key=os.getenv('STORAGE_KEY',default="I5mSGj5Ak1lTT3AOVwjD8oEdhpHVWPAQxCnv21cj8q0i/agOwjqPR79iQE3VfIVTNwcWYx8DX4i8IyXmdiYAlw=="))
    mv_reqs_resp = table_service.query_entities('OpUnits')
    operationalunits = []
    for m in mv_reqs_resp:
        operationalunits.append(m['OperationalUnit'])
    return operationalunits

def addunit(unit):
    table_service = TableService(account_name=os.getenv('STORAGE_ACC',default="rovest001"), account_key=os.getenv('STORAGE_KEY',default="I5mSGj5Ak1lTT3AOVwjD8oEdhpHVWPAQxCnv21cj8q0i/agOwjqPR79iQE3VfIVTNwcWYx8DX4i8IyXmdiYAlw=="))
    mv_reqs_resp = table_service.query_entities('OpUnits')
    operationalunits = []
    for m in mv_reqs_resp:
        operationalunits.append(m['OperationalUnit'])
    j = len(operationalunits)
    j += 1
    entity = {'PartitionKey':'ROVE','RowKey':str(j),'OperationalUnit':unit}
    table_service.insert_or_merge_entity('OpUnits',entity)
    return "success"