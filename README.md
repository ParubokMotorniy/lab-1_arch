The `Dockerfile` allows to run the services in a container:              
* build it: `docker build -t whale -f Dockerfile .`
* start and log into it: `docker run -it whale /bin/zsh`
* start the microservices (the script receives the number of nodes and name of the cluster as its arguments): `. ./meow/bin/activate && ./deployment.sh 3 dev`
* Proceed with GET/POST requests

