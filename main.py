import os
import json
import redis
import pickle
from markdown import markdown
from flask import Flask, request, jsonify, abort, make_response, Markup, render_template
from models.StandardModels import LinearRegression
from models import ModelFactory

app = Flask(__name__)

# initialize redis connection for local and CF deployment
def connect_db():
    if os.environ.get('VCAP_SERVICES') is None: # running locally
        DB_HOST = 'localhost'
        DB_PORT = 6379
        DB_PW = ''
        REDIS_DB = 1 if app.config["TESTING"] else 0 # use other db for testing

    else:                                       # running on CF
        env_vars = os.environ['VCAP_SERVICES']
        rediscloud_service = json.loads(env_vars)['rediscloud'][0]
        credentials = rediscloud_service['credentials']
        DB_HOST = credentials['hostname']
        DB_PORT = credentials['port']
        DB_PW = password=credentials['password']
        REDIS_DB = 0

    app.r = redis.StrictRedis(host=DB_HOST,
                              port=DB_PORT,
                              password=DB_PW,
                              db=REDIS_DB)


# define routes
@app.route('/')
def hello():
    with open ("README.md", "r") as mdfile:
        content = mdfile.read()

    content = Markup(markdown(content, extensions=['markdown.extensions.fenced_code']))
    return render_template('index.html', **locals())


@app.route('/flushDB')
def flushDB():
    app.r.flushdb()
    return 'db flushed', 200


@app.route('/createModel', methods=['POST'])
def createModel():
    json_data = request.get_json(force=True)

    # check if all fields are there
    if json_data.get('model_name') is None:
        abort(make_response("model_name field is missing.\n", 422))

    if json_data.get('model_type') is None:
        abort(make_response("model_type field is missing.\n", 422))

    if json_data.get('retrain_counter') is None:
        abort(make_response("no retrain information set.\n", 422))

    # add model to list of models
    app.r.sadd('models', json_data.get('model_name'))

    # save model definition
    mdl = ModelFactory.createModel(json_data.get('model_type'),
                                   json_data.get('model_name'),
                                   json_data.get('retrain_counter'))

    app.r.set(json_data.get('model_name') + '_object', pickle.dumps(mdl))

    return "created model: " + str(mdl) + "\n", 201


@app.route('/models')
def modelOverview():
    return str(app.r.smembers('models')), 200


@app.route('/models/<model_name>')
def modelInfo(model_name):
    return str(pickle.loads(app.r.get(model_name + '_object'))), 200


@app.route('/ingest', methods=['POST'])
def ingest():
    json_data = request.get_json(force=True)

    if json_data.get('model_name') is None:
        abort(make_response("model_name field is missing.\n", 422))

    # prepare db keys
    mdlname = json_data.get('model_name')
    data_key = mdlname + '_data'

    # get the model from the db
    model_json = app.r.get(mdlname + '_object')
    #print model_json
    mdl = pickle.loads(model_json)
    mdl.avail_data_incr()

    # save data to redis
    del json_data['model_name']
    app.r.rpush(data_key, json.dumps(json_data))

    # kick off re-training
    if (mdl.available_data % mdl.retrain_counter) == 0:
        data = app.r.lrange(data_key, 0, mdl.available_data)
        mdl.train(data)

    app.r.set(mdlname + '_object', pickle.dumps(mdl))

    return json.dumps(json_data) + " added at " + data_key + "\n", 201


# run app
if __name__ == "__main__":
    if os.environ.get('VCAP_SERVICES') is None: # running locally
        PORT = 8080
        DEBUG = True
    else:                                       # running on CF
        PORT = int(os.getenv("VCAP_APP_PORT"))
        DEBUG = False

    connect_db()
    app.run(host='0.0.0.0', port=PORT, debug=DEBUG)
