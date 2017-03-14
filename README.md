# redirs

Welcome to redirs!

This python script tests and traces redirections, so that you don't have to. It runs on Python 2.7, but will be tested for Python 3.x soon.

======== GETTING STARTED ==========

* Install Python 2.7 on your machine (https://www.python.org/downloads/)
* Install Pip if you don't already have it (https://pip.pypa.io/en/stable/installing/)
* Install Requests, a library that makes http requests easy (http://requests.readthedocs.io/en/master/user/install/#install)

======== USAGE ==========

To try it out, run `python redirthr.py test.csv` if you downloaded the sample redirections file with the script. <br>

This script accepts two plaintext filetypes: txt and csv. The txt or csv file must have one column of urls, for example:

`https://www.wikipedia.org` <br>
`https://www.google.com` <br>

The file may also have two columns. The second column must be the expected url to land on:

`https://wikipedia.org, https://www.wikipedia.org` <br>
`https://google.com, https://www.google.com` <br>

You can also supply the script with a directory full of files with the layouts specified above, such as <br>
`python redirthr.py /dir/of/redirections/`
