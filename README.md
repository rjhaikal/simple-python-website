# Get Started with Docker Compose
On this page you build a simple Python web application running on Docker Compose. This web application has a feature to accept visitor of our websites and reset the visitor number that might we have in the future.
I use Redis as a simple approach how to build web application that store some of their data from the client. Redis might be configured as persistent key-value store. But in this tutorial we won’t have that. As long Redis is running, client data will be persist temporarily. While the sample uses Python, the concepts demonstrated here should be understandable even if you’re not familiar with it.

## Prerequites
Make sure you have already installed both `Docker Engine` and `Docker Compose`. You don’t need to install Python or Redis, as both are provided by Docker images.

## Step 1: Setup
Define the application dependencies.
1. Create a file called `main.py` in your project directory and paste this in:
```
import redis
import os
from flask import Flask

app = Flask(__name__)
redis = redis.Redis(host='redis', port=6379, db=0)

@app.route('/')
def hello_world():
    return 'Hello, World with Nevtik!'

@app.route('/visitor')
def visitor():
    redis.incr('visitor')
    visitor_num = redis.get('visitor').decode("utf-8")
    return "Pengunjung: %s" % (visitor_num)

@app.route('/visitor/reset')
def reset_visitor():
    redis.set('visitor', 0)
    visitor_num = redis.get('visitor').decode("utf-8")
    return "Pengunjung di reset ke %s" % (visitor_num)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
```

In this example, `redis` is the hostname of the redis container on the application’s network. We use the default port for Redis, `6379`.

2. Create another file called `requirements.txt` in your project directory and paste this in:
```
Flask==1.1.2
redis==3.4.1
gunicorn>=19,<20
itsdangerous==2.0.1
```

## Step 2: Create a Dockerfile
In this step, you write a Dockerfile that builds a Docker image. The image contains all the dependencies the Python application requires, including Python itself.

In your project directory, create a file named `Dockerfile` and paste the following:
```
FROM python:3.7-alpine
RUN mkdir /app
WORKDIR /app
ADD requirements.txt /app
ADD main.py /app
RUN pip3 install -r requirements.txt
CMD ["gunicorn", "-w 4", "-b", "0.0.0.0:8000", "main:app"]
```
This tells Docker to:

* Build an image starting with the `Python:3.7-alpine` image.
* Set the working directory to `/app`.
* Add `requirements.txt` and `main.py` to `/app`.
* Install the Python dependencies.
* Set the command for the container.

So, what is the difference between RUN and CMD? RUN executed your command only once at build time. But CMD let your command run continuously once your image run as a container. If you want to let our web application run forever, we have to use CMD instead RUN.

## Step 3: Define services in a Compose file
Create a file called `docker-compose.yml` in your project directory and paste the following:
```
version: '3'

services:
  app:
    build: .
    container_name: python-redis
    restart: always
    ports:
      - "8080:8000"
    depends_on:
      - redis
    volumes:
      - app:/app

  redis:
    image: "redis:alpine"
    container_name: redis
    restart: always
    ports:
      - "6379"

volumes:
  app:
```
This Compose file defines two services: web and redis

### App service
The `app` service uses an image that’s built from the `Dockerfile` in the current directory. It then binds the container and the host machine to the exposed port, `8080`. This example service uses port for the Flask web server, `8000`.

### Redis service
The `redis` service uses a public Redis image pulled from the Docker Hub registry.

## Step 4: Build and run your app with Compose
1. From your project directory, start up your application by running `docker-compose up`.
```
$ docker-compose up

Creating network "python-demo_default" with the default driver
Creating volume "python-demo_app" with default driver
Building app
---
Creating redis ... done
Creating python-redis ... done
Attaching to redis, python-redis
redis    | 1:C 15 Mar 2022 08:18:25.584 # oO0OoO0OoO0Oo Redis is starting oO0OoO0OoO0Oo
redis    | 1:C 15 Mar 2022 08:18:25.584 # Redis version=6.2.6, bits=64, commit=00000000, modified=0, pid=1, just started
redis    | 1:C 15 Mar 2022 08:18:25.584 # Warning: no config file specified, using the default config. In order to specify a config file use redis-server /path/to/redis.conf
redis    | 1:M 15 Mar 2022 08:18:25.586 * monotonic clock: POSIX clock_gettime
redis    | 1:M 15 Mar 2022 08:18:25.587 * Running mode=standalone, port=6379.
redis    | 1:M 15 Mar 2022 08:18:25.587 # Server initialized
redis    | 1:M 15 Mar 2022 08:18:25.587 * Ready to accept connections
python-redis | [2022-03-15 08:18:29 +0000] [1] [INFO] Starting gunicorn 19.10.0
python-redis | [2022-03-15 08:18:29 +0000] [1] [INFO] Listening at: http://0.0.0.0:8000 (1)
python-redis | [2022-03-15 08:18:29 +0000] [1] [INFO] Using worker: sync
```

Compose pulls a Redis image, builds an image for your code, and starts the services you defined. In this case, the code is statically copied into the image at build time.

2. Enter http://localhost:8080/ in a browser to see the application running.
If you’re using Docker natively on Linux, Docker Desktop for Mac, or Docker Desktop for Windows, then the web app should now be listening on port 8000 on your Docker daemon host. Point your web browser to http://localhost:8080 to find the `Hello World with Nevtik` message. If this doesn’t resolve, you can also try http://127.0.0.1:8080.

You should see a message in your browser saying:

![11](https://user-images.githubusercontent.com/72386335/158336533-7023f1d0-c277-456c-a7a3-838c70147b4b.png)

And if you go to endpoint http://127.0.0.1:8000/visitor:

![12](https://user-images.githubusercontent.com/72386335/158337427-07425ed8-65ca-4f6c-af81-aa667a3392de.png)

The more you refresh your browser, visitor count will be stay increasing.

![13](https://user-images.githubusercontent.com/72386335/158336842-4e001be8-6fda-4fa8-85db-a41b77f296aa.png)

If you consider to reset the number back to zero, you could hit this endpoint.

![14](https://user-images.githubusercontent.com/72386335/158337883-b451fb4f-cad2-4feb-9291-3df59ff36467.png)


