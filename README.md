# Derivative Trade Data Monitoring System

Prototype system to monitor derivative trade data. It provides user to import/delete/edit trades in the system, generates a report and lets add new products and companies to the system.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install tools required to run the system. python3 is required.

```bash
sudo apt install python3-django
pip install tensorflow
pip install keras
pip install unidecode
pip install reportlab
pip install django-crispy-forms
```

## Usage

To run the server on localhost, execute command below in main ***group_project/*** directory.

```bash
python manage.py runserver
```
