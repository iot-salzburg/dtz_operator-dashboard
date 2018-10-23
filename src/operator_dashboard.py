import os
import sys
import json
import socket
import pytz
from datetime import datetime
from dateutil.parser import parse
from flask import Flask, jsonify, request, render_template, redirect, abort
from redis import Redis

# confluent_kafka is based on librdkafka, details in requirements.txt
from confluent_kafka import Producer, KafkaError

__date__ = "23 October 2018"
__version__ = "1.3"
__email__ = "christoph.schranz@salzburgresearch.at"
__status__ = "Development"
__desc__ = """This program a dashboard for operators of 3d printers."""

PORT = int(os.getenv("PORT", "6789"))

LOGSTASH_HOST = os.getenv('LOGSTASH_HOST', 'localhost')  # Using localhost if no host was found.
LOGSTASH_PORT = int(os.getenv('LOGSTASH_PORT', '5000'))

# Define Kafka Producer
# topics and servers should be of the form: "topic1,topic2,..."
KAFKA_TOPIC_METRIC = os.getenv('KAFKA_TOPIC_METRIC', "dtz.sensorthings")
KAFKA_TOPIC_LOGS = os.getenv('KAFKA_TOPIC_LOGS', "dtz.logging")
BOOTSTRAP_SERVERS = os.getenv('BOOTSTRAP_SERVERS', '192.168.48.81:9092,192.168.48.82:9092,192.168.48.83:9092')
KAFKA_GROUP_ID = os.getenv('KAFKA_GROUP_ID', "operator-adapter")

# Creating dashboard
FILAMENTS = "filaments.json"
path = os.sep.join(os.path.abspath(__file__).split(os.sep)[:-1])+os.sep+"app"

# webservice setup
app = Flask(__name__, template_folder=path)
redis = Redis(host='redis', port=PORT)

dir_path = os.path.dirname(os.path.realpath(__file__))
datastream_file = os.path.join(dir_path, "app", "sensorthings", "sensorthings.json")
with open(datastream_file) as ds_file:
    DATASTREAM_MAPPING = json.load(ds_file)["Datastreams"]

conf = {'bootstrap.servers': BOOTSTRAP_SERVERS}
producer = Producer(**conf)


# noinspection PyBroadException
def publish_message(message):
    """
    Publish the canonical data format (Version: i-maintenance first iteration)    to the Kafka Bus.
    Keyword argument:
    :param message: dictionary with 4 keywords
    :return: None
    """
    try:
        producer.produce(KAFKA_TOPIC_METRIC, json.dumps(message).encode('utf-8'),
                         key=str(message['Datastream']['@iot.id']).encode('utf-8'))
        producer.poll(0)  # using poll(0), as Eden Hill mentions it avoids BufferError: Local: Queue full
        # producer.flush() poll should be faster here
        print("sent: {} {}".format(message, message['Datastream']['@iot.id']))
    except Exception as e:
        kafka_logger("Exception while sending: {} \non kafka topic: {} \n{}"
                     .format(message, KAFKA_TOPIC_METRIC, e), level='WARNING')


def kafka_logger(payload, level="debug"):
    """
    Publish the canonical data format (Version: i-maintenance first iteration)
    to the Kafka Bus.

    Keyword argument:
    :param payload: message content as json or string
    :param level: log-level
    :return: None
    """
    message = {"Datastream": "dtz.operator-adapter.logging",
               "phenomenonTime": datetime.utcnow().replace(tzinfo=pytz.UTC).isoformat(),
               "result": payload,
               "level": level,
               "host": socket.gethostname()}

    print("Level: {} \tMessage: {}".format(level, payload))
    try:
        producer.produce(KAFKA_TOPIC_LOGS, json.dumps(message).encode('utf-8'),
                         key=str(message['Datastream']).encode('utf-8'))
        producer.poll(0)  # using poll(0), as Eden Hill mentions it avoids BufferError: Local: Queue full
        # producer.flush() poll should be faster here
    except Exception as e:
        print("Exception while sending metric: {} \non kafka topic: {}\n Error: {}"
              .format(message, KAFKA_TOPIC_LOGS, e))


kafka_logger('Started operator Dashboard publishing on kafka topics {},{}'.format(KAFKA_TOPIC_LOGS, KAFKA_TOPIC_METRIC),
             level='INFO')

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
        message = dict({'result': None, 'resultTime': datetime.utcnow()
                       .replace(tzinfo=pytz.UTC).replace(microsecond=0).isoformat()})

        if "update_filament" in request.form:
            phenomenontime, filament = add_fil_change(request)
            if filament is None:
                return abort(406)
            kafka_logger("Changed filament to {}".format(str(filament)), level='INFO')
            message['result'] = None
            message["phenomenonTime"] = phenomenontime
            message['parameters'] = dict({"filament": filament})
            message['Datastream'] = dict({'@iot.id':
                        DATASTREAM_MAPPING["prusa3d.filament.event.change"]["id"]})  # "3DPrinterFilamentChange"}})
            publish_message(message)
            return render_template('success-fil.html', filament=filament)
        elif "annotate_comment" in request.form:
            phenomenontime, event = annotate_form(request)
            if event is None:
                return abort(406)
            kafka_logger("Added annotation with values: {}".format(event), level='INFO')
            message['result'] = None
            message["phenomenonTime"] = phenomenontime
            message['parameters'] = event
            message['Datastream'] = dict({'@iot.id':
                        DATASTREAM_MAPPING["prusa3d.print.event.annotation"]["id"]})  # "3DPrintAnnotations"}})
            publish_message(message)
            return render_template('success-ano.html',
                                   text=event)
        elif "nozzle_cleaning" in request.form:
            # We already know that the nozzle was cleaned
            phenomenontime = report_nozzle_cleaning(request)
            if phenomenontime is None:
                return abort(406)
            kafka_logger("The nozzle was cleaned", level='INFO')
            message['result'] = None
            message["phenomenonTime"] = phenomenontime
            message['parameters'] = dict({"status": "The nozzle was cleaned"})
            message['Datastream'] = dict({'@iot.id':
                        DATASTREAM_MAPPING["prusa3d.nozzle.event.cleaning"]["id"]})  # "3DPrinterNozzleCleansing"}})
            publish_message(message)
            return render_template('success-noz.html')

        else:
            kafka_logger("Unknown request form", level='WARNING')

    filaments = get_filaments()
    curfil = get_cur_filament()
    curdt = datetime.utcnow().replace(tzinfo=pytz.UTC).isoformat().split(".")[0]
    return render_template('dashboard.html',  filaments=filaments, curfil=curfil, curdt=curdt)


@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST':
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
            kafka_logger("Edited filaments", level='INFO')
            return redirect("/display_filaments")
        except json.decoder.JSONDecodeError:
            kafka_logger("Invalid filaments.json", level='INFO')
            return jsonify("Invalid json")

    filaments = open(path+os.sep+FILAMENTS).read()
    return render_template('edit_filament.html', old_filaments=filaments)


def add_fil_change(req):
    filament = req.form['filament']
    dt = get_dt(request)
    if filament == "select filament" or dt == "invalid datetime":
        return None

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

    with open(filepath, "w") as f:
        f.write(json.dumps(events, indent=2))

    return dt, filament


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
    status = req.form.get('status', "empty")
    text = req.form.get('textbox', "")
    aborted = [True if "aborted" in req.form.keys() else False][0]
    dt = get_dt(request)
    if dt == "invalid datetime":
        return None

    filepath = path + os.sep + "data" + os.sep + dt.split("T")[0] + ".log"
    if os.path.exists(filepath):
        with open(filepath) as f:
            events = json.loads(f.read())
    else:
        events = dict({"data": list()})

    event = {"status": status,
             "aborted": aborted,
             "annotation": text}
    events["data"].append(event)
    with open(filepath, "w") as f:
        f.write(json.dumps(events, indent=2))
    return dt, event


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
    dt = get_dt(request)
    if dt == "invalid datetime":
        return None

    logline = dt + "\n"
    filepath = path + os.sep + "data" + os.sep + "nozzle_cleanings.log"
    with open(filepath, "a+") as f:
        f.write(logline)
    return dt


def get_dt(request):
    # dt_default = datetime.now().isoformat()
    dt = request.form.get('datetime', "")

    try:
        validstring = parse(dt).replace(tzinfo=pytz.UTC).isoformat()
        return validstring
    except:
        return "invalid datetime"



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
    app.run(host="0.0.0.0", debug=True, port=PORT)
