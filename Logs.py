
from sqlalchemy.orm import relationship, scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy import ForeignKey
from sqlalchemy.sql import func
from sqlalchemy import Column, Integer, String, Date, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from os import path
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
import datetime
from flaskXMLRPC import XMLRPCHandler
from flask import Flask

app = Flask(__name__)

handler = XMLRPCHandler('api')
handler.connect(app, '/api')


DATABASE_FILE = "logs.sqlite"
db_exists = False
if path.exists(DATABASE_FILE):
    db_exists = True
    print("\t database already exists")

Base = declarative_base()
engine = create_engine('sqlite:///%s'%(DATABASE_FILE), echo=False) #echo = True shows all SQL calls




class Log(Base):
    __tablename__ = 'Log'

    id = Column(Integer, primary_key=True)
    




class Request(Base):
    __tablename__ = 'Request'

    id = Column(Integer, ForeignKey("Log.id"), primary_key=True)
    timestamp = Column(String)

    IP = Column(String)
    endpoint = Column(String)
    content = Column(String)    
    
    def __repr__(self):
        return "<Request (ID=%d, timestamp=%s, IP=%s, endpoint=%s, content=%s)>" % (
                                self.id, self.timestamp, self.IP, self.endpoint, self.content)
    def to_dictionary(self):
        return {"id": self.id, "timestamp":self.timestamp,"IP":self.IP, "endpoint": self.endpoint, "content":self.content}


class DataCreationEvent(Base):
    __tablename__ = 'DataCreationEvent'

    id = Column(Integer, ForeignKey("Log.id"), primary_key=True)
    timestamp = Column(String)

    data_type = Column(String)
    content = Column(String)  
    user_id = Column(String)  
    
    def __repr__(self):
        return "<DataCreationEvent (ID=%d, timestamp=%s, data_type=%s, content=%s, user_id=%s)>" % (
                                self.id, self.timestamp, self.data_type, self.content, self.user_id)
    def to_dictionary(self):
        return {"id": self.id, "timestamp":self.timestamp,"data_type":self.data_type, "content": self.content, "user_id":self.user_id}


Session = sessionmaker(bind=engine)
session = scoped_session(Session)
#session = Session()





@handler.register
def LogRequest(timestamp, IP, endpoint, content):
 
    log = Log()
    try:
        session.add(log)
        session.flush()
        req = Request(timestamp=timestamp, id = log.id, IP = IP, endpoint = endpoint, content=content)
        session.add(req)
        session.commit()
        session.close() 
        print(req.id)
        return req.id
    except:
        return None


@handler.register
def LogDataCreationEvent(timestamp, data_type, content, user_id):
    log = Log()
    try:
        session.add(log)
        session.flush()
        #session.commit()

        dce = DataCreationEvent(timestamp=timestamp,id = log.id, data_type = data_type, content = content, user_id = user_id)
        session.add(dce)
        session.commit()

        session.close()
        return dce.id
    except:
        return None



def listRequests():
    v = session.query(Request).all()
    session.close()
    
    return v

def listDataCreationEvents():
    v = session.query(DataCreationEvent).all()
    session.close()
    
    return v

@handler.register
def listDataCreationEventsDICT():
    ret_list = []
    ll = listDataCreationEvents()
    
    for log in ll:
        logd = log.to_dictionary()
        ret_list.append(logd)
    ret_list = sorted(ret_list, key=lambda k: k['id'], reverse=True) 
    return ret_list

@handler.register
def listRequestsDICT():
    ret_list = []
    ll = listRequests()
    
    for log in ll:
        logd = log.to_dictionary()
        ret_list.append(logd)
    ret_list = sorted(ret_list, key=lambda k: k['id'], reverse=True) 
    return ret_list

@handler.register
def listLogsDICT():
    ret_list = listRequestsDICT() + listDataCreationEventsDICT()
    ret_list = sorted(ret_list, key=lambda k: k['id'], reverse=True) 
    return ret_list

Base.metadata.create_all(engine)

if __name__ == "__main__":
    #pass
    app.run(host='127.0.0.1', port=8003, debug=True)