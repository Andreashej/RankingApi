from flask_restful import Resource, reqparse
from app import db, auth

from app.models import Horse, HorseSchema

horses_schema = HorseSchema(many=True)
horse_schema = HorseSchema()

class HorsesResource(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str, required=True, location='json')
        self.reqparse.add_argument('feif_id', type=str, required=True, location='json')
    
    def get(self):
        horses = Horse.query.all()
        horses = horses_schema.dump(horses).data

        return {'status': 'OK', 'data': horses}, 200
    
    @auth.login_required
    def post(self):
        args = self.reqparse.parse_args()

        horse = Horse(
            feif_id=args['feif_id'],
            name=args['name']
        )

        try:
            db.session.add(horse)
            db.session.commit()
        except Exception as inst:
            print (inst.args)
            return {'status': 'ERROR'}, 500
        
        horse = horse_schema.dump(horse).data

        return {'status': 'OK', 'data': horse},200

    @auth.login_required
    def delete(self):
        try:
            Horse.query.delete()
            db.session.commit()
        except:
            return {'status': 'ERROR'}, 500
        
        return {'status': 'OK'}, 204
    
class HorseResource(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str, required=True, location='json')
        self.reqparse.add_argument('feif_id', type=str, required=True, location='json')
    
    def get(self,horse_id):
        horse = Horse.query.get(horse_id)

        if not horse:
            return {'status': 'NOT FOUND'},404

        horse = horse_schema.dump(horse).data
        
        return {'status': 'OK', 'data': horse},200