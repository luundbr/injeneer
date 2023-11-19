#!/usr/bin/python

from flask import Flask, render_template, request, jsonify
import subprocess
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'key'

class CommandForm(FlaskForm):
    command = StringField('Command', validators=[DataRequired()])
    submit = SubmitField('Execute')

@app.route('/home', methods=['GET', 'POST'])
def home():
    form = CommandForm()
    print('COMMAND', form.command)
    if form.validate_on_submit():
        command = form.command.data
        try:
            output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
            return output.decode()
        except subprocess.CalledProcessError as e:
            return str(e), 500
    return render_template('home.html', form=form)

@app.route('/run-command', methods=['POST'])
def run_command():
    data = request.json
    command = data.get('command')
    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        return jsonify(message='Command executed successfully', output=output.decode())
    except subprocess.CalledProcessError as e:
        return jsonify(error=str(e)), 500

if __name__ == '__main__':
    app.run(debug=True, port=3111)
