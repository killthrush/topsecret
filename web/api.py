import json
from flask import Flask, request, Response
from voluptuous import Schema, Required, All, Length, Range, Invalid, Coerce
from common.data_facade import DataFacade, DEFAULT_PAGE_SIZE

app = Flask('topsecret')
data_facade = DataFacade(app)

# Cross-platform way to have a single class that reporesents a string
try:
    basestring
except NameError:
    basestring = str

validate_get_page = Schema({
    Required('page', default=1): All(Coerce(int), Range(min=1), msg='Page must be an integer >= 1'),
    Required('page_size', default=DEFAULT_PAGE_SIZE): All(Coerce(int), Range(min=1, max=1000), msg='Page size must be an integer >= 1 and <= 1000'),
    'body': All(basestring, Length(min=1), msg="Body search must be a nonzero-length string if specified"),
    'sender': All(basestring, Length(min=1), msg="Sender search must be a nonzero-length string if specified"),
    'recipient': All(basestring, Length(min=1), msg="Recipient search must be a nonzero-length string if specified"),
    'sort': All(basestring, Length(min=1), msg="Sort attribute must be a nonzero-length string if specified")
})


@app.route('/emails/<id>', methods=['GET'])
def emails_by_id(id):
    """
    Load an email by its unique ID/hash
    :param id: the ID/hash of the email to load
    :return: A json object containing the email (200), 404 if not found, or 400 if id is invalid.
    """
    email = data_facade.db.email.find_one_or_404({'_id': id})
    return json.dumps(email)


@app.route('/emails', methods=['GET'])
def emails_all():
    """
    Load a group of multiple emails using optional query parameters
    :return: A json array containing matching emails (200) or 400 if one or more parameters are invalid.
    """
    try:
        querystring = validate_get_page(request.args)
    except Invalid as e:
        return e.error_message, 400

    # sender = querystring.get('sender')
    # if sender:
    #     sender = re.compile(re.escape(sender))
    #
    # recipient = querystring.get('recipient')
    # if sender:
    #     recipient = re.compile(re.escape(recipient))
    #
    # body = querystring.get('body')
    # if body:
    #     body = re.compile(re.escape(body))
    # page = querystring.get('page')
    # page_size = querystring.get('page_size')

    emails = data_facade.load('email', **querystring)

    json_data = json.dumps([email for email in emails])
    return Response(json_data, mimetype='application/json')


if __name__ == "__main__":
    app.run()
