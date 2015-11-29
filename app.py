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
from executor import execute

@Request.application
def application(request):
    """
    To use this application, the user must send a POST request with
    base64 or form encoded encoded HTML content and the wkhtmltopdf Options in
    request data, with keys 'base64_html' and 'options'.
    The application will return a response with the PDF file.
    """
    if request.method != 'POST':
        return

    request_is_json = request.content_type.endswith('json')

    if request_is_json:
        # If a JSON payload is there, all data is in the payload
        payload = json.loads(request.data)
        ficheros = payload.get('fichs', {})
        options = payload.get('options', {})
    elif request.files:
        # Check if any files were uploaded
        ficheros = request.files.getlist('fichs')
        # Load any options that may have been provided in options
        options = json.loads(request.form.get('options', '{}'))
    
    # Adding the args for wkhtmltopdf
    args = ['wkhtmltopdf']

    # Add Global Options
    if options:
        for option, value in options.items():
            args.append('--%s' % option)
            if value:
                args.append('"%s"' % value)

    if ficheros:
        if request_is_json:
            for f, value in ficheros.items():
                sf = tempfile.NamedTemporaryFile(suffix='.html', delete=False)
                sf.write(value.decode('base64'))
                sf.close()
                # Add source file name
                args += [sf.name]
        elif request.files:
            for f in ficheros:
                sf = tempfile.NamedTemporaryFile(suffix='.html', delete=False)
                sf.write(f.read())
                sf.close()
                # Add source file name
                args += [sf.name]

    # Add source file name and output file name
    pdf_file_name = 'pdf_file.pdf'
    args += [pdf_file_name]

    # Execute the command using executor
    execute(' '.join(args))

    if request_is_json:
        return Response(open(pdf_file_name, 'r').read().encode('base64'))
    else:
        return Response(
            wrap_file(request.environ, open(pdf_file_name, 'r')),
            mimetype='application/pdf'
        )

if __name__ == '__main__':
    from werkzeug.serving import run_simple
    run_simple(
        '127.0.0.1', 5000, application, use_debugger=True, use_reloader=True
    )

    