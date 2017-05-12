from mongoengine import *
import datetime

connect('test_database')

class User(Document):
    # id = LongField(unique=True, primary_key=True, required=True)
    username = StringField(required=True)
    cw_geroj_info = DictField()

    vk_link = StringField()

    found_new_text_ids = ListField(LongField())
    text_ids = ListField(LongField())

    achievements_ids = ListField(LongField())

class QuestDescriptor(Document):
    # id = LongField(unique=True, primary_key=True, required=True)
    message_id = LongField(unique=True)

    yield_res = IntField()
    yield_exp = IntField()
    yield_gold = IntField()

    text_id = LongField()
    text = StringField() # Fill this only when no text_id could be get from QuestText collection

    meta = {
        'indexes': ['message_id']
    }

class QuestText(Document):
    type = StringField()
    text = StringField()

