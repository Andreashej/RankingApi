from flask_restful import Resource, reqparse, current_app, request, url_for
from app import db, auth
from app.models import Rider, RiderSchema

riders_schema = RiderSchema(many=True, exclude=("results",))
rider_schema = RiderSchema()

class RidersResource(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('fname', type= str, required = True, location = 'json')
        self.reqparse.add_argument('lname', type= str, required = True, location = 'json')

    def get(self):
        page = request.args.get('page', 1, type=int)

        riders = Rider.query.paginate(page, current_app.config['RIDERS_PER_PAGE'],False)
        riders_json = riders_schema.dump(riders.items).data

        wrapper = {
            "_links": {
                "next": url_for("api.riders",page=riders.next_num) if riders.has_next else None,
                "prev": url_for("api.riders",page=riders.prev_num) if riders.has_prev else None
            },
            "items": riders_json
        }

        return {'status': 'success', 'data': wrapper}, 200
    
    @auth.login_required
    def post(self):
        args = self.reqparse.parse_args()
        rider = Rider(
            first=args['fname'],
            last=args['lname']
        )

        try:
            db.session.add(rider)
            db.session.commit()
        except:
            return {'status': 'ERROR'}, 500

        rider = rider_schema.dump(rider).data

        return {'status': 'OK', 'data': rider}, 200
    
    @auth.login_required
    def delete(self):
        try:
            Rider.query.delete()
            db.session.commit()
        except:
            return {'status': 'ERROR'}, 500
        
        return {'status': 'OK'}, 204

class RiderResource(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('fname', type= str, required = True, location = 'json')
        self.reqparse.add_argument('lname', type= str, required = True, location = 'json')

    def get(self, rider_id):
        rider = Rider.query.get(rider_id)
        if not rider:
            return {'status': 'NOT FOUND'}, 404
        
        rider = rider_schema.dump(rider).data   
        return {'status': 'OK', 'data': rider}
    
    @auth.login_required
    def patch(self, rider_id):
        args = self.reqparse.parse_args()
        
        rider = Rider.query.get(rider_id)
        if not rider:
            return {'status': 'NOT FOUND'}, 404
        
        if args['fname'] is not None:
            rider.firstname = args['fname']

        if args['lname'] is not None:
            rider.lastname = args['lname']
        
        rider = rider_schema.dump(rider).data
        
        return {'status': 'OK', 'data': rider}

    @auth.login_required
    def delete(self, rider_id):
        rider = Rider.query.get(rider_id)

        try:
            db.session.delete(rider)
            db.session.commit()
        except:
            return {'status': 'ERROR'}, 500
        return {'status': 'OK'}, 204