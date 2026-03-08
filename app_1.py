import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, datetime, timedelta

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2.service_account import Credentials

st.markdown("""
# 🚀 Life Tracker OS
A personal analytics system to track **health, productivity, career and growth**.
""")

# -----------------------------
# Load CSV files
# -----------------------------
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)

client = gspread.authorize(creds)

sheet = client.open("life_tracker_os")

daily_sheet = sheet.worksheet("daily_log")
linkedin_sheet = sheet.worksheet("linkedin")
freelance_sheet = sheet.worksheet("freelance")

@st.cache_data(ttl=60)
def load_data():
    daily = pd.DataFrame(daily_sheet.get_all_records())
    linkedin = pd.DataFrame(linkedin_sheet.get_all_records())
    freelance = pd.DataFrame(freelance_sheet.get_all_records())
    return daily, linkedin, freelance

daily, linkedin, freelance = load_data()

# Handle empty sheets (avoid errors)
if daily.empty:
    daily = pd.DataFrame(columns=[
        "date","steps","sleep","exercise","healthy_meal","dsa",
        "focus_hours","ml_hours","freelance_hours",
        "project_hours","academic_hours","class_hours"
    ])

if linkedin.empty:
    linkedin = pd.DataFrame(columns=["date","followers","posts"])

if freelance.empty:
    freelance = pd.DataFrame(columns=[
        "date","portfolio_project_hours",
        "portfolio_projects_done","portfolio_website_progress"
    ])

# -----------------------------
# Sidebar Navigation
# -----------------------------

st.sidebar.markdown("## 🧭 Navigation")

page = st.sidebar.radio(
    "",
    [
        "📊 Dashboard",
        "📝 Daily Log",
        "❤️ Health",
        "⏱ Time Analytics",
        "📈 Career",
        "🌐 LinkedIn",
        "💻 Freelancing"
    ]
)

st.sidebar.divider()

# Dynamic descriptions
if page == "📊 Dashboard":
    st.sidebar.info("""
Overview of your entire system.

Includes:
• Today's productivity snapshot  
• Year progress  
• DSA progress  
• LinkedIn growth  
• Key metrics  
• Freelancing progress  
• Productivity heatmap
""")

elif page == "📝 Daily Log":
    st.sidebar.info("""
Log daily activities.

Track:
• Steps
• Sleep
• Exercise
• DSA
• Focus hours
• ML work
• Projects
• Classes

This powers all analytics.
""")

elif page == "❤️ Health":
    st.sidebar.info("""
Visualize health habits.

Includes:
• Steps trend
• Sleep trend
• Exercise consistency
""")

elif page == "⏱ Time Analytics":
    st.sidebar.info("""
Understand where your time goes.

Shows breakdown of hours spent on:
• ML
• Freelancing
• Projects
• Academics
• Classes
""")

elif page == "📈 Career":
    st.sidebar.info("""
Track career progress.

Includes:
• Total DSA solved
• Focus hours trend
• ML work trend
""")

elif page == "🌐 LinkedIn":
    st.sidebar.info("""
Track LinkedIn growth.

Log followers and posts to monitor
progress toward your growth goal.
""")

elif page == "💻 Freelancing":
    st.sidebar.info("""
Track freelance preparation.

Includes:
• Portfolio projects completed
• Website development progress
""")

# =============================
# DAILY LOG
# =============================

if page == "📝 Daily Log":

    st.markdown("### 📝 Daily Log")

    st.info("Log your daily activity. This data powers the dashboard.")

    col1,col2,col3 = st.columns(3)

    with col1:
        steps = st.number_input("Steps",0,50000,8000)
        sleep = st.number_input("Sleep (hours)",0.0,12.0,7.0)

    with col2:
        exercise = st.checkbox("Exercise")
        healthy_meal = st.checkbox("Healthy Meal")

    with col3:
        dsa = st.checkbox("DSA Problem Solved")
        focus_hours = st.number_input("Focus Hours",0.0,12.0,3.0)

    ml_hours = st.number_input("ML Hours",0.0,12.0,0.0)
    freelance_hours = st.number_input("Freelance Work Hours",0.0,12.0,0.0)
    project_hours = st.number_input("MLIP / ChemE Cube Hours",0.0,12.0,0.0)
    academic_hours = st.number_input("Self Study / Academics",0.0,12.0,0.0)
    class_hours = st.number_input("Class Hours",0.0,12.0,0.0)

    if st.button("Save Entry"):

        daily_sheet.append_row([
            str(date.today()),
            steps,
            sleep,
            int(exercise),
            int(healthy_meal),
            int(dsa),
            focus_hours,
            ml_hours,
            freelance_hours,
            project_hours,
            academic_hours,
            class_hours
        ])

        st.success("Entry saved!")
        st.cache_data.clear()
        st.rerun()

# =============================
# DASHBOARD
# =============================

if page == "📊 Dashboard":

    st.markdown("## Overview")

# -----------------------------
# Today Snapshot
# -----------------------------

    st.markdown("### Today Snapshot")

    if not daily.empty:

        latest = daily.iloc[-1]

        col1,col2,col3,col4 = st.columns(4)

        col1.metric("Focus Hours", latest["focus_hours"], delta="today")
        col2.metric("Steps", latest["steps"])
        col3.metric("Sleep", latest["sleep"])
        col4.metric("DSA Done", "Yes" if latest["dsa"]==1 else "No")

    st.divider()

# -----------------------------
# Progress Tracker
# -----------------------------

    st.markdown("### Progress Tracker")

    col1,col2,col3 = st.columns(3)

    today = datetime.now()
    start_year = datetime(today.year,1,1)
    end_year = datetime(today.year,12,31)

    year_progress = (today-start_year).days/(end_year-start_year).days

    with col1:
        st.write("Year Progress")
        st.progress(year_progress)
        st.caption(f"{today.timetuple().tm_yday}/365 days")

    DSA_TARGET = 454
    DSA_INITIAL = 239

    dsa_done = DSA_INITIAL + (int(daily["dsa"].sum()) if not daily.empty else 0)

    with col2:
        st.write("DSA Sheet Progress")
        st.progress(min(dsa_done/DSA_TARGET,1))
        st.caption(f"{dsa_done}/{DSA_TARGET}")

    LINKEDIN_TARGET = 2000

    followers = (
        int(linkedin["followers"].iloc[-1])
        if not linkedin.empty else 1263
    )

    with col3:
        st.write("LinkedIn Growth")
        st.progress(min(followers/LINKEDIN_TARGET,1))
        st.caption(f"{followers}/{LINKEDIN_TARGET}")

    st.divider()

# -----------------------------
# Key Metrics
# -----------------------------

    st.markdown("### Key Metrics")

    if not daily.empty:

        col1,col2,col3,col4 = st.columns(4)

        col1.metric("Total Focus Hours", round(daily["focus_hours"].sum(),1))
        col2.metric("DSA Logged", int(daily["dsa"].sum()))
        col3.metric("Exercise Days", int(daily["exercise"].sum()))
        col4.metric("Average Sleep", round(daily["sleep"].mean(),1))

        weekly_focus = daily[
        pd.to_datetime(daily["date"]) >= datetime.now() - timedelta(days=7)
        ]["focus_hours"].sum()

        st.metric("Focus Hours (Last 7 Days)", round(weekly_focus,1))
    st.divider()

# -----------------------------
# Freelancing Progress
# -----------------------------

    st.markdown("### Freelancing Progress")

    if not freelance.empty:

        total_projects = int(freelance["portfolio_projects_done"].max())
        website_sessions = int(freelance["portfolio_website_progress"].sum())

        col1,col2 = st.columns(2)

        col1.metric("Portfolio Projects Completed", total_projects)
        col2.metric("Website Progress Sessions", website_sessions)

    st.divider()

# -----------------------------
# LinkedIn Growth Chart
# -----------------------------

    st.markdown("### LinkedIn Growth")

    if not linkedin.empty:

        fig = px.line(linkedin,x="date",y="followers")
        st.plotly_chart(fig,use_container_width=True)

    st.divider()

# -----------------------------
# Productivity Heatmap
# -----------------------------

    st.markdown("### 🔥 Yearly Productivity Heatmap")

    if not daily.empty:

        df_heat = daily.copy()
        df_heat["date"] = pd.to_datetime(df_heat["date"])

        year = datetime.now().year
        start = pd.Timestamp(f"{year}-01-01")
        end = pd.Timestamp(f"{year}-12-31")

        full_range = pd.DataFrame({"date":pd.date_range(start,end)})

        df_heat = full_range.merge(df_heat,on="date",how="left")
        df_heat["focus_hours"] = df_heat["focus_hours"].fillna(0)

        df_heat["week"] = df_heat["date"].dt.isocalendar().week
        df_heat["weekday"] = df_heat["date"].dt.weekday

        heatmap = df_heat.pivot(
            index="weekday",
            columns="week",
            values="focus_hours"
        )

        fig = px.imshow(
            heatmap,
            color_continuous_scale="greens",
            aspect="auto",
            labels=dict(
                x="Week of Year",
                y="Day",
                color="Focus Hours"
            )
        )

        fig.update_traces(
            hovertemplate=
            "<b>Day:</b> %{y}<br>" +
            "<b>Week:</b> %{x}<br>" +
            "<b>Focus Hours:</b> %{z}<extra></extra>"
        )
 
        fig.update_yaxes(
            tickvals=[0,1,2,3,4,5,6],
            ticktext=["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
        )

        st.plotly_chart(fig,use_container_width=True)

# =============================
# HEALTH PAGE
# =============================

if page == "❤️ Health":

    st.markdown("### ❤️ Health Trends")

    if not daily.empty:

        fig = px.line(daily,x="date",y="steps")
        st.plotly_chart(fig)

        fig = px.line(daily,x="date",y="sleep")
        st.plotly_chart(fig)

        exercise_rate = daily["exercise"].mean()*100
        st.metric("Exercise Consistency",f"{exercise_rate:.1f}%")

# =============================
# TIME ANALYTICS
# =============================

if page == "⏱ Time Analytics":

    st.markdown("### ⏱ Where Your Time Went (Last 7 Days)")

    if not daily.empty:

        df = daily.copy()
        df["date"] = pd.to_datetime(df["date"])

        last_week = df[df["date"] >= df["date"].max()-timedelta(days=7)]

        totals = {
            "ML":last_week["ml_hours"].sum(),
            "Freelance":last_week["freelance_hours"].sum(),
            "Projects":last_week["project_hours"].sum(),
            "Academics":last_week["academic_hours"].sum(),
            "Classes":last_week["class_hours"].sum()
        }

        df = pd.DataFrame({"Activity":totals.keys(),"Hours":totals.values()})

        fig = px.pie(df,names="Activity",values="Hours")
        st.plotly_chart(fig)

# =============================
# CAREER PAGE
# =============================

if page == "📈 Career":

    st.markdown("### 📈 Career Progress")

    DSA_INITIAL = 239

    if not daily.empty:

        total_dsa = DSA_INITIAL + int(daily["dsa"].sum())
        st.metric("Total DSA Problems Solved",total_dsa)

        fig = px.line(daily,x="date",y="focus_hours")
        st.plotly_chart(fig)

        fig = px.line(daily,x="date",y="ml_hours")
        st.plotly_chart(fig)

# =============================
# LINKEDIN PAGE
# =============================

if page == "🌐 LinkedIn":

    st.markdown("### 🌐 LinkedIn Tracker")

    followers = st.number_input("Followers",0,100000,1263)
    posts = st.number_input("Posts Today",0,10,0)

    if st.button("Save LinkedIn Data"):

        linkedin_sheet.append_row([
            str(date.today()),
            followers,
            posts
        ])

        st.success("Saved!")
        st.cache_data.clear()
        st.rerun()

# =============================
# FREELANCING PAGE
# =============================

if page == "💻 Freelancing":

    st.markdown("### 💻 Freelance Portfolio Progress")

    project_hours = st.number_input("Portfolio Project Hours",0.0,12.0,0.0)
    projects_done = st.number_input("Projects Completed",0,20,0)
    website_progress = st.checkbox("Worked on Portfolio Website")

    if st.button("Save Freelance Progress"):

        freelance_sheet.append_row([
            str(date.today()),
            project_hours,
            projects_done,
            int(website_progress)
        ])

        st.success("Saved!")
        st.cache_data.clear()

        st.rerun()




