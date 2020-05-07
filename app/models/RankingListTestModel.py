from app import db, cache
from sqlalchemy import func, and_
from sqlalchemy.orm import contains_eager
from datetime import datetime, timedelta

from app.models import Result, Test, Competition, Rider, RankingList, Horse



class RankingListTest(db.Model):
    __tablename__ = 'rankinglist_tests'
    id = db.Column(db.Integer, primary_key=True)
    testcode = db.Column(db.String(3))
    rankinglist_id = db.Column(db.Integer, db.ForeignKey('rankinglists.id'), nullable=False)
    included_marks = db.Column(db.Integer, default=2)
    order = db.Column(db.String(4), default='desc')
    grouping = db.Column(db.String(5), default='rider')
    min_mark = db.Column(db.Float)
    rounding_precision = db.Column(db.Integer)
    
    @cache.memoize(timeout=1440)
    def get_ranking(self):
        ranking = self.rankinglist

        if self.order == 'desc':
            results = db.session.query(Result).filter(Result.mark >= self.min_mark)\
                .join(Test, Result.test_id == Test.id).filter_by(testcode=self.testcode)\
                .join(Competition).filter(Competition.last_date >= (datetime.now() - timedelta(days=ranking.results_valid_days)))\
                .join(RankingList, Competition.include_in_ranking).filter_by(shortname=ranking.shortname)\
                .order_by(Result.mark.desc())\
                .subquery()
        else:
            results = db.session.query(Result).filter(and_(Result.mark <= self.min_mark, Result.mark > 0))\
                .join(Test, Result.test_id == Test.id).filter_by(testcode=self.testcode)\
                .join(Competition).filter(Competition.last_date >= (datetime.now() - timedelta(days=ranking.results_valid_days)))\
                .join(RankingList, Competition.include_in_ranking).filter_by(shortname=ranking.shortname)\
                .order_by(Result.mark.asc())\
                .subquery()

        if self.grouping == 'rider':
            items = db.session.query(Rider)\
                .join(results, Rider.id == results.c.rider_id)\
                .options(contains_eager(Rider.results, alias=results))\
                .all()
            
            from app.models import RiderSchema
            schema = RiderSchema(many=True)

        elif self.grouping == 'horse':
            items = db.session.query(Horse)\
                .join(results, Horse.id == results.c.horse_id)\
                .options(contains_eager(Horse.results, alias=results))\
                .all()

            from app.models import HorseSchema
            schema = HorseSchema(many=True)

        items = schema.dump(items).data

        valid_results = []

        for item in items:
            if (len(item['results']) > self.included_marks - 1):
                item['results'] = item['results'][:self.included_marks]
                final_mark = 0
                for result in item['results']:
                    final_mark += result['mark']

                final_mark = round(final_mark / len(item['results']), self.rounding_precision)
                item.update({'final_mark': final_mark})
                valid_results.append(item)
            
        valid_results = sorted(valid_results, key=lambda i: i['final_mark'], reverse=self.order=='desc')

        current_rank = 0
        prev_score = 0

        for result in valid_results:
            if prev_score != result['final_mark']:
                current_rank += 1

            result.update({'rank': current_rank})

            prev_score = result['final_mark']
        
        return valid_results