import pandas as pd
import streamlit
import streamlit as st
import random
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import time
import numpy as np
# nltk.download('punkt')
# nltk.download('stopwords')
import base64

def add_bg_from_local(image_file):
    """
    design
    :param image_file: backround
    :return:
    """
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url(data:image/{"jpeg"};base64,{encoded_string.decode()});
        background-size: cover
    }}
    </style>
    """,
    unsafe_allow_html=True
    )
add_bg_from_local('food5.jpg')

def cosine_similarity(X, Y):
    """
    get two summary for two recipes, return their cosine similarity
    based on their tockenizer representaion
    :param X: recipe 1 summary
    :param Y: recipe 1 summary
    :return: cosine similarity
    """
    # tokenization
    X_list = word_tokenize(X)
    Y_list = word_tokenize(Y)
    sw = stopwords.words('english')
    l1 = []
    l2 = []

    X_set = {w for w in X_list if not w in sw}
    Y_set = {w for w in Y_list if not w in sw}

    rvector = X_set.union(Y_set)
    for w in rvector:
        if w in X_set:
            l1.append(1)
        else:
            l1.append(0)
        if w in Y_set:
            l2.append(1)
        else:
            l2.append(0)
    c = 0
    for i in range(len(rvector)):
        c += l1[i] * l2[i]
    cosine = c / float((sum(l1) * sum(l2)) ** 0.5)
    return cosine


def find_best_neigb(data_filter, org):
    """
    given filtered data and previous suggested recipe, the function search for the closest
    recipe using the function for cosine similarity
    :param data_filter: data based on accumulated preferences
    :param org: previous recipe suggestion
    :return: index of the nest suggestion
    """
    best_score = 0
    best_neigb = 1
    if len(data_filter) != 0:
        data = data_filter.reset_index(drop=True)
        for i, row in data.iterrows():
            score = cosine_similarity(org, data.iloc[i]['summary'])
            # temp = data.iloc[i]['summary']
            if score >= best_score:
                best_score = score
                best_neigb = i
    else:
        return -1

    return best_neigb


data = pd.read_csv('final_data.csv') # data after preprocces


# def show_full_screen(inx):
#     st.session_state.summery = filtered.iloc[inx]['summary']
#     st.session_state.link = filtered.iloc[inx]['link']
#     st.session_state.image = filtered.iloc[inx]['image']
#     st.write(str(st.session_state.summery))
#     st.image(str(st.session_state.image), width=400, )

# opening
st.write("""
# The Perfect Recipe Just For You
*Welcome! our system can suggest you the most fit recipe, according your health prefrences and needs*
""")
# choosing cuisine
cuisine = st.radio("What cuisine would you like to cook today?",
    ('', 'Italian', 'Indian', 'Mediterranean', 'American', 'Asian', 'Dessert'))
if cuisine == '':
    time.sleep(3)
else:
    cuisine = cuisine.lower()

if "curr_data" not in st.session_state:
    st.session_state.curr_data = data
if "inx" not in st.session_state:
    st.session_state.inx = random.randint(0, len(st.session_state.curr_data) - 1)

filtered = st.session_state.curr_data
inx = st.session_state.inx

# initialize the session state
if "kitchen" not in st.session_state:
    st.session_state.kitchen = filtered.iloc[inx]['kitchen']
if "summery" not in st.session_state:
    st.session_state.summery = filtered.iloc[inx]['summary']
if "link" not in st.session_state:
    st.session_state.link = filtered.iloc[inx]['link']
if "image" not in st.session_state:
    st.session_state.image = filtered.iloc[inx]['image']
if "favorite" not in st.session_state:
    st.session_state.favorite = False
if "feature" not in st.session_state:
    st.session_state.feature = 'Your selection:'
if "feature_new" not in st.session_state:
    st.session_state.feature_new = ''
if "this" not in st.session_state:
    st.session_state.this = 0
if "other" not in st.session_state:
    st.session_state.other = 0
if "feedback" not in st.session_state:
    st.session_state.feedback = 0
if "feature_selected" not in st.session_state:
    st.session_state.feature_selected = 0

# filtering data according to cuisine, show suggestion
if cuisine != st.session_state.kitchen:
    st.session_state.kitchen = cuisine
    try:
        st.session_state.curr_data = data[data['kitchen'] == cuisine].reset_index()
        filtered = st.session_state.curr_data
        st.session_state.inx = random.randint(0, len(filtered) - 1)
        inx = st.session_state.inx
    except:
#        st.info("Please refresh the page")
        st.stop()


    st.session_state.summery = filtered.iloc[inx]['summary']
    st.session_state.link = filtered.iloc[inx]['link']
    st.session_state.image = filtered.iloc[inx]['image']
    st.write(str(st.session_state.summery))
    st.image(str(st.session_state.image), width=200, )
    st.info("If ypu want to add some feature, Please press the *Give me another recipe* botton.")
    yes_bot = st.button('I want this recipe', key='this')
    no_bot = st.button('Give me another recipe', key='other')

# flow if recipe chosen
if st.session_state.this:
    st.write(str(st.session_state.summery))
    st.image(str(st.session_state.image), width=200, )
    st.write("Here You can find the recipe:")
    st.write(st.session_state.link)
    st.write("Have a great meal!")


    favor = st.button('Add this recipe to my favorites', key='favorite')
    if favor:
        st.session_state.favorite = True

    st.session_state.feature_selected = False


    text_input = st.text_input("If you want, you can write here for as how your experience was",)
    st.write("After pressing 'enter' we will start the process again" )
    st.info("To start again, refresh the page")
# flow if recipe added to favorites
if st.session_state.favorite:
    st.write(str(st.session_state.summery))
    st.image(str(st.session_state.image), width=200, )
    st.write("Here You can find the recipe:")
    st.write(st.session_state.link)
    st.success("Successfully added! Have a great meal!")
    text_input = st.text_input("If you want, you can write here for as how your experience was", )
    st.write("After pressing 'enter' we will start the process again")
    st.info("To start again, refresh the page")

# flow if a recipe declined
if st.session_state.other or st.session_state.feature_selected:
    feature = st.selectbox(
        "What would you change?",
        ('Your selection:',
         'Dairy Free',
         'Slow Cooker Recipes',
         'Keto Recipes',
         'Vegetarian Meals',
         'Gluten Free',
         'Meal Prep Recipes',
         'Air Fryer',
         'Paleo',
         'Kid Friendly',
         'Pressure Cooker Recipes',
         'Whole 30 Recipes',
         'Under 30 Minutes',
         'Low Carb',
         'Freezer Meals',
         'Same as before'))

    # when choosing new added feature
    if feature != st.session_state.feature:

        st.session_state.feature_new = feature
        st.session_state.feature = st.session_state.feature_new

        filtered = st.session_state.curr_data
        filtered = filtered.drop(index=st.session_state.inx)
        if feature == 'Same as before':
            st.session_state.curr_data = filtered
        else:
            st.session_state.curr_data = filtered[filtered[st.session_state.feature] == 1].reset_index(drop=True)
        filtered = st.session_state.curr_data

        st.session_state.inx = find_best_neigb(st.session_state.curr_data, st.session_state.summery)
        inx = st.session_state.inx

        # if there is no possible index for recipe the satisfy all requirements
        if inx == -1:
            st.warning('Sorry, we run off all recipes on this combination of preferences.')
            st.info("To start again, refresh the page")

        # when the system finds new recipe fits the requirements
        else:
            st.write('# How about this great recipe?')
            st.session_state.summery = filtered.iloc[inx]['summary']
            st.session_state.link = filtered.iloc[inx]['link']
            st.session_state.image = filtered.iloc[inx]['image']
            st.write(str(st.session_state.summery))
            st.image(str(st.session_state.image), width=200, )
            st.write(""" *The system gave you the closest recipe to previous suggestion based on your preferences* """)
            yes_bot = st.button('I want this recipe', key='this')
            no_bot = st.button('Give me another recipe', key='other')

    else:
        st.session_state.feature_selected = True



