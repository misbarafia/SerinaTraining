from azure.storage.blob import BlobServiceClient
import pandas as pd
from io import BytesIO
import time
from datetime import datetime
import model
from session import engine
from sqlalchemy.orm import load_only
from session import Session as SessionLocal
import traceback


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def remove_expired_tokens_task():
    print("function running")
    start_time = time.time()
    # READ EXCEL
    # excel_pth = 'ItemHardTagging_update.xlsx'
    # sheet = 'Batch1'
    db = next(get_db())
    excel_pth = None
    try:
        excel_pth = db.query(model.ItemMapUploadHistory).options(load_only("uploaded_file", "uploaded_by")).filter_by(
            status="File Uploaded").limit(1).one()
        # to get status if already file is being processed
        is_executing = db.query(
            model.ItemMapUploadHistory.iditemmappinguploadhistory).filter_by(status="File Processing").scalar()
    except Exception as e:
        # no excel files to process
        return
    if excel_pth and is_executing is None:
        print("function executed")
        db.query(model.ItemMapUploadHistory).filter_by(
            iditemmappinguploadhistory=excel_pth.iditemmappinguploadhistory).update({"status": "File Processing"})
        db.commit()
        UserID = excel_pth.uploaded_by
        con_details = db.query(model.FRConfiguration.ConnectionString,
                               model.FRConfiguration.ContainerName).filter_by(
            idFrConfigurations=1).one()
        blob_service_client = BlobServiceClient.from_connection_string(con_details.ConnectionString)
        blob_client = blob_service_client.get_blob_client(container=con_details.ContainerName,
                                                          blob=excel_pth.uploaded_file)
        data = blob_client.download_blob().readall()
        # data = BytesIO(data)
        ItemHardTagging_df = pd.read_excel(data, sheet_name=0)
        ItemHardTagging_df['ItemId'] = ItemHardTagging_df['ItemId'].astype(object)

        # get Vendor data
        vendor_String = "SELECT idVendorAccount,Account,entityBodyID FROM vendoraccount;"
        vendor_df = pd.read_sql(vendor_String, engine)

        # read meta data
        itemmetadata_String = "SELECT * FROM itemmetadata;"
        itemmetadata_df = pd.read_sql(itemmetadata_String, engine)

        # desc check:
        usrMetaData = list(itemmetadata_df['description'])
        vdrUpload = list(ItemHardTagging_df['Item Name'])
        newDescList = [set(vdrUpload) - set(usrMetaData)]

        # newDescList
        # insert newDesc list in metadata if itemcode is present:
        newDescInst = []
        newItmCdInst = []
        if len(newDescList) > 0:

            for nwDsc in newDescList[0]:
                # print(nwDsc)
                chkDesc = nwDsc
                if len(chkDesc.replace(' ', '')) > 0:
                    # print(ItemHardTagging_df[ItemHardTagging_df['ITEM NAME']==nwDsc])
                    if len(list(ItemHardTagging_df[ItemHardTagging_df['Item Name'] == nwDsc]['ItemId'])) > 0:
                        itmCD = list(ItemHardTagging_df[ItemHardTagging_df['Item Name'] == nwDsc]['ItemId'])[0]
                        if itmCD not in itemmetadata_df['itemcode']:
                            newDescInst.append(nwDsc)
                            newItmCdInst.append(itmCD)
        if len(newDescInst) > 0 and (len(newDescInst) == len(newItmCdInst)):
            createdOn = [datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")] * len(newItmCdInst)
            iditemmetadata = [0] * len(newItmCdInst)
            entityVendorid = [0] * len(newItmCdInst)
            insertMetadata_df = pd.DataFrame()
            insertMetadata_df['iditemmetadata'] = iditemmetadata
            insertMetadata_df['itemcode'] = newItmCdInst
            insertMetadata_df['description'] = newDescInst
            insertMetadata_df['vendoraccountID'] = entityVendorid
            insertMetadata_df['entityid'] = entityVendorid
            insertMetadata_df['createdOn'] = createdOn

            # insert to DB - new records
            insertMetadata_df.to_sql("itemmetadata", engine, if_exists="append", index=False)
            time.sleep(2)

        # read meta data again to get updated data
        itemmetadata_String = "SELECT * FROM itemmetadata;"
        itemmetadata_df = pd.read_sql(itemmetadata_String, engine)

        # desc check:
        usrMetaData = list(itemmetadata_df['description'])
        vdrUpload = list(ItemHardTagging_df['Item Name'])
        newDescList = [set(vdrUpload) - set(usrMetaData)]

        # Check if any duplicate records found!!
        left_out_records = []
        rejectDF = pd.DataFrame()
        if len(newDescList) > 0:

            for ltot in newDescList[0]:
                rejectDF = rejectDF.append(ItemHardTagging_df[ItemHardTagging_df['Item Name'] == ltot])
                rejectDF = rejectDF.reset_index(drop=True)

        mappedDataStr = "SELECT * FROM itemusermap;"
        mappedData_all_df = pd.read_sql(mappedDataStr, engine)

        duplicateMapDf = pd.DataFrame()
        addMappData = pd.DataFrame(columns=mappedData_all_df.columns)

        for vdr_ in set(ItemHardTagging_df['Vendor Account']):
            vnd_itemTagData = ItemHardTagging_df[ItemHardTagging_df['Vendor Account'] == vdr_].reset_index(drop=True)
            ved_accID = set(vendor_df[vendor_df['Account'] == vdr_]['idVendorAccount'])
            vnd_itemTagData['ItemId'] = vnd_itemTagData['ItemId'].astype(object)

            for itmHdTg in range(len(vnd_itemTagData)):
                invoDescMap = vnd_itemTagData['Item Hard Tagging'][itmHdTg]
                iditemmetadata = list \
                    (itemmetadata_df[itemmetadata_df['itemcode'] == str(vnd_itemTagData['ItemId'][itmHdTg])][
                         'iditemmetadata'])
                # print("invoDescMap: " ,invoDescMap ," iditemmetadata: " ,iditemmetadata)
                if len(iditemmetadata) > 0:
                    iditemmetadata = iditemmetadata[0]
                    # print("invoDescMap: " ,invoDescMap ," iditemmetadata: " ,iditemmetadata)
                    # loop for each entity:
                    for Vdr_scID in ved_accID:
                        # mappedDataStr = "SELECT * FROM itemusermap WHERE vendoraccountID = "+str(Vdr_scID)+ ";"
                        mappedData_df = mappedData_all_df[mappedData_all_df['vendoraccountID'] == Vdr_scID]
                        mappedData_df = mappedData_df.reset_index(drop=True)

                        iditemusermap = 0
                        documentID = None
                        itemmetadataid = iditemmetadata
                        vendoraccountID = Vdr_scID
                        mappedinvoiceitemcode = None
                        mappedinvoitemdescription = invoDescMap
                        batcherrortype = 5
                        previousitemmetadataid = None
                        createdOn = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

                        if iditemmetadata in list(mappedData_df['itemmetadataid']):
                            # print("Present in mappedData_df: ",iditemmetadata)
                            # if invoDescMap in list(mappedData_df[mappedData_df['itemmetadataid'] == iditemmetadata]
                            #                            ['mappedinvoitemdescription']):
                            if len(mappedData_df[mappedData_df['mappedinvoitemdescription'] == invoDescMap]) > 0:

                                duplicateMapDf = duplicateMapDf.append \
                                    (mappedData_df[mappedData_df['itemmetadataid'] == iditemmetadata])
                            else:
                                # print("line 30")
                                if len(addMappData) > 0:
                                    if iditemmetadata in list(addMappData['itemmetadataid']):
                                        # print(mappedData_df[mappedData_df['mappedinvoitemdescription'] == invoDescMap])
                                        if len(mappedData_df[
                                                   mappedData_df['mappedinvoitemdescription'] == invoDescMap]) == 0:
                                            addMappData.loc[len(addMappData.index)] = [iditemusermap, documentID
                                                , itemmetadataid, vendoraccountID
                                                , mappedinvoiceitemcode
                                                , mappedinvoitemdescription
                                                , batcherrortype, previousitemmetadataid
                                                , UserID, createdOn]
                                            # print("WORKING")
                                        else:
                                            # duplicate
                                            duplicateMapDf = duplicateMapDf.append \
                                                (mappedData_df[mappedData_df['itemmetadataid'] == iditemmetadata])
                                    else:
                                        if len(mappedData_df[
                                                   mappedData_df['mappedinvoitemdescription'] == invoDescMap]) == 0:
                                            addMappData.loc[len(addMappData.index)] = [iditemusermap, documentID
                                                , itemmetadataid, vendoraccountID
                                                , mappedinvoiceitemcode
                                                , mappedinvoitemdescription
                                                , batcherrortype, previousitemmetadataid
                                                , UserID, createdOn]
                                            # print("WORKING")
                                        else:
                                            # duplicate
                                            duplicateMapDf = duplicateMapDf.append \
                                                (mappedData_df[mappedData_df['itemmetadataid'] == iditemmetadata])

                                else:

                                    if len(mappedData_df[
                                               mappedData_df['mappedinvoitemdescription'] == invoDescMap]) == 0:
                                        addMappData.loc[len(addMappData.index)] = [iditemusermap, documentID,
                                                                                   itemmetadataid
                                            , vendoraccountID, mappedinvoiceitemcode
                                            , mappedinvoitemdescription, batcherrortype
                                            , previousitemmetadataid, UserID, createdOn]
                                        # print("WORKING")
                                    else:
                                        # duplicate
                                        duplicateMapDf = duplicateMapDf.append \
                                            (mappedData_df[mappedData_df['itemmetadataid'] == iditemmetadata])

                        else:

                            if len(addMappData) > 0:
                                if iditemmetadata in list(addMappData['itemmetadataid']):
                                    if vendoraccountID not in list(
                                            addMappData[addMappData['itemmetadataid'] == iditemmetadata][
                                                'vendoraccountID']):
                                        addMappData.loc[len(addMappData.index)] = [iditemusermap, documentID,
                                                                                   itemmetadataid
                                            , vendoraccountID, mappedinvoiceitemcode
                                            , mappedinvoitemdescription, batcherrortype
                                            , previousitemmetadataid, UserID, createdOn]
                                    else:
                                        # duplicate
                                        duplicateMapDf = duplicateMapDf.append(
                                            mappedData_df[mappedData_df['itemmetadataid'] == iditemmetadata])
                                #                                     rejectDF = rejectDF.append(ItemHardTagging_df[ItemHardTagging_df['Item Hard Tagging']==invoDescMap])
                                #                                     rejectDF = rejectDF.reset_index(drop=True)
                                else:
                                    # insert
                                    addMappData.loc[len(addMappData.index)] = [iditemusermap, documentID, itemmetadataid
                                        , vendoraccountID, mappedinvoiceitemcode
                                        , mappedinvoitemdescription, batcherrortype
                                        , previousitemmetadataid, UserID, createdOn]


                            else:
                                addMappData.loc[len(addMappData.index)] = [iditemusermap, documentID, itemmetadataid,
                                                                           vendoraccountID, mappedinvoiceitemcode,
                                                                           mappedinvoitemdescription, batcherrortype,
                                                                           previousitemmetadataid, UserID, createdOn]

                else:
                    # duplicateMapDf = duplicateMapDf.append(mappedData_df[mappedData_df['itemmetadataid']==iditemmetadata])
                    rejectDF = rejectDF.append(
                        ItemHardTagging_df[ItemHardTagging_df['Item Hard Tagging'] == invoDescMap])
                    rejectDF = rejectDF.reset_index(drop=True)
        addMappData['itemmetadataid'] = addMappData['itemmetadataid'].astype(int)
        addMappData.to_sql("itemusermap", engine, if_exists="append", index=False)
        print("_________________________________________________________________________________________")
        print("Records Inserted to itemusermap: ", len(addMappData))
        print("_________________________________________________________________________________________")
        print("Rejected Records: ", len(rejectDF))
        print("_________________________________________________________________________________________")
        print("Duplicate Records: ", len(duplicateMapDf))
        print("_________________________________________________________________________________________")
        print("Execution Time:", str(time.time() - start_time), "seconds")
        print("_________________________________________________________________________________________")
        try:
            excel_object = BytesIO()
            writer = pd.ExcelWriter("temp.xlsx", engine='openpyxl')
            rejectDF.to_excel(writer, sheet_name="rejected records", index=False)
            duplicateMapDf.to_excel(writer, sheet_name="duplicate records", index=False)
            # return rejectDF, duplicateMapDf
            writer.book.save(excel_object)
            error_file_path = f"itemmasterexcel/error_recods{excel_pth.iditemmappinguploadhistory}.xlsx"
            blob_client = blob_service_client.get_blob_client(container=con_details.ContainerName,
                                                              blob=error_file_path)
            blob_client.upload_blob(excel_object.getbuffer().tobytes(), overwrite=True)
            db.query(model.ItemMapUploadHistory).filter_by(
                iditemmappinguploadhistory=excel_pth.iditemmappinguploadhistory).update(
                {"status": "Processing Completed", "error_file": error_file_path})
            print(excel_pth.iditemmappinguploadhistory)
            db.commit()
            print("completed")
        except Exception as e:
            print(traceback.format_exc())
            time.sleep(5)


if __name__ == "__main__":
    remove_expired_tokens_task()
