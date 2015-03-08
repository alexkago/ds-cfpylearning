#DS-CFpyLearning

Author: Alexander Kagoshima

This app demonstrates a very simple API that can be used to create model instances, feed data to them and let these models retrain periodically. Currently, it uses redis to store model instances, model state and data as well - for scalability and distributed processing of data this should be replaced by a distributed data storage.

For all the tests below replace ```http://<model_domain>``` with your Cloud Foundry app domain.


Tests
--

These model creation commands should all fail, because they are missing required information.

```
curl -i -X POST -H "Content-Type: application/json" -d '{"model_name": "model1", "model_type": "LinearRegression"}' http://<model_domain>/createModel
curl -i -X POST -H "Content-Type: application/json" -d '{"model_type": "LinearRegression"}' http://<model_domain>/createModel
curl -i -X POST -H "Content-Type: application/json" -d '{"model_name": "model1"}' http://<model_domain>/createModel
```


Create a model
--

This should work properly:

```
curl -i -X POST -H "Content-Type: application/json" -d '{"model_name": "model1", "model_type": "LinearRegression", "retrain_counter": 10}' http://<model_domain>/createModel
```


Add in some data
--

This example shows how to send data into the model created before, s.t. the linear regression model becomes y = x. Since we set the retrain_counter to 10 previously, the model will retrain after it received the 10th data instance.

```
curl -i -X POST -H "Content-Type: application/json" -d '{"model_name": "model1", "input": 1, "label": 1}' http://<model_domain>/ingest
curl -i -X POST -H "Content-Type: application/json" -d '{"model_name": "model1", "input": 2, "label": 2}' http://<model_domain>/ingest
curl -i -X POST -H "Content-Type: application/json" -d '{"model_name": "model1", "input": 3, "label": 3}' http://<model_domain>/ingest
curl -i -X POST -H "Content-Type: application/json" -d '{"model_name": "model1", "input": 4, "label": 4}' http://<model_domain>/ingest
curl -i -X POST -H "Content-Type: application/json" -d '{"model_name": "model1", "input": 5, "label": 5}' http://<model_domain>/ingest
curl -i -X POST -H "Content-Type: application/json" -d '{"model_name": "model1", "input": 6, "label": 6}' http://<model_domain>/ingest
curl -i -X POST -H "Content-Type: application/json" -d '{"model_name": "model1", "input": 7, "label": 7}' http://<model_domain>/ingest
curl -i -X POST -H "Content-Type: application/json" -d '{"model_name": "model1", "input": 8, "label": 8}' http://<model_domain>/ingest
curl -i -X POST -H "Content-Type: application/json" -d '{"model_name": "model1", "input": 9, "label": 9}' http://<model_domain>/ingest
curl -i -X POST -H "Content-Type: application/json" -d '{"model_name": "model1", "input": 10, "label": 10}' http://<model_domain>/ingest
```


Look at all created models
--

There's a very rudimentary view on the redis set of all models that have been created:

```http://<model_domain>/models/```


Look at model details
--

This lets you check out the status of the previously created model as well as its trained parameters:

```http://<model_domain>/models/model1```


Todo
--

- Instead of sending data in manually, add command to bind a model to a data source sitting on Hadoop
- Do the training within Hadoop as well, e.g. via Spark or HAWQ.
- The only model available right now is linear regression. It should be possible to use the model_type parameter to switch between different types of models. The models should be implemented in a way s.t. they are easily extendable
- It should also be easy to write your custom model trainers and scorers. Maybe turn this app into a buildpack: just define a model training and a model scoring function and push it together with this app which will then make use of the custom training and scoring functions.
- Scoring functionality: send new data without a label in and get a json as return with the prediction value generated with a previously trained model. Maybe in a separate app? Or should learning and scoring be in the same app?
- Visualization layer that shows model statistics and evaluation results.


License
--

This application is released under the Modified BSD license. Please see the LICENSE.txt file for details.
