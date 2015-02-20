import os
import json
import redis
from flask import Flask, request, jsonify, abort, make_response

app = Flask(__name__)

# set up redis service, check previously if we're running locally by checking for env variable
if os.environ.get('VCAP_SERVICES') is None:
    r = redis.Redis(host='localhost', port=6379, password='')
else:
    rediscloud_service = json.loads(os.environ['VCAP_SERVICES'])['rediscloud'][0]
    credentials = rediscloud_service['credentials']
    r = redis.Redis(host=credentials['hostname'], port=credentials['port'], password=credentials['password'])

# get port where this app should run on
# in case we run locally it doesn't exist - then just run it on 8080
port = int(os.getenv("VCAP_APP_PORT", 8080))


# define routes
@app.route('/')
def hello():
    return 'Hello World!', 200


@app.route('/test', methods=['POST'])
def test():
    print request.json
    return jsonify({"data": str(request.json)}), 200


@app.route('/createModel', methods=['POST'])
def createModel():
    # check if all fields are there
    if request.json.get('model_name') is None:
        abort(make_response("model_name field is missing.\n", 422))

    if request.json.get('model_type') is None:
        abort(make_response("model_type field is missing.\n", 422))

    if request.json.get('retrain_counter') is None and request.json.get('retrain_period') is None:
        abort(make_response("no retrain information set.\n", 422))

    # add model to list of models
    r.sadd('models', request.json.get('model_name'))

    # save model definition
    request.json['status'] = 'untrained'
    r.set(request.json.get('model_name') + '_model_definition', str(request.json))

    # create a counter for the data
    r.set(request.json.get('model_name') + '_data_counter',0)

    # prepare output
    request.json['model_name'] = request.json.get('model_name')

    return jsonify({"model": str(request.json)}), 201


@app.route('/models')
def modelOverview():
    return str(r.smembers('models')), 200


@app.route('/models/<model_name>')
def modelInfo(model_name):
    return str(r.get(model_name + '_model_definition')), 200


@app.route('/dataInput', methods=['POST'])
def dataInput():
    if request.json.get('model_name') is None:
        abort(make_response("model_name field is missing.\n", 422))

    mdlname = request.json.get('model_name')
    counter_key = mdlname + '_data_counter'
    data_key = mdlname + '_data_' + r.get(counter_key)

    # save data
    r.set(data_key, request.json)
    r.incr(counter_key)
    return str(request.json) + " added at " + key + "\n", 201


# run app
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(port), debug=True)
