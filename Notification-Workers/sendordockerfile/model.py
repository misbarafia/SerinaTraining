from sqlalchemy import MetaData
from session import Base
from datetime import datetime
from sqlalchemy import Table
from session import engine


metadata = MetaData()


class PendingNotification(Base):
    __table__ = Table('pendingnotification', Base.metadata,
                      autoload=True, autoload_with=engine)


class PullNotification(Base):
    __table__ = Table('pullnotification', Base.metadata,
                      autoload=True, autoload_with=engine)
    def datadict(self):
        d = {
            "idPullNotification": self.idPullNotification,
            "notificationPriorityID": self.notificationPriorityID,
            "notificationTypeID": self.notificationTypeID,
            "notificationMessage": self.notificationMessage,
            "CreatedOn": self.CreatedOn.strftime("%Y-%m-%d %H:%M:%S"),
        }
        return d


class PullNotificationTemplate(Base):
    __table__ = Table('pullnotificationtemplate', Base.metadata,
                      autoload=True, autoload_with=engine)


class Document(Base):
    __table__ = Table('document', Base.metadata,
                      autoload=True, autoload_with=engine)


class DocumentHistoryLogs(Base):
    __table__ = Table('documenthistorylog', Base.metadata,
                      autoload=True, autoload_with=engine)


class TriggerDescription(Base):
    __table__ = Table('triggerdescription', Base.metadata,
                      autoload=True, autoload_with=engine)


class User(Base):
    __table__ = Table('user', Base.metadata,
                      autoload=True, autoload_with=engine)


class Entity(Base):
    __table__ = Table('entity', Base.metadata,
                      autoload=True, autoload_with=engine)


class Acl(Base):
    __table__ = Table('topic_acls', Base.metadata,
                      autoload=True, autoload_with=engine)
