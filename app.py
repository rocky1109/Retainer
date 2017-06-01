
import sys
import json

db_path = None

with open("settings.json") as fh:
    settings = json.load(fh)
    if not (settings.has_key("NO_OF_STATES") or settings.has_key("STATES")):
        print """
Either "NO_OF_STATES" or "STATES" should be configured in settings.json
        """
        sys.exit(-1)
    elif not settings.has_key("NO_OF_STATES"):
        settings["NO_OF_STATES"] = len(settings["STATES"])
    elif not settings.has_key("STATES"):
        settings["STATES"] = range(settings["NO_OF_STATES"])

    if not settings.has_key("SQL_DB_PATH"):
        settings["SQL_DB_PATH"] = "sqlite:///apps.sqlite3"


from flask import Flask, jsonify, request, make_response, url_for

from database import db_session, init_db
from models import App


application = Flask(__name__)
application.config['SQLALCHEMY_DATABASE_URI'] = settings["SQL_DB_PATH"]


init_db()


STATES_INDEX = range(settings["NO_OF_STATES"])


def make_public_app(app):
    new_app = {}
    for field in app:
        if field == 'id':
            new_app['uri'] = url_for('get_app', app_id=app['id'], _external=True)
        elif settings["STATES"] and field == 'state':
            new_app['state'] = settings["STATES"][app['state']]
        else:
            new_app[field] = app[field]
    return new_app


@application.route('/api/v1.0/apps', methods=['GET'])
def get_apps():
    apps = App.query.all()
    return jsonify({'apps': [make_public_app(app.serialize) for app in apps]})


@application.route('/api/v1.0/apps/<string:app_name>', methods=['GET'])
def get_app_with_name(app_name):
    apps = App.query.filter(App.name == app_name).all()
    if not apps:
        return jsonify({
            'result': False,
            'reason': "App with name {0} not found.".format(app_name)
        }), 404
    return jsonify({'apps': [make_public_app(app.serialize) for app in apps]})


@application.route('/api/v1.0/apps/<int:app_id>', methods=['GET'])
def get_app(app_id):
    app = App.query.filter(App.id == app_id).first()
    if not app:
        return jsonify({
            'result': False,
            'reason': "App with id {0} not found.".format(app_id)
        }), 404
    return jsonify({'app': make_public_app(app.serialize)})


@application.route('/api/v1.0/apps', methods=['POST'])
def create_app():
    if not request.json or not 'name' in request.json:
        return jsonify({
            'result': False,
            'reason': "No data was found to create."
        }), 404
    a = App(name=request.json['name'], state=0)
    db_session.add(a)
    db_session.commit()
    return jsonify({'app': make_public_app(a.serialize)}), 201


@application.route('/api/v1.0/apps/<int:app_id>', methods=['PUT'])
def update_app(app_id):
    app = App.query.filter(App.id == app_id).first()
    if not app:
        return jsonify({
            'result': False,
            'reason': "App with id {0} not found.".format(app_id)
        }), 404
    if not request.json:
        return jsonify({
            'result': False,
            'reason': "No data was found to update."
        }), 404

    app.name = request.json.get('name', app.name)
    app.state = request.json.get('state', app.state)
    if app.state > max(STATES_INDEX):
        return jsonify({
            'result': False,
            'reason': "Reached to maximum state value."
        }), 404

    db_session.commit()
    return jsonify({'app': make_public_app(app.serialize)})


@application.route('/api/v1.0/apps/<int:app_id>/incr', methods=['GET'])
def increment_state(app_id):
    app = App.query.filter(App.id == app_id).first()
    if not app:
        return jsonify({
            'result': False,
            'reason': "App with id {0} not found.".format(app_id)
        }), 404
    app.state = app.state + 1

    if app.state > max(STATES_INDEX):
        return jsonify({
            'result': False,
            'reason': "Reached to maximum state value."
        }), 404

    db_session.commit()
    return jsonify({'app': make_public_app(app.serialize)})


@application.route('/api/v1.0/apps/<int:app_id>', methods=['DELETE'])
def delete_app(app_id):
    app = App.query.filter(App.id == app_id).first()
    if not app:
        return jsonify({
            'result': False,
            'reason': "App with id {0} not found.".format(app_id)
        }), 404
    db_session.delete(app)
    db_session.commit()
    return jsonify({'result': True})


@application.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@application.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


if __name__ == "__main__":
    application.run(debug=settings["DEBUG"], port=settings["PORT"])
