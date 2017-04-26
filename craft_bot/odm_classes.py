from mongoengine import *
import datetime

class User(Document):
    id = LongField(unique=True, primary_key=True, required=True)
    username = StringField(required=True)
    cw_username = StringField(required=True)

    vk_link = StringField()

    found_new_texts = DictField()
    text_ids = ListField(LongField())

    achievements_ids = ListField(LongField())

class QuestDescriptor(Document):
    id = LongField(unique=True, primary_key=True, required=True)
    message_id = LongField()

    type = StringField()

    text_id = LongField()
    text = StringField()

    meta = {
        'indexes': ['message_id']
    }
