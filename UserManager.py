
from sqlalchemy.orm import relationship, scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy import ForeignKey
from sqlalchemy import Column, Integer, String, Date, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from os import path
from sqlalchemy import create_engine
import datetime
from flask import Flask, request
from flaskXMLRPC import XMLRPCHandler
from datetime import datetime
import xmlrpc.client

Logs_proxy = xmlrpc.client.ServerProxy("http://127.0.0.1:8003/api")

DATABASE_FILE = "users.sqlite"
db_exists = False
if path.exists(DATABASE_FILE):
    db_exists = True
    print("\t database already exists")

Base = declarative_base()
engine = create_engine('sqlite:///%s'%(DATABASE_FILE), echo=False) #echo = True shows all SQL calls




class User(Base):
    __tablename__ = 'User'

    id = Column(String, primary_key=True)

    name = Column(String)

    admin = Column(Boolean, default = False)

    def __repr__(self):
        return "<User (ID=%s, Name=%s, Admin=%s)>" % (
                                self.id, self.name, self.admin)
    def to_dictionary(self):
        return {"id": self.id, "name": self.name, "admin": self.admin}


Session = sessionmaker(bind=engine)
sess = scoped_session(Session)
#session = Session()

app = Flask(__name__)
handler= XMLRPCHandler('api')
handler.connect(app, '/api')




def getTimestamp():
    return datetime.now().strftime("%d/%m/%Y, %H:%M:%S.%f")

@app.before_request
def before_request_fnc():
    endpoint = request.url
    IP = request.remote_addr
    content = request.get_data(as_text=True)
    Logs_proxy.LogRequest(getTimestamp(), IP, endpoint, content)


@handler.register
def getUserName(user_id):
    return getUserDICT(user_id)['name']


def listUsers():
    v = sess.query(User).all()
    sess.close()
    return v

@handler.register
def listUsersDICT():
    ret_list = []
    lu = listUsers()
    for u in lu:
        vu = u.to_dictionary()
        ret_list.append(vu)
    return ret_list

def getUser(user_id):
    v = sess.query(User).filter(User.id==user_id).first()
    sess.close()
    return v

@handler.register
def getUserDICT(user_id):
    user = getUser(user_id).to_dictionary()
    return user

@handler.register
def getUserString(user_id):
    user = str(getUser(user_id))
    return user

@handler.register
def newUser(ISTID, name, admin):
    u = User(id = ISTID, name = name, admin=admin)
    try:
        sess.add(u)
        sess.commit()
        print(u.id)
        sess.close()
        return u.id
    except:
        return None


@handler.register
def UserExists(id):         
    if getUser(id) == None:
        return False
    else:
        return True


@handler.register
def isAdmin(user_id):
    return getUserDICT(user_id)['admin']


Base.metadata.create_all(engine)

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8002, debug=True)