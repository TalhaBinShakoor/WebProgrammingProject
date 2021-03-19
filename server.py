from geventwebsocket.handler import WebSocketHandler
from gevent.pywsgi import WSGIServer
from geventwebsocket import WebSocketError

from flask import Flask, jsonify, request
app = Flask(__name__, static_url_path='')
app.debug = True

import database_handler
import json
from uuid import uuid4
import logging
import clx.xms
import requests
import random
import string
import hashlib

sockets = dict()

# initialization the logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('server.log')
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)

# This is the root method that will return the static website
@app.route('/')
def root():
    return app.send_static_file('client.html')

# This method is responsible for closing the database connection.
@app.teardown_request
def after_request(exception):
    database_handler.disconnect_db()

# This method is responsible for bidirectional communication between client and server. We are using the websockets here because we want only one user to be active at a time. If a user will try to login from a diffrent browser then the old session will be discarded automatically.
@app.route('/socket')
def web_socket():
    if request.environ.get('wsgi.websocket'):
        ws = request.environ['wsgi.websocket']
        obj = ws.receive()
        data = json.loads(obj)

        try:
            sockets[data['email']] = ws

            while True:
                obj = ws.receive()
                if obj is None:
                    del sockets[data['email']]
                    ws.close()
                    return ""

        except WebSocketError as e:
            del sockets[data['email']]

    return ""

# This method is responsible fot signup process. For sending the password to the server the hashing is also implemented here for security.
@app.route('/signup', methods=['POST'])
def SignUp():
    data = request.get_json()
    if 'email' in data and 'firstname' in data and 'familyname' in data and 'gender' in data and 'country' in data and 'city' in data and 'telephone' in data and 'password' in data:
        try:
            hashed_password = hashlib.sha3_256(data['password'].encode()).hexdigest()
            result = database_handler.sign_up(data['email'], data['firstname'], data['familyname'], data['gender'], data['country'], data['city'] ,data['telephone'], hashed_password)
            if (result == True):
                return "", 201   #User created sucessfully
            else:
                return "", 500  #Something went wrong on database
        except Exception as e:
            if(str(e.args[0])=='UNIQUE constraint failed: User.email'):
                return "", 409   #Email already exist.
            else:
                logging.debug("Error4 while signup ",e)
                return "", 500  #Something went wrong

    else:
        return "", 400 #Not good data.

# This method is responsible fot signin process. For sending the password to the server the hashing is also implemented for security.
@app.route('/signin', methods=['POST'])
def SignIn():
    data = request.get_json()
    if 'email' in data and 'password' in data:
        try:
            is_user_loggedIn(data['email'])
            result = database_handler.sign_in(data['email'], data['password'])
            return jsonify({"token": result}), 200
        except Exception as e:
            print("Exception ",e)
            if(str(e.args[0])== 'Incorrect Password'):
                return "", 401 #Incorrect Password
            else:
                return "", 500 #Something went wrong.
    else:
        return "", 400 #Not good data


# This method is responsible fot signout process. It checks the token. If token exists? it will be signout.  
@app.route('/signout', methods=['GET'])
def SignOut():
    data = request.headers
    if 'Token' in data:
        result = database_handler.sign_out(data['Token'])
        if (result == True):
            return "", 200 #User Signout Sucessfully.
        else:
            return "", 401 #invalid token / Login First.
    else:
        return "", 400 #Not good data.



# This method is responsible fot change password process. It checks the token as well as comapre the old password to the existing password. If token exists + Passwords matched? password will be changes sucessfuly. 
@app.route('/changepassword', methods=['POST'])
def ChangePassword():
    h_data = request.headers
    data = request.get_json()
    if 'Token' in h_data and 'oldPassword' in data and 'newPassword' in data:
        result = database_handler.change_password(h_data['Token'], data['oldPassword'], data['newPassword'])
        if (result == "success"):
            return "", 201 #Password Changed Sucessfully
        elif(result == "password is incorrect"):
            return "", 401 #Your Password is inncorrect
        elif(result == "Login First"):
            return "", 401  #You are logged out please login first.
        else:
            return "", 500 #Something went wrong

    else:
        return "", 400 #Not good data.


# This method is responsible for fetching the data of a user by using token. It checks the token in data. If token exists? it will returns the user data of that coresponding token. 
@app.route('/getuserdatabytoken', methods=['GET'])
def GetUserDataByTocken():
    data = request.headers
    if 'Token' in data:
        try:
            result = database_handler.get_user_data_by_token(data['Token'])
            x = {
                "email": result[0][0],
                "first_name": result[0][1],
                "last_name": result[0][2],
                "gender": result[0][3],
                "Country": result[0][4],
                "City": result[0][5]
                }
            result=json.dumps(x)
            return result, 200
        except Exception as e:
            return "", 401 #invalid token
    else:
        return "", 400 #Not good data


# This method is responsible for fetching the data of a user by using token + email. It checks the token and email in data. If token and email matches? it will returns the user data of that coresponding token+email.
@app.route('/getuserdatabyemail', methods=['POST'])
def GetUserDataByEmail():
    h_data =request.headers
    data = request.get_json()
    if 'Token' in h_data and 'email' in data:
        try:
            result = database_handler.get_user_data_by_email(h_data['Token'], data['email'])

            x = {
                "email": result[0][0],
                "first_name": result[0][1],
                "last_name": result[0][2],
                "gender": result[0][3],
                "Country": result[0][4],
                "City": result[0][5]
                }
            result=json.dumps(x)
            return result, 200
    
        except Exception as e:
            if(str(e.args[0])=='invalid token / logIn First'):
                return "", 401 #Inavlid token / please login first.
            return "", 500 #Server side probelm

    else:
        return "", 400 #Not good data


# This method is responsible for fetching all the messages of a user by using token. It checks the token in data. If token exists? it will returns all the messages of that coresponding user.
@app.route('/getusermessagebytoken', methods=['GET'])
def GetUserMessageByToken():
    data = request.headers
    if 'Token' in data:
        try:
            result = database_handler.get_user_message_by_token(data['Token'])
            result = convert_resultset_to_Json(result)
     
            result=json.dumps(result)
            return result, 200
    
        except Exception as e:
            if(str(e.args[0])=='invalid token / logIn First'):
                return "", 401  #Inavlid token / please login first.
            elif (str(e.args[0])=='Token is Invalid'):
                return "", 401 #Tocken is Invalid.
            return "", 500  #Something went wrong.
    else:
        return "", 400 #Not good data


# This method is responsible for fetching all the messages of a user by using email + token. It checks the token and email in data. If token exists+email matched? it will returns all the messages of that coresponding user.
@app.route('/getusermessagebyemail', methods=['POST'])
def GetUserMessageByEmail():
    h_data = request.headers
    data = request.get_json()
    if 'Token' in h_data and 'email' in data:
        try:
            result = database_handler.get_user_message_by_email(h_data['Token'], data['email'])
            result = convert_resultset_to_Json(result)
            result=json.dumps(result)
            if(len(result)==2):
                return jsonify(""),204
            return result, 200
    
        except Exception as e:
            if(str(e.args[0])=='invalid token / logIn First'):
                return "", 401 #Inavlid token / please login first
            return "", 500 #Something went wrong
    else:
        return "", 400  #Not good data.


# This method is responsible for posting the message of a user onto the database by using email + token. It checks the token and email in data. If token exists (means: session is active) + email matched? it will post the message of that coresponding user onto the database.
@app.route('/postmessage', methods=['POST'])
def PostMessage():
    h_data = request.headers
    data = request.get_json()
    if 'Token' in h_data and 'email' in data and 'message' in data:
        try:
            result = database_handler.post_message(h_data['Token'], data['email'], data['message'])
            
            return "", 201  #Message posted successfully
    
        except Exception as e:
            if(str(e.args[0])=='invalid token / logIn First'):
                return "", 401  #Inavlid token / please login first
            return "", 500 #Something went wrong.
    else:
        return "", 400 #Not good data

# This method is responsible for posting the message of a user onto the database by using email + token. It checks the token and email in data. If token exists (means: session is active) + email matched? it will post the message of that coresponding user onto the database.
@app.route('/forgetpassword', methods=['POST'])
def ForgetPassword():
    h_data =request.headers
    data = request.get_json()
    if  'email' in data:
        try:
            logger.debug('@server.forgetPassword() :token and email values '+h_data['Token']+data['email'])
            result = database_handler.get_user_data_by_email_only(data['email'])
            logger.debug('@server.forgetPassword() :database result '+str(len(result)))
            telephone_no = result[0][6]
            generated_password = get_random_password(10)
            original_generated_password = generated_password
            generated_password = hashlib.sha3_256(generated_password.encode()).hexdigest()
            database_handler.update_user_password(generated_password,data['email']) 
            sms_result = send_sms(telephone_no,original_generated_password)

            if sms_result==False:
                return "",400  # 
            return "", 200
    
        except Exception as e:
            if(str(e.args[0])=="Email dosen't exist"):
                return "", 204 
            return "", 500 #Server side probelm

    else:
        return "", 400 #Not good data

# **************** Utility Methods *******************
# This method is responsble for removing the unwanted chracters from the end of the string. 
def remove_dummy_chars_from_the_end_of_string(result):
    result=str(result)[2:(len(result)-4)]
    return result.strip()


# This method is responsble for converting the result (fields) of database into JSON format. 
def convert_resultset_to_Json(resultSet):
    json_array=[]
    for i in resultSet:
        x = {
                "message": remove_dummy_chars_from_the_end_of_string(i)
                }
        json_array.append(x)
    return json_array

# This method is responsble for checking the status that user is 'logdin' or 'logedout'. 
def is_user_loggedIn(userEmail):
    loggedIn = database_handler.get_session_status_by_email(userEmail)
    if loggedIn ==True:
        if userEmail in sockets:
            try:
                ws = sockets[userEmail]
                ws.send(json.dumps({'success': False, 'message': 'You have been logged out'}))
            except WebSocketError as e:
                del sockets[userEmail]
            database_handler.deactivate_session_status(userEmail)#remove_logged_in_user(database_helper.get_logged_in_user_by_email(email)[1])


# This method is responsble for generating the random password. 
def get_random_password(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


# This method is responsble for sending the SMS to the user's phone number.
def send_sms(phoneNo,message):
    client = clx.xms.Client(service_plan_id='5f6994c19d3f4e259e9fbfdd1b72a378', token='854a424f285948faa89ba678e8bad891')
    create = clx.xms.api.MtBatchTextSmsCreate()
    create.sender = "Twidder"
    to = {str(phoneNo)}
    create.recipients = set((phoneNo, ))
    create.body = "your new Password "+message

    try:
        batch = client.create_batch(create)
        return True
    except (requests.exceptions.RequestException,clx.xms.exceptions.ApiException) as ex:
        logging.debug('Failed to communicate with XMS: %s' % str(ex))
        return False

if __name__ == '__main__':
    http_server = WSGIServer(('',8000), app, handler_class=WebSocketHandler)
    http_server.serve_forever()
    #app.run()
