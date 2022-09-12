from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table
from sqlalchemy.types import Date, Integer
from sqlalchemy.orm import relationship
from uatsession import uatengine1
from uatsession import UATBase
import datetime


from sqlalchemy.ext.automap import automap_base
from sqlalchemy import MetaData

metadata = MetaData()
# UATBase = automap_base(bind=uatengine1, metadata=metadata)


class DocumentModel(UATBase):
    __table__ = Table('documentmodel', UATBase.metadata,
                      autoload=True, autoload_with=uatengine1)

# creating class to load DocumentType table


class DocumentType(UATBase):
    __table__ = Table('documenttype', UATBase.metadata,
                      autoload=True, autoload_with=uatengine1)

# creating class to load Document table


class Document(UATBase):
    __table__ = Table('document', UATBase.metadata,
                      autoload=True, autoload_with=uatengine1)

# creating class to load Document table


class DocumentStatus(UATBase):
    __table__ = Table('documentstatus', UATBase.metadata,
                      autoload=True, autoload_with=uatengine1)

# creating class to load DocumentData table


class DocumentData(UATBase):
    __table__ = Table('documentdata', UATBase.metadata,
                      autoload=True, autoload_with=uatengine1)

# creating class to load DocumentTagDef table


class DocumentTagDef(UATBase):
    __table__ = Table('documenttagdef', UATBase.metadata,
                      autoload=True, autoload_with=uatengine1)

# creating class to load DocumentTags table
# class DocumentTags(UATBase):
#     __table__ = Table('DocumentTags', UATBase.metadata,
#                           autoload=True, autoload_with=uatengine1)

# creating class to load DocumentUpdates table


class DocumentUpdates(UATBase):
    __table__ = Table('documentupdates', UATBase.metadata,
                      autoload=True, autoload_with=uatengine1)

# creating class to load DocumentStage table


class DocumentStage(UATBase):
    __table__ = Table('documentstage', UATBase.metadata,
                      autoload=True, autoload_with=uatengine1)

# creating class to load DocumentTableDef table


class DocumentTableDef(UATBase):
    __table__ = Table('documenttabledef', UATBase.metadata,
                      autoload=True, autoload_with=uatengine1)

# creating class to load DocumentLineItems table


class DocumentLineItems(UATBase):
    __table__ = Table('documentlineitems', UATBase.metadata,
                      autoload=True, autoload_with=uatengine1)

# creating class to load DocumentLineItemTags table


class DocumentLineItemTags(UATBase):
    __table__ = Table('documentlineitemtags', UATBase.metadata,
                      autoload=True, autoload_with=uatengine1)


class DocumentHistoryLogs(UATBase):
    __table__ = Table('documenthistorylog', UATBase.metadata,
                      autoload=True, autoload_with=uatengine1)

# USER TABLES

# creating class to load customer table


class Customer(UATBase):
    __table__ = Table('customer', UATBase.metadata,
                      autoload=True, autoload_with=uatengine1)

    def datadict(self):
        d = {
            "idCustomer": self.idCustomer,
            "CustomerName": self.CustomerName,
        }
        return d

# creating class to load entitytype table


class EntityType(UATBase):
    __table__ = Table('entitytype', UATBase.metadata,
                      autoload=True, autoload_with=uatengine1)

# creating class to load entity table


class Entity(UATBase):
    __table__ = Table('entity', UATBase.metadata,
                      autoload=True, autoload_with=uatengine1)

# creating class to load entitybodytype table


class EntityBodyType(UATBase):
    __table__ = Table('entitybodytype', UATBase.metadata,
                      autoload=True, autoload_with=uatengine1)

# creating class to load entitybody table


class EntityBody(UATBase):
    __table__ = Table('entitybody', UATBase.metadata,
                      autoload=True, autoload_with=uatengine1)

# creating class to load entitybody table


class Department(UATBase):
    __table__ = Table('department', UATBase.metadata,
                      autoload=True, autoload_with=uatengine1)


class UserAccess(UATBase):
    """
    stores user access for entity and entity body
    """
    __table__ = Table('useraccess', UATBase.metadata,
                      autoload=True, autoload_with=uatengine1)

    def datadict(self):
        d = {
            "idUserAccess": self.idUserAccess,
            "UserID": self.UserID,
            "EntityID": self.EntityID,
            "EntityBodyID": self.EntityBodyID,
            "CreatedBy": self.CreatedBy
        }
        return d


# to store the login table
class Login_info(UATBase):
    __table__ = Table('login_info_log', UATBase.metadata,
                      autoload=True, autoload_with=uatengine1)


# to store the otp and expiry date
class Otp_Code(UATBase):
    __table__ = Table('password_otp', UATBase.metadata,
                      autoload=True, autoload_with=uatengine1)


# creating class to load entitybody table
class User(UATBase):
    __table__ = Table('user', UATBase.metadata,
                      autoload=True, autoload_with=uatengine1)

    def datadict(self):
        d = {
            "idUser": self.idUser,
            "customerID": self.customerID,
            "firstName": self.firstName,
            "lastName": self.lastName,
            "contact": self.contact,
            "UserCode": self.UserCode,
            "Designation": self.Designation,
            "email": self.email
        }
        return d


# Vendor Table
class Vendor(UATBase):
    # __tablename__ = 'Vendor'
    __table__ = Table('vendor', UATBase.metadata,
                      autoload=True, autoload_with=uatengine1)


# VendorAccount Table
class VendorAccount(UATBase):
    # __tablename__ = 'VendorAccount'
    __table__ = Table('vendoraccount', UATBase.metadata,
                      autoload=True, autoload_with=uatengine1)


# VendorUserAccess Table
class VendorUserAccess(UATBase):
    # __tablename__ = 'VendorAccount'
    __table__ = Table('vendoruseraccess', UATBase.metadata,
                      autoload=True, autoload_with=uatengine1)


# Vendor Service Table
class ServiceProvider(UATBase):
    # __tablename__ = 'Service'
    __table__ = Table('serviceprovider', UATBase.metadata,
                      autoload=True, autoload_with=uatengine1)


# ServiceAccount Table
class ServiceAccount(UATBase):
    # __tablename__ = 'ServiceAccount'
    __table__ = Table('serviceaccount', UATBase.metadata,
                      autoload=True, autoload_with=uatengine1)


# SupplierSchedule Table
class ServiceProviderSchedule(UATBase):
    # __tablename__ = 'SupplierSchedule'
    __table__ = Table('serivceproviderschedule', UATBase.metadata,
                      autoload=True, autoload_with=uatengine1)


# BatchTriggerHistory Table
class BatchTriggerHistory(UATBase):
    __table__ = Table('batchprocesshistory', UATBase.metadata,
                      autoload=True, autoload_with=uatengine1)


# AccountCostAllocation Table
class AccountCostAllocation(UATBase):
    # __tablename__ = 'AccountCostAllocation'
    __table__ = Table('accountcostallocation', UATBase.metadata,
                      autoload=True, autoload_with=uatengine1)

# Credentials Table


class Credentials(UATBase):
    # __tablename__ = 'AccountCostAllocation'
    __table__ = Table('credentials', UATBase.metadata,
                      autoload=True, autoload_with=uatengine1)
# Preparing the classes to reflect the existing table structure
# UATBase.prepare(uatengine1, reflect=True)
# Permisiions


class AccessPermission(UATBase):
    """
    holds access permission details of the user and vendor
    """
    # __tablename__ = 'accesspermission'
    __table__ = Table('accesspermission', UATBase.metadata,
                      autoload=True, autoload_with=uatengine1)

    def datadict(self):
        """
        custom dictionary function to return only required columns
        :return: dictionary of selected columns
        """
        d = {
            "idAccessPermission": self.idAccessPermission,
            "permissionDefID": self.permissionDefID,
            "userID": self.userID,
            "vendorUserID": self.vendorUserID,
            "approvalLevel": self.approvalLevel
        }
        return d


# idAccessPermissionDef Table
class AccessPermissionDef(UATBase):
    """
    stores the definition of the permission and permission id
    """
    # __tablename__ = 'accesspermissiondef'
    __table__ = Table('accesspermissiondef', UATBase.metadata,
                      autoload=True, autoload_with=uatengine1)

    def datadict(self):
        """
        custom dictionary function to return only required columns
        :return: dictionary of selected columns
        """
        d = {
            "idAccessPermissionDef": self.idAccessPermissionDef,
            "NameOfRole": self.NameOfRole,
            "Priority": self.Priority,
            "User": self.User,
            "Permissions": self.Permissions,
            "AccessPermissionTypeId": self.AccessPermissionTypeId,
            "NewInvoice": self.NewInvoice,
            "amountApprovalID": self.amountApprovalID
        }
        return d


# AccessPermissionType Table
class AccessPermissionType(UATBase):
    # __tablename__ = 'accesspermissiontype'
    __table__ = Table('accesspermissiontype', UATBase.metadata,
                      autoload=True, autoload_with=uatengine1)


# AmountApproveLevel Table
class AmountApproveLevel(UATBase):
    # __tablename__ = 'amountapprovelevel'
    __table__ = Table('amountapprovelevel', UATBase.metadata,
                      autoload=True, autoload_with=uatengine1)

    def datadict(self):
        d = {
            "idAmountApproveLevel": self.idAmountApproveLevel,
            "MaxAmount": self.MaxAmount
        }
        return d


#
class ColumnPosDef(UATBase):
    # __tablename__ = 'amountapprovelevel'
    __table__ = Table('columnnamesdef', UATBase.metadata,
                      autoload=True, autoload_with=uatengine1)


class DocumentColumnPos(UATBase):
    # __tablename__ = 'amountapprovelevel'
    __table__ = Table('documentcolumns', UATBase.metadata,
                      autoload=True, autoload_with=uatengine1)


# ----------- FR Tables ------------------

# FR configuration Table


class FRConfiguration(UATBase):
    __table__ = Table('frconfigurations', UATBase.metadata,
                      autoload=True, autoload_with=uatengine1)

# FR Meta Data Table


class FRMetaData(UATBase):
    __table__ = Table('frmetadata', UATBase.metadata,
                      autoload=True, autoload_with=uatengine1)
# OCR Log Table


class OCRLogs(UATBase):
    __table__ = Table('ocrlogs', UATBase.metadata,
                      autoload=True, autoload_with=uatengine1)

# OCR UserItem Mapping


class UserItemMapping(UATBase):
    __table__ = Table('useritemmapping', UATBase.metadata,
                      autoload=True, autoload_with=uatengine1)


# Application General config

class GeneralConfig(UATBase):
    __table__ = Table('generalconfig', UATBase.metadata,
                      autoload=True, autoload_with=uatengine1)



# documentRules data


class Rule(UATBase):
    __table__ = Table('documentrules', UATBase.metadata,
                      autoload=True, autoload_with=uatengine1)

class AGIRule(UATBase):
    __table__ = Table('erprulecodes', UATBase.metadata,
                      autoload=True, autoload_with=uatengine1)


class DocumentSubStatus(UATBase):
    __table__ = Table('documentsubstatus', UATBase.metadata,
                      autoload=True, autoload_with=uatengine1)



class DocumentRulemapping(UATBase):
    __table__ = Table('docrulestatusmapping', UATBase.metadata,
                      autoload=True, autoload_with=uatengine1)

class DocumentRuleupdates(UATBase):
    __table__ = Table('documentruleshistorylog', UATBase.metadata,
                      autoload=True, autoload_with=uatengine1)

class DocumentModelComposed(UATBase):
    __table__ = Table('documentmodelcomposed', UATBase.metadata,
                      autoload=True, autoload_with=uatengine1)


# notification Models

class PullNotification(UATBase):
    __table__ = Table('pullnotification', UATBase.metadata,
                      autoload=True, autoload_with=uatengine1)


class PullNotificationTemplate(UATBase):
    __table__ = Table('pullnotificationtemplate', UATBase.metadata,
                      autoload=True, autoload_with=uatengine1)


class NotificationCategoryRecipient(UATBase):
    __table__ = Table('notificationrecipents', UATBase.metadata,
                      autoload=True, autoload_with=uatengine1)


class TriggerDescription(UATBase):
    __table__ = Table('triggerdescription', UATBase.metadata,
                          autoload=True, autoload_with=uatengine1)


class BatchErrorType(UATBase):
    __table__ = Table('batcherrortypes', UATBase.metadata,
                      autoload=True, autoload_with=uatengine1)


class ItemMetaData(UATBase):
    __table__ = Table('itemmetadata', UATBase.metadata,
                      autoload=True, autoload_with=uatengine1)


class ItemUserMap(UATBase):
    __table__ = Table('itemusermap', UATBase.metadata,
                      autoload=True, autoload_with=uatengine1)

class DefaultFields(UATBase):
    __table__ = Table('defaultfields', UATBase.metadata,
                      autoload=True, autoload_with=uatengine1)


class AgiCostAlloc(UATBase):
    __table__ = Table('agicostallocation', UATBase.metadata,
                      autoload=True, autoload_with=uatengine1)

