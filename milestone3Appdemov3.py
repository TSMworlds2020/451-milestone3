import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QAction, QTableWidget,QTableWidgetItem,QVBoxLayout, QTextEdit
from PyQt5 import uic, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap
from collections import Counter
import psycopg2
from flask import Flask
from flask import render_template
import pandas as pd
import tensorflow as tf
import numpy as np
from tensorflow import keras
from tensorflow.keras import layers
import matplotlib.pyplot as plt
import psycopg2
print('TensorFlow version: %s' % tf.__version__)
print('Keras version: %s' % tf.keras.__version__)

list =[]

try:
    connection = psycopg2.connect(user="postgres",
                                  password="shadow99",
                                  host="localhost",
                                  port="5432",
                                  database="milestone2db")
    cursor = connection.cursor()
    postgreSQL_select_Query = "SELECT tip.user_id, business.business_id, business.stars, address FROM business, tip WHERE tip.business_id = business.business_id;"

    cursor.execute(postgreSQL_select_Query)
    print("Selecting rows from user and business table using cursor.fetchall")
    user_records = cursor.fetchall()

    print("Print each row and it's columns values")
    for row in user_records:

        list.append(row)
except (Exception, psycopg2.Error) as error:
    print("Error while fetching data from PostgreSQL", error)

finally:
    # closing database connection.
    if connection:
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")
df = pd.DataFrame(list)

df = df.rename(columns={0:"userID",1:"businessID",2:"stars",3:"address"})
#print(df)
users_ids = df["userID"].unique().tolist()


user2user_encoded = {x: i for i, x in enumerate(users_ids)}
userencoded2user = {i:x for i, x in enumerate(users_ids)}
business_ids = df["businessID"].unique().tolist()
business2business_encoded = {x: i for i, x in enumerate(business_ids)}
business_encoded2business = {i: x for i, x in enumerate(business_ids)}

df["user"] = df["userID"].map(user2user_encoded)
df["business"] = df["businessID"].map(business2business_encoded)
num_users = len(user2user_encoded)
num_business = len(business2business_encoded)

x = df[["user", "business"]].values
df["stars"] = df["stars"].values.astype(np.float32)

min_rating = min(df["stars"])
max_rating = max(df["stars"])

#print(
#    "Number of users: {}, Number of Business: {}, Min rating: {}, Max rating: {}".format(
#        num_users, num_business, min_rating, max_rating
#    )
#)

df = df.sample(frac=1, random_state=42)
x = df[["user", "business"]].values
# Normalize the targets between 0 and 1. Makes it easy to train.
y = df["stars"].apply(lambda x: (x - min_rating) / (max_rating - min_rating)).values
# Assuming training on 90% of the data and validating on 10%.
train_indices = int(0.9 * df.shape[0])
x_train, x_val, y_train, y_val = (
    x[:train_indices],
    x[train_indices:],
    y[:train_indices],
    y[train_indices:],
)

###Create the model
EMBEDDING_SIZE = 50


class RecommenderNet(keras.Model):
    def __init__(self, num_users, num_business, embedding_size, **kwargs):
        super(RecommenderNet, self).__init__(**kwargs)
        self.num_users = num_users
        self.num_business = num_business
        self.embedding_size = embedding_size
        self.user_embedding = layers.Embedding(
            num_users,
            embedding_size,
            embeddings_initializer="he_normal",
            embeddings_regularizer=keras.regularizers.l2(1e-6),
        )
        self.user_bias = layers.Embedding(num_users, 1)
        self.num_business_embedding = layers.Embedding(
            num_business,
            embedding_size,
            embeddings_initializer="he_normal",
            embeddings_regularizer=keras.regularizers.l2(1e-6),
        )
        self.business_bias = layers.Embedding(num_business, 1)

    def call(self, inputs):
        user_vector = self.user_embedding(inputs[:, 0])
        user_bias = self.user_bias(inputs[:, 0])
        business_vector = self.num_business_embedding(inputs[:, 1])
        business_bias = self.business_bias(inputs[:, 1])
        dot_user_business = tf.tensordot(user_vector, business_vector, 2)
        # Add all the components (including bias)
        x = dot_user_business + user_bias + business_bias
        # The sigmoid activation forces the rating to between 0 and 1
        return tf.nn.sigmoid(x)

model = tf.keras.models.load_model("neural_network")
model = RecommenderNet(num_users, num_business, EMBEDDING_SIZE)
model.compile(
    loss=tf.keras.losses.BinaryCrossentropy(), optimizer=keras.optimizers.Adam(lr=0.001)
)

qtCreatorFile = "milestone3demoappV2.ui" # Enter file here.

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

class milestone2(QMainWindow):
    def __init__(self):
        super(milestone2, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.loadStateList()
        self.ui.stateList_2.currentTextChanged.connect(self.stateChanged)
        self.ui.cityList_2.itemSelectionChanged.connect(self.cityChanged)
        self.ui.zipcodeList_2.itemSelectionChanged.connect(self.zipcodeChanged)
        self.ui.categoryList_2.itemSelectionChanged.connect(self.categoryChanged)
        self.ui.businessTable_2.cellClicked.connect(self.businessChanged)
        #self.ui.friendslist.cellClicked.connect(self.friendsChanged)
        self.ui.useridlist.itemSelectionChanged.connect(self.useridchanged2)

        self.ui.useridlist.itemSelectionChanged.connect(self.useridChanged)

        self.ui.login_user.textEdit = QTextEdit(self)  ##user
        self.ui.push_login.clicked.connect(self.check_login)

        # self.loaduseridlist()
        #self.ui.useridlist.currentTextChanged.connect(self.check_login)
        #self.ui.useridlist.itemSelectionChanged.connect(self.user_info)
        #self.ui.che

    def executeQuery(self,sql_str):
        try:
            conn = psycopg2.connect("dbname='milestone2db' user='postgres' host='localhost' password='shadow99'")
        except:
            print('executeQuery failed!')
        cur = conn.cursor()
        cur.execute(sql_str)
        conn.commit()
        result = cur.fetchall()
        conn.close()
        return result

    def loadStateList(self):
        self.ui.stateList_2.clear()
        sql_str = "SELECT distinct state FROM business ORDER BY state;"
        try:
            results = self.executeQuery(sql_str)
            for row in results:
                self.ui.stateList_2.addItem(row[0])
        except:
            print("loadStateList failed!")
        self.ui.stateList_2.setCurrentIndex(-1)
        self.ui.stateList_2.clearEditText()

    def stateChanged(self):
        self.ui.cityList_2.clear()
        state = self.ui.stateList_2.currentText()
        if (self.ui.stateList_2.currentIndex()>=0):
            sql_str = "SELECT distinct city FROM business WHERE state ='" + state + "' ORDER BY city;"
            try:
                results = self.executeQuery(sql_str)
                for row in results:
                    self.ui.cityList_2.addItem(row[0])
            except:
                print("stateChanged failed!")
            sql_str = "SELECT city, AVG(stars) FROM business WHERE state = '" + state + "' GROUP BY 1 ORDER BY avg DESC;"
            try:
                results = self.executeQuery(sql_str)
                style = "::section {""background-color: #f3f3f3; }"
                self.ui.rec_cityList.horizontalHeader().setStyleSheet(style)
                self.ui.rec_cityList.setColumnCount(len(results[0]))
                self.ui.rec_cityList.setRowCount(len(results))
                self.ui.rec_cityList.setHorizontalHeaderLabels(
                    ['City', 'Avg. Rating'])
                self.ui.rec_cityList.resizeColumnsToContents()
                self.ui.rec_cityList.setColumnWidth(0, 150)
                self.ui.rec_cityList.setColumnWidth(1, 40)
                currentRowCount = 0
                for row in results:
                    for colCount in range(0, len(results[0])):
                        self.ui.rec_cityList.setItem(currentRowCount, colCount, QTableWidgetItem(str(row[colCount])))
                    currentRowCount += 1
            except:
                print("Rec_Cities failed!")

    def cityChanged(self):
        self.ui.zipcodeList_2.clear()
        if (self.ui.stateList_2.currentIndex() >= 0) and (len(self.ui.cityList_2.selectedItems()) > 0):
            state = self.ui.stateList_2.currentText()
            city = self.ui.cityList_2.selectedItems()[0].text()
            sql_str = "SELECT distinct postal_code FROM business WHERE state = '" + state + "' AND city='" + city + "' ORDER BY postal_code ;"
            try:
                results = self.executeQuery(sql_str)
                for row in results:
                    self.ui.zipcodeList_2.addItem(row[0])
            except:
                print("cityChanged failed!")
            sql_str = "SELECT postal_code, AVG(stars) FROM business WHERE state = '" + state + "' AND city='" + city + "' GROUP BY 1 ORDER BY avg DESC;"
            try:
                results = self.executeQuery(sql_str)
                style = "::section {""background-color: #f3f3f3; }"
                self.ui.rec_zipcodeList.horizontalHeader().setStyleSheet(style)
                self.ui.rec_zipcodeList.setColumnCount(len(results[0]))
                self.ui.rec_zipcodeList.setRowCount(len(results))
                self.ui.rec_zipcodeList.setHorizontalHeaderLabels(
                    ['Zipcode', 'Avg. Rating'])
                self.ui.rec_zipcodeList.resizeColumnsToContents()
                self.ui.rec_zipcodeList.setColumnWidth(0, 50)
                self.ui.rec_zipcodeList.setColumnWidth(1, 30)
                currentRowCount = 0
                for row in results:
                    for colCount in range(0, len(results[0])):
                        self.ui.rec_zipcodeList.setItem(currentRowCount, colCount, QTableWidgetItem(str(row[colCount])))
                    currentRowCount += 1
            except:
                print("Rec_Zipcodes failed!")

    def zipcodeChanged(self):
        self.ui.categoryList_2.clear()
        self.ui.topCategories_2.clear()
        self.ui.numBus_2.clear()
        self.ui.businessTable_2.clear()
        self.ui.Attributelist.clear()
        if (len(self.ui.zipcodeList_2.selectedItems()) > 0):
            zipcode = self.ui.zipcodeList_2.selectedItems()[0].text()
            sql_str = "SELECT distinct category FROM business JOIN category on category.business_id = business.business_id WHERE postal_code = '" + \
                      zipcode + "' ORDER BY category ;"
            try:
                results = self.executeQuery(sql_str)
                for row in results:
                    self.ui.categoryList_2.addItem(row[0])
            except:
                print("cityChanged failed!")
            sql_str = "SELECT name, address, city, stars, numtips FROM business WHERE postal_code = '" + zipcode + "' ORDER BY name ;"
            try:
                results = self.executeQuery(sql_str)
                style = "::section {""background-color: #f3f3f3; }"
                self.ui.businessTable_2.horizontalHeader().setStyleSheet(style)
                self.ui.businessTable_2.setColumnCount(len(results[0]))
                self.ui.businessTable_2.setRowCount(len(results))
                #self.ui.businessTable_2.setText(results[3])
                #self.ui.businessTable_2.setText(results[4])

                self.ui.businessTable_2.setHorizontalHeaderLabels(['Business Name', 'Address', 'City', 'Stars', 'Number of Tips'])
                self.ui.businessTable_2.resizeColumnsToContents()
                self.ui.businessTable_2.setColumnWidth(0, 200)
                self.ui.businessTable_2.setColumnWidth(1, 200)
                self.ui.businessTable_2.setColumnWidth(2, 200)
                self.ui.businessTable_2.setColumnWidth(3, 100)
                self.ui.businessTable_2.setColumnWidth(4, 100)

                currentRowCount = 0
                for row in results:
                    for colCount in range(0, len(results[0])):
                        self.ui.businessTable_2.setItem(currentRowCount, colCount, QTableWidgetItem(str(row[colCount])))
                    currentRowCount += 1
            except:
                print("businessTable Population failed!")
            sql_str = "SELECT category, count(category) as numbus FROM category a join business on a.business_id = business.business_id WHERE postal_code = '" + zipcode + "' GROUP BY 1 ORDER BY numbus DESC;"
            try:
                results = self.executeQuery(sql_str)
                style = "::section {""background-color: #f3f3f3; }"
                self.ui.topCategories_2.horizontalHeader().setStyleSheet(style)
                self.ui.topCategories_2.setColumnCount(len(results[0]))
                self.ui.topCategories_2.setRowCount(len(results))


                self.ui.topCategories_2.setHorizontalHeaderLabels(
                    ['Category', '# of Business'])
                self.ui.topCategories_2.resizeColumnsToContents()

                self.ui.topCategories_2.setColumnWidth(0, 100)
                self.ui.topCategories_2.setColumnWidth(1, 50)
                currentRowCount = 0
                for row in results:
                    for colCount in range(0, len(results[0])):
                        self.ui.topCategories_2.setItem(currentRowCount, colCount, QTableWidgetItem(str(row[colCount])))
                    currentRowCount += 1

            except:
                print("statistics failed!")
            sql_str = "SELECT count(business_id) as numbusiness FROM business WHERE postal_code = '" + zipcode + "' GROUP BY postal_code;"
            try:
                results = self.executeQuery(sql_str)
                numBusinesses = str(results[0][0])
                self.ui.numBus_2.setText(numBusinesses)
            except:
                print("statistics 2 failed!")
            sql_str = "SELECT  attribute.name, COUNT(attribute.name) FROM attribute JOIN (SELECT business_id, stars FROM business WHERE stars >= 4.5 AND postal_code = '" + zipcode + "') a ON attribute.business_id = a.business_id GROUP BY 1 ORDER BY 2 DESC;"
            try:
                results = self.executeQuery(sql_str)
                style = "::section {""background-color: #f3f3f3; }"
                self.ui.Attributelist.horizontalHeader().setStyleSheet(style)
                self.ui.Attributelist.setColumnCount(len(results[0]))
                self.ui.Attributelist.setRowCount(len(results))


                self.ui.Attributelist.setHorizontalHeaderLabels(
                    ['Attribute', 'Count'])
                self.ui.Attributelist.resizeColumnsToContents()

                self.ui.Attributelist.setColumnWidth(0, 150)
                self.ui.Attributelist.setColumnWidth(1, 50)
                currentRowCount = 0
                for row in results:
                    for colCount in range(0, len(results[0])):
                        self.ui.Attributelist.setItem(currentRowCount, colCount, QTableWidgetItem(str(row[colCount])))
                    currentRowCount += 1
            except:
                print("statistics 3 failed!")
    def categoryChanged(self):
        self.ui.businessTable_2.clear()
        self.ui.Attributelist.clear()

        if (self.ui.stateList_2.currentIndex() >= 0) and (len(self.ui.cityList_2.selectedItems()) > 0) and \
                (len(self.ui.zipcodeList_2.selectedItems()) > 0) and (len(self.ui.categoryList_2.selectedItems()) > 0):
            zipcode = self.ui.zipcodeList_2.selectedItems()[0].text()
            category = self.ui.categoryList_2.selectedItems()[0].text()
            sql_str = "SELECT name, address, city, stars, numtips FROM business JOIN category on category.business_id = " \
                      "business.business_id WHERE postal_code = '" + zipcode + "' AND category = '" + category + "' ORDER BY name ;"
            try:
                results = self.executeQuery(sql_str)
                style = "::section {""background-color: #f3f3f3; }"
                self.ui.businessTable_2.horizontalHeader().setStyleSheet(style)
                self.ui.businessTable_2.setColumnCount(len(results[0]))
                self.ui.businessTable_2.setRowCount(len(results))

                #self.ui.businessTable_2.setText(results[3])
                #self.ui.businessTable_2.setText(results[4])
                self.ui.businessTable_2.setHorizontalHeaderLabels(['Business Name', 'Address', 'City', 'Stars', 'Number of Tips'])
                self.ui.businessTable_2.resizeColumnsToContents()

                self.ui.businessTable_2.setColumnWidth(0, 200)
                self.ui.businessTable_2.setColumnWidth(1, 200)
                self.ui.businessTable_2.setColumnWidth(2, 200)
                self.ui.businessTable_2.setColumnWidth(3, 100)
                self.ui.businessTable_2.setColumnWidth(4, 100)
                currentRowCount = 0
                for row in results:
                    for colCount in range(0, len(results[0])):
                        self.ui.businessTable_2.setItem(currentRowCount, colCount, QTableWidgetItem(str(row[colCount])))
                    currentRowCount += 1
            except:
                print("businessTable Population failed!")


            sql_str = "SELECT  attribute.name, COUNT(attribute.name) FROM category, attribute JOIN (SELECT business_id, stars FROM business WHERE stars >= 4.5 AND postal_code = '" + zipcode + "') a ON attribute.business_id = a.business_id WHERE category.business_id = attribute.business_id AND category = '" + category + "' GROUP BY 1 ORDER BY 2 DESC;"
            try:
                results = self.executeQuery(sql_str)
                style = "::section {""background-color: #f3f3f3; }"
                self.ui.Attributelist.horizontalHeader().setStyleSheet(style)
                self.ui.Attributelist.setColumnCount(len(results[0]))
                self.ui.Attributelist.setRowCount(len(results))


                self.ui.Attributelist.setHorizontalHeaderLabels(
                    ['Attribute', 'Count'])
                self.ui.Attributelist.resizeColumnsToContents()

                self.ui.Attributelist.setColumnWidth(0, 150)
                self.ui.Attributelist.setColumnWidth(1, 50)
                currentRowCount = 0
                for row in results:
                    for colCount in range(0, len(results[0])):
                        self.ui.Attributelist.setItem(currentRowCount, colCount, QTableWidgetItem(str(row[colCount])))
                    currentRowCount += 1
            except:
                print("statistics 4 failed!")

    def businessChanged(self, row, column):
        self.ui.categorylist.clear()
        self.ui.selectedattributelist.clear()

        print("Row %d and Column %d was clicked" % (row, column))
        business = self.ui.businessTable_2.item(row, column).text()
        print(type(business))


        #business = self.ui.businessTable_2.selectedItems()[0].text()
        sql_str = "SELECT category.category FROM category JOIN business ON category.business_id = business.business_id WHERE business.name = '" + business + "' ORDER BY name ;"
        try:
            results = self.executeQuery(sql_str)
            style = "::section {""background-color: #f3f3f3; }"
            for row in results:
                self.ui.categorylist.addItem(row[0])

        except:
            print("categorylist Population failed!")
        sql_str = "SELECT attribute.name FROM attribute JOIN business ON attribute.business_id = business.business_id WHERE business.name = '" + business + "' GROUP BY 1 ORDER BY name; "
        try:
            results = self.executeQuery(sql_str)
            style = "::section {""background-color: #f3f3f3; }"
            for row in results:
                self.ui.selectedattributelist.addItem(row[0])

        except:
            print("categorylist Population failed!")




    def useridChanged(self):
        self.ui.friendslist.clear()
        self.ui.friendsoflist.clear()
        self.ui.name.clear()
        self.ui.stars.clear()
        self.ui.yelpsince.clear()
        self.ui.funny.clear()
        self.ui.cool.clear()
        self.ui.useful.clear()
        self.ui.review.clear()
        if (len(self.ui.useridlist.selectedItems()) > 0):
            userid = self.ui.useridlist.selectedItems()[0].text()
            #print(userid)
            #rec_businesses = self.rec_model(userid)
            #print(rec_businesses)
            sql_str = "SELECT a.name, a.average_stars, a.fans, a.tipcount, a.yelping_since FROM usertable a, (SELECT friends.friend_user_id from friends, friends a WHERE a.user_id = friends.user_id AND friends.user_id = '" + userid + "') b WHERE a.user_id = b.friend_user_id GROUP BY 1,2,3,4,5;"
            try:
                results = self.executeQuery(sql_str)
                style = "::section {""background-color: #f3f3f3; }"
                self.ui.friendslist.horizontalHeader().setStyleSheet(style)
                self.ui.friendslist.setColumnCount(len(results[0]))
                self.ui.friendslist.setRowCount(len(results))

                # self.ui.businessTable_2.setText(results[3])
                # self.ui.businessTable_2.setText(results[4])
                self.ui.friendslist.setHorizontalHeaderLabels(
                    ['Name', 'Stars', 'Fans', 'Tipcount', 'YelpingSince'])
                self.ui.friendslist.resizeColumnsToContents()

                self.ui.friendslist.setColumnWidth(0, 100)
                self.ui.friendslist.setColumnWidth(1, 100)
                self.ui.friendslist.setColumnWidth(2, 50)
                self.ui.friendslist.setColumnWidth(3, 50)
                self.ui.friendslist.setColumnWidth(4, 50)
                currentRowCount = 0
                for row in results:
                    for colCount in range(0, len(results[0])):
                        self.ui.friendslist.setItem(currentRowCount, colCount, QTableWidgetItem(str(row[colCount])))
                    currentRowCount += 1
            except:
                print("friendstable Population failed!")

            sql_str = "SELECT name, average_stars,yelping_since, funny, cool, useful  FROM usertable where user_id = '" + userid + "' ORDER BY user_ID "
            try:
                results = self.executeQuery(sql_str)
                for row in results:
                    self.ui.name.addItem(str(row[0]))
                    self.ui.stars.addItem(str(row[1]))
                    self.ui.yelpsince.addItem(str(row[2]))
                    self.ui.funny.addItem(str(row[3]))
                    self.ui.cool.addItem(str(row[4]))
                    self.ui.useful.addItem(str(row[5]))

            except:
                print("stateChanged failed!")

            sql_str = "SELECT '1' as p, a.name, a.average_stars, a.fans, a.tipcount, a.yelping_since, a.user_id FROM usertable a, (SELECT friends.user_id, friends.friend_user_id as degree FROM friends JOIN (SELECT friends.friend_user_id f from friends, friends a WHERE a.user_id = friends.user_id AND friends.user_id = '" + userid + "'GROUP BY 1) c ON friends.user_id = c.f) de WHERE a.user_id = de.degree"

            try:
                results = self.executeQuery(sql_str)
                #print(results)
                style = "::section {""background-color: #f3f3f3; }"
                self.ui.friendsoflist.horizontalHeader().setStyleSheet(style)
                self.ui.friendsoflist.setColumnCount(len(results[0]))
                self.ui.friendsoflist.setRowCount(len(results))

                # self.ui.businessTable_2.setText(results[3])
                # self.ui.businessTable_2.setText(results[4])
                self.ui.friendsoflist.setHorizontalHeaderLabels(
                    ['Degree', 'Name', 'Stars', 'Fans', 'Tipcount', 'YelpingSince'])
                self.ui.friendslist.resizeColumnsToContents()

                self.ui.friendsoflist.setColumnWidth(0, 100)
                self.ui.friendsoflist.setColumnWidth(1, 100)
                self.ui.friendsoflist.setColumnWidth(2, 50)
                self.ui.friendsoflist.setColumnWidth(3, 50)
                self.ui.friendsoflist.setColumnWidth(4, 50)
                currentRowCount = 0
                currentRowCount2 = 0
                #print(results[0][6])
                for row in results:
                    for colCount in range(0, ((len(results[0]))-1)):
                        #print(row)
                        self.ui.friendsoflist.setItem(currentRowCount, colCount, QTableWidgetItem(str(row[colCount])))
                        #sql_str2 = "SELECT '2' as p, a.name, a.average_stars, a.fans, a.tipcount, a.yelping_since FROM usertable a, (SELECT friends.user_id, friends.friend_user_id as degree FROM friends JOIN (SELECT friends.friend_user_id f from friends, friends a WHERE a.user_id = friends.user_id AND friends.user_id = '" + row[6] + "'GROUP BY 1) c ON friends.user_id = c.f) de WHERE a.user_id = de.degree"
                        #results2 = self.executeQuery(sql_str2)
                        #for row2 in results2:
                        #    for colCount2 in range(0, ((len(results2[0]))-1)):
                                # print(row)
                        #        self.ui.friendsoflist.setItem(currentRowCount, colCount2,
                        #                                      QTableWidgetItem(str(row2[colCount2])))
                        #    currentRowCount += 1
                        #print(results2)
                    currentRowCount += 1
            except:
                print("degree failed")
            if (len(self.ui.useridlist.selectedItems()) > 0):

                    try:
                        sql_str = "SELECT usertable.name, business.name, business.city, latest.date, latest.text FROM usertable, business, (SELECT tip.business_id, tip.user_id, tip.date, tip.text FROM tip JOIN (SELECT user_id, MAX(date) as MaxDate FROM tip, (SELECT friends.friend_user_id from friends WHERE friends.user_id = '" + userid + "') fr WHERE fr.friend_user_id = tip.user_id GROUP BY 1) dat ON tip.date = dat.maxDate) latest WHERE business.business_id = latest.business_id AND usertable.user_id = latest.user_id"
                        results = self.executeQuery(sql_str)
                        style = "::section {""background-color: #f3f3f3; }"
                        self.ui.review.horizontalHeader().setStyleSheet(style)
                        self.ui.review.setColumnCount(len(results[0]))
                        self.ui.review.setRowCount(len(results))

                        # self.ui.businessTable_2.setText(results[3])
                        # self.ui.businessTable_2.setText(results[4])
                        self.ui.review.setHorizontalHeaderLabels(
                            ['Name', 'Business', 'City', 'Date', 'Review'])
                        self.ui.review.resizeColumnsToContents()

                        self.ui.review.setColumnWidth(0, 100)
                        self.ui.review.setColumnWidth(1, 100)
                        self.ui.review.setColumnWidth(2, 100)
                        self.ui.review.setColumnWidth(3, 100)
                        self.ui.review.setColumnWidth(4, 50)
                        currentRowCount = 0
                        for row in results:
                            for colCount in range(0, len(results[0])):
                                self.ui.review.setItem(currentRowCount, colCount, QTableWidgetItem(str(row[colCount])))
                            currentRowCount += 1
                    except:
                        print("review load failed")

    def useridchanged2(self):
        self.ui.recommendation.clear()
        if (len(self.ui.useridlist.selectedItems()) > 0):
            user_id = self.ui.useridlist.selectedItems()[0].text()
            sql_str = "SELECT '1' as p, a.name, a.average_stars, a.fans, a.tipcount, a.yelping_since FROM usertable a WHERE a.user_id = '" + user_id + "' ORDER BY 1"
            results = self.executeQuery(sql_str)
            #print(results)
            if (results[0][4] != 0):

                business_df = df[['businessID']]
                #print(business_df)
                business_visited_by_user = df[df.userID == user_id]
               # print(user_id)
                business_not_visisted = \
                    business_df[~business_df["businessID"].isin(business_visited_by_user.businessID.values)][
                        "businessID"]

                business_not_visisted = set(business_not_visisted).intersection(set(business2business_encoded.keys()))

                business_not_visisted = [[business2business_encoded.get(x)] for x in business_not_visisted]
                #print(business_not_visisted)
                user_encoder = user2user_encoded.get(user_id)
                user_busiuness_array = np.hstack(
                    ([[user_encoder]] * len(business_not_visisted), business_not_visisted)
                )
               # print(user_busiuness_array)

                ratings = model.predict(user_busiuness_array).flatten()
                top_ratings_indices = ratings.argsort()[-10:][::-1]
                recommended_business_ids = [
                    business_encoded2business.get(business_not_visisted[x][0]) for x in top_ratings_indices
                ]

                #print(recommended_business_ids)

                sql_str = "SELECT business.name FROM business WHERE business_id = '" + recommended_business_ids[
                    0] + "'           OR business_id = '" + recommended_business_ids[1] + "' OR business_id = '" + \
                          recommended_business_ids[2] + "' OR business_id = '" + recommended_business_ids[
                              3] + "' OR business_id = '" + recommended_business_ids[4] + "' OR business_id = '" + \
                          recommended_business_ids[5] + "' OR business_id = '" + recommended_business_ids[
                              6] + "' OR business_id = '" + recommended_business_ids[7] + "' OR business_id = '" + \
                          recommended_business_ids[8] + "'OR business_id = '" + recommended_business_ids[
                              9] + "' ORDER BY 1"
                try:
                    results = self.executeQuery(sql_str)
                    style = "::section {""background-color: #f3f3f3; }"
                    for row in results:
                        self.ui.recommendation.addItem(row[0])

                except:
                    print("recommendation failed")

    def check_login(self):
        self.ui.useridlist.clear()
        name = self.ui.login_user.toPlainText()
        self.ui.useridlist.clear()

        if (len(name) > 0):
            sql_str = "SELECT user_id FROM usertable where name = '" + name + "' ORDER BY user_ID "
            try:
                results = self.executeQuery(sql_str)
                style = "::section {""background-color: #f3f3f3; }"
                for row in results:
                    self.ui.useridlist.addItem(row[0])

            except:
                print("loaduseridliost failed!")


        try:
            results = self.executeQuery(sql_str)
        except:
            self.warning()



    '''def rec_model(self, input_id):
        list = []

        try:
            connection = psycopg2.connect(user="postgres",
                                          password="shadow99",
                                          host="localhost",
                                          port="5432",
                                          database="milestone2db")
            cursor = connection.cursor()
            postgreSQL_select_Query = "SELECT tip.user_id, business.business_id, business.stars, address FROM business, tip WHERE tip.business_id = business.business_id;"

            cursor.execute(postgreSQL_select_Query)
            print("Selecting rows from user and business table using cursor.fetchall")
            user_records = cursor.fetchall()

            print("Print each row and it's columns values")
            for row in user_records:
                list.append(row)
        except (Exception, psycopg2.Error) as error:
            print("Error while fetching data from PostgreSQL", error)

        finally:
            # closing database connection.
            if connection:
                cursor.close()
                connection.close()
                print("PostgreSQL connection is closed")
        df = pd.DataFrame(list)

        df = df.rename(columns={0: "userID", 1: "businessID", 2: "stars", 3: "address", 4: "totalieks"})
        #print(df)
        users_ids = df["userID"].unique().tolist()

        user2user_encoded = {x: i for i, x in enumerate(users_ids)}
        userencoded2user = {i: x for i, x in enumerate(users_ids)}
        business_ids = df["businessID"].unique().tolist()
        business2business_encoded = {x: i for i, x in enumerate(business_ids)}
        business_encoded2business = {i: x for i, x in enumerate(business_ids)}

        df["user"] = df["userID"].map(user2user_encoded)
        df["business"] = df["businessID"].map(business2business_encoded)
        num_users = len(user2user_encoded)
        num_business = len(business2business_encoded)

        x = df[["user", "business"]].values
        df["stars"] = df["stars"].values.astype(np.float32)

        min_rating = min(df["stars"])
        max_rating = max(df["stars"])

        #print(
        #    "Number of users: {}, Number of Business: {}, Min rating: {}, Max rating: {}".format(
        #        num_users, num_business, min_rating, max_rating
        #    )
        #)

        df = df.sample(frac=1, random_state=42)
        x = df[["user", "business"]].values
        # Normalize the targets between 0 and 1. Makes it easy to train.
        y = df["stars"].apply(lambda x: (x - min_rating) / (max_rating - min_rating)).values
        # Assuming training on 90% of the data and validating on 10%.
        train_indices = int(0.9 * df.shape[0])
        x_train, x_val, y_train, y_val = (
            x[:train_indices],
            x[train_indices:],
            y[:train_indices],
            y[train_indices:],
        )

        ###Create the model
        EMBEDDING_SIZE = 50

        class RecommenderNet(keras.Model):
            def __init__(self, num_users, num_business, embedding_size, **kwargs):
                super(RecommenderNet, self).__init__(**kwargs)
                self.num_users = num_users
                self.num_business = num_business
                self.embedding_size = embedding_size
                self.user_embedding = layers.Embedding(
                    num_users,
                    embedding_size,
                    embeddings_initializer="he_normal",
                    embeddings_regularizer=keras.regularizers.l2(1e-6),
                )
                self.user_bias = layers.Embedding(num_users, 1)
                self.num_business_embedding = layers.Embedding(
                    num_business,
                    embedding_size,
                    embeddings_initializer="he_normal",
                    embeddings_regularizer=keras.regularizers.l2(1e-6),
                )
                self.business_bias = layers.Embedding(num_business, 1)

            def call(self, inputs):
                user_vector = self.user_embedding(inputs[:, 0])
                user_bias = self.user_bias(inputs[:, 0])
                business_vector = self.num_business_embedding(inputs[:, 1])
                business_bias = self.business_bias(inputs[:, 1])
                dot_user_business = tf.tensordot(user_vector, business_vector, 2)
                # Add all the components (including bias)
                x = dot_user_business + user_bias + business_bias
                # The sigmoid activation forces the rating to between 0 and 1
                return tf.nn.sigmoid(x)

        model = tf.keras.models.load_model("neural_network")
        model = RecommenderNet(num_users, num_business, EMBEDDING_SIZE)
        model.compile(
            loss=tf.keras.losses.BinaryCrossentropy(), optimizer=keras.optimizers.Adam(lr=0.001)
        )

        business_df = df[['businessID']]
        business_df = df[['businessID']]
        #print(business_df)
        user_id = input_id

        business_visited_by_user = df[df.userID == user_id]
        #print(user_id)
        business_not_visisted = \
        business_df[~business_df["businessID"].isin(business_visited_by_user.businessID.values)]["businessID"]

        business_not_visisted = set(business_not_visisted).intersection(set(business2business_encoded.keys()))

        business_not_visisted = [[business2business_encoded.get(x)] for x in business_not_visisted]
        #print(business_not_visisted)
        user_encoder = user2user_encoded.get(user_id)
        user_busiuness_array = np.hstack(
            ([[user_encoder]] * len(business_not_visisted), business_not_visisted)
        )
        #print(user_busiuness_array)

        ratings = model.predict(user_busiuness_array).flatten()
        top_ratings_indices = ratings.argsort()[-10:][::-1]
        recommended_business_ids = [
            business_encoded2business.get(business_not_visisted[x][0]) for x in top_ratings_indices
        ]

        return recommended_business_ids'''
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = milestone2()
    window.show()
    sys.exit(app.exec_())