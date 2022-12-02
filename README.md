# SeniorDesign

### Virtual Environment:

We are using a python venv virtual environment. This was created using 'py -m pip install --user virtualenv'
The dependencies that are installed in our vm can be found in requirements.txt

To activate the virtual environment run the following command while in the main directory:
./env/Scripts/activate

To deactivate the virtual environment run:
deactivate

To update/install the dependenices in vm, first activate the vm, then run the following commands:
py -m pip install --upgrade pip
py -m pip install -r requirements.txt

To ensure all scripts are run with the correct dependencies and the correct versions, they should be run within the vm
