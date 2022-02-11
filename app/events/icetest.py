from typing import ByteString
from kombu import Connection, Exchange, Queue, Consumer, Message
import socket
import threading
import json
from sqlalchemy.orm.exc import NoResultFound

from app.models.CompetitionModel import Competition
from app.models.PersonModel import Person
from app.models.HorseModel import Horse
from app.models.ResultModel import Result
from app.models.TestModel import Test
from app.models.MarkModel import Mark, Time, Flag
from app import db, create_app
from flask import current_app
from datetime import datetime

connection = Connection(hostname="southpole.icetestng.com", userid="icecompass", password="n-6TaDR-zRErUBF7U@qQ", virtual_host="dev")

connection.connect()

exchange = Exchange("-- default --", type="direct")
queue = Queue(name="icecompass", exchange=exchange, routing_key="icecompass")

def process_message(body: ByteString, message: Message):
    try:
        data = json.loads(body)['MESSAGE']

        try:
            competition = Competition.query.filter_by(ext_id = data['COMPASSID']).one()
        except NoResultFound:
            # The competition ID does not match anything we have - ignore the result
            message.reject()
            return
        
        try:
            test = competition.tests.filter(Test.test_name == data['TESTCODE']).one()
        except NoResultFound:
            test = Test.create_from_catalog(data['ORIGINALTESTCODE'])
            test.test_name = data['TESTCODE']
            competition.tests.append(test)
            db.session.add(test)

        try:
            rider = Person.find_by_name(data['RIDER'])
            rider.date_of_birth = datetime.strptime(data['BIRTHDAY'], "%Y-%m-%d")
        except NoResultFound:
            rider = Person.create_by_name(data['RIDER'])
            db.session.add(rider)

        try:
            horse = Horse.query.filter_by(feif_id = data['FEIFID']).one()
        except NoResultFound:
            horse = Horse(data['FEIFID'], data['HORSE'])
            db.session.add(horse)

        try:
            result = Result.query.filter_by(test_id=test.id, rider_id=rider.id, horse_id=horse.id).one()
            result.mark = data['MARK']
            result.state = data['STATE']
        except NoResultFound:
            result = Result(test, data['MARK'], rider, horse, data['STATE'])
            result.created_at = datetime.fromtimestamp(data['TIMESTAMP'])
            db.session.add(result)
        
        result.sta = data['STA']
        result.rider_class = data['CLASS']
        result.updated_at = datetime.fromtimestamp(data['TIMESTAMP'])

        result.marks.delete()
        for mark_raw in data['MARKS']:
            mark = Mark(mark = mark_raw['mark'], judge_no = int(mark_raw['judge']), judge_id=mark_raw['JUDGEID'])

            # Find cards associated with this mark
            for card in [card for card in data['CARDS'] if card['judge'] == mark.judge_no]:
                mark.red_card = card['color'] == 'R'
                mark.yellow_card = card['color'] == 'Y'
                mark.blue_card = card['color'] == 'B'

            result.marks.append(mark)


        db.session.commit()
        message.ack()
    except Exception as e:
        db.session.rollback()
        message.reject(True)

consumer = Consumer(connection, queues=queue, callbacks=[process_message])

def establish_connection():
    revived_connection = connection.clone()
    revived_connection.ensure_connection(max_retries=3)
    channel = revived_connection.channel()
    consumer.revive(channel)
    consumer.consume()
    return revived_connection

def consume():
    new_conn = establish_connection()
    while True:
        try:
            new_conn.drain_events(timeout=2)
        except socket.timeout:
            new_conn.heartbeat_check()

def run():
    app = create_app()
    app.app_context().push()
    while True:
        try:
            consume()
        except connection.connection_errors:
            print("connection revived")

# x = threading.Thread(target=run, daemon=True)
# x.start()