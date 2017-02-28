# ctdata-sots-search

Build the search portal requires a few steps.

First, create a new EC2 instance:

```bash
docker-machine create --driver amazonec2 --amazonec2-region us-east-1 --amazonec2-zone a --amazonec2-instance-type t2.medium --amazonec2-root-size 32 --amazonec2-security-group launch-wizard-1 {{ instance_name }}
```

Activate the newly created docker machine:

`eval $(docker-machine env {instance_name})`

Next bring the database up:

`docker-compose up -d db`

Then use the [ctdata-sots-cli](https://github.com/CT-Data-Collaborative/ctdata-sots-cli) to build the database tables and populate with the clean dataset

Build and relaunch the application.

`docker-compose build` followed by `docker-compose up -d`

Finally, deactivate the docker-machine:

`eval $(docker-machine env -u)`