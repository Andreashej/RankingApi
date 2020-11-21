from .. import ma
from marshmallow import fields
from . import Rider, Horse, Result, Competition, Test, RankingList, Task, RankingListTest, User, RankingResultsCache, TestCatalog

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        exclude = ["password_hash", "id"]

    _links = ma.Hyperlinks(
        {
            "self": ma.URLFor("api.user", username="<id>"),
        }
    )

class RiderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Rider

    results = ma.List(ma.Nested("ResultSchema", exclude=("rider",)))
    number_of_results = fields.Integer()
    fullname = fields.String()

    testlist = fields.List(fields.String())

    _links = ma.Hyperlinks(
        {
            "self": ma.URLFor("api.rider", rider_id="<id>"),
        }
    )

class HorseSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Horse
    
    results = ma.List(ma.Nested("ResultSchema", exclude=("horse",)))
    number_of_results = fields.Integer()
    
    testlist = fields.List(fields.String())
        
    _links = ma.Hyperlinks(
        {
            "self": ma.URLFor("api.horse", horse_id="<id>")
        }
    )

class ResultSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Result

    rider = ma.Nested("RiderSchema", exclude=("results",))
    horse = ma.Nested("HorseSchema", exclude=("results",))
    test = ma.Nested("TestSchema", exclude=("results","id",))

    _links = ma.Hyperlinks(
        {
            "self": ma.URLFor("api.result", result_id="<id>"),
            "rider": ma.URLFor("api.rider", rider_id="<rider_id>"),
            "horse": ma.URLFor("api.horse", horse_id="<horse_id>"),
            "competition": ma.URLFor("api.competition", competition_id="<test.competition_id>")
        }
    )

class CompetitionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Competition
        include_relationships = True

    tests = ma.List(ma.Nested("TestSchema", exclude=("competition","results")))
    include_in_ranking = ma.List(ma.Nested("RankingListSchema", only=("shortname","listname","results_valid_days",)))

    _links = ma.Hyperlinks(
        {
            "self": ma.URLFor("api.competition", competition_id="<id>")
        }
    )

class TestSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Test
        include_relationships = True    

    competition = ma.Nested("CompetitionSchema", only=("name","last_date","first_date","id", "include_in_ranking"))
    results = ma.Nested("ResultSchema", only=("rider.id", "rider.fullname", "horse.id", "horse.horse_name", "horse.feif_id", "mark"), many=True)

    _links = ma.Hyperlinks(
        {
            "self": ma.URLFor("api.test", test_id="<id>"),
            "competition": ma.URLFor("api.competition", competition_id="<competition_id>")
        }
    )

class RankingListSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = RankingList
        include_relationships = True
    
    competitions = ma.List(ma.Nested("CompetitionSchema", exclude=("include_in_ranking",)))

    tests = ma.Nested("RankingListTestSchema", only=("testcode",), many=True)
    
    _links = ma.Hyperlinks(
        {
            "self": ma.URLFor("api.ranking", listname="<shortname>"),
            # "competitions": ma.List(
            #     ma.URLFor("api.competition", competition_id="<competitions>")
            # )
        }
    )

class RankingListTestSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = RankingListTest
    
    _links = ma.Hyperlinks(
        {
            "self": ma.URLFor("api.rankinglist", id="<id>" ),
            "results": ma.URLFor("api.resultlist", listname="<rankinglist.shortname>", testcode="<testcode>")
        }
    )

class RankingListResultSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = RankingResultsCache

        exclude = ["cached_results"]

    riders = ma.Nested("RiderSchema", many=True, only=("id","fullname",))
    horses = ma.Nested("HorseSchema", many=True, only=("id","horse_name","feif_id",))
    marks = ma.Nested("ResultSchema", many=True, only=("mark","horse.horse_name","horse.feif_id","test.competition.name","test.competition.id", "test.testcode"))

class TaskSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Task
    
    progress = fields.Integer()

    _links = ma.Hyperlinks(
        {
            "self": ma.URLFor("api.task", task_id="<id>")
        }
    )

class TestCatalogSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = TestCatalog
    
    # _links = ma.Hyperlinks(
    #     {
    #         "self": ma.URLFor("api.rankinglist", id="<id>" ),
    #         "results": ma.URLFor("api.resultlist", listname="<rankinglist.shortname>", testcode="<testcode>")
    #     }
    # )