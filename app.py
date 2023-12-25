import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.figure_factory as ff
from Api.Processor.processor import preprocess
from Api.Helper import helper

sns.set(
    rc={
        "figure.facecolor": "black",
        "ytick.color": "white",
        "xtick.color": "white",
        "axes.facecolor": "black",
    }
)

df = pd.read_csv(r"E:\Olympics Analysis\Data\athlete_events.csv")
df_region = pd.read_csv(r"E:\Olympics Analysis\Data\noc_regions.csv")

df_m = preprocess(df, df_region)

st.sidebar.title("Olympics Analysis")
# st.sidebar.image(
#     "https://e7.pngegg.com/pngimages/1020/402/png-clipart-2024-summer-olympics-brand-circle-area-olympic-rings-olympics-logo-text-sport.png"
# )
user_menu = st.sidebar.radio(
    "Select an Option",
    (
        "Medal Tally 🥇 ",
        "Overall Analysis 📈",
        "Country-wise Analysis 🎌",
        "Athlete wise Analysis 🤾‍♂️🤾‍♀️",
    ),
)


if user_menu == "Medal Tally 🥇 ":
    st.sidebar.header("Medal Tally")
    year, country = helper.country_year_list(df_m)
    selected_year = st.sidebar.selectbox("Select Year", year)
    selected_country = st.sidebar.selectbox("Select Country", country)
    medal_tally = helper.fetch_medal_tally(df_m, selected_year, selected_country)

    if selected_year == "Overall" and selected_country == "Overall":
        st.title("Overall Tally")
    if selected_year != "Overall" and selected_country == "Overall":
        st.title("Medal Tally in " + str(selected_year) + " Olympics")
    if selected_year == "Overall" and selected_country != "Overall":
        st.title(selected_country + " overall performance")
    if selected_year != "Overall" and selected_country != "Overall":
        st.title(
            selected_country + " performance in " + str(selected_year) + " Olympics"
        )
    st.table(medal_tally)


if user_menu == "Overall Analysis 📈":
    editions = df_m["Year"].unique().shape[0] - 1
    cities = df_m["City"].unique().shape[0]
    sports = df_m["Sport"].unique().shape[0]
    events = df_m["Event"].unique().shape[0]
    athletes = df_m["Name"].unique().shape[0]
    nations = df_m["region"].unique().shape[0]

    st.title("Main Statistic")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.header("Editions")
        st.title(editions)
    with col2:
        st.header("Cities")
        st.title(cities)
    with col3:
        st.header("Sport")
        st.title(sports)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.header("Events")
        st.title(events)
    with col2:
        st.header("Athletes")
        st.title(athletes)
    with col3:
        st.header("Nations")
        st.title(nations)

    nations_data = helper.participating_nations_over_time(df_m, "region")
    fig = px.line(
        nations_data, x=nations_data.Year, y=nations_data["Number of Countries"]
    )
    st.title("Participating users over the years")
    st.plotly_chart(figure_or_data=fig)
    events_data = helper.participating_nations_over_time(df_m, "Event")
    fig = px.line(events_data, x=events_data.Year, y=events_data["Number of Countries"])
    st.title("Events over the years")
    st.plotly_chart(figure_or_data=fig)
    athlete_data = helper.participating_nations_over_time(df_m, "Name")
    fig = px.line(
        athlete_data, x=athlete_data.Year, y=athlete_data["Number of Countries"]
    )
    st.title("Athlete participation over the years")
    st.plotly_chart(figure_or_data=fig)

    st.title("No. of Events over time(Every Sport)")
    fig, ax = plt.subplots(figsize=(20, 20))
    heat = helper.heatmap_maker(df_m)
    sns.heatmap(heat, annot=True, cmap="rocket", ax=ax, annot_kws={"fontsize": 12})
    st.pyplot(fig)

    value = st.slider("Select the top-k athletes", 0, 100)
    sp_unique = df_m.Sport.unique().tolist()
    sp_unique.insert(0, "Overall")
    # print(sp_unique)
    sport = st.selectbox("Select a sport", tuple(sp_unique))
    successful = helper.most_successful(df_m, sport, int(value))
    st.table(successful)

if user_menu == "Country-wise Analysis 🎌":
    _, country = helper.country_year_list(df_m)
    country.remove("Overall")
    selected = st.selectbox("Select a Country", country)
    d = helper.country_wise_tally(df_m, selected)
    if isinstance(d, int):
        st.header(f"No games won by {selected}")
    else:
        fig, ax = plt.subplots(figsize=(20, 10))
        data = px.bar(x=d.Year, y=d.Medal, data_frame=d)
        st.header(f"Games won by {selected}")
        st.plotly_chart(data)
    fig, ax = plt.subplots(figsize=(20, 10))
    sns.heatmap(
        helper.country_heatmap_per_sport(df_m, selected),
        annot=True,
        cmap="rocket",
        ax=ax,
        annot_kws={"fontsize": 12},
    )
    st.header(f"Heatmap Distribution of games won by {selected}")
    st.pyplot(fig)

    st.header(f"Table Distribution of games won by {selected}")
    value = st.slider("Select the top-k athletes", 0, 100)
    sp_unique = df_m.Sport.unique().tolist()
    sp_unique.insert(0, "Overall")
    sport = st.selectbox("Select a sport", tuple(sp_unique))
    successful = helper.most_successful_country(df_m, sport, int(value), selected)
    st.table(successful)

if user_menu == "Athlete wise Analysis 🤾‍♂️🤾‍♀️":
    athlete_df = df_m.drop_duplicates(subset=["Name", "region"])

    x1 = athlete_df["Age"].dropna()
    x2 = athlete_df[athlete_df["Medal"] == "Gold"]["Age"].dropna()
    x3 = athlete_df[athlete_df["Medal"] == "Silver"]["Age"].dropna()
    x4 = athlete_df[athlete_df["Medal"] == "Bronze"]["Age"].dropna()

    fig = ff.create_distplot(
        [x1, x2, x3, x4],
        ["Overall Age", "Gold Medalist", "Silver Medalist", "Bronze Medalist"],
        show_hist=False,
        show_rug=False,
    )
    fig.update_layout(autosize=False, width=1000, height=600)
    st.title("Distribution of Age")
    st.plotly_chart(fig)

    x = []
    name = []
    famous_sports = [
        "Basketball",
        "Judo",
        "Football",
        "Tug-Of-War",
        "Athletics",
        "Swimming",
        "Badminton",
        "Sailing",
        "Gymnastics",
        "Art Competitions",
        "Handball",
        "Weightlifting",
        "Wrestling",
        "Water Polo",
        "Hockey",
        "Rowing",
        "Fencing",
        "Shooting",
        "Boxing",
        "Taekwondo",
        "Cycling",
        "Diving",
        "Canoeing",
        "Tennis",
        "Golf",
        "Softball",
        "Archery",
        "Volleyball",
        "Synchronized Swimming",
        "Table Tennis",
        "Baseball",
        "Rhythmic Gymnastics",
        "Rugby Sevens",
        "Beach Volleyball",
        "Triathlon",
        "Rugby",
        "Polo",
        "Ice Hockey",
    ]
    for sport in famous_sports:
        temp_df = athlete_df[athlete_df["Sport"] == sport]
        x.append(temp_df[temp_df["Medal"] == "Gold"]["Age"].dropna())
        name.append(sport)

    fig = ff.create_distplot(x, name, show_hist=False, show_rug=False)
    fig.update_layout(autosize=False, width=1000, height=600)
    st.title("Distribution of Age wrt Sports(Gold Medalist)")
    st.plotly_chart(fig)

    sport_list = df["Sport"].unique().tolist()
    sport_list.sort()
    sport_list.insert(0, "Overall")

    st.title("Height Vs Weight")
    selected_sport = st.selectbox("Select a Sport", sport_list)
    temp_df = helper.weight_v_height(df_m, selected_sport)
    fig, ax = plt.subplots()
    fig = px.scatter(
        x=temp_df["Weight"],
        y=temp_df["Height"],
        color=temp_df["Medal"],
        symbol=temp_df["Sex"],
        height=700,
        width=1000,
        data_frame=temp_df,
    )
    fig.update_traces(
        marker=dict(
            size=12,
            line=dict(width=2, color="DarkSlateGrey"),
        ),
        selector=dict(mode="markers"),
    )
    st.plotly_chart(fig)

    st.title("Men Vs Women Participation Over the Years")
    final = helper.men_vs_women(df_m)
    fig = px.line(final, x="Year", y=["Male", "Female"])
    fig.update_layout(autosize=False, width=1000, height=600)
    st.plotly_chart(fig)
