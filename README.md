# WebDevelopment-with-Python-Flask
 Complete Web Application using Python Flask, SQLAlchemy, FlaskXMLRPC for the backend, and Javascript, HTML for the frontend



## Project Requirements

In this project should be developed a system (VQA) that will provide a Q&A (question and
answers) application around videos.
Users will be able to see videos stored in the system and make questions concerning particular instants
of the videos and answer previous made questions.

### Goals:

• Define the set of resources to be made available

• Define the relevant information (attributes) of such resources

• Define the interfaces (WEB and REST) to access such resources

• Implement a server prototype the illustrates the access to the information

• Implement a simple web server for access and management of resources

### Users

The system will be operated by two classes of users:

• Regular users

• Administrator that will access the admin pages

All users will be authenticated using the FENIX login page.
The system should store a list of user that are administrators. The administrators will also login using
the FENIX.

### User Functionalities
The system will provide a set of web-pages where regular users will be able to perform the following
functionalities:

• add a new video

• access a stored video

• play the a video

• post a question related to a particular instant of the video

• answer a question posted by another user

#### Video Listing

In one of the application's pages, it is possible to see the list of videos registered into the system and add
new videos.
The Video List will provide the title/Description of the registers videos, a way to load the video page
and the number of questions made in it.
To register a new video to the system, users should provide the URL for the YouTube page of such
video and a description/Title.

#### Video Page

After selecting a video in the Video Listing, the video page appears.
There the user can

• see the video,

• pause and resume playing

• make a question

• see other question

• answer to a question.

The page will present a video player that can be controlled by two buttons: play and pause.
The list questions of present the various questions previously made about the current video.
For each question the list shows the time on the video and the question text.

#### New question

When viewing the video, if the user wants to make a new question, he should click the New Question
button.
The videos should be paused to allow the user to write the text of the question.
After submitting the question text and time, the video continues executing.

#### View question

If the user selects one particular question he will see following information

• Text of the question

• The time instant on the video

• the user that made the question

• the various answers to that question

By clicking in the New Answer Button the user can add his only answer to the current question

### Administrator functionalities

Administrator user will have access to two additional pages:

• Log listing

• User statistics

The Log listing will show all the events registers in the Log service.
The user statistics will show for each user the following:

• the number of videos registered

• the number of video views

• the number of questions made by him

• the number of answers made by him

### Architecture of the system

The system will be implemented following the micro-service architecture, where each functionality is
implemented by a simple web-service and will have the following components

List of components:

• FENIX – service that will allow user authentication and provides user names

• Proxy – web application that will hide all other components and provide to the user web pages
and a set of REST APIs to be called from the JavaScript.

• User manager – Service that will store all user related information

• Video DB – component that will store the list of videos

• QA – component that will contain the list of questions and corresponding answers.

• Log – component that will record all events in the system

#### FENIX

The FENIX system will allow users to authenticate using the FENIX password.
It is possible to use the FENIX TecnicoID and password in web applications using the OAuth protocol.
A description of the way to integrate on web application with the Técnico authentication is available
here: https://fenixedu.org/dev/tutorials/use-fenixedu-api-in-your-application/
The FENIX system exports a set of APIs that provide information about the IST users.
The REST endpoints for FENIX are available in https://fenixedu.org/dev/api/

#### Proxy

The Proxy can be implemented in FLASK and export a set of endpoints
These endpoint will serve the HTML pages and the suitable REST API to be used by the browser
JavaScript.
This proxy should store the minimum information possible.
In order to answers the requests, the Proxy should contact other components.
The proxy can be further divided into 3 components. Each component will have one specific set of
functionalities.

##### User Web pages

The web pages module will present a set of web pages that will allow users to access information:

• Administrators will be able see the logs and users information.

• Regular will access the tow pages (Video Listing and Video Page) to process the information.

These web pages can have JavaScript code that call the supporting REST APIs

##### Authentication

This component will allow users to login into the VQA system using the FENIX password.
The authentication module will allow users to authenticate themselves using the FENIX TecnicoID and
password.
VQA should implement the OAuth protocol.

##### API

The API component will export all the REST endpoint necessary by JavaScript code.
These endpoints can replicate those in the components or use as supporting data information from
multiple components

##### Admin web pages

The admin pages will be accessed by the administrator to:

• list the logs

• list the registered users with statistics

Only administrators are authorized to access these pages.

#### User manager
This component will store all users information:

• User id

• Name

• Any other necessary information.

Whenever a user logins for the first time, a user record is stored.

#### Video DB

This component will store the basic information about a video:

• URL

• description/Title

• user that created it

#### QA

This component will store all the questions made along with its answers.
The minimal information for a question is:

• Video identifier

• Time

• User

• Text

If a question has some answers then it is also necessary to store for each answer:

• User

• Text

#### Log

The log component will store every relevant event of the system:

• every message exchange with any of the components (requests made to the proxy or any other
component)

• data creation events (new user, new video, new question or new answer)

For the events it is necessary the request information (IP, endpoint) and a timestamp
For the data creation it is necessary to store the data type, the content of the data creation, the
timestamp and the user responsible for such creation

## System Architecture

![image](https://user-images.githubusercontent.com/60743836/181995011-9aa41834-5a80-47a2-a45d-6b187be38864.png)

## REST Endpoints

• GET /API/admin/users/ - Returns the list of users.

• GET /API/admin/users/<string:user_id>/ - Returns statistics regarding the specified user ID.

• GET /API/admin/listLog/ - Returns the list of all logs, requests and creates data (endpoint not used).

• GET /API/admin/listRequests/ - Returns the list of logs referring to requests.

• GET /API/admin/listDataCreationEvents/ - Returns the list of logs referring to data creation.


Regarding user features, the following endpoints were defined:

• GET /API/private/videos/ - Returns the list of videos.

• POST /API/private/videos/ - Create a new video.

• GET /API/private/videos/<int:id>/ - Returns data for the specified video.

• GET /API/private/videos/<int:video_id>/questions/ - Returns the questions referring to the specified video.

• POST /API/private/videos/<int:video_id>/questions/ - Creates a new question in the specified video.

• GET /API/private/videos/<int:video id>/questions/<int:question id>/ - Returns the specified question relative to the indicated video (unused endpoint).

• GET /API/private/videos/<int:video_id>/questions/<int:question id>/answers - Returns the answers regarding a video question.

• POST /API/private/videos/<int:video_id>/questions/<int:question id>/answers/ - Creates a new answer to a video question.

• GET /API/private/videos/<int:video_id>/questions/<int:question id>/answers/<int:answer_id>/ - Returns the specified response referring to a question and respective video (endpoint not used).

• PUT /API/private/videos/<int:video_id>/views/ - Increments the number of views of the respective video.


## User Interface

#### Initial Page (http://127.0.0.1:5000/)

![image](https://user-images.githubusercontent.com/60743836/181995624-fbac2a6c-6502-4b23-a3cd-bf631083d67c.png)

#### Videos List Page (http://127.0.0.1:5000/private/videos/)

![image](https://user-images.githubusercontent.com/60743836/181995766-2dd404e1-2739-4bca-8e0f-7fc41df4eaf0.png)

#### Video Page (http://127.0.0.1:5000/private/videos/video?id=1)

![image](https://user-images.githubusercontent.com/60743836/181995778-75accf08-97a3-4d18-82f6-ee3d454a1494.png)

#### Ask questions and see/answer questions in a video (http://127.0.0.1:5000/private/videos/video?id=1)

![image](https://user-images.githubusercontent.com/60743836/181995795-11805c71-6680-467b-a89a-37e79fbd3778.png)

#### Logs (http://127.0.0.1:5000/private/Logs/)

![image](https://user-images.githubusercontent.com/60743836/181995878-11d98043-5894-4034-8cef-d931896ef7c0.png)

#### User Statistics (http://127.0.0.1:5000/private/userstats/)

![image](https://user-images.githubusercontent.com/60743836/181995872-1c1b8242-f556-489d-9a5e-7cdafae869fc.png)

