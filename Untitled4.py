#!/usr/bin/env python
# coding: utf-8

import base64
from io import BytesIO
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st


REQUIRED_COLUMNS = {
	"Watch_Date",
	"Region",
	"Monthly_Revenue",
	"Subscription_Plan",
	"Rating",
	"Category",
}
WEEKDAY_ORDER = [
	"Monday",
	"Tuesday",
	"Wednesday",
	"Thursday",
	"Friday",
	"Saturday",
	"Sunday",
]
CHART_COLORS = ["#e50914", "#b20710", "#f04452", "#8f0710", "#ff737b", "#c4121a"]


@st.cache_data
def load_data(file_bytes):
	return pd.read_csv(BytesIO(file_bytes))


def draw_bar_chart(data, title, value_label, horizontal=False, order=None):
	if data.empty:
		st.info("No values available for this chart.")
		return

	if order is not None:
		data = data.reindex(order).dropna()
	data = data.sort_values(ascending=True) if horizontal else data
	figure, axis = plt.subplots(figsize=(8, 3.5), facecolor="#ffffff")
	axis_color = "#202020"
	axis.set_facecolor("#ffffff")
	positions = range(len(data))
	if horizontal:
		axis.barh(positions, data.values, color=CHART_COLORS[0])
		axis.set_yticks(list(positions), labels=data.index.astype(str))
	else:
		axis.bar(positions, data.values, color=CHART_COLORS[: len(data)])
		axis.set_xticks(list(positions), labels=data.index.astype(str))
		axis.tick_params(axis="x", labelrotation=25)
	axis.set_title(title, loc="left", fontweight="bold", pad=14)
	axis.set_ylabel(value_label if horizontal else "")
	axis.set_xlabel("" if horizontal else value_label)
	axis.tick_params(colors=axis_color)
	axis.xaxis.label.set_color(axis_color)
	axis.yaxis.label.set_color(axis_color)
	axis.title.set_color(axis_color)
	axis.grid(axis="x" if horizontal else "y", color="#e5e5e5", linewidth=0.7, alpha=0.9)
	axis.set_axisbelow(True)
	for spine in axis.spines.values():
		spine.set_color("#dddddd")
	axis.spines[["top", "right"]].set_visible(False)
	figure.tight_layout()
	st.pyplot(figure, use_container_width=True)
	plt.close(figure)


st.set_page_config(page_title="Netflix Insights", page_icon="N", layout="wide")
project_dir = Path(__file__).parent
logo_path = project_dir / "images netflix.png"
background_path = project_dir / "images netflix 2.jpg"
background_image = base64.b64encode(background_path.read_bytes()).decode("ascii")
st.markdown(
	f"""
	<style>
	.stApp {{
		background-image: linear-gradient(rgba(255, 255, 255, 0.94), rgba(255, 255, 255, 0.97)),
			url("data:image/jpeg;base64,{background_image}");
		background-size: cover;
		background-position: center;
		background-attachment: fixed;
	}}
	[data-testid="stAppViewContainer"], [data-testid="stHeader"] {{ background: transparent; }}
	[data-testid="stSidebar"] {{
		background: rgba(255, 255, 255, 0.97);
		border-right: 2px solid #e50914;
	}}
	[data-testid="stMetric"] {{
		background: rgba(255, 255, 255, 0.96);
		border-left: 3px solid #e50914;
		padding: 8px;
		box-shadow: 0 1px 5px rgba(0, 0, 0, 0.08);
	}}
	[data-testid="stMetricValue"] {{ font-size: 1.5rem !important; }}
	[data-testid="stMetricLabel"], [data-testid="stMetricValue"],
	[data-testid="stMarkdownContainer"] p, label, h1, h2, h3 {{ color: #202020 !important; }}
	[data-baseweb="select"] > div, [data-baseweb="input"] > div,
	[data-baseweb="textarea"] > div, [data-testid="stDateInput"] input {{
		background-color: #ffffff !important;
		color: #202020 !important;
		border-color: #e50914 !important;
	}}
	[data-testid="stDateInput"] [data-baseweb="input"] > div,
	[data-testid="stMultiSelect"] [data-baseweb="select"] > div {{
		background-color: #ffffff !important;
		border-color: #e50914 !important;
	}}
	[data-testid="stDateInput"] [role="group"],
	[data-testid="stMultiSelect"] [role="group"] {{
		background-color: #ffffff !important;
		border-color: #e50914 !important;
	}}
	[data-testid="stDateInput"] input, [data-testid="stMultiSelect"] input {{
		color: #202020 !important;
		-webkit-text-fill-color: #202020 !important;
	}}
	[data-baseweb="tag"] {{ background-color: #e50914; color: #ffffff; }}
	[data-baseweb="popover"] > div, [role="listbox"] {{ background-color: #ffffff; color: #202020; }}
	[role="option"] {{ color: #202020; }}
	[role="option"]:hover {{ background-color: #ffe5e7; }}
	input[type="checkbox"] {{ accent-color: #e50914; }}
	section[data-testid="stFileUploaderDropzone"] {{
		background: #ffffff;
		border-color: #e50914;
	}}
	section[data-testid="stFileUploaderDropzone"] button {{
		background: #e50914;
		color: #ffffff;
		border-color: #e50914;
	}}
	[data-testid="stDataFrame"] {{ border: 1px solid #dddddd; }}
	[data-testid="stExpander"] {{ border-color: #dddddd; }}
	hr {{ border-color: #dddddd; }}
	</style>
	""",
	unsafe_allow_html=True,
)

logo_column, title_column = st.columns([0.18, 0.82], vertical_alignment="center")
with logo_column:
	if logo_path.exists():
		st.image(str(logo_path), width=132)
with title_column:
	st.title("Netflix Insights")
	st.caption("Explore viewing activity, ratings, and monthly revenue.")

uploaded_file = st.sidebar.file_uploader("Upload a Netflix CSV", type=["csv"])
local_csv = project_dir / "netflix.csv"

if uploaded_file is not None:
	csv_bytes = uploaded_file.getvalue()
elif local_csv.exists():
	csv_bytes = local_csv.read_bytes()
	st.sidebar.caption("Using netflix.csv from the project folder.")
else:
	st.info("Upload your Netflix CSV to open the dashboard, or place netflix.csv beside this script.")
	st.stop()

try:
	netflix = load_data(csv_bytes)
except Exception as error:
	st.error(f"Could not read this CSV: {error}")
	st.stop()

missing_columns = sorted(REQUIRED_COLUMNS - set(netflix.columns))
if missing_columns:
	st.error("The CSV is missing columns required by this dashboard.")
	st.write(", ".join(missing_columns))
	st.stop()

netflix["Watch_Date"] = pd.to_datetime(netflix["Watch_Date"], errors="coerce")
netflix["Monthly_Revenue"] = pd.to_numeric(netflix["Monthly_Revenue"], errors="coerce")
netflix["Rating"] = pd.to_numeric(netflix["Rating"], errors="coerce")
for column in ["Region", "Subscription_Plan", "Category"]:
	netflix[column] = netflix[column].astype("string")

duplicate_count = int(netflix.duplicated().sum())
include_duplicates = st.sidebar.checkbox("Include duplicate rows", value=False)
filtered = netflix.copy() if include_duplicates else netflix.drop_duplicates().copy()

date_values = filtered["Watch_Date"].dropna()
if not date_values.empty:
	date_range = st.sidebar.date_input(
		"Watch date range",
		value=(date_values.min().date(), date_values.max().date()),
		min_value=date_values.min().date(),
		max_value=date_values.max().date(),
	)
	if isinstance(date_range, tuple) and len(date_range) == 2:
		start_date, end_date = date_range
		filtered = filtered[
			filtered["Watch_Date"].dt.date.between(start_date, end_date)
		]
else:
	st.sidebar.caption("No valid watch dates available for filtering.")

filter_columns = [
	("Region", "Regions"),
	("Subscription_Plan", "Subscription plans"),
	("Category", "Categories"),
]
for column, label in filter_columns:
	options = sorted(filtered[column].dropna().unique().tolist())
	selected = st.sidebar.multiselect(label, options, default=options)
	filtered = filtered[filtered[column].isin(selected)]

if filtered.empty:
	st.warning("No rows match the selected filters.")
	st.stop()

revenue_total = filtered["Monthly_Revenue"].sum()
rating_average = filtered["Rating"].mean()
metric_columns = st.columns(4)
metric_columns[0].metric("Records", f"{len(filtered):,}")
metric_columns[1].metric(
	"Monthly revenue", f"${revenue_total:,.0f}" if pd.notna(revenue_total) else "N/A"
)
metric_columns[2].metric(
	"Average rating", f"{rating_average:.2f}" if pd.notna(rating_average) else "N/A"
)
metric_columns[3].metric("Regions", f"{filtered['Region'].nunique():,}")

st.divider()
left_chart, right_chart = st.columns(2)
with left_chart:
	revenue_by_region = filtered.groupby("Region")["Monthly_Revenue"].sum().sort_values()
	draw_bar_chart(revenue_by_region, "Revenue by region", "Revenue", horizontal=True)
with right_chart:
	revenue_by_category = filtered.groupby("Category")["Monthly_Revenue"].sum().sort_values()
	draw_bar_chart(revenue_by_category, "Revenue by category", "Revenue", horizontal=True)

left_chart, right_chart = st.columns(2)
with left_chart:
	rating_by_plan = filtered.groupby("Subscription_Plan")["Rating"].sum()
	rating_by_plan = rating_by_plan[rating_by_plan > 0].sort_values(ascending=False)
	if rating_by_plan.empty:
		st.info("No positive rating totals available for this chart.")
	else:
		figure, axis = plt.subplots(figsize=(8, 3.5), facecolor="#ffffff")
		axis.set_facecolor("#ffffff")
		axis.pie(
			rating_by_plan.values,
			labels=rating_by_plan.index.astype(str),
			autopct="%1.0f%%",
			startangle=90,
			colors=CHART_COLORS[: len(rating_by_plan)],
			wedgeprops={"width": 0.48, "edgecolor": "#ffffff"},
			textprops={"color": "#ffffff"},
		)
		axis.set_title("Rating total by subscription plan", loc="left", fontweight="bold", color="#202020")
		legend = axis.legend(
			rating_by_plan.index.astype(str),
			loc="lower center",
			bbox_to_anchor=(0.5, -0.12),
			ncol=min(len(rating_by_plan), 3),
			frameon=False,
		)
		for label in legend.get_texts():
			label.set_color("#202020")
		st.pyplot(figure, use_container_width=True)
		plt.close(figure)
with right_chart:
	dated_rows = filtered.dropna(subset=["Watch_Date"])
	revenue_by_weekday = dated_rows.groupby(
		dated_rows["Watch_Date"].dt.day_name()
	)["Monthly_Revenue"].sum()
	draw_bar_chart(
		revenue_by_weekday,
		"Revenue by day of week",
		"Revenue",
		order=WEEKDAY_ORDER,
	)

dated_rows = filtered.dropna(subset=["Watch_Date"])
if not dated_rows.empty:
	monthly_revenue = dated_rows.groupby(
		dated_rows["Watch_Date"].dt.to_period("M").astype(str)
	)["Monthly_Revenue"].sum()
	figure, axis = plt.subplots(figsize=(11, 3.5), facecolor="#ffffff")
	axis.set_facecolor("#ffffff")
	axis.plot(monthly_revenue.index, monthly_revenue.values, color=CHART_COLORS[0], marker="o")
	axis.fill_between(range(len(monthly_revenue)), monthly_revenue.values, color=CHART_COLORS[0], alpha=0.1)
	axis.set_title("Monthly revenue trend", loc="left", fontweight="bold", pad=14)
	axis.set_ylabel("Revenue")
	axis.tick_params(axis="x", labelrotation=25)
	axis.tick_params(colors="#202020")
	axis.yaxis.label.set_color("#202020")
	axis.title.set_color("#202020")
	axis.grid(axis="y", color="#e5e5e5", linewidth=0.7, alpha=0.9)
	for spine in axis.spines.values():
		spine.set_color("#dddddd")
	axis.spines[["top", "right"]].set_visible(False)
	figure.tight_layout()
	st.pyplot(figure, use_container_width=True)
	plt.close(figure)

with st.expander("Dataset details"):
	detail_columns = st.columns(3)
	detail_columns[0].metric("Rows in source", f"{len(netflix):,}")
	detail_columns[1].metric("Exact duplicate rows", f"{duplicate_count:,}")
	detail_columns[2].metric("Rows shown", f"{len(filtered):,}")
	st.dataframe(filtered, use_container_width=True, hide_index=True)
	st.caption("Missing values by column")
	st.dataframe(
		filtered.isna().sum().rename("Missing values").to_frame(),
		use_container_width=True,
	)




