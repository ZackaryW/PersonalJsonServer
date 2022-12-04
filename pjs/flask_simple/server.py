from flask import Flask
from pjs.universal.db import base, log
from flask_sqlalchemy import SQLAlchemy
from flask import request
from flask_restful import Api, Resource, reqparse
from pjs.universal.configManager import ConfigManager
from pjs.universal.utils import flask_jsonify_response
import datetime
from uuid import uuid4

flask_app = Flask(__name__)
flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///PersonalJsonServer.db'
flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  
db = SQLAlchemy(flask_app, model_class=base)
api = Api(flask_app)
config = ConfigManager()


searchParser = reqparse.RequestParser()
searchParser.add_argument('tags', type=str, action=lambda x: [i.strip() for i in x.split(',')])
searchParser.add_argument('start')
searchParser.add_argument('end')
searchParser.add_argument('limit', type=int)
searchParser.add_argument('data', type=dict)

def _check_token():
    # check token here
    if config.get_config('token',"") != request.headers.get('token'):
        return flask_jsonify_response(code=401, message='Unauthorized')

class Log(Resource):
    def get(self, uuid: str):
        res : log = db.session.query(log).filter(log.uuid == uuid).first()

        if res is None:
            return flask_jsonify_response(code=404, message='Not Found')
        
        return flask_jsonify_response(data=res.jsonify())

    def post(self):
        try:
            res = searchParser.parse_args()
            timestamp = res.get('timestamp', datetime.datetime.utcnow())
            if not isinstance(timestamp, datetime.datetime):
                timestamp = datetime.datetime.fromisoformat(timestamp)
            
            new_log = log(
                data=res.get('data', {}),
                tags=res.get('tags', []),
                timestamp=timestamp
            )
            db.session.add(new_log)
            db.session.commit()
            return flask_jsonify_response(data=new_log.jsonify())
        except Exception as e:
            return flask_jsonify_response(code=400, message='Bad Request')
        
    def delete(self, uuid: str):
        res : log = db.session.query(log).filter(log.uuid == uuid).first()

        if res is None:
            return flask_jsonify_response(code=404, message='Not Found')
        
        db.session.delete(res)
        db.session.commit()
        return flask_jsonify_response(uuid=uuid)
    
class LogAll(Resource):
    def get(self):
        res = db.session.query(log).all()
        return flask_jsonify_response(data=[i.jsonify() for i in res])
    
class LogSearch(Resource):
    def get(self):
        args = searchParser.parse_args()
        start = args.get('start', None)
        end = args.get('end', None)
        tags = args.get('tags', None)
        limit = args.get('limit', 100)
        if start is not None:
            start = datetime.datetime.fromisoformat(start)
        if end is not None:
            end = datetime.datetime.fromisoformat(end)
            
        if start and end:
            
            res = db.session.query(log).filter(log.timestamp >= start, log.timestamp <= end).limit(limit).all()
        elif start: 
            res = db.session.query(log).filter(log.timestamp >= start).limit(limit).all()
        elif end:
            res = db.session.query(log).filter(log.timestamp <= end).limit(limit).all()
        else:
            res = db.session.query(log).limit(limit).all()
    
        if tags is not None:
            res = [i for i in res if set(tags).issubset(set(i.tags))]
            
        return flask_jsonify_response(data=[i.jsonify() for i in res])

def setup():
    flask_app.app_context().push()
    db.create_all()
    config.write_config()
    flask_app.before_request(_check_token)  
    api.add_resource(Log, '/api')
    api.add_resource(LogAll, '/api/all')
    api.add_resource(LogSearch, '/api/search')
    
    
