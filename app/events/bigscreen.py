from datetime import datetime, timedelta
from os import name
from app import socketio
from app.models import BigScreen, ScreenGroup, Test
from flask_socketio import emit, join_room, leave_room
from flask import request
from sqlalchemy import event

@socketio.on('Screen.Connected', namespace='/bigscreen')
def on_screen_connected(data):
    screen = BigScreen.query.get(data['screenId']) if data['screenId'] is not None else None
        
    if screen is None:
        screen = BigScreen()
    
    screen.client_id = request.sid
    screen.save()
    emit('Screen.Created', screen.to_json(), namespace='/bigscreen')

    if screen.screen_group:
        join_room(screen.screen_group_id, namespace='/bigscreen')
        emit('Screen.ScreenGroupChanged', screen.screen_group.to_json(expand=['competition','test']), namespace='/bigscreen')

@socketio.on('ScreenGroup.Joined', namespace='/bigscreen')
def join_screengroup(data):
    join_room(data['id'], namespace='/bigscreen')
    screen_group = ScreenGroup.query.get(data['id'])
    # socketio.emit('ScreenGroup.TemplateChanged', screen_group.template, namespace="/bigscreen")

@socketio.on('ScreenGroup.SetTemplate', namespace='/bigscreen')
def change_template(updated_screengroup):
    screen_group = ScreenGroup.query.get(updated_screengroup['id'])
    screen_group.template = updated_screengroup['template']
    emit('ScreenGroup.TemplateChanged', {
        'template': updated_screengroup['template'],
        'templateData': updated_screengroup['templateData']
    }, namespace="/bigscreen", to=screen_group.id, include_self=True)
    screen_group.save()

@socketio.on('Screen.SetScreenGroup', namespace='/bigscreen')
def set_screengroup(screen_id, new_screengroup):
    screen = BigScreen.query.get(screen_id)

    leave_room(screen.screen_group_id, namespace='/bigscreen')
    join_room(new_screengroup['id'], namespace='/bigscreen')

    screen.screen_group_id = new_screengroup['id']
    screen.save()
    emit('Screen.ScreenGroupChanged', screen.screen_group.to_json(expand=['screens']), namespace='/bigscreen', include_self=True)

@socketio.on('CollectingRing.Call', namespace='/bigscreen')
def call_collectingring(screen_group_id, test_id, start_group):
    
    screen_group = ScreenGroup.query.get(screen_group_id)
    test = Test.query.get(test_id)
    start_list_entries = test.startlist.filter_by(start_group = start_group).all()

    end_time = datetime.now() + timedelta(seconds=180)

    emit('CollectingRing.ShowCall', {
        'startListEntries': [entry.to_json(expand=['rider']) for entry in start_list_entries],
        'endTime': end_time.isoformat()
    }, namespace="/bigscreen", to=screen_group.id)

@socketio.on('ScreenGroup.HideAll', namespace='/bigscreen')
def hide_all(screen_group_id):
    emit('ScreenGroup.HideAll', namespace="/bigscreen", to=screen_group_id)

@event.listens_for(ScreenGroup.test_id, 'set')
def screen_group_test_changed(screen_group, test_id, initiator, *args):
    test = Test.query.get(test_id)
    socketio.emit('ScreenGroup.TestChanged', test.to_json(), namespace="/bigscreen", to=screen_group.id, include_self=True)