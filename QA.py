
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy import ForeignKey
from sqlalchemy.sql import func
from sqlalchemy import Column, Integer, String, Date, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from os import path
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
import datetime
from flask import Flask, request
from flaskXMLRPC import XMLRPCHandler
from datetime import datetime
import xmlrpc.client

Logs_proxy = xmlrpc.client.ServerProxy("http://127.0.0.1:8003/api")

app = Flask(__name__)

handler = XMLRPCHandler('api')
handler.connect(app, '/api')


DATABASE_FILE = "QA.sqlite"
db_exists = False
if path.exists(DATABASE_FILE):
    db_exists = True
    print("\t database already exists")

Base = declarative_base()
engine = create_engine('sqlite:///%s'%(DATABASE_FILE), echo=False) #echo = True shows all SQL calls




class Question(Base):
    __tablename__ = 'Question'

    id = Column(Integer, primary_key=True)

    video_id = Column(Integer, primary_key=True)

    user_id = Column(String)

    text = Column(String)
    time_instant = Column(String)


    def __repr__(self):
        return "<Question (ID=%d Video ID=%d, User ID=%s, Text=%s, Time Instant=%s)>" % (
                                self.id, self.video_id, self.user_id,  self.text, self.time_instant)
    def to_dictionary(self):
        return {"id": self.id, "video_id": self.video_id, "user_id": self.user_id, "text": self.text, "time_instant":self.time_instant}


class Answer(Base):
    __tablename__ = 'Answer'

    id = Column(Integer, primary_key=True)

    video_id = Column(Integer, ForeignKey("Question.video_id"), primary_key=True)
    question_id = Column(Integer, ForeignKey("Question.id"), primary_key=True)

    user_id = Column(String)

    text = Column(String)

    def __repr__(self):
        return "<Answer (ID=%d Video ID=%d, Question ID=%d, User ID=%s, Text=%s)>" % (
                                self.id, self.video_id, self.question_id, self.user_id,  self.text)
    def to_dictionary(self):
        return {"id": self.id, "video_id":self.video_id, "question_id": self.question_id,
                 "user_id": self.user_id, "text": self.text}


Session = sessionmaker(bind=engine)
session = scoped_session(Session)
#session = Session()



def getTimestamp():
    return datetime.now().strftime("%d/%m/%Y, %H:%M:%S.%f")

@app.before_request
def before_request_fnc():
    endpoint = request.url
    IP = request.remote_addr
    content = request.get_data(as_text=True)
    Logs_proxy.LogRequest(getTimestamp(), IP, endpoint, content)

def listVideoQuestions(video_id):
    v = session.query(Question).filter(Question.video_id == video_id).all()
    session.close()
    return v

@handler.register
def NumberVideoQuestions(video_id):
    v = session.query(Question).filter(Question.video_id == video_id).count()
    session.close()
    return v

@handler.register
def listVideoQuestionsDICT(video_id):
    ret_list = []
    lq = listVideoQuestions(video_id)
    for q in lq:
        vq = q.to_dictionary()
        ret_list.append(vq)
    return ret_list

@handler.register
def getQuestion(video_id, question_id):
    v =  session.query(Question).filter(Question.id==question_id, Question.video_id==video_id).first()
    session.close()
    return v

@handler.register
def getQuestionDICT(video_id, question_id):
    return getQuestion(video_id, question_id).to_dictionary()

@handler.register
def getQuestionString(video_id, question_id):
    return str(getQuestion(video_id, question_id))

@handler.register
def newQuestion(video_id, user_id, text, time_instant):
    try:
        qry = session.query(func.max(Question.id).label("max_id")).filter(Question.video_id==video_id) #max id of Question from that video
        id = qry.one().max_id + 1
    except:
        id = 1
    q = Question(id = id, video_id = video_id, user_id = user_id, text=text, time_instant=time_instant)
    try:
        session.add(q)
        session.commit()
        print(q.id)
        session.close()
        return q.id
    except:
        return None




@handler.register
def listAnswersOfQuestion(video_id, question_id):
    v = session.query(Answer).filter(Answer.question_id == question_id, Answer.video_id == video_id).all()
    session.close()
    return v

@handler.register
def listAnswersOfQuestionDICT(video_id, question_id):
    ret_list = []
    la = listAnswersOfQuestion(video_id, question_id)
    for a in la:
        va = a.to_dictionary()
        ret_list.append(va)
    return ret_list

@handler.register
def getAnswer(video_id,question_id,answer_id):
    v =  session.query(Answer).filter(Answer.id==answer_id,Answer.question_id==question_id,Answer.video_id==video_id).first()
    session.close()
    return v

@handler.register
def getAnswerDICT(video_id,question_id,answer_id):
    return getAnswer(video_id,question_id,answer_id).to_dictionary()

@handler.register
def getAnswerString(video_id,question_id,answer_id):
    return str(getAnswer(video_id,question_id,answer_id))

@handler.register
def newAnswer(question_id, video_id, user_id, text):
    try:
        qry = session.query(func.max(Answer.id).label("max_id")).filter(Answer.video_id==video_id, Answer.question_id==question_id) #max id from Answer of that Question
        id = qry.one().max_id + 1
    except:
        id = 1
    a = Answer(id=id,question_id=question_id, video_id = video_id, user_id = user_id, text=text)
    try:
        session.add(a)
        session.commit()
        print(a.id)
        session.close()
        return a.id
    except:
        return None

@handler.register
def getNumberOfQuestionsOfUser(user_id):
    n = session.query(Question).filter(Question.user_id==user_id).count()
    session.close()
    return n

@handler.register
def getNumberOfAnswersOfUser(user_id):
    n = session.query(Answer).filter(Answer.user_id==user_id).count()
    session.close()
    return n


Base.metadata.create_all(engine)

if __name__ == "__main__":
    #pass
    app.run(host='127.0.0.1', port=8001, debug=True)