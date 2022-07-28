from flask import Flask, abort
from flask_dance.consumer import OAuth2ConsumerBlueprint
from flask import redirect
from flask import render_template
from flask import request
from flask import jsonify, url_for
from flask import session
import xmlrpc.client

import requests

from datetime import datetime


#necessary so that our server does not need https
import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'




#Go to FENIX -> Pessoal ->  Aplicações Externas   -> Gerir Aplicações
#Go to FENIX -> Personal -> External Applications -> Manage Applications
#Click Criar / Create
#Fill the form with the following inforamrion:
#      Namè - name of your Application
#      Description - description of your Application
#      Site - http://127.0.0.1:5000/    !!!!!!!! copy from the conselo when running the application
#      Redirect URL - http://127.0.0.1:5000/fenix-example/authorized   !!!!!!! the endpoint should be exactly this one
#      Scopes - Information
# Create the new application recold
# Click details do get the Client Id and Client Secret and fille the next constructor
app = Flask(__name__)
app.secret_key = "supersekrit"  # Replace this with your own secret!
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
fenix_blueprint = OAuth2ConsumerBlueprint(
    "fenix-example", __name__,
    # this value should be retrived from the FENIX OAuth page
    client_id="1132965128044788",
    # this value should be retrived from the FENIX OAuth page
    client_secret="fO7s1UVLL+38Nq1ycW64+27+YPACH0cJTOOdxgWxp9UF2cqvhGhAS9ZJAUHTLmn8r+MhEeTcIsJGmK0odJ5M2g==",
    # do not change next lines
    base_url="https://fenix.tecnico.ulisboa.pt/",
    token_url="https://fenix.tecnico.ulisboa.pt/oauth/access_token",
    authorization_url="https://fenix.tecnico.ulisboa.pt/oauth/userdialog",
)

app.register_blueprint(fenix_blueprint)

QA_proxy = xmlrpc.client.ServerProxy("http://127.0.0.1:8001/api")
Video_proxy = xmlrpc.client.ServerProxy("http://127.0.0.1:8000/api")
Logs_proxy = xmlrpc.client.ServerProxy("http://127.0.0.1:8003/api")
User_proxy = xmlrpc.client.ServerProxy("http://127.0.0.1:8002/api")

def getTimestamp():
    return datetime.now().strftime("%d/%m/%Y, %H:%M:%S.%f")

#function executed before each request - log the request
@app.before_request
def before_request_fnc():
    endpoint = request.url
    IP = request.remote_addr
    content = request.get_data(as_text=True)
    Logs_proxy.LogRequest(getTimestamp(), IP, endpoint, content)



#---------------Web-pages------------------------------
#homepage
@app.route('/')
def home_page():
    # The access token is generated everytime the user authenticates into FENIX
    data = verifyLogin()
    if type(data) == type(dict()) and 'username' in data.keys(): #user is logged in
        return render_template("appPage.html", loggedIn = fenix_blueprint.session.authorized, admin = User_proxy.isAdmin(data["username"]))
    else:
        return render_template("appPage.html", loggedIn = False, admin = False)

#videos list page      
@app.route('/private/videos/')
def videos_list():
    data = verifyLogin()
    if type(data) == type(dict()) and 'username' in data.keys(): #user is logged in
        return app.send_static_file('videolist.html') 
    else:
        return data #log in page
    
#individual video page
@app.route('/private/videos/video')
def video():
    data = verifyLogin()
    if type(data) == type(dict()) and 'username' in data.keys(): #user is logged in
        args = request.args
        if "id" in args:
            id = args["id"]
        else:
            abort(400)
            #the arguments were incorrect
        
        if Video_proxy.videoExists(id): #video exists in database
            return app.send_static_file('video.html')
        else:
            abort(404)#video does not exist
    else:
        return data #log in page


#-----------------Authentication------------------

#verifies if the user is logged in fenix - returns its information
def verifyLogin():
    # verification of the user is  logged in
    if fenix_blueprint.session.authorized == False:
        #if not logged in browser is redirected to login page (in this case FENIX handled the login)
        return redirect(url_for("fenix-example.login"))
    else:
        try:
            #if the user is authenticated then a request to FENIX is made
            resp = fenix_blueprint.session.get("/api/fenix/v1/person/")
        except:
            return redirect(url_for("fenix-example.login"))
        #res contains the responde made to /api/fenix/vi/person (information about current user)
        data = resp.json() 
        #add user to database
        if not User_proxy.UserExists(data['username']):
            if data['username'] in ['ist186980', 'ist14028', 'ist187057']:
                uid=User_proxy.newUser(data['username'],data['name'], True)
            else:
                uid=User_proxy.newUser(data['username'],data['name'], False)
            Logs_proxy.LogDataCreationEvent(getTimestamp(), 'User', User_proxy.getUserString(uid), data['username'])
        return data


@app.route('/logout')
def logout():
    # this clears all server information about the access token of this connection
    res = str(session.items())
    print(res)
    session.clear()
    res = str(session.items())
    print(res)
    # when the browser is redirected to home page it is not logged in anymore
    return redirect(url_for("home_page"))

#------------------Admin web pages-------------------

#logs page
@app.route('/private/Logs/')
def Log_list():
    data = verifyLogin()
    if type(data) == type(dict()) and 'username' in data.keys() and User_proxy.isAdmin(data['username']): #user is admin
        return app.send_static_file('logs.html') 
    else:
        return data #log in page

#user statistics page
@app.route('/private/userstats/')
def userstats():
    data = verifyLogin()
    if type(data) == type(dict()) and 'username' in data.keys() and User_proxy.isAdmin(data['username']): #user is admin
        return app.send_static_file('userstats.html') 
    else:
        return data #log in page


#---------------API------------------------------

#returns a list with all the logs
@app.route('/API/admin/listLog/')
def listLog():
    data = verifyLogin()
    if type(data) == type(dict()) and 'username' in data.keys() and User_proxy.isAdmin(data['username']): #user is admin
        try:
            logs=Logs_proxy.listLogsDICT() #list of logs
            
            return {"Logs": logs}
        except:
            abort(404)
    else:
        abort(403)

#returns the list of Requests
@app.route('/API/admin/listRequests/')
def listRequests():
    data = verifyLogin()
    if type(data) == type(dict()) and 'username' in data.keys() and User_proxy.isAdmin(data['username']): #user is admin
        try:
            logs=Logs_proxy.listRequestsDICT() #list of requests
            
            return {"Requests": logs}
        except:
            abort(404)
    else:
        abort(403)

#returns the list of DataCreationEvents
@app.route('/API/admin/listDataCreationEvents/')
def listDataCreationEvents():
    data = verifyLogin()
    if type(data) == type(dict()) and 'username' in data.keys() and User_proxy.isAdmin(data['username']): #user is admin
        try:
            logs=Logs_proxy.listDataCreationEventsDICT() #list of creation events
            
            return {"DataCreationEvents": logs}
        except:
            abort(404)
    else:
        abort(403)



#returns list of videos
@app.route('/API/private/videos/', methods=['GET'])
def getVideosList():
    data = verifyLogin()
    if type(data) == type(dict()) and 'username' in data.keys(): #user is logged in
        try:
            videos=Video_proxy.listVideosDICT() #list of videos
            for vd in videos:
                number_questions = QA_proxy.NumberVideoQuestions(vd['id'])
                vd['number_questions'] = number_questions #add the number of questions of each video
            
            return {"videos": videos}
        except:
            abort(404)
    else:
        abort(403) #user not loggen in - FORBIDDEN
    
#creates a new video
@app.route('/API/private/videos/', methods=['POST'])
def createNewVideo():
    data = verifyLogin()
    if type(data) == type(dict()) and 'username' in data.keys(): #user is logged in
       
        j = request.get_json()
        ret = False
        try:
            ret = Video_proxy.newVideo(j["description"], j['url'], data['username'])
        except:
            abort(400)
            #the arguments were incorrect
        if ret:
            Logs_proxy.LogDataCreationEvent(getTimestamp(), 'Video', Video_proxy.getVideoString(ret), data['username'])
            return {"id": ret}
        else:
            abort(409)  #if there is an erro return ERROR 409
    else:
        abort(403) #user not logged in - FORBIDDEN

#Returns a single video
@app.route("/API/private/videos/<int:id>/", methods=['GET'])
def returnSingleVideoJSON(id):
    
    data = verifyLogin()
    if type(data) == type(dict()) and 'username' in data.keys(): #user logged in
        try:
            v = Video_proxy.getVideoDICT(id)
            return v
        except:
            abort(404) #video not found
    else:
        abort(403) #user not logged in - FORBIDDEN


#returns the list of questions of a given video
@app.route("/API/private/videos/<int:video_id>/questions/", methods=['GET'])
def getQuestionsList(video_id):
    
    data = verifyLogin()
    if type(data) == type(dict()) and 'username' in data.keys(): #user logged in
        try:

            questions = QA_proxy.listVideoQuestionsDICT(video_id)
            for q in questions:
                user_id = q['user_id']
                try:
                    q["user_name"] = User_proxy.getUserName(user_id)
                except:
                    q["user_name"] = "NOT FOUND"
            return {"questions": questions}
        except:
            abort(404)
    else:
        abort(403) #user not logged in - FORBIDDEN

#creates a new question
@app.route("/API/private/videos/<int:video_id>/questions/", methods=['POST'])
def createNewQuestion(video_id):
    data = verifyLogin()
    if type(data) == type(dict()) and 'username' in data.keys(): #user is logged in
        try:
            if not Video_proxy.videoExists(video_id):
                abort(404) #video does not exist

            j = request.get_json()
            ret = False
            
            #print(video_id, data['username'], j['text'], j['time_instant'])
            try:
                ret = QA_proxy.newQuestion(video_id, data['username'], j['text'], j['time_instant'])
            except:
                abort(400)
                #the arguments were incorrect
            if ret:
                Logs_proxy.LogDataCreationEvent(getTimestamp(), 'Question', QA_proxy.getQuestionString(video_id,ret), data['username'])
                return {"id": ret}
            else:
                abort(409)
        except:
            abort(404)
    
    else:
        abort(403) #user not logged in - FORBIDDEN

    
        
#returns a single question
@app.route("/API/private/videos/<int:video_id>/questions/<int:question_id>/", methods=['GET'])
def returnSingleQuestionJSON(video_id,question_id):
    data = verifyLogin()
    if type(data) == type(dict()) and 'username' in data.keys(): #user is logged in
        try:
            v = QA_proxy.getQuestionDICT(video_id,question_id)
            user_id = v['user_id']
            try:
                v["user_name"] = User_proxy.getUserName(user_id)
            except:
                v["user_name"] = "NOT FOUND"
            return v
        except:
            abort(404) #question not found
    else:
        abort(403) #user not logged in - FORBIDDEN
    


#returns the list of answers
@app.route("/API/private/videos/<int:video_id>/questions/<int:question_id>/answers", methods=['GET'])
def getAnswersList(video_id,question_id):

    data = verifyLogin()
    if type(data) == type(dict()) and 'username' in data.keys(): #user logged in
        try:
            answers=QA_proxy.listAnswersOfQuestionDICT(video_id, question_id)
            for a in answers:
                user_id = a['user_id']
                try:
                    a["user_name"] = User_proxy.getUserName(user_id)
                except:
                    a["user_name"] = "NOT FOUND"

            #print(answers)
            return {"answers": answers}
        except:
            abort(404)
    else:
        abort(403) #user not logged in - FORBIDDEN

#creates a new Answer
@app.route("/API/private/videos/<int:video_id>/questions/<int:question_id>/answers/", methods=['POST'])
def createNewAnswer(video_id,question_id):
    data = verifyLogin()
    if type(data) == type(dict()) and 'username' in data.keys(): #user is logged in
        try:
            if not Video_proxy.videoExists(video_id):
                abort(404) #video does not exist

            j = request.get_json()
            ret = False
            try:
                ret = QA_proxy.newAnswer(question_id, video_id, data['username'], j['text'])
            except:
                abort(400)
                #the arguments were incorrect
            if ret:
                Logs_proxy.LogDataCreationEvent(getTimestamp(), 'Answer', QA_proxy.getAnswerString(video_id,question_id,ret), data['username'])
                return {"id": ret}
            else:
                abort(409)
        except:
            abort(404)
    
    else:
        abort(403) #user not logged in - FORBIDDEN

    
        
#returns a single answer
@app.route("/API/private/videos/<int:video_id>/questions/<int:question_id>/answers/<int:answer_id>/", methods=['GET'])
def returnSingleAnswerJSON(video_id,question_id,answer_id):
    data = verifyLogin()
    if type(data) == type(dict()) and 'username' in data.keys(): #user is logged in
        try:
            v = QA_proxy.getAnswerDICT(video_id,question_id,answer_id)
            user_id = v['user_id']
            try:
                v["user_name"] = User_proxy.getUserName(user_id)
            except:
                v["user_name"] = "NOT FOUND"
            return v
        except:
            abort(404)
    else:
        abort(403) #user not logged in - FORBIDDEN
   


#returns list of users
@app.route("/API/admin/users/", methods=['GET'])
def getUsersList():
    data = verifyLogin()
    if type(data) == type(dict()) and 'username' in data.keys() and User_proxy.isAdmin(data['username']): #user is admin
        try:
            return {"users": User_proxy.listUsersDICT()}
        except:
            abort(404)
    else:
        abort(403) #user is not logged in or is not admin - FORBIDDEN
    

#returns statistics for a single user
@app.route("/API/admin/users/<string:user_id>/", methods=['GET'])
def getSingleUserStatisticsJSON(user_id):

    data = verifyLogin()
    if type(data) == type(dict()) and 'username' in data.keys() and User_proxy.isAdmin(data['username']): #user is admin
        try:
            statistics = {"user":User_proxy.getUserDICT(user_id), 
            "number_videos":Video_proxy.getNumberRegisteredVideosOfUser(user_id), 
            "number_views":Video_proxy.getNumberUserViews(user_id), 
            "number_questions":QA_proxy.getNumberOfQuestionsOfUser(user_id), 
            "number_answers":QA_proxy.getNumberOfAnswersOfUser(user_id)}
            return statistics
        except:
            abort(404)
    else:
        abort(403) #user is not logged in or is not admin - FORBIDDEN
 

#adds a new view for user on video video_id
@app.route("/API/private/videos/<int:video_id>/views/", methods=['PUT', 'PATCH'])
def newView(video_id):
    data = verifyLogin()
    if type(data) == type(dict()) and 'username' in data.keys(): #user is logged in
        try:
            if not Video_proxy.videoExists(video_id):
                abort(404)
            n = Video_proxy.newVideoView(video_id, data['username'])
            return {"views":n}
        except:
            abort(404)
    else:
        abort(403) #user is not logged in - FORBIDDEN

if __name__ == '__main__':
    app.run(debug=True)
 