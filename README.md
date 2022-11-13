# PyTablut

Tablut game client in Python. Made for the Tablut challenge project for the 2022 FAIKR course module 1 of the master
degree in AI (University Of Bologna)

## Installation

Make sure you have Python 3 on your system, then install `pipenv`:

```
pip install pipenv
```

Once you have cloned the repo, go into its root folder and run

```
pipenv install      # installs required packages
pipenv install -d   # installs development packages
pipenv shell        # activates virtual environment
```

You are now ready to run the client. Note that `pipenv shell` is still required every time you want to execute the
client!

## Running

### Client

The client can be run using the following arguments:

```
usage: main.py [-h] [-p PORT] [-i IP] [-l] [-d DEPTH] [--skip-connection]
               {BLACK,WHITE}

positional arguments:
  {BLACK,WHITE}         Player role (either 'BLACK' or 'WHITE')

options:
  -h, --help            show this help message and exit
  -p PORT, --port PORT  Server connection port (defaults to 5800 for WHITE and
                        5801 for BLACK)
  -i IP, --ip IP        Server IP address (defaults to localhost)
  -l, --local           Do not connect to server and run player against itself
                        locally
  -d DEPTH, --depth DEPTH
                        Minmax tree maximum depth (default is 3, value <= 0 to
                        ignore depth cutoff)
  --skip-connection     [DEPRECATED, USE --local] If provided, ignore failed
                        connection to server
```

Usually, the only two required arguments are the player role (always required) and the server IP address (could run on
localhost, most likely the server is on a different computer).

### Server

Refer to [the reference repo](https://github.com/AGalassi/TablutCompetition) to know how to run the game server
yourself.