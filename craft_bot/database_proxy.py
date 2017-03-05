class DataBaseProxy:
    db = None
    def setDb(db):
        DataBaseProxy.db = db

class Resources(DataBaseProxy):
    def resetResource(name, cost):
        res = db.Resources.find_one({'name': name})
        if !res:
            db.Resources.insert_one({'name': name, 'cost': cost})
            return 2

        if res['cost'] != cost:
            db.Resources.update_one({'name': name}, {'$set': {'cost': cost}})
            return 1

        return 0

    def getResource(name):
        return db.Resources.find_one({'name': name})

    def getAll():
        a_res = []
        for res in db.Resources.find():
            a_res.append(res)

        return a_res

class Users(DataBaseProxy):
    def getUserStock(name, user_stock):
        user = db.Users.find_one('name')
        if not user:
            raise "Trying to get stock from non-existing user"

        unknown_res_names = []
        #add 'cost' field to all stock entries
        for stock_entry in user['stock']:
            res = Resources.getResource(stock_entry['name'])
            if not res:
                unknown_res_names.append(stock_entry['name'])
            else:
                stock_entry['cost'] = res['cost']

        user_stock = user
