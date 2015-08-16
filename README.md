valis, a lojbanic information system
====================================

valis is intended as a successor to [jbovlaste](http://jbovlaste.lojban.org),
the Perl-powered, web-based dictionary for [lojban](http://www.lojban.org) that
has been in continuous use since 2003.

Installation
------------

valis requires an instance of the jbovlaste postgresql database.

Install the python dependencies:

    pip install -r requirements.txt

Then create a configuration file, "config.py":

    SERVER_NAME = 'HOST:PORT'
    SQLALCHEMY_DATABASE_URI = 'postgresql://USER@HOST/INSTANCE'

API Resources
-------------

* valsi: /data/valsi

Lojban words, searchable by type, prefix, suffix, and author,
including etymologies and a list of definitions by language.

Options: type, user, word_prefix, word_suffix, after_word, limit

* definitions: e.g. /data/valsi/bangu/en

Language-specific definitions of lojban words, including examples,
gloss words and place keywords.

* words: e.g. /data/languages/en/words

Language-specific keywords, including links to definitions where
they are used.

Options: word_prefix, word_suffix, after_word, limit

Acknowledgments
---------------

valis builds on the work of Jay Kominek, who first developed jbovlaste, as well
as Robin Lee Powell, who added numerous features and was the principal
maintainer for ten years.

valis also takes inspiration from Dag Odenhall's [vlasisku](http://vlasisku.lojban.org/),
a modern web interface to jbovlaste data.

License
-------
valis is distributed under the terms of the GNU General Public License (GPL) v3.
The complete text of the license can be found in the LICENSE file in this
distribution.

