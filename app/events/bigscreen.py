from app import socketio
from app.models import BigScreen, ScreenGroup
from flask_socketio import emit, join_room, leave_room, send
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
        emit('Screen.ScreenGroupChanged', screen.screen_group.to_json(), namespace='/bigscreen')

@socketio.on('ScreenGroup.Joined', namespace='/bigscreen')
def join_screengroup(data):
    join_room(data['id'], namespace='/bigscreen')
    screen_group = ScreenGroup.query.get(data['id'])
    socketio.emit('ScreenGroup.TemplateChanged', screen_group.template, namespace="/bigscreen")

@socketio.on('ScreenGroup.SetTemplate', namespace='/bigscreen')
def change_template(updated_screengroup):
    screengroup = ScreenGroup.query.get(updated_screengroup['id'])
    emit('ScreenGroup.SetPreview', screengroup.to_json(), namespace='/bigscreen')
    screengroup.template = updated_screengroup['template']
    screengroup.save()

@socketio.on('Screen.SetScreenGroup', namespace='/bigscreen')
def set_screengroup(screen_id, new_screengroup):
    screen = BigScreen.query.get(screen_id)

    leave_room(screen.screen_group_id, namespace='/bigscreen')
    join_room(new_screengroup['id'], namespace='/bigscreen')

    screen.screen_group_id = new_screengroup['id']
    screen.save()
    emit('Screen.ScreenGroupChanged', screen.screen_group.to_json(expand=['screens']), namespace='/bigscreen', include_self=True)
    

@event.listens_for(ScreenGroup.template, 'set')
def screen_template_change(screen_group, template, initiator, *args):
    socketio.emit('ScreenGroup.TemplateChanged', template, namespace="/bigscreen", to=screen_group.id, include_self=True)
