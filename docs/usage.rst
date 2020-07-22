Usage
=====

.. warning::
    An alma api key is REQUIRED for this tool to work

To get a MARC record from the bib id and save it to a file, use the --bibid
flag and the bib id, followed by --output flag and a filename

Example::

    getmarc --bibid=100 --output 100.xml --alma-apikey=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx