# pycolytics
A tiny event logging library for software analytics.

The goal of this library is to be as easy to set up and use as possible. Minimal dependencies, no complicated database setups.

One-command setup on any linux machine or in wsl:

```
pip install -r requirements.txt
```

One-command launch:

```
fastapi dev
```

After launch, API docs are available at: http://127.0.0.1:8000/docs 

# Configuration
Edit the .env file, or specify these parameters as enviroment variables:

```
# Name of the database file to write into.
SQLITE_FILE_NAME="database.db"

# A list of secret keys. The server won't accept events that do not contain one of these keys in the request body.
API_KEYS=["I-am-an-unsecure-dev-key-REPLACE_ME"]
```

# Launching a production server
Generate an API key:

```
openssl rand -base64 24
```

Replace `API_KEYS=["I-am-an-unsecure-dev-key-REPLACE_ME"]` in the .env file.

Start the server:
```
gunicorn app -w 4 -k uvicorn.workers.UvicornWorker
```

## As a background service

Create a systemd service: `/etc/systemd/system/pytolytics.service`

```
[Unit]
Description=Gunicorn instance to serve pycolytics
After=network.target

[Service]
User=your_username
Group=your_groupname
WorkingDirectory=/path/to/pytholitycs
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn app -w 4 -k uvicorn.workers.UvicornWorker
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

Reload the systemd to read the config:

   `sudo systemctl daemon-reload`

Enable the service to start on boot:

   `sudo systemctl enable pytolytics`

Start the service:

   `sudo systemctl start pytolytics`

Check for errors using:

   `sudo systemctl status pytolytics`


# Planned features:
    - HTTPS communication for you security nerds out there