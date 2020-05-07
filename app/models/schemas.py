from app import ma
from marshmallow import fields
from app.models import Rider, Horse, Result, Competition, Test, RankingList, Task, RankingListTest, User

class UserSchema(ma.ModelSchema):
    class Meta:
        model = User
        exclude = ["password_hash", "id"]

    _links = ma.Hyperlinks(
        {
            "self": ma.URLFor("api.user", username="<id>")
        }
    )

class RiderSchema(ma.ModelSchema):
    class Meta:
        model = Rider

    results = ma.List(ma.Nested("ResultSchema", exclude=("rider",)))

    _links = ma.Hyperlinks(
        {
            "self": ma.URLFor("api.rider", rider_id="<id>"),
        }
    )

class HorseSchema(ma.ModelSchema):
    class Meta:
        model = Horse
    
    results = ma.List(ma.Nested("ResultSchema", exclude=("horse",)))

    _links = ma.Hyperlinks(
        {
            "self": ma.URLFor("api.horse", horse_id="<id>")
        }
    )

class ResultSchema(ma.ModelSchema):
    class Meta:
        model = Result

    rider = ma.Nested("RiderSchema", exclude=("results","id",))
    horse = ma.Nested("HorseSchema", exclude=("results","id",))
    test = ma.Nested("TestSchema", exclude=("results","id",))

    _links = ma.Hyperlinks(
        {
            "self": ma.URLFor("api.result", result_id="<id>"),
            "rider": ma.URLFor("api.rider", rider_id="<rider_id>"),
            "horse": ma.URLFor("api.horse", horse_id="<horse_id>"),
            "competition": ma.URLFor("api.competition", competition_id="<test.competition_id>")
        }
    )

class CompetitionSchema(ma.ModelSchema):
    class Meta:
        model = Competition

    tests = ma.List(ma.Nested("TestSchema", exclude=("competition","results")))
    
    _links = ma.Hyperlinks(
        {
            "self": ma.URLFor("api.competition", competition_id="<id>")
        }
    )

class TestSchema(ma.ModelSchema):
    class Meta:
        model = Test

    # competition = ma.Nested("CompetitionSchema", exclude=("tests",))

    _links = ma.Hyperlinks(
        {
            "self": ma.URLFor("api.test", test_id="<id>"),
            "competition": ma.URLFor("api.competition", competition_id="<competition_id>")
        }
    )

class RankingListSchema(ma.ModelSchema):
    class Meta:
        model = RankingList
    
    competitions = ma.List(ma.Nested("CompetitionSchema", exclude=("include_in_ranking",)))
    
    _links = ma.Hyperlinks(
        {
            "self": ma.URLFor("api.ranking", listname="<shortname>"),
            # "competitions": ma.List(
            #     ma.URLFor("api.competition", competition_id="<competitions>")
            # )
        }
    )

class RankingListTestSchema(ma.ModelSchema):
    class Meta:
        model = RankingListTest
    
    _links = ma.Hyperlinks(
        {
            "self": ma.URLFor("api.rankinglist", listname="<rankinglist.shortname>", testcode="<testcode>" ),
            "results": ma.URLFor("api.resultlist", listname="<rankinglist.shortname>", testcode="<testcode>")
        }
    )

class TaskSchema(ma.ModelSchema):
    class Meta:
        model = Task
    
    progress = fields.Integer()

    _links = ma.Hyperlinks(
        {
            "self": ma.URLFor("api.task", task_id="<id>")
        }
    )