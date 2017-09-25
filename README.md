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

Then use the [ctdata-sots-cli](https://github.com/CT-Data-Collaborative/ctdata-sots-cli) to build the database tables and populate with the updated data.

Once the data load is complete, build and relaunch the entire application stack:

`docker-compose build`

followed by

`docker-compose up -d`

Finally, deactivate the docker-machine:

`eval $(docker-machine env -u)`

# Config Settings

Search forms require setting the start and end date as env variables in the .env files.

Dates should be specified in the form of:

```
START_DATE=1900-01-01
END_DATE=2017-09-01
```

The `END_DATE` should always reference the first day of the month that immediately follows the most recent month of data that was processed. For example, when processing the data dump uploaded on September 2nd, 2017, the end date should be 2017-09-01.
