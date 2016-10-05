# NLPipe [![Build Status](https://travis-ci.org/vanatteveldt/nlpipe.png?branch=master)](https://travis-ci.org/vanatteveldt/nlpipe)

Client/server based NLP Pipelining

This is a simple, filesystem-based format- and progress agnostic setup for running document processing.
The intended usage is to make it easy to package and distribute different parsers, preprocessors etc.,
and call them from other programs such as R or python without worrying about dependencies, installation, etc. 

Components:

- Storage
- HTTP Server
- Client bindings
- Workers

Command line usage
===

The workers and client can be activated from the command line. (currently quite limited)

To start the workers with the provided example.conf configuration, run:

```{sh}
$ env/bin/python -m nlpipe.worker example.conf 
```

To test the workers, you can call the client directly:

echo "Walter loves politicians" | env/bin/python -m nlpipe.client /tmp/nlpipe test_upper
WALTER LOVES POLITICIANS
```{sh}
$ echo "Mary hates bugs" | env/bin/python -m nlpipe.client /tmp/nlpipe test_upper
MARY HATES BUGS

$ echo "Mary hates bugs" | env/bin/python -m nlpipe.client /tmp/nlpipe corenlp_lemmatize
<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet href="CoreNLP-to-HTML.xsl" type="text/xsl"?>
<root>
  <document>
...
```


Storage directory layout
===

Ths server uses file system to manage task queue and results cache. 
Each task (e.g. corenlp_lemmatize) contains subfolders containing the documents

```
- <task>
  - queue
  - in_process
  - results
  - errors
```

Process flow:
- client puts document into `<task>/queue`
- worker moves a document from `<task>/queue` to `<task>/in_process` and gets the text
- worker processes the document
- worker stores the result in `<task>/results` and removes it from `<task>/in_process`
- client retrieves the document from `<task>/results`

Clients/workers can either access the filesystem directly or use the HTTP server. 

HTTP Server
====

An HTTP server will allow access to the NLPipe service with the following REST endpoints:

From client perspective:

```
PUT <task>/<hash> # adds a document by hash
POST <task> # adds a document, returning the hash
HEAD <task>/<hash> # gets status of task
GET <task>/<hash> # get result for task (or 404 / error)
```

From worker perspective:

```
GET <task> # gets one document from task (and moves from queue to in_process)
GET <task>?n=N # gets N documents from task (and moves from queue to in_process)
PUT <task>/<hash> # stores result 
```

Client bindings
===

There are client bindings for the direct filesystem access and (in the future) for the HTTP server.
Browse the [Python client bindings API documentation](http://nlpipe.readthedocs.io/en/latest/nlpipe.html)
