from flask import Flask
from flask import render_template
import pandas as pd
import tensorflow as tf
import numpy as np
from tensorflow import keras
from tensorflow.keras import layers

import psycopg2
print('TensorFlow version: %s' % tf.__version__)
print('Keras version: %s' % tf.keras.__version__)

list =[]

try:
    connection = psycopg2.connect(user="postgres",
                                  password="0115",
                                  host="localhost",
                                  port="5432",
                                  database="project")
    cursor = connection.cursor()
    postgreSQL_select_Query = "SELECT tip.user_id, business.business_id, business.stars FROM business, tip WHERE tip.business_id = business.business_id;"

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

df = df.rename(columns={0:"userID",1:"businessID",2:"stars",3:"address",4:"totalieks"})

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

print(
    "Number of users: {}, Number of Business: {}, Min rating: {}, Max rating: {}".format(
        num_users, num_business, min_rating, max_rating
    )
)

df = df.sample(frac=1, random_state=42)
x = df[["user", "business"]].values

y = df["stars"].apply(lambda x: (x - min_rating) / (max_rating - min_rating)).values

train_indices = int(0.9 * df.shape[0])


x_train, x_val, y_train, y_val = (
    x[:train_indices],
    x[train_indices:],
    y[:train_indices],
    y[train_indices:],
)

###Create the model
EMBEDDING_SIZE = 500


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
        # The sigmoid activation forces the rating to between 1 and 5
        return tf.nn.sigmoid(x)


model = RecommenderNet(num_users, num_business, EMBEDDING_SIZE)
model.compile(
    loss=tf.keras.losses.BinaryCrossentropy(), optimizer=keras.optimizers.Adam(lr=0.001)
)

model = model.fit(
    x=x_train,
    y=y_train,
    batch_size=64,
    epochs=5,
    verbose=1,
    validation_data=(x_val, y_val),
)

model.save("neural_network4")


