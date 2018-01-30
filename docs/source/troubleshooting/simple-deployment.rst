Basic Deployment
================

simple-deployment.sh
--------------------

Promenade container failures
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Parse errors on "Building bootstrap scripts" stage, like the one shown below, 
might be caused by non-matching versions of promenade container images and 
configuration files you are using.

.. code-block:: console

    
    $ sudo ./tools/simple-deployment.sh examples/basic build
    ...
    === Building bootstrap scripts ===
    ...
    2018-01-29 16:29:07,419 WARNING  - - - promenade.validation:check_schema [ 64] Skipping validation for unknown schema: deckhand/LayeringPolicy/v1
    2018-01-29 16:29:07,420 INFO     - - - promenade.config:from_streams [ 31] Successfully validated documents from LayeringPolicy.yaml
    Traceback (most recent call last):
      File "/usr/local/bin/promenade", line 10, in <module>
        sys.exit(promenade())
    ...
      File "/usr/local/lib/python3.6/site-packages/jsonpath_ng/parser.py", line 69, in p_error
        raise Exception('Parse error at %s:%s near token %s (%s)' % (t.lineno, t.col, t.value, t.type))
    Exception: Parse error at 1:0 near token . (.)
    $ 

Possible solution would be to pull updated promenade container image with 
``docker pull quay.io/attcomdev/promenade`` command, and retry configuration 
files build.
