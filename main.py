import os
import json
import redis
from markdown import markdown
from flask import Flask, request, jsonify, abort, make_response, Markup, render_template, g

from models.StandardModels import LinearRegression

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


@app.route('/createModel', methods=['POST'])
def createModel():
    json_data = request.get_json(force=True)

    # check if all fields are there
    if json_data.get('model_name') is None:
        abort(make_response("model_name field is missing.\n", 422))

    if json_data.get('model_type') is None:
        abort(make_response("model_type field is missing.\n", 422))

    if json_data.get('retrain_counter') is None and json_data.get('retrain_period') is None:
        abort(make_response("no retrain information set.\n", 422))

    # add model to list of models
    app.r.sadd('models', json_data.get('model_name'))

    # save model definition
    json_data['training_status'] = 'untrained'
    json_data['used_training_data'] = 0
    app.r.set(json_data.get('model_name') + '_model_definition', json.dumps(json_data))

    # create a counter for the data
    app.r.set(json_data.get('model_name') + '_counter',0)

    # prepare output
    json_data['model_name'] = json_data.get('model_name')

    return jsonify({"model": str(json_data)}), 201


@app.route('/models')
def modelOverview():
    return str(app.r.smembers('models')), 200


@app.route('/models/<model_name>')
def modelInfo(model_name):
    return str(app.r.get(model_name + '_model_definition')), 200


@app.route('/ingest', methods=['POST'])
def ingest():
    json_data = request.get_json(force=True)

    if json_data.get('model_name') is None:
        abort(make_response("model_name field is missing.\n", 422))

    # prepare db keys
    mdlname = json_data.get('model_name')
    counter_key = mdlname + '_counter'
    data_key = mdlname + '_data_' + app.r.get(counter_key)

    # get some info about the model
    print app.r.get(mdlname + '_model_definition')
    model_def = json.loads(app.r.get(mdlname + '_model_definition'))

    # prepare data for db
    del json_data['model_name']

    print app.r.get(counter_key)
    print int(model_def['retrain_counter'])

    # save data to redis
    app.r.set(data_key, json.dumps(json_data))
    app.r.incr(counter_key)

    # kick off re-training
    if int(app.r.get(counter_key)) % int(model_def['retrain_counter']) == 0:
        data_keys = app.r.keys(mdlname + '_data_' + '*')
        lr_parameters = LinearRegression.train(app.r.mget(data_keys))
        print lr_parameters
        model_def['training_status'] = 'trained'
        model_def['used_training_data'] = int(app.r.get(counter_key))
        model_def['parameters'] = json.dumps(lr_parameters)
        app.r.set(mdlname + '_model_definition', json.dumps(model_def))

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
