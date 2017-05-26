from mongoengine import *
import datetime

connect('test_database')

class QuestText(Document):
    type = StringField()
    text = StringField()

class QuestDescriptor(Document):
    # id = LongField(unique=True, primary_key=True, required=True)
    timestamp = DateTimeField(required=True)

    yield_res = DictField()
    yield_exp = IntField()
    yield_gold = IntField()

    text_id = ReferenceField(QuestText)
    text = StringField() # Fill this only when no text_id could be get from QuestText collection

    meta = {
        'indexes': ['timestamp']
    }

    def find_the_same(self):
        res = QuestDescriptor.objects(timestamp=self.timestamp,
                                      yield_res=self.yield_res,
                                      yield_exp=self.yield_exp,
                                      yield_gold=self.yield_gold,
                                      text_id=self.text_id)

        return res

class User(Document):
    # id = LongField(unique=True, primary_key=True, required=True)
    username = StringField(required=True)
    tg_user_id = LongField(required=True, unique=True)
    cw_geroj_info = DictField()

    vk_link = StringField()

    found_new_text_quest_ids = ListField(ReferenceField(QuestDescriptor))
    quest_ids = ListField(ReferenceField(QuestDescriptor))

    achievements_ids = ListField(LongField())



