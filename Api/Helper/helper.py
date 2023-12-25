import pandas as pd
import numpy as np


def medal_tally(df: pd.DataFrame) -> pd.DataFrame:
    """
    Medal Tally maker
    Keyword arguments:df : pd.DataFrame
    argument -- A dataframe
    Return: A medal based Dataframe
    """

    medal_tally = df.drop_duplicates(
        subset=["Team", "NOC", "Games", "Year", "City", "Event", "Medal", "Season"]
    )
    medal_main = (
        medal_tally.groupby("region")
        .sum()[["Gold", "Silver", "Bronze"]]
        .sort_values("Gold", ascending=False)
        .reset_index()
    )
    medal_main["Total"] = medal_main.Gold + medal_main.Silver + medal_main.Bronze

    return medal_main


def country_year_list(df):
    years = df["Year"].unique().tolist()
    years.sort()
    years.insert(0, "Overall")

    country = np.unique(df.region.dropna().values).tolist()
    country.sort()
    country.insert(0, "Overall")
    return years, country


def fetch_medal_tally(df, year, country):
    medal_df = df.drop_duplicates(
        subset=["Team", "NOC", "Games", "Year", "City", "Sport", "Event", "Medal"]
    )
    flag = 0
    if year == "Overall" and country == "Overall":
        temp_df = medal_df
    if year == "Overall" and country != "Overall":
        flag = 1
        temp_df = medal_df[medal_df["region"] == country]
    if year != "Overall" and country == "Overall":
        temp_df = medal_df[medal_df["Year"] == int(year)]
    if year != "Overall" and country != "Overall":
        temp_df = medal_df[(medal_df["Year"] == year) & (medal_df["region"] == country)]

    if flag == 1:
        x = (
            temp_df.groupby("Year")
            .sum()[["Gold", "Silver", "Bronze"]]
            .sort_values("Year")
            .reset_index()
        )
    else:
        x = (
            temp_df.groupby("region")
            .sum()[["Gold", "Silver", "Bronze"]]
            .sort_values("Gold", ascending=False)
            .reset_index()
        )

    x["total"] = x["Gold"] + x["Silver"] + x["Bronze"]

    x["Gold"] = x["Gold"].astype("int")
    x["Silver"] = x["Silver"].astype("int")
    x["Bronze"] = x["Bronze"].astype("int")
    x["total"] = x["total"].astype("int")

    return x


def participating_nations_over_time(df, col):
    nations_over_time = (
        df.drop_duplicates(["Year", col])
        .Year.value_counts()
        .reset_index()
        .sort_values("Year")
    )
    return nations_over_time.rename(columns={"count": "Number of Countries"})


def heatmap_maker(df):
    temp = df.drop_duplicates(["Year", "Sport", "Event"])
    return temp.pivot_table(
        index="Sport", columns="Year", values="Event", aggfunc="count"
    ).fillna(0)


def most_successful(df, sport, top_x):
    temp = df.dropna(subset=["Medal"])

    if sport != "Overall":
        temp = temp[temp.Sport == sport]

    return (
        temp.Name.value_counts()
        .reset_index()
        .head(top_x)
        .merge(df.dropna(subset=["Medal"]), on="Name")
        .drop_duplicates(["Name"])
    )[["Name", "count", "Team", "Sport"]].set_index("Name")


def country_wise_tally(df, country):
    temp_df = df.dropna(subset=["Medal"])
    temp_df = temp_df.drop_duplicates(
        subset=["Team", "NOC", "Games", "Year", "City", "Sport", "Event", "Medal"]
    )

    d = (
        temp_df[temp_df.region == str(country)]
        .groupby("Year")
        .count()
        .Medal.reset_index()
    )
    if d.Medal.sum() == 0:
        return 0
    else:
        return d


def country_heatmap_per_sport(df, country):
    temp = df.drop_duplicates(["Year", "Sport", "Event"])
    return (
        temp[temp.region == country]
        .pivot_table(index="Sport", columns="Year", values="Event", aggfunc="count")
        .fillna(0)
    )


def most_successful_country(df, sport, top_x, country):
    temp = df.dropna(subset=["Medal"])

    if sport != "Overall":
        temp = temp[temp.Sport == sport]

    return (
        temp[temp.region == country]
        .Name.value_counts()
        .reset_index()
        .head(top_x)
        .merge(df.dropna(subset=["Medal"]), on="Name")
        .drop_duplicates(["Name"])[["Name", "count", "Team", "Sport"]]
        .set_index("Name")
        .rename(columns={"count": "Medals"})
    )


def weight_v_height(df, sport):
    athlete_df = df.drop_duplicates(subset=["Name", "region"])
    athlete_df["Medal"].fillna("No Medal", inplace=True)
    if sport != "Overall":
        temp_df = athlete_df[athlete_df["Sport"] == sport]
        return temp_df
    else:
        return athlete_df


def men_vs_women(df):
    athlete_df = df.drop_duplicates(subset=["Name", "region"])

    men = (
        athlete_df[athlete_df["Sex"] == "M"]
        .groupby("Year")
        .count()["Name"]
        .reset_index()
    )
    women = (
        athlete_df[athlete_df["Sex"] == "F"]
        .groupby("Year")
        .count()["Name"]
        .reset_index()
    )

    final = men.merge(women, on="Year", how="left")
    final.rename(columns={"Name_x": "Male", "Name_y": "Female"}, inplace=True)

    final.fillna(0, inplace=True)

    return final
