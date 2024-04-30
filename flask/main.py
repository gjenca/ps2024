#!/usr/bin/env python3
from flask import Flask
import random
from jinja2 import Template,FileSystemLoader,Environment

env=Environment(loader=FileSystemLoader('templates'),
    line_statement_prefix='%%')
app = Flask(__name__)

zoz=['heads','tails','middle']

@app.route("/")
def hello_world():
    ht=random.choice(zoz)
    t=env.get_template('template.html')
    return t.render(choice=ht)

app.run(debug=True)
