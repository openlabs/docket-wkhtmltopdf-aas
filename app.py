#! /usr/bin/env python
"""
    WSGI APP to convert wkhtmltopdf As a webservice

    :copyright: (c) 2013 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
import json
import tempfile

from werkzeug.wsgi import wrap_file
from werkzeug.wrappers import Request, Response
from werkzeug.urls import url_decode
from executor import execute


def generate(url, options):
    # Evaluate argument to run with subprocess
    args = ['wkhtmltopdf']

    # Add Global Options
    if options:
        for option, value in options.items():
            args.append('--%s' % option)
            if value:
                args.append('"%s"' % value)

    # Create unique output file name
    output_filename = tempfile.mktemp()
    # Add source file name and output file name
    args += [url, output_filename + ".pdf"]

    # Execute the command using executor
    execute(' '.join(args))

    return output_filename


def respond(request, file_name):
    return Response(
        wrap_file(request.environ, open(file_name + '.pdf')),
        mimetype='application/pdf',
    )


@Request.application
def application(request):
    """
    To use this application, the user sends a GET request with the parameter
    'url' set to the desired source location and the desired wkhtmltopdf
    options also encoded as url-parameters, or a POST request with
    base64 or form encoded HTML content and the wkhtmltopdf Options in
    request data, with keys 'content' and 'options'.
    The application will return a response with the PDF file.
    """
    if request.method == 'GET':
        params = url_decode(request.query_string)
        url = params.get('url', '')
        options = {k: v for k, v in params.items() if k != 'url'}
        if not url:
            return
        file_name = generate(url, options)
        return respond(request, file_name)

    if request.method != 'POST':
        return

    request_is_json = request.content_type.endswith('json')

    with tempfile.NamedTemporaryFile(suffix='.html') as source_file:

        if request_is_json:
            # If a JSON payload is there, all data is in the payload
            payload = json.loads(request.data)
            source_file.write(payload['contents'].decode('base64'))
            options = payload.get('options', {})
        elif request.files:
            # First check if any files were uploaded
            source_file.write(request.files['file'].read())
            # Load any options that may have been provided in options
            options = json.loads(request.form.get('options', '{}'))

        source_file.flush()

        file_name = generate(source_file.name, options)
        return respond(request, file_name)

if __name__ == '__main__':
    from werkzeug.serving import run_simple
    run_simple(
        '127.0.0.1', 5000, application, use_debugger=True, use_reloader=True
    )
