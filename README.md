# task_execution_control
 Monitor task performance and receive real-time reports
 with native Flask + jQuery (without Vue/React/etc)

 ## Usage

 1. Run ```server``` and look at ```http://127.0.0.1:5000/``` -- you can see this:

 ![1](/images/1.png)

 2. Run ```client``` -- you should to see this if everything is OK:

 ![2](/images/2.png)
 
 3. Check ```http://127.0.0.1:5000/``` again -- you should see this:

 ![3](/images/3.png)

 ## Remarks
 
 Client request:

 ```python
 url = 'http://localhost:5000/api/task'
 myobj = {'data': 'd6a63c444cf80fd218ff9b665948ce5250ba97ad3d4d189e2b48adafd5f09b9f'}
 ```

Server process request:

 ```python
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
 ```

Real-time update of only part of the HTML:

```python
clients = []
app_signals = Namespace()
app_income_api_request_signal = app_signals.signal('app_income_api_request')
...
@app_income_api_request_signal.connect_via(app)
def when_app_income_api_request_signal(sender, **extra):
    print(f'when_app_income_api_request_signal')
    for client in clients:
        client.put('update')
...
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
```

 ```js
// POLLING UPDATE METHOD
// setInterval(renderTasks, 5000);

// SSE UPDATE METHOD
const eventSource = new EventSource('/stream');
eventSource.onmessage = function (event) {
    if (event.data === 'update') {
        renderTasks();
    }
};
 ```

 > [!NOTE]
 > Now active SSE update method, but for most tasks POLLING is simpler and better


