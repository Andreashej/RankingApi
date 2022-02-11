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
        emit('Screen.ScreenGroupChanged', screen.screen_group.to_json(expand=['competition']), namespace='/bigscreen')

@socketio.on('ScreenGroup.Joined', namespace='/bigscreen')
def join_screengroup(data):
    join_room(data['id'], namespace='/bigscreen')
    screen_group = ScreenGroup.query.get(data['id'])
    socketio.emit('ScreenGroup.TemplateChanged', screen_group.template, namespace="/bigscreen")

@socketio.on('ScreenGroup.SetTemplate', namespace='/bigscreen')
def change_template(updated_screengroup):
    screengroup = ScreenGroup.query.get(updated_screengroup['id'])
    screengroup.template = updated_screengroup['template']
    # emit('ScreenGroup.SetPreview', screengroup.to_json(), namespace='/bigscreen')
    screengroup.save()

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
    

@event.listens_for(ScreenGroup.template, 'set')
def screen_template_change(screen_group, template, initiator, *args):
    socketio.emit('ScreenGroup.TemplateChanged', template, namespace="/bigscreen", to=screen_group.id, include_self=True)
