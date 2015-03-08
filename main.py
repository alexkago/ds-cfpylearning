import os
import json
import redis
import markdown
from flask import Flask, request, jsonify, abort, make_response, Markup, render_template

from models.StandardModels import LinearRegression

app = Flask(__name__)

# set up redis service, port and debug flag for local and CF deployment
# check if we're running locally by checking for env variable
if os.environ.get('VCAP_SERVICES') is None:
    # run locally
    r = redis.Redis(host='localhost',
                    port=6379,
                    password='')

    port = 8080
    debug_flag = True
else:
    # run on CF
    env_vars = os.environ['VCAP_SERVICES']
    rediscloud_service = json.loads(env_vars)['rediscloud'][0]
    credentials = rediscloud_service['credentials']
    r = redis.Redis(host=credentials['hostname'],
                    port=credentials['port'],
                    password=credentials['password'])

    port = int(os.getenv("VCAP_APP_PORT"))
    debug_flag = False


# define routes
@app.route('/')
def hello():
    with open ("README.md", "r") as mdfile:
        content = mdfile.read()

    content = Markup(markdown.markdown(content, extensions=['markdown.extensions.fenced_code']))
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
    r.sadd('models', json_data.get('model_name'))

    # save model definition
    json_data['training_status'] = 'untrained'
    json_data['used_training_data'] = 0
    r.set(json_data.get('model_name') + '_model_definition', json.dumps(json_data))

    # create a counter for the data
    r.set(json_data.get('model_name') + '_counter',0)

    # prepare output
    json_data['model_name'] = json_data.get('model_name')

    return jsonify({"model": str(json_data)}), 201


@app.route('/models')
def modelOverview():
    return str(r.smembers('models')), 200


@app.route('/models/<model_name>')
def modelInfo(model_name):
    return str(r.get(model_name + '_model_definition')), 200


@app.route('/ingest', methods=['POST'])
def ingest():
    json_data = request.get_json(force=True)
    if json_data.get('model_name') is None:
        abort(make_response("model_name field is missing.\n", 422))

    # prepare db keys
    mdlname = json_data.get('model_name')
    counter_key = mdlname + '_counter'
    data_key = mdlname + '_data_' + r.get(counter_key)

    # get some info about the model
    print r.get(mdlname + '_model_definition')
    model_def = json.loads(r.get(mdlname + '_model_definition'))

    # prepare data for db
    del json_data['model_name']

    print r.get(counter_key)
    print int(model_def['retrain_counter'])

    # save data to redis
    r.set(data_key, json.dumps(json_data))
    r.incr(counter_key)

    # kick off re-training
    if int(r.get(counter_key)) % int(model_def['retrain_counter']) == 0:
        data_keys = r.keys(mdlname + '_data_' + '*')
        lr_parameters = LinearRegression.train(r.mget(data_keys))
        print lr_parameters
        model_def['training_status'] = 'trained'
        model_def['used_training_data'] = int(r.get(counter_key))
        model_def['parameters'] = json.dumps(lr_parameters)
        r.set(mdlname + '_model_definition', json.dumps(model_def))

    return json.dumps(json_data) + " added at " + data_key + "\n", 201


# run app
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=port, debug=debug_flag)
