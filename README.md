# Active learning in Label Studio
## Introductuion in active learning

To create annotated training data for supervised machine learning models can be expensive and time-consuming. Active Learning is a branch of machine learning that seeks to minimize the total amount of data required for labeling by strategically sampling observations that provide new insight into the problem. In particular, Active Learning algorithms aim to select diverse and informative data for annotation, rather than random observations, from a pool of unlabeled data using prediction scores.

After a user creates an annotation in Label Studio, the configured webhook sends a message to the machine learning backend with the information about the created annotation. The fit() method of the ML backend runs to train the model. When the user moves on to the next labeling task, Label Studio retrieves the latest prediction for the task from the ML backend, which runs the predict() method on the task.


![image](https://docs.heartex.com/images/LS-active-learning.jpg)


### To set up this active learning, do the following:

1. Set up an ML model as an ML backend for active learning.
2. Connect the ML backend for getting predictions to Label Studio. 
3. Configure webhooks to send a training event to the ML backend (optional). 
4. Set up task sampling with prediction scores. 
5. Label the tasks. 

As you label tasks, Label Studio sends webhook events to your machine learning backend and prompts it to retrain. As the model retrains, the predictions from the latest model version appear in Label Studio

## How to run Label Studio
### Install locally with Docker
Official Label Studio docker image is here and it can be downloaded with docker pull. Run Label Studio in a Docker container and access it at http://localhost:8080.

    docker pull heartexlabs/label-studio:latest 
    docker run -it -p 8080:8080 -v `pwd`/mydata:/label-studio/data heartexlabs/label-studio:latest

### Create project and import data
Data can be imported easily through UI interface. __Preannotated data__ can be added in Label Studio format which expects JSON object. You can see an example in ``YoloToLabelStudio.py``

#### Don't forget to add labeling UI !


## Create ML backend with `LabelStudioMLBase`
As you can see for creating backend you must simply inherit  created model class from `label_studio_ml.LabelStudioMLBase`

Then override the 2 methods:
* `predict()`, which takes input tasks and outputs predictions in the Label Studio JSON format.
* `fit()`, which receives annotations iterable and returns a dictionary with created links and resources. This dictionary is used later to load models with the `self.train_output` field. 

Here is example of DummyModel:

      from label_studio_ml.model import LabelStudioMLBase

      class DummyModel(LabelStudioMLBase):
        def __init__(self, **kwargs):
            # don't forget to call base class constructor
            super(DummyModel, self).__init__(**kwargs)
        
            # you can preinitialize variables with keys needed to extract info from tasks and annotations and form predictions
            from_name, schema = list(self.parsed_label_config.items())[0]
            self.from_name = from_name
            self.to_name = schema['to_name'][0]
            self.labels = schema['labels']
    
        def predict(self, tasks, **kwargs):
            """ This is where inference happens: model returns 
                the list of predictions based on input list of tasks 
            """
            predictions = []
            for task in tasks:
                predictions.append({
                    'score': 0.987,  # prediction overall score, visible in the data manager columns
                    'model_version': 'delorean-20151021',  # all predictions will be differentiated by model version
                    'result': [{
                        'from_name': self.from_name,
                        'to_name': self.to_name,
                        'type': 'choices',
                        'score': 0.5,  # per-region score, visible in the editor 
                        'value': {
                            'choices': [self.labels[0]]
                        }
                    }]
                })
            return predictions
    
        def fit(self, annotations, **kwargs):
            """ This is where training happens: train your model given list of annotations, 
                then returns dict with created links and resources
            """
            return {'path/to/created/model': 'my/model.bin'}

In `yolo_test/model_backend.py` you can find example for fire detection models ML backend on `Yolov7`

## Create ML backend configs & scripts
Label Studio can __automatically__ create all necessary configs and scripts needed to run ML backend from your newly created model.

Call your ML backend my_backend and from the command line, initialize the ML backend directory ./my_backend:

    label-studio-ml init my_backend --script /path/to/my/script.py

## Using ML backend with Label Studio
Initialize and start a new Label Studio project connecting to the running ML backend:

    label-studio start my_project --init --ml-backends http://localhost:9090

After that add ML backend to Label Studio through pressing `Settings / Machine Learning` in webapp interface