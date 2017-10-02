### Secretary of the State Business Registration Data Update Instructions

#### These instructions include the following processes:

##### SOTS Search Portal
1. Data Download from FTP Server
2. Data Processing for both:
  - Local Deployment
  - Production Deployment
3. Public Server configuration

##### SOTS Business Formations
For instructions on the business formations procedure, see the [ctdata-sots-formations-data-processing README](https://github.com/CT-Data-Collaborative/ctdata-sots-formations-data-processing)

***

##### SOTS Search Portal

***

**Local directory setup**

1. Create your working directory on your local machine i.e. a 'SOTS' folder. In the terminal window cd to your 'SOTS' folder to setup the folder structure. 

To do this, first clone two repos from the CTData GitHub. 

a) the ctdata-sots-search repo (this is the application directory)
b) the sots-db-schema repo (the sots-db-schema dir holds the .yml files for each table schema)

Perform the following two commands:

```git clone git@github.com:CT-Data-Collaborative/ctdata-sots-search.git```
```git clone git@github.com:CT-Data-Collaborative/sots-db-schema.git```

2. Take the file called 'create_folders.sh' from the 'ctdata-sots-search' folder and move it to your 'SOTS' folder. 

From the terminal window, run:

```bash create_folders.sh```

This creates the folder structure that will hold the raw, intermediate, and final versions of the SOTS database tables. Your file structure should look like this (with corresponding date sub-folders):

![Folder-structure](https://user-images.githubusercontent.com/8619681/30936212-1d487560-a3a1-11e7-8b72-2aea72009ae1.png)

***

**Data Download from FTP Server**

Now that you have your local environment setup, now we can go over to the FTP Server and transfer the data files from there to your local machine. 

1. Log into server on Filezilla

> If you do not have Filezilla downloaded, perform the following commands:

```sudo apt-get update```
```sudo apt-get install filezilla```

2. Obtain the log-in credentials from the administrator, enter the credentials to open the Server

3. Go to the server side (the right side) and create a new folder on the server (this should be the date of transfer from SOTS) move the ZIP files into this newly created folder

4. Now go over to the left side (your local environment) and cd to the corresponding date folder in your monthlies directory where you would like these files to live. Highlight files in server window and drag and drop into your newly created folder. 

![Filezilla-transfer](https://user-images.githubusercontent.com/8619681/31088059-4ddb8e04-a76d-11e7-8730-44b74619d850.png)

Once file download is complete, you should have all the zip folders saved to your local folder.

You are now ready to move on to the SOTS Data Processing Steps. 

***

**Data Processing**

> These steps come after running the steps outlined in the SOTS Data Download from FTP Server instructions.

First set of instructions are for the local deployment. This is advised to do first, before the application is deployed to production. 

These instructions assume the user is working on a Linux / Mac system. Steps within this process are not supported from a Windows machine.

Building a local or production instance of this application requires a similar set of sets.

The flask application is deployed using docker and is served using nginx.

## Local deployment

***

### A note about database and application ports for local deployment:

> When developing locally, it is possible that services may already be running on the specified exposed ports. For example, if you have a local running instance of a postgres server, it will already be listening on 0.0.0.0:5432, which would lead to a port collision when launching the database locally.

> This can be solved by changing the exposed ports in the dev.yml to `XXXXX:5432`, with 'XXXXX' being the port of your choice. 
Make sure to then update the dev.env settings with this port maps, so that the Flask application can discover and connect to the database correctly. And all the steps within the sots-cli would include this change as well, i.e. --dbport XXXXX

> The nginx server is set up to expose the application at port 80. This can be changed to any port, so long as it is forwarded to port 8000.

***

1. In the terminal window cd to the 'ctdata-sots-search' folder you cloned from GitHub.

2. Copy the dev.env file to this directory (this file should be supplied to you by the administrator and should not be committed to GitHub)

> Search forms require setting the start and end date as env variables in the .env files. In the .env files dates should be specified in the form of:

```
START_DATE=1900-01-01
END_DATE=2017-09-01
```

2a. If needed, add both START_DATE and END_DATE variables, and change the `END_DATE` variable to the current month

> The `END_DATE` should always reference the first day of the month that immediately follows the most recent month of data that was processed. For example, when processing the data dump uploaded on September 2nd, 2017, the end date should be 2017-09-01.

> The dev.env file does two separate things, when you first build, it’s used to set certain values and then when the application runs, it uses those same values to authenticate commands.

You do not have to create a virtualenv for this command, run:

```docker-compose -f dev.yml up db``` 

This activates the docker service (the server credentials come from the dev.yml and dev.env files)

Keep this terminal window running. Any time you want to see when this service gets pinged, you can go back and see the activity here. You also have the option of running it in detached mode, to do this simply add the -d flag before the db.

4. In a new terminal window, cd to the 'monthly_rebuilds' folder.

5. Create a virtualenv

```python3 -m venv venv```

6. Activate the virtualenv

```source venv/bin/activate```

7. Install the requirements for the sots-cli from github

```pip install git+https://github.com/CT-Data-Collaborative/ctdata-sots-cli.git#egg=sotscli```

> Whenever these requirements change, you will need to upgrade them with the following command:

```pip install --upgrade git+https://github.com/CT-Data-Collaborative/ctdata-sots-cli.git#egg=sotscli```

8. Use the [ctdata-sots-cli](https://github.com/CT-Data-Collaborative/ctdata-sots-cli) to build the database tables and populate with the updated data.

8a. Unzip monthlies folders from FTP server, run: (approx 2 min)

```sots unzip --zipdir monthlies/09_28_2017/```

8b. Clean text files using individual schema files for each table to create csv files (approx 15 min)

```sots clean --indir monthlies/09_28_2017/ --outdir clean/09_2017 ../sots-db-schema```

Run `wc -l [link to csv]` to check number of lines in file

for example `wc -l clean/09_2017/BUS_MASTER.csv` should result in 861975 lines

8c. Data base prep, preps the Postgres server (creates the tables) on the docker-environment for the data to be loaded in (if tables/indices/views already exist, they are dropped and created again) (approx 15 min)

```sots prepdb --dbhost 0.0.0.0 --dbport 5432 --dbuser sots --dbpass [password] --data clean/09_2017 ../sots-db-schema```

> --dbhost 0.0.0.0 (hosts the application on your local machine at your localhost)
> --dbport 5432 (port at which the postgres server listens on the docker container)
> --dbuser sots (server configuration, set in the dev.env file)
> --dbpass [password] (server password, set in the dev.env file)
> --data [link to data] (points to where the .csvs live)
> [link to schema directory] (.yml files for sots db schema) 

8d. Drop supplemental tables

```sots drop_supplemental --dbhost 0.0.0.0 --dbport 5432 --dbuser sots --dbpass [password]```

8e. Recreate supplemental tables

```sots add_supplemental --dbhost 0.0.0.0 --dbport 5432 --dbuser sots --dbpass [password]```

8f. Load the database into the postgres db

```sots loaddb --dbhost 0.0.0.0 --dbport 5432 --dbuser sots --dbpass [password] --data clean/9_2017 ../sots-db-schema```

9. Open up PgAdminIII

> If not downloaded, run the following commands:*

Download postgresql data base package

```sudo apt-get install postgresql```

Download PgAdminIII (interface to manage the DB) 

```sudo apt-get install pgadmin3```

Set up the server connection, enter password from dev.env file that you have been using for the scripts.

![Server-config](https://user-images.githubusercontent.com/8619681/31088164-a9d3ebf2-a76d-11e7-9ce5-890a1a153aff.png)

10. Navigate to the tables (make sure the dbname, in this case its called postgres) matches the db_name and postgres_db variables in the dev.env file. Right click on a table to view first 100 lines to verify data is in tables:

![PgAdmin-table-view](https://user-images.githubusercontent.com/8619681/31088209-d2c7af4e-a76d-11e7-932f-4a38dd98a223.png)

11. Now run the following command to relaunch the entire flask application stack (note this command is without the db):

```docker-compose -f dev.yml up```

12. Check to make sure your application is running on your local docker engine. In the web browser, go to http://0.0.0.0/

> You should see the application running at this site, this confirms its running locally.

![Local-app](https://user-images.githubusercontent.com/8619681/31088240-fa2d78a2-a76d-11e7-8a8e-20dae0c45e81.png)

## Production deployment

***

This application is deployed to an EC2 instance that is created via docker-machine.

1. Create a new EC2 instance on AWS:

```docker-machine create --driver amazonec2 --amazonec2-region us-east-1 --amazonec2-zone a --amazonec2-instance-type t2.medium --amazonec2-root-size 32 --amazonec2-security-group launch-wizard-1 [instance_name]```

[instance_name] will be the name of the instance, this instance (remote docker machine) can only be accessed from the creating machine, so you will need to create a new instance everytime you want it to host new database (i.e. every month)

2. Run to check env variables on machine

```docker-machine env [instance_name]```

3. Activate the instance

```eval $(docker-machine env [instance_name])```

If for some reason the EC2 instance cannot be activated (the IP address changes if it was taken down and relaunched), the TLS certificates may need to be regenerated, run the following command:

```docker-machine regenerate-certs [instance_name]```

4. Bring up the database

```docker-compose up -d db``` notice this is run in detached mode and uses the docker-compose.yml and .env config files

In same window run `docker ps`, should be hosted on 0.0.0.0 internally

5. Repeat the build steps but replace 0.0.0.0 with the IP thats on AWS EC2 instance

![AWS-EC2-admin](https://user-images.githubusercontent.com/8619681/31088815-f6d22d68-a76f-11e7-8a57-7b545096f081.png)

6. Start with the Prep db step  

> If the EC2 instance IPv4 Public IP = 54.166.38.72 the prepdb command would be: --dbhost 54.166.38.72 --dbport 5432 and dbname, dbuser, and dbpass are all set to postgres in .env file

6a. Prep the db (approx 20 min)

```sots prepdb --dbhost 54.166.38.72 --dbport 5432 --dbname postgres --dbuser sots --dbpass [password] --data clean/9_2017 ../sots-db-schema```

6b. Drop supplemental tables

```sots drop_supplemental --dbhost 54.166.38.72 --dbport 5432 --dbname postgres --dbuser sots --dbpass [password]```

6c. Recreate supplemental tables

```sots add_supplemental --dbhost 54.166.38.72 --dbport 5432 --dbname postgres --dbuser sots --dbpass  [password]```

6d. Load the database (approx 20 min)

```sots loaddb --dbhost 54.166.38.72 --dbport 5432 --dbname postgres --dbuser sots --dbpass [password] --data clean/9_2017 ../sots-db-schema```

7. Check on PgAdmin that you can bring up the service running on the EC2 instance IP

![PgAdmin-tree-view](https://user-images.githubusercontent.com/8619681/31088898-3ae147b4-a770-11e7-8f81-396397516c18.png)

8. Relaunch the application (this deploys it to the public facing IP)

```docker-compose build```

```docker-compose up -d```

***

## Public Server Configuration

Now, as the final steps, you need to update the GoDaddy settings. 

1. Log into GoDaddy

2. Go to the DNS Mgmt page <https://dcc.godaddy.com/>

3. Click on the pencil icon next to the searchctbusiness entry and replace the IP address in the "Points to" field with the new IP address.

4. Click Save.

5. Once you have confirmed that searchctbusiness.ctdata.org is pointing to the new site, you can deactivate the docker-machine so as to not inadvertently run commands against the remote server.

```eval $(docker-machine env -u)```

Now the updated application should be running on CTData. Run `ping searchctbusiness.ctdata.org` and confirm that it shows the correct IP address.




