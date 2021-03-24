# Wikimapia scraper
A service that scrapes points of interest in a given country.

---
## Installation
First, install docker and dokcer-compose as well as python (preferably version 3.8.3). \
After cloning the repository, download the required modules (when in the repository's main folder):
```bash
$ python -m pip install -r ./docker/scraper/requirements.txt
```
From the main folder, cd into docker and again into docker-compose. There, execute docker-compose up:
```bash
$ cd ./docker/docker-compose
$ docker-compose up
```
Then, in a new terminal, cd back to the repository's main folder, and run the main script along with a country and an output json:
```bash
$ python ./source_code/main.py france france.json
```
---
## Architecture
This tool consists of 3 main pieces:
* MongoDB container
* Tor container
* Main Script

To use it, first run docker-compose which will run the two containers.\
Then, when running the script from the repository's main folder (as shown above), the script will check the DB to see if the data of the given country has already been collected.\
If it hasn't, wikimapia will be scraped for the said data, and will insert it to the DB.\
The need for the tor container is to bypass the connection limit to the server (which is set by IP). Tor acts as a proxy.\
In either case, a GeoJSON will be created in the file specified in the CLI.

---
## Configuration
The configuration files in this project are the __docker-compose.yml__ (which will usually work fine without modification), and the __.env__ (which also should work).




