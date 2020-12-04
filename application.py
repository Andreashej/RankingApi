from .app import create_app
from rq import Connection, Worker
import multiprocessing


application = create_app()

if __name__ == '__main__':
    with Connection(application.redis):
        multiprocessing.Process(target=Worker(application.config['QUEUE']).work())

    application.debug = True
    application.run(host='0.0.0.0', threaded=True)