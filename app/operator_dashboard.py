import os
import sys
import json
import logging
from datetime import datetime
from flask import Flask, jsonify, request, render_template, redirect
from redis import Redis


__date__ = "3 June 2018"
__version__ = "1.0"
__email__ = "christoph.schranz@salzburgresearch.at"
__status__ = "Development"
__desc__ = """This program a dashboard for operators of 3d printers."""

FILAMENTS = "filaments.json"
PORT = 6789
hostname = os.uname()[1]
baseurl = "http://" + hostname + ":" + str(PORT) + os.sep

# webservice setup
path = os.sep.join(os.path.abspath(__file__).split(os.sep)[:-1])
print(path)
app = Flask(__name__, template_folder=path)
redis = Redis(host='redis', port=6379)


# http://0.0.0.0:6789/
@app.route('/')
@app.route('/status')
def print_status():
    """
    This function returns the status.
    :return:
    """
    status = {"date": __date__,
              "email": __email__,
              "version": __version__,
              "dev status": __status__,
              "description": __desc__,
              "status": "ok"}
    return jsonify(status)


# Dashboard
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if request.method == 'POST':
        print(request.form)
        if "filament" in request.form:
            filament = request.form["filament"]
            return render_template('success-fil.html', filament=filament)
        elif "type" in request.form:
            processed_text = annotate_form(request)
            return render_template('success-ano.html',
                                   text=processed_text)
        else:
            print("Unknown exception")

    filaments = get_filaments()
    return render_template('dashboard.html',  filaments=filaments)


@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST':
        print(request.form)
        filament = request.form["filament"]
        return render_template('success-fil.html', filament=filament)

    filaments = get_filaments()
    return render_template('submit-fil.html', filaments=filaments)


@app.route('/annotate', methods=['GET', 'POST'])
def annotate():
    if request.method == 'POST':
        processed_text = annotate_form(request)
        return render_template('success-ano.html',
                               text=processed_text)

    return render_template('annotate.html')


@app.route('/display_filaments')
def display_filaments():
    filaments = json.loads(open(path+os.sep+FILAMENTS).read())
    return jsonify(filaments)


@app.route('/edit_filaments', methods=['GET', 'POST'])
def edit_filaments():
    if request.method == 'POST':
        try:
            new_filaments = json.loads(request.form["textbox"])
            with open(path+os.sep+FILAMENTS, "w") as f:
                f.write(json.dumps(new_filaments, indent=2))
            return redirect(baseurl + "/display_filaments")
        except json.decoder.JSONDecodeError:
            return jsonify("Invalid json")

    filaments = open(path+os.sep+FILAMENTS).read()
    return render_template('edit_filament.html', old_filaments=filaments)


def get_filaments():
    filaments = json.loads(open(path+os.sep+FILAMENTS).read())
    return filaments["filaments"]


def annotate_form(req):
    text = req.form['textbox']
    typ = req.form['type']

    dt = datetime.now().isoformat()
    filepath = "app" + os.sep + "events" + os.sep + dt.split("T")[0] + ".log"
    if os.path.exists(filepath):
        with open(filepath) as f:
            events = json.loads(f.read())
    else:
        events = dict({"events": list()})

    event = {"datetime": dt,
             "type": typ,
             "annotation": text}
    events["events"].append(event)
    processed_text = "Type: {}, Text: {}, Datetime: {}". \
        format(typ, text, dt)

    with open(path, "w") as f:
        f.write(json.dumps(events, indent=2))

    return processed_text


def run_tests():
    filaments = json.loads(open(path + os.sep + FILAMENTS).read())
    fila1 = filaments["filaments"]
    fila2 = list(set(fila1))
    if len(fila1) != len(fila2):
        print("Invalid filament.json")
        sys.exit()


if __name__ == '__main__':
    run_tests()
    print("Started Program")
    app.run(host="0.0.0.0", debug=False, port=PORT)
