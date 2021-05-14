#CptS 451 - Spring 2021
# https://www.psycopg.org/docs/usage.html#query-parameters

#  if psycopg2 is not installed, install it using pip installer :  pip install psycopg2  (or pip3 install psycopg2)
import json
import psycopg2


def listToString(s):
    # initialize an empty string
    str1 = ""

    # traverse in the string
    for ele in s:
        str1 += ele

        # return string
    return str1

def cleanStr4SQL(s):
    return s.replace("'","`").replace("\n"," ")

def int2BoolStr (value):
    if value == 0:
        return 'False'
    else:
        return 'True'

def connectDb():
    global conn
    if conn is not None:   # Error occurs on this line
        return

def insert2BusinessTable():
    with open('.//yelp_business.JSON','r') as f:    #TODO: update path for the input file
        line = f.readline()
        count_line = 0

        try:
            #TODO: update the database name, username, and password
            conn = psycopg2.connect("dbname='fix' user='postgres' host='localhost' password='123'")
        except:
            print('Unable to connect to the database!')
        cur = conn.cursor()

        while line:
            data = json.loads(line)
            try:
                cur.execute("INSERT INTO business (business_id, name, address, state, city, postal_code, latitude, longitude, stars, numCheckins, numTips, is_open)"
                       + " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                         (data['business_id'],cleanStr4SQL(data["name"]), cleanStr4SQL(data["address"]), data["state"], data["city"], data["postal_code"], data["latitude"], data["longitude"], data["stars"], 0 , 0 , [False,True][data["is_open"]] ) )
            except Exception as e:
                print("Insert to businessTABLE failed!",e)
            conn.commit()

            line = f.readline()
            count_line +=1

        cur.close()
        conn.close()

    print(count_line)
    f.close()

def insert2checkinTable():
    with open('.//yelp_checkin.JSON','r') as f:    #TODO: update path for the input file
        line = f.readline()
        count_line = 0


        try:

            conn = psycopg2.connect("dbname='fix' user='postgres' host='localhost' password='123'")
        except:
            print('Unable to connect to the database!')
        cur = conn.cursor()

        while line:
            data = json.loads(line)

            dates = data["date"].split(",")


            for i in dates:
                cur.execute("INSERT INTO checkin (business_id, date)"
                            + " VALUES (%s, %s)",
                            (data['business_id'], i))
                print(i)
                conn.commit()

            """while i < (len(dates)):
                try:
                    cur.execute("INSERT INTO checkin (business_id, date)"
                           + " VALUES (%s, %s)",
                             (data['business_id'], (dates[i]) ) )
                except Exception as e:
                    print("Insert to checkin failed!",e)
                conn.commit()"""
            line = f.readline()
            count_line +=1

        cur.close()
        conn.close()

    print(count_line)

    f.close()


def insert2tipTable():
    with open('.//yelp_tip.JSON', 'r') as f:  # TODO: update path for the input file
        line = f.readline()
        count_line = 0

        try:

            conn = psycopg2.connect("dbname='fix' user='postgres' host='localhost' password='123'")
        except:
            print('Unable to connect to the database!')
        cur = conn.cursor()

        while line:
            data = json.loads(line)

            try:
                cur.execute("INSERT INTO tip (business_id, date, likes, text, user_id)"
                            + " VALUES (%s, %s, %s, %s, %s)",
                            (cleanStr4SQL(data['business_id']), cleanStr4SQL(data["date"]), data["likes"], cleanStr4SQL(data["text"]), cleanStr4SQL(data["user_id"])))
            except Exception as e:
                print("Insert to tip failed!", e)
            conn.commit()
            line = f.readline()
            count_line += 1

        cur.close()
        conn.close()

    print(count_line)

    f.close()


    f.close()

def insert2userTable():
    with open('.//yelp_user.JSON','r') as f:    #TODO: update path for the input file
        line = f.readline()
        count_line = 0


        try:

            conn = psycopg2.connect("dbname='fix' user='postgres' host='localhost' password='123'")
        except:
            print('Unable to connect to the database!')
        cur = conn.cursor()

        while line:
            data = json.loads(line)

            try:
                cur.execute("INSERT INTO userTable (average_stars, cool, fans, friends, funny, name, tipcount, useful, user_id, yelping_since)"
                       + " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                         (data['average_stars'], (data["cool"]), (data["fans"]), (data["friends"]), (data["funny"]), cleanStr4SQL(data["name"]), (data["tipcount"]), (data["useful"]), cleanStr4SQL(data["user_id"]), cleanStr4SQL(data["yelping_since"]) ) )
            except Exception as e:
                print("Insert to user failed!",e)
            conn.commit()
            line = f.readline()
            count_line +=1

        cur.close()
        conn.close()

    print(count_line)


def insert2friendsTable():
    with open('.//yelp_user.JSON','r') as f:    #TODO: update path for the input file
        line = f.readline()
        count_line = 0

        try:

            conn = psycopg2.connect("dbname='fix' user='postgres' host='localhost' password='123'")
        except:
            print('Unable to connect to the database!')
        cur = conn.cursor()

        while line:
            data = json.loads(line)


            friend = data["friends"]
            listToString(friend).split(', ')
            i = 0
            while i < (len(friend)):
                try:
                    cur.execute("INSERT INTO friends (user_id, friend_user_id)"
                                + " VALUES (%s, %s) ",
                                (data['user_id'], (friend[i])))
                except Exception as e:
                    print("Insert to checkin failed!", e)
                conn.commit()
                i = i + 1
            line = f.readline()
            count_line += 1

        cur.close()
        conn.close()

    print(count_line)

    f.close()

def insert2categoryTable():
        with open('.//yelp_business.JSON', 'r') as f:  # TODO: update path for the input file
            line = f.readline()
            count_line = 0

            try:

                conn = psycopg2.connect("dbname='fix' user='postgres' host='localhost' password='123'")
            except:
                print('Unable to connect to the database!')
            cur = conn.cursor()

            while line:
                data = json.loads(line)
                categories = data["categories"].split(', ')
                i = 0
                while i < (len(categories)):
                    try:
                        cur.execute("INSERT INTO category (business_id, category)"
                                    + " VALUES (%s, %s) ",
                                    (data['business_id'], (categories[i])))
                    except Exception as e:
                        print("Insert to checkin failed!", e)
                    conn.commit()
                    i = i + 1
                line = f.readline()
                count_line += 1

            cur.close()
            conn.close()

        print(count_line)

        f.close()

def insert2BusinessHoursTable():
    with open('.//yelp_business.JSON','r') as f:    #TODO: update path for the input file
        line = f.readline()
        count_line = 0

        try:
            #TODO: update the database name, username, and password
            conn = psycopg2.connect("dbname='fix' user='postgres' host='localhost' password='123'")
        except:
            print('Unable to connect to the database!')

        cur = conn.cursor()
        while line:

            data = json.loads(line)
            for d, t in (data["hours"]).items():
                try:
                    time = t.split('-')
                    cur.execute("INSERT INTO hours (business_id, day, open, close)"
                                + "VALUES (%s, %s, %s, %s)",
                                (data['business_id'], d, time[0], time[1]))
                    conn.commit()
                except Exception as e:
                    print("Insert to checkin failed!", e)
                    conn.commit()

            """data = json.loads(line)
            hour = data["hours"]
            i = 0"""


            """while i < (len(hour)):
                try:
                    cur.execute("INSERT INTO hours (business_id, category)"
                                + " VALUES (%s, %s) ",
                                (data['business_id'], (hour[i])))
                except Exception as e:
                    print("Insert to checkin failed!", e)
                conn.commit()
                i = i + 1"""
            line = f.readline()
            count_line += 1

        cur.close()
        conn.close()

    print(count_line)
    f.close()

def flatten(d):
    result = []
    for k, v in d.items():
            if isinstance(v, dict):
                result += flatten(v)
            else:
                if v != "False":
                    result.append((k, v))

    return result


def insert2AttributeTable():
    with open('.//yelp_business.JSON', 'r') as f:  # TODO: update path for the input file
        line = f.readline()
        count_line = 0

        try:
            # TODO: update the database name, username, and password
            conn = psycopg2.connect("dbname='fix' user='postgres' host='localhost' password='123'")
        except:
            print('Unable to connect to the database!')
        cur = conn.cursor()
        while line:
            data = json.loads(line)
            try:
                for k, v in flatten(data["attributes"]):
                    cur.execute("INSERT INTO attribute (business_id, name, value)"
                                + "VALUES (%s, %s, %s)",
                                (data['business_id'], k, v))
                    conn.commit()
            except Exception as e:
                print("Insert to checkin failed!", e)
                conn.commit()


            count_line += 1
            line = f.readline()
        cur.close()
        conn.close()


    """        try:
                cur.execute(
                    "INSERT INTO business (business_id, name, address, state, city, postal_code, latitude, longitude, stars, numCheckins, numTips, is_open)"
                    + " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (data['business_id'], cleanStr4SQL(data["name"]), cleanStr4SQL(data["address"]), data["state"],
                     data["city"], data["postal_code"], data["latitude"], data["longitude"], data["stars"], 0, 0,
                     [False, True][data["is_open"]]))
            except Exception as e:
                print("Insert to businessTABLE failed!", e)"""

    print(count_line)
    f.close()


if __name__ == "__main__":
    #insert2friendsTable()
    #insert2checkinTable()
    #insert2categoryTable()
    #insert2BusinessTable()
    #insert2BusinessHoursTable()
    #insert2AttributeTable()
    insert2userTable()
    #insert2tipTable()