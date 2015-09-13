blerg-engine
============

This is the engine behind `my blog`_. It is a bunch of python code that gets
the job done. It is not a python package (yet) but this repository does include
some example files to get you up and running if you want to play with what I've
got.

.. _my blog: http://blog.elijahcaine.me

Up and Running
--------------

To start using the blerg-engine run the following commands (preferably in
order):

.. code::

    $ virtualenv -p /usr/bin/python3 venv
    $ source venv
    (venv)$ pip install -r requirements.txt
    (venv)$ cd example
    (venv)[example/]$ ./blerg.py # This just builds the website
    Rendered site in 0.1305 second
    (venv)[example/]$ ./blerg.py server # This starts an auto-updating server
    Serving on http://127.0.0.1:8080
    Rendered site in 0.1306 seconds

While the server is running if you go to http://127.0.0.1:8080 you will see a
live site that is updated automatically any time content content/ or
templates/ or metadata.yml get updated.

Doing Your Own Thing
--------------------

To start developing your own site simply copy the contents of example into a
new directory (within the blerg-engine repository) and edit the files to your
liking. Things to note:

* metadata.yml is a required file at the top level of your project.
* You can only build and run the server from the top level of your project.
* You can copy blerg.py to any directory and it will work just fine as long as
  you are in virtualenv (i.e., using python 3 and have the right dependencies
  installed).

**note:** The engine is very new and very unstable. If things break `file an
issue on Github`_. Thank you :)

.. _file an issue on Github: https://github.com/ElijahCaine/blerg-engine/issues
