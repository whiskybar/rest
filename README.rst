Greetings dear reader,

this small web application renders user's input in reStructuredText into HTML. It is a port of my very old `mod_python application </mod_python>`_ using AWS Lambda this time. It is Public Domain again.

The source code is short again, the configuration is very complex.

:Author: Jiri Barton <jbar@tele3.cz>

render.py
=========

::

    from docutils.core import publish_string
    from urllib import unquote_plus
    
    def render(event, context):
        return publish_string(
            source=unquote_plus(event.get('content', '')),
            settings_overrides={'file_insertion_enabled': 0, 'raw_enabled': 0},
            writer_name='html',
        )

rest.html
=========

::

    <html>
    <head>
    
    <title>reST renderer</title>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    
    </head>
    <body>
    
    <h1>reST to HTML conversion</h1>
    
    <form action="/render" method="post">
        <label>Type some reST into the box below:</label>
        <br />
        <textarea name="content" rows="20" cols="80"></textarea>
        <br /><br />
        <input type="submit" value="Render" />
    </form>
    
    <p align="center"><a href="/about.html"><font size="-1">about...</font></a></p>
    </body>
    </html>

API Gateway /render POST configuration
======================================

Integration Request - Body Mapping Template
-------------------------------------------

:Content-Type: application/x-www-form-urlencoded

::

    ## convert HTTP POST data to JSON for insertion directly into a Lambda function
     
    ## first we we set up our variable that holds the tokenised key value pairs
    #set($httpPost = $input.path('$').split("&"))
     
    ## next we set up our loop inside the output structure
    {
    #foreach( $kvPair in $httpPost )
     ## now we tokenise each key value pair using "="
     #set($kvTokenised = $kvPair.split("="))
     ## finally we output the JSON for this pair and add a "," if this isn't the last pair
     "$kvTokenised[0]" : "$kvTokenised[1]"#if( $foreach.hasNext ),#end
    #end
    }

Integration Response - Header Mapping
-------------------------------------

:Content-Type: 'text/html'

Integration Response - Body Mapping Template
--------------------------------------------

:Content-Type: text/html

::

    $input.path('$')

Method Response - Response Headers for 200
------------------------------------------

* Content-Type


API Gateway / GET configuration
===============================

Integration Request
-------------------

:Integration type: AWS Service Proxy

:AWS Region: us-east-1 (different from the lambda code)

:AWS Service: S3

:HTTP method: GET

:Path override: rest.lurkingideas.net/rest.html

:Execution role: arn:aws:iam::916642710835:role/service-role/rest_renderer (lambda code)

Integration Response - Header Mappings
--------------------------------------

:Timestamp: integration.response.header.Date

:Content-Length: integration.response.header.Content-Length

:Content-Type: integration.response.header.Content-Type

Method Response - Response Headers for 200
------------------------------------------

* Timestamp
* Content-Length
* Content-Type

API Gateway /about GET configuration
====================================

This is very much the same as `API Gateway / GET configuration`_.


API Gateway Custom Domains
==========================

* CNAME to the specified CloudFront server
* Generate SSL certificate using `ZeroSSL <https://zerossl.com>`_

S3 Configuration
================

:Bucket: rest.lurkingideas.net

Bucket policy::

    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "ServeAndProxy",
                "Effect": "Allow",
                "Principal": "*",
                "Action": [
                    "s3:GetObject",
                    "s3:PutObject"
                ],
                "Resource": "arn:aws:s3:::rest.lurkingideas.net/*"
            }
        ]
    }

IAM Configuration
=================

Trusted relations for `rest_renderer` policy::

    {
      "Version": "2012-10-17",
      "Statement": [
        {
          "Effect": "Allow",
          "Principal": {
            "Service": "lambda.amazonaws.com"
          },
          "Action": "sts:AssumeRole"
        },
        {
          "Sid": "",
          "Effect": "Allow",
          "Principal": {
            "Service": "apigateway.amazonaws.com"
          },
          "Action": "sts:AssumeRole"
        }
      ]
    }

