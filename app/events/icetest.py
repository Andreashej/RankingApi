from typing import ByteString
from kombu import Connection, Exchange, Queue, Consumer, Message
import socket
import json
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import or_

from app.models.CompetitionModel import Competition
from app.models.PersonModel import Person
from app.models.HorseModel import Horse
from app.models.ResultModel import Result
from app.models.TestModel import Test
from app.models.MarkModel import JudgeMark
from app import db, create_app
from flask import current_app
from datetime import datetime
from sentry_sdk import capture_exception
import traceback

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
            try:
                test = competition.tests.filter(Test.testcode == data['ORIGINALTESTCODE'], or_(Test._test_name.is_(None), Test._test_name == '')).one()
                test.test_name = data['TESTCODE']
            except NoResultFound:

                test = Test.create_from_catalog(data['ORIGINALTESTCODE'])
                test.test_name = data['TESTCODE']
                competition.tests.append(test)

                rank_test = competition.tests.filter(Test.testcode == data['ORIGINALTESTCODE']).first()

                if rank_test is not None:
                    test.include_in_ranking = rank_test.include_in_ranking

                db.session.add(test)
            
        result = test.add_icetest_result(data)

        # try:
        #     rider = Person.find_by_name(data['RIDER'])
        #     rider.date_of_birth = datetime.strptime(data['BIRTHDAY'], "%Y-%m-%d")
        # except NoResultFound:
        #     rider = Person.create_by_name(data['RIDER'])
        #     db.session.add(rider)

        # try:
        #     horse = Horse.query.filter_by(feif_id = data['FEIFID']).one()
        # except NoResultFound:
        #     horse = Horse(data['FEIFID'], data['HORSE'])
        #     db.session.add(horse)

        # try:
        #     result = Result.query.filter_by(test_id=test.id, rider_id=rider.id, horse_id=horse.id, phase=data["PHASE"]).one()
        #     result.mark = data['MARK']
        #     result.state = data['STATE']
        # except NoResultFound:
        #     result = Result(test, data['MARK'], rider, horse, data['PHASE'], data['STATE'])
        #     result.created_at = datetime.fromtimestamp(data['TIMESTAMP'])
        #     db.session.add(result)
        
        # result.sta = data['STA']
        # result.rider_class = data['CLASS']
        # result.updated_at = datetime.fromtimestamp(data['TIMESTAMP'])

        # result.marks.delete()
        # for mark_raw in data['MARKS']:
        #     try:
        #         m = mark_raw['MARK']
        #         judge_no = mark_raw['JUDGE']
        #     except KeyError:
        #         m = mark_raw['mark']
        #         judge_no = mark_raw['judge']

        #     mark = JudgeMark(mark = m, judge_no = int(judge_no), judge_id=mark_raw['JUDGEID'], mark_type="mark")

        #     # Find cards associated with this mark
        #     for card in data['CARDS']:
        #         try:
        #             card_judge = card['judge']
        #         except KeyError:
        #             card_judge = card['JUDGE']
                
        #         if card_judge != mark.judge_no:
        #             continue

        #         try:
        #             card_color = card['color']
        #         except KeyError:
        #             card_color = card['COLOR']

        #         mark.red_card = card_color == 'R'
        #         mark.yellow_card = card_color == 'Y'
        #         mark.blue_card = card_color == 'B'

        #     result.marks.append(mark)

        # for ranking in result.test.include_in_ranking.all():
        #     try:
        #         ranking.propagate_result(result)
        #     except Exception as e:
        #         print(e)
        #         capture_exception(e)

        db.session.commit()
        print(f"Result saved {result}")
        message.ack()
    except Exception as e:
        capture_exception(e)
        print (f"Error saving mark. Rolling back DB.")
        traceback.print_exc(e)
        db.session.rollback()
        message.reject(True)



def establish_connection(connection, consumer):
    revived_connection = connection.clone()
    revived_connection.ensure_connection(max_retries=3)
    channel = revived_connection.channel()
    consumer.revive(channel)
    consumer.consume()
    return revived_connection

def consume(connection, consumer):
    new_conn = establish_connection(connection, consumer)
    while True:
        try:
            new_conn.drain_events(timeout=2)
        except socket.timeout:
            new_conn.heartbeat_check()

def run():
    print("Starting RabbitMQ listener...")
    connection = Connection(
        hostname=current_app.config['ICETEST_RABBIT_HOST'], 
        userid=current_app.config['ICETEST_RABBIT_USER'], 
        password=current_app.config['ICETEST_RABBIT_PASSWORD'], 
        virtual_host=current_app.config['ICETEST_RABBIT_VHOST']
    )

    exchange = Exchange("-- default --", type="direct")
    queue = Queue(name="icecompass", exchange=exchange, routing_key="icecompass")

    consumer = Consumer(connection, queues=queue, callbacks=[process_message])

    connection.connect()

    app = create_app()
    app.app_context().push()
    while True:
        try:
            consume(connection, consumer)
        except connection.connection_errors:
            print("connection revived")
