# installation

known-dependencies: 

* python3
* python3-urwid
* mplayer (for music)
* pygame for python3 (for tile based mode)

## how to install and run the game 

install the dependencies and run the executeMe.py file

### debian based sytems

* install the dependencies
  * `sudo apt-get install python3 python3-urwid`
  * or simply `pip install -r requirements.txt`

* clone or download the game
  * `git clone https://github.com/MarxMustermann/OfMiceAndMechs.git`
  * or use the download as ZIP button and unzip

* start the game with:
  * cd into the OfMiceAndMechs
  * run with: `python3 executeMe.py`

* for tile based:
  * `sudo apt-get python3-pip`
  * `pyvenv <path-of-virtualenv-to-create>`
  * `source <path-of-virtualenv-to-create>/bin/activate`
  * `pip install -r requirements.txt`
  * run with: `python3 executeMe.py -t`
