import os

from flask_environments import Environments
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import logging
import connexion

__version__ = '0.1'

db = None
migrate = None
login = None
debug_toolbar = None
app = None


def create_app(broker_start=False, log_level=logging.ERROR):
    """
    This method create the Flask application.
    :return: Flask App Object
    """
    global db
    global app
    global migrate
    global login

    api_app = connexion.App(
        __name__,
        server='flask',
        specification_dir='openapi/')

    # getting the flask app
    app = api_app.app

    flask_env = os.getenv('FLASK_ENV', 'None')
    if flask_env == 'development':
        config_object = 'config.DevConfig'
    elif flask_env == 'testing':
        config_object = 'config.TestConfig'
    elif flask_env == 'production':
        config_object = 'config.ProdConfig'
    else:
        raise RuntimeError(
            "%s is not recognized as valid app environment. You have to setup the environment!" % flask_env)

    # Load config
    env = Environments(app)
    env.from_object(config_object)

    # configuring logging
    logging.basicConfig(level=log_level)

    # loading communications
    import gooutsafe.comm as comm

    if broker_start:
        if flask_env != 'testing':
            comm.init_rabbit_mq(app)
        else:
            comm.disabled = True

    # registering db
    db = SQLAlchemy(
        app=app
    )

    # importing models
    try:
        import gooutsafe.models.reservation
    except ImportError:
        raise RuntimeError('Cannot import the models!')

    # creating migrate
    migrate = Migrate(
        app=app,
        db=db
    )

    # checking the environment
    if flask_env == 'testing':
        # we need to populate the db
        db.create_all()

    # registering to api app all specifications
    register_specifications(api_app)

    return app


def register_specifications(_api_app):
    """
    This function registers all resources in the flask application
    :param _api_app: Flask Application Object
    :return: None
    """

    # we need to scan the specifications package and add all yaml files.
    from importlib_resources import files
    folder = files('gooutsafe.specifications')
    for _, _, files in os.walk(folder):
        for file in files:
            if file.endswith('.yaml') or file.endswith('.yml'):
                file_path = folder.joinpath(file)
                _api_app.add_api(file_path)
