import os
import sys
import json
import logging
from datetime import datetime
from flask import Flask, jsonify, request, render_template, redirect
from redis import Redis

from logstash import TCPLogstashHandler


__date__ = "7 June 2018"
__version__ = "1.0"
__email__ = "christoph.schranz@salzburgresearch.at"
__status__ = "Development"
__desc__ = """This program a dashboard for operators of 3d printers."""

FILAMENTS = "filaments.json"
PORT = 6789

LOGSTASH_HOST = os.getenv('LOGSTASH_HOST', 'il060')
LOGSTASH_PORT = int(os.getenv('LOGSTASH_PORT', '5000'))

# Creating dashboard
# hostname = os.uname()[1]
# baseurl = "http://" + hostname + ":" + str(PORT)
path = os.sep.join(os.path.abspath(__file__).split(os.sep)[:-1])
print(path)

# webservice setup
app = Flask(__name__, template_folder=path)
redis = Redis(host='redis', port=6379)

# logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
loggername = 'operator-dashboard.logging'
logger = logging.getLogger(loggername)
logger.setLevel(logging.DEBUG)
#  use default and init Logstash Handler
logstash_handler = TCPLogstashHandler(host=LOGSTASH_HOST,
                                      port=LOGSTASH_PORT,
                                      version=1)
logger.addHandler(logstash_handler)
logger.info('Added Logstash Logger for the operator Dashboard with loggername: {}'.format(loggername))


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
        if "update_filament" in request.form:
            filament = add_fil_change(request)
            logger.info("Changed filament to {}".format(str(filament)))
            return render_template('success-fil.html', filament=filament)
        elif "annotate_comment" in request.form:
            processed_text = annotate_form(request)
            logger.info("Added annotation with values: {}".format(processed_text))
            return render_template('success-ano.html',
                                   text=processed_text)
        elif "nozzle_cleaning" in request.form:
            # We already know that the nozzle was cleaned
            ret = report_nozzle_cleaning(request)
            logger.info("The nozzle was cleaned")
            return render_template('success-noz.html')

        else:
            logger.info("Unknown exception")

    filaments = get_filaments()
    curfil = get_cur_filament()
    return render_template('dashboard.html',  filaments=filaments, curfil=curfil)


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


@app.route('/filament_changes')
def filament_changes():
    filepath = path + os.sep + "data" + os.sep + "filament_changes.log"
    if os.path.exists(filepath):
        with open(filepath) as f:
            filchanges = json.loads(f.read())
    else:
        filchanges = dict({"doc": "Reported Filament Changes",
                           "values": list()})
    return jsonify(filchanges)


@app.route('/edit_filaments', methods=['GET', 'POST'])
def edit_filaments():
    if request.method == 'POST':
        try:
            new_filaments = json.loads(request.form["textbox"])
            with open(path+os.sep+FILAMENTS, "w") as f:
                f.write(json.dumps(new_filaments, indent=2))
            logger.info("Edited filaments")
            return redirect("/display_filaments")
        except json.decoder.JSONDecodeError:
            logger.info("Invalid filaments.json")
            return jsonify("Invalid json")

    filaments = open(path+os.sep+FILAMENTS).read()
    return render_template('edit_filament.html', old_filaments=filaments)


def add_fil_change(req):
    filament = req.form['filament']

    dt = datetime.now().isoformat().split(".")[0]
    filepath = path + os.sep + "data" + os.sep + "filament_changes.log"

    if os.path.exists(filepath):
        with open(filepath) as f:
            events = json.loads(f.read())
    else:
        events = dict({"data": list()})

    event = {"datetime": dt,
             "type": "filament change",
             "annotation": filament}
    events["data"].append(event)
    processed_text = "Type: {}, Text: {}, Datetime: {}". \
        format("filament change", filament, dt)

    with open(filepath, "w") as f:
        f.write(json.dumps(events, indent=2))

    return filament


def get_cur_filament():
    filepath = path + os.sep + "data" + os.sep + "filament_changes.log"
    if os.path.exists(filepath):
        with open(filepath) as f:
            filchanges = json.loads(f.read())
        curfil = filchanges["data"][-1]["annotation"]
    else:
        curfil = "No initial filament found"
    return curfil


def get_filaments():
    filaments = json.loads(open(path+os.sep+FILAMENTS).read())
    return filaments["filaments"]


@app.route('/view_events')
def view_event_days():
    days = os.listdir(path + os.sep + "data")
    output = dict({"Days": list(days)})
    output["usage"] = "To watch the data on a specific day, browse 'http://hostname:port/view_events/YYYY-MM-DD"
    return jsonify(output)


@app.route('/view_events/<string:date>')
def view_event(date):
    events = json.loads(open(path+os.sep+"data"+os.sep+date+".log").read())
    return jsonify(events)


def annotate_form(req):
    typ = req.form['type']
    text = req.form.get('textbox', "")

    dt = datetime.now().isoformat()
    filepath = path + os.sep + "data" + os.sep + dt.split("T")[0] + ".log"
    if os.path.exists(filepath):
        with open(filepath) as f:
            events = json.loads(f.read())
    else:
        events = dict({"data": list()})

    event = {"datetime": dt,
             "type": typ,
             "annotation": text}
    events["data"].append(event)
    processed_text = "Type: {}, Text: {}, Datetime: {}". \
        format(typ, text, dt)

    with open(filepath, "w") as f:
        f.write(json.dumps(events, indent=2))

    return processed_text

@app.route('/nozzle_cleanings')
def nozzle_cleanings():
    filepath = path + os.sep + "data" + os.sep + "nozzle_cleanings.log"
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            cleanings = f.readlines()
        cleanings = [x.strip() for x in cleanings]
    else:
        cleanings = list()

    output = dict({"doc": "Reported Nozzle Cleanings"})
    output["values"] = cleanings
    return jsonify(output)


def report_nozzle_cleaning(req):
    # Just to be safe, there is only one option
    ret = req.form['nozzle_cleaning']
    # No milliseconds
    dt = datetime.now().isoformat().split(".")[0]
    logline = dt + "\n"

    filepath = path + os.sep + "data" + os.sep + "nozzle_cleanings.log"
    with open(filepath, "a+") as f:
        f.write(logline)
    return dt


def run_tests():
    filaments = json.loads(open(path + os.sep + FILAMENTS).read())
    fila1 = filaments["filaments"]
    fila2 = list(set(fila1))
    if len(fila1) != len(fila2):
        print("Invalid filament.json")
        sys.exit()


if __name__ == '__main__':
    run_tests()
    # print("Started Program on host: {}".format(baseurl))
    app.run(host="0.0.0.0", debug=False, port=PORT)
