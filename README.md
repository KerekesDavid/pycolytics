# Pycolytics
A tiny webservice for logging software analytics events. It takes HTTP requests, and puts them into an SQLite database,

The goal of this library is to be easy to set up and easy to use. Minimal dependencies, no complicated database setups.

- Easy setup on any linux machine, or in wsl:

    ```
    git clone git@github.com:KerekesDavid/pycolytics.git
    cd pycolytics
    pip install -r requirements.txt
    ```

- Launches out of the box:

    ```
    fastapi dev
    ```

- After launch, API docs are available at: http://127.0.0.1:8000/docs 

## How We Got Here

Pycolytics is written in python, based on [SQLite](https://github.com/sqlite/sqlite) and [FastAPI](https://github.com/fastapi/fastapi), and was inspired by [Attolytics](https://github.com/ttencate/attolytics/). 

When I was looking at Attolytics, I was too lazy to set up a rust compile environment and install postgresql for something so simple, so I spent two days writing Pycolytics instead. To help you avoid my mistake, I made it so you can just clone it and move on with your life.

True to its name, Pycolytics is probably 10<sup>6</sup> times slower than Attolytics, but who cares if it still serves my entire userbase from a rasberry-pi. It does asyncio and fancy multi-worker stuff to try and compensate.

Open an issue if you wish to contribute, or buy me a coffee if you find my work useful.

<a href='https://ko-fi.com/E1E712JJXK' target='_blank'><img height='36' style='border:0px;height:36px;' src='https://storage.ko-fi.com/cdn/kofi3.png?v=3' border='0' alt='Buy Me a Coffee at ko-fi.com' /></a>


## Clients
Comes with a client addon for Godot 4.x: [https://github.com/KerekesDavid/pycolytics-godot](https://github.com/KerekesDavid/pycolytics-godot)

## Configuration
Edit the .env file, or specify these parameters as environment variables:

    ```
    # Name of the database file to write.
    SQLITE_FILE_NAME="database.db"

    # A list of secret keys. The server won't accept events
    # that do not contain one of these keys in the request body.
    API_KEYS=["I-am-an-unsecure-dev-key-REPLACE_ME"]
    ```

## API
The server will listen to POST requests at `http://ip:port/v1.0/event`, and will expect a request body in the following format:

```
{
  "event_type": "string",
  "application": "string",
  "version": "string",
  "platform": "string",
  "user_id": "string",
  "session_id": "string",
  "value": {
    "event_description": "Life, the universe and everything.",
    "event_data": 42
    },
  "api_key": "I-am-an-unsecure-dev-key-REPLACE_ME"
}
```

There is also a more performant batch interface at `http://ip:port/v1.0/events`, expecting a list of events:
```
[
  {"event_type": ...}, 
  {"event_type": ...},
  ...
]
```

An example curl call for logging an event:

```
curl -X 'POST' \
  'http://127.0.0.1:8000/v1.0/event' \
  -H 'accept: */*' \
  -H 'Content-Type: application/json' \
  -d '{
  "event_type": "string",
  "application": "string",
  "version": "string",
  "platform": "string",
  "user_id": "string",
  "session_id": "string",
  "value": {
    "event_description": "Life, the universe and everything."
    "event_data": 42
    },
  "api_key": "I-am-an-unsecure-dev-key-REPLACE_ME"
}'
```

The `value` field can contain an arbitrary JSON with event details.

The POST request will return `204: No Content` on successful inserts.

## Database
The database will contain an `event` table with all logged events.
The columns are:
```
event_type VARCHAR NOT NULL
platform VARCHAR NOT NULL
version VARCHAR NOT NULL
user_id VARCHAR NOT NULL
session_id VARCHAR NOT NULL
value JSON NOT NULL
id INTEGER NOT NULL, PRIMARY KEY
time DATETIME NOT NULL
```

It can be opened using any sqlite database browser, or in python using the built in sqlite package. 

My personal choice for performing data analytics is a [jupyter notebook](https://jupyter.org/) using [pandas](https://pandas.pydata.org/). They have a wonerful cheat sheet [here](https://pandas.pydata.org/Pandas_Cheat_Sheet.pdf).

## Launching a Production Server
Setting up a permanent server as a service is also quite simple:
- Generate an API key:
    ```
    openssl rand -base64 24
    ```
    This will stop random people from logging events in your database, it will not stop a script kiddie who can decompile the key from your app, or pluck it from network traffic. I'd suggest creating a new one for every version of your application, and retiring old ones after a while.

- Replace `API_KEYS=["I-am-an-unsecure-dev-key-REPLACE_ME"]` in the .env file with the newly generated key.

- Create a systemd service file: `/etc/systemd/system/pycolytics.service`

    ```
    [Unit]
    Description=Gunicorn instance to serve pycolytics
    After=network.target

    [Service]
    User=your_username
    Group=your_groupname
    WorkingDirectory=/path/to/pycolytics
    Environment="PATH=/path/to/venv/bin"
    ExecStart=/path/to/venv/bin/gunicorn app -w 4 -k uvicorn.workers.UvicornWorker
    ExecReload=/bin/kill -s HUP $MAINPID
    KillMode=mixed
    TimeoutStopSec=5
    PrivateTmp=true

    [Install]
    WantedBy=multi-user.target
    ```

- Reload the systemd to read the config:

   ```sudo systemctl daemon-reload```

- Enable the service start on boot:

   ```sudo systemctl enable pycolytics```

- Start the service:

   ```sudo systemctl start pycolytics```

- Check for errors:

   ```sudo systemctl status pycolytics```


## Planned Features
- HTTPS communication for you security nerds out there

