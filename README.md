# ctdata-sots-search

Building a local or production instance of this application requires a similar set of sets.

The flask application is deployed using docker and is served using nginx.

## Local deployment

1. Bring up a database for loading data: `docker-compose -f dev.yml up -d db`

2. Use the [ctdata-sots-cli](https://github.com/CT-Data-Collaborative/ctdata-sots-cli) to build the database tables and populate with the updated data.

3. Bring up the entire application stack: `docker-compose -f dev.yml up -d`

## Production deployment

This application is deployed to an ec2 instance that is created via docker-machine.

First, create a new EC2 instance:

```bash
docker-machine create --driver amazonec2 --amazonec2-region us-east-1 --amazonec2-zone a --amazonec2-instance-type t2.medium --amazonec2-root-size 32 --amazonec2-security-group launch-wizard-1 {{ instance_name }}
```

Next, activate the newly created docker machine:

`eval $(docker-machine env {instance_name})`

Next, the stack needs to be rebuilt on the remote server.

As before, first bring up the database.:

`docker-compose up -d db`

Then use the [ctdata-sots-cli](https://github.com/CT-Data-Collaborative/ctdata-sots-cli) to build the database tables and populate with the updated data.

1. unzip
2. clean
3. prep
4. drop_supplemental
5. load_supplemental
6. loaddb

Finally, when the data load is complete, build and relaunch the entire application stack:

`docker-compose build`

followed by

`docker-compose up -d`

After deploying, deactivate the docker-machine so as to not inadvertently run commands against the remote server.

`eval $(docker-machine env -u)`



## Config Settings

Search forms require setting the start and end date as env variables in the .env files.

Dates should be specified in the form of:

```
START_DATE=1900-01-01
END_DATE=2017-09-01
```

The `END_DATE` should always reference the first day of the month that immediately follows the most recent month of data that was processed. For example, when processing the data dump uploaded on September 2nd, 2017, the end date should be 2017-09-01.


### Database and application ports

When developing locally, it is possible that services may already be running on the specified exposed ports.

For example, if you have a local running instance of a postgres server, it will already be listening on 0.0.0.0:5432, which
would lead to a port collision when launching the database locally.

This can be solved by changing the exposed ports in the dev.yml to `XXXXX:5432`, with 'XXXXX' being the port of your choice.
Make sure to then update the dev.env settings with this port maps, so that the Flask application can discover and connect to the database correctly.

The nginx server is set up to expose the application at port 80. This can be changed to any port, so long as it is forwarded to port 8000.