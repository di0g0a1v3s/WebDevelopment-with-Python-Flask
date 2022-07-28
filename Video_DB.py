from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, Date, Float, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from os import path
from sqlalchemy import create_engine
from flask import Flask, request
from flaskXMLRPC import XMLRPCHandler
from datetime import datetime
import xmlrpc.client

Logs_proxy = xmlrpc.client.ServerProxy("http://127.0.0.1:8003/api")

DATABASE_FILE = "videos.sqlite"
db_exists = False
if path.exists(DATABASE_FILE):
    db_exists = True
    print("\t Video_BD database already exists")

Base = declarative_base()
engine = create_engine('sqlite:///%s'%(DATABASE_FILE), echo=False) #echo = True shows all SQL calls

Session = sessionmaker(bind=engine)
session = scoped_session(Session)
#session = Session()

#Declaration of data
class YTVideo(Base):
    __tablename__ = 'YTVideo'

    id = Column(Integer, primary_key=True)

    description = Column(String)

    url = Column(String)

    user_id = Column(String)

    def __repr__(self):
        return "<YouTubeVideo (ID=%d Description=%s, URL=%s, User ID=%s)>" % (
                                self.id, self.description, self.url, self.user_id)
    def to_dictionary(self):
        return {"id": self.id, "description": self.description, "url": self.url, "user_id":self.user_id}



class Visualizations(Base):
    __tablename__ = 'Visualizations'
    video_id = Column(Integer,ForeignKey("YTVideo.id"), primary_key = True)

    user_id = Column(Integer, primary_key = True)
    

    number_of_views = Column(Integer, default = 0)



 
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
def videoExists(id):
           
    if getVideo(id) == None:
        return False
    else:
        return True

def listVideos():
    v = session.query(YTVideo).all()
    session.close()
    return v

@handler.register
def listVideosDICT():
    ret_list = []
    lv = listVideos()
    for v in lv:
        vd = v.to_dictionary()
        ret_list.append(vd)
    
    return ret_list

def getVideo(id):
     v =  session.query(YTVideo).filter(YTVideo.id==id).first()
     session.close()
     return v

@handler.register
def getVideoDICT(id):
    return getVideo(id).to_dictionary()

@handler.register
def getVideoString(id):
    return str(getVideo(id))

@handler.register
def newVideo(description , url, user_id):
    vid = YTVideo(description = description, url = url, user_id=user_id)
    try:
        session.add(vid)
        session.commit()
        print(vid.id)
        session.close()
        return vid.id
    except:
        return None

@handler.register
def getNumberRegisteredVideosOfUser(user_id):
    n = session.query(YTVideo).filter(YTVideo.user_id==user_id).count()
    session.close()
    return n

@handler.register
def getNumberUserViews(user_id):
    visualizations = session.query(Visualizations).filter(Visualizations.user_id == user_id).all()
    n = 0
    for view in visualizations:
        n += view.number_of_views
    session.close()
    return n

@handler.register
def newVideoView(video_id, user_id):
    b = session.query(Visualizations).filter(Visualizations.video_id==video_id, Visualizations.user_id==user_id).first()
    if b==None:
        b = Visualizations(video_id = video_id, user_id = user_id)
        try:
            session.add(b)
            session.commit()
        except:
            session.close()
            return None
    b.number_of_views+=1
    n=b.number_of_views
    session.commit()
    session.close()
    return n



Base.metadata.create_all(engine)


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8000, debug=True)