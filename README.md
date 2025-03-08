The `Dockerfile` allows to run the services in a container:              
* build it: `docker build -t whale -f Dockerfile .`
* start and log into it: `docker run -it whale /bin/zsh`
* start the microservices: `. ./meow/bin/activate && ./deployment.sh`
* Proceed with GET/POST requests

