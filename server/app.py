from flask import Flask, render_template, jsonify, abort, make_response, request, redirect, flash, Response
from flask import request_started, request_finished, template_rendered, before_render_template, got_request_exception, request_tearing_down, appcontext_tearing_down, appcontext_pushed, appcontext_popped, message_flashed
from blinker import Namespace
from secrets import token_hex
import queue


app = Flask(__name__)
app.secret_key = token_hex(8)


def log_template_renders(sender, template, context, **extra):
    print('Rendering template "%s" with context %s',
                        template.name or 'string template',
                        context)


clients = []
app_signals = Namespace()
app_income_api_request_signal = app_signals.signal('app_income_api_request')
template_rendered.connect(log_template_renders, app)


@app_income_api_request_signal.connect_via(app)
def when_app_income_api_request_signal(sender, **extra):
    print(f'when_app_income_api_request_signal')
    for client in clients:
        client.put('update')


tasks = [
    {
        'id': 'd38f8689',
        'data': '4d9f1fbc773c729ad896f381415b3441d957aae6072b6bd6ce95cb9053dc3948',
    },
    {
        'id': 'aa0a7e8a',
        'data': 'c4ca1319e6b0a21743c864a40a64dd69b1d26b1b2306a289d905a30b464aae1f',
    },
]
print(tasks)


@app.route('/', methods=['GET', 'POST', 'PUT', 'DELETE'])
def main():
    global tasks
    data = dict()
    data['tasks'] = tasks
    return render_template('main.html', **data)


# GET ALL request GET
# curl -i -H "Content-Type: application/json" -X GET http://localhost:5000/api/tasks 
@app.route('/api/tasks', methods=['GET'])
def get_tasks_list():
    return jsonify({'tasks': tasks})


# GET request GET
# curl -i -H "Content-Type: application/json" -X GET -d "{\"id\":\"aa0a7e8a\"}" http://localhost:5000/api/task  
@app.route('/api/task', methods=['GET'])
def get_task():
    if not request.json or 'id' not in request.json:
        abort(400)
    id = request.json.get('id', '')
    try:
        task = list(filter(lambda task: task['id'] == id, tasks))[0]
        return jsonify({'task' : task}), 201
    except:
        abort(400)


# ADD request POST
# curl -i -H "Content-Type: application/json" -X POST -d "{\"data\":\"d6a63c444cf80fd218ff9b665948ce5250ba97ad3d4d189e2b48adafd5f09b9f\"}" http://localhost:5000/api/task  
@app.route('/api/task', methods=['POST'])
def add_task():
    global tasks
    if not request.json or 'data' not in request.json:
        abort(400)
    task = {
        'id': token_hex(4),
        'data': request.json.get('data', ''),
    }
    tasks.append(task)
    app_income_api_request_signal.send(app)
    return jsonify({'task' : task}), 201


# UPDATE request PUT
# curl -i -H "Content-Type: application/json" -X PUT -d "{\"id\":\"aa0a7e8a\", \"data\":\"88e765fda4872bd217c21f9697e1b5dccec726a78947ba50d9e045d83706e86d\"}" http://localhost:5000/api/task
@app.route('/api/task', methods=['PUT'])
def update_task():
    global tasks
    if not request.json or 'id' not in request.json or 'data' not in request.json:
        abort(400)
    id = request.json.get('id', '')
    data = request.json.get('data', '')
    try:
        list(filter(lambda task: task['id'] == id, tasks))[0].update({'data': data})
        task = list(filter(lambda task: task['id'] == id, tasks))[0]
        app_income_api_request_signal.send(app)
        return jsonify({'task' : task}), 201
    except:
        abort(400)


# ADD request DELETE
# curl -i -H "Content-Type: application/json" -X DELETE -d "{\"id\":\"aa0a7e8a\"}" http://localhost:5000/api/task  
@app.route('/api/task', methods=['DELETE'])
def del_task():
    global tasks
    if not request.json or 'id' not in request.json:
        abort(400)
    id = request.json.get('id', '')
    try:
        if any(task['id'] == id for task in tasks):
            tasks = [task for task in tasks if task['id'] != id]
            app_income_api_request_signal.send(app)
            return jsonify({'task' : {}}), 201
        else:
            abort(400)
    except:
        abort(400)


@app.route('/stream')
def stream():
    def event_stream(client):
        while True:
            try:
                message = client.get()
                yield f'data: {message}\n\n'
            except GeneratorExit:
                break

    client = queue.Queue()
    clients.append(client)
    return Response(event_stream(client), content_type='text/event-stream')


@app.errorhandler(404)
def error_404(e):
    return make_response(jsonify({'error' : 'not found'}), 404)
