from app import create_app
from rq import Connection, Worker

application = create_app()

if __name__ == '__main__':
    application.debug = True
    application.run(host='0.0.0.0', threaded=True)

    with Connection(application.redis):
        worker = Worker(application.config['QUEUE'])
        worker.work()
        print("working")