from flask import Flask, jsonify, request, Response
from flask_pymongo import PyMongo
from bson import json_util
from bson.objectid import ObjectId
from datetime import datetime
import json
import os

from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.secret_key = 'myawesomesecretkey'

app.config['MONGO_URI'] = 'mongodb://mongodb_css:27017/nso_info'

mongo = PyMongo(app)

def toDate(dateString):
    return datetime.strptime(dateString, '%Y-%m-%dT%H:%M:%S')
'''
@app.route('/change_info', methods=['POST'])
def create_user():
    # Receiving Data
    username = request.json['username']
    email = request.json['email']
    password = request.json['password']

    if username and email and password:
        hashed_password = generate_password_hash(password)
        id = mongo.db.change_info.insert(
            {'username': username, 'email': email, 'password': hashed_password})
        response = jsonify({
            '_id': str(id),
            'username': username,
            'password': password,
            'email': email
        })
        response.status_code = 201
        return response
    else:
        return not_found()
'''

@app.route('/change_info', methods=['GET'])
def get_changes():
    mongo_info = mongo.db.change_info.find()
    response = json_util.dumps(mongo_info)
    format_info = json.loads(response)
    if type(format_info) is list:
        for i in format_info:
            i['Init_Transaction_Time'] = i['Init_Transaction_Time']['$date']
    else:
        format_info['Init_Transaction_Time'] = format_info['Init_Transaction_Time']['$date']
    response = json.dumps(format_info)
    return Response(response, mimetype="application/json")


@app.route('/change_info/id=<id>', methods=['GET'])
def get_change_info_by_id(id):
    print(id)
    mongo_info = mongo.db.change_info.find_one({'_id': ObjectId(id), })
    response = json_util.dumps(mongo_info)
    format_info = json.loads(response)
    if type(format_info) is list:
        for i in format_info:
            i['Init_Transaction_Time'] = i['Init_Transaction_Time']['$date']
    else:
        format_info['Init_Transaction_Time'] = format_info['Init_Transaction_Time']['$date']
    response = json.dumps(format_info)
    return Response(response, mimetype="application/json")


@app.route('/change_info/username=<user_name>', methods=['GET'])
def get_change_info_by_user(user_name):
    print(user_name)
    mongo_info = mongo.db.change_info.find({'User_Name': user_name, })
    response = json_util.dumps(mongo_info)
    format_info = json.loads(response)
    if type(format_info) is list:
        for i in format_info:
            i['Init_Transaction_Time'] = i['Init_Transaction_Time']['$date']
    else:
        format_info['Init_Transaction_Time'] = format_info['Init_Transaction_Time']['$date']
    response = json.dumps(format_info)
    return Response(response, mimetype="application/json")


@app.route('/change_info/transaction_id=<tid>', methods=['GET'])
def get_change_info_by_tid(tid):
    print(tid)
    mongo_info = mongo.db.change_info.find({'Transaction_ID': tid, })
    response = json_util.dumps(mongo_info)
    format_info = json.loads(response)
    if type(format_info) is list:
        for i in format_info:
            i['Init_Transaction_Time'] = i['Init_Transaction_Time']['$date']
    else:
        format_info['Init_Transaction_Time'] = format_info['Init_Transaction_Time']['$date']
    response = json.dumps(format_info)
    return Response(response, mimetype="application/json")


#Time format: %y-%m-%dT%H:%M:%S --- ex: 2022-08-15T14:52:00
@app.route('/change_info/date', methods=['GET'])
def get_change_info_by_date():
    start = request.args.get('startAt', type = toDate)
    end = request.args.get('endAt', default = datetime.now(), type = toDate)
    mongo_info = mongo.db.change_info.find({'Init_Transaction_Time':{'$gte': start, '$lt': end}})
    response = json_util.dumps(mongo_info)
    format_info = json.loads(response)
    if type(format_info) is list:
        for i in format_info:
            i['Init_Transaction_Time'] = i['Init_Transaction_Time']['$date']
    else:
        format_info['Init_Transaction_Time'] = format_info['Init_Transaction_Time']['$date']
    response = json.dumps(format_info)
    return Response(response, mimetype="application/json")


@app.route('/update_info_nso', methods=['POST'])
def update_info_nso():
    # Receiving Data
    code = os.system("/home/csd/script_modules/main.py")
    if code == 0:
        response = jsonify({'message': 'execution ' + str(code)})
        response.status_code = 200
    else:
        response = jsonify({'message': 'execution ' + str(code)})
        response.status_code = 400

    return response

'''
@app.route('/change_info/<id>', methods=['DELETE'])
def delete_user(id):
    mongo.db.change_info.delete_one({'_id': ObjectId(id)})
    response = jsonify({'message': 'User' + id + ' Deleted Successfully'})
    response.status_code = 200
    return response


@app.route('/change_info/<_id>', methods=['PUT'])
def update_user(_id):
    username = request.json['username']
    email = request.json['email']
    password = request.json['password']
    if username and email and password and _id:
        hashed_password = generate_password_hash(password)
        mongo.db.change_info.update_one(
            {'_id': ObjectId(_id['$oid']) if '$oid' in _id else ObjectId(_id)}, {'$set': {'username': username, 'email': email, 'password': hashed_password}})
        response = jsonify({'message': 'User' + _id + 'Updated Successfuly'})
        response.status_code = 200
        return response
    else:
      return not_found()



@app.errorhandler(404)
def not_found(error=None):
    message = {
        'message': 'Resource Not Found ' + request.url,
        'status': 404
    }
    response = jsonify(message)
    response.status_code = 404
    return response
'''

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5500)
