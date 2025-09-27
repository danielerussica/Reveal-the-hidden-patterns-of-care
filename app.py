import streamlit as st
import pandas as pd
import altair as alt
import os
from pyvis.network import Network
import networkx as nx
import numpy as np
from data_viz import create_directed_network
import openai
import os

@st.cache_resource
def get_openai_client():
    return openai.OpenAI(
        api_key=os.getenv("SWISS_AI_PLATFORM_API_KEY"),
        base_url="https://api.swisscom.com/layer/swiss-ai-weeks/apertus-70b/v1"
    )
client = get_openai_client()
prompt_path = "context.txt"

filename = "data/data_css_challenge.csv"
@st.cache_data
def load_data(filename):
    return pd.read_csv(filename)

df = load_data(filename)
st.title("Patient Treatment Analysis")

###################################################################################################

# Aggregate counts by age and reason_for_treatment
counts = df.groupby(["age", "reason_for_treatment"])["patient_id"].count().reset_index()
counts.rename(columns={"patient_id": "count"}, inplace=True)


st.subheader("Patient Counts by Age and Reason for Treatment")
chart = (
    alt.Chart(counts)
    .mark_bar()
    .encode(
        x=alt.X("age:O", title="Age"),  # treat age as categorical
        y=alt.Y("count:Q", title="Count"),
        color="reason_for_treatment:N"
    )
)

st.altair_chart(chart, use_container_width=True)


###################################################################################################

title = "Healthcare Provider ID → Client Network ID"
output_file = "id_links_network.html"
create_directed_network(
    df, 
    feature1='healthcare_provider_id', 
    feature2='client_id', 
    title=title, 
    min_count=1000, 
    output_file=output_file
)

st.subheader(title)
st.components.v1.html(open(output_file, "r", encoding="utf-8").read(), height=750)


###################################################################################################

title = "Healthcare Provider Type → Client Type Network"
output_file = "type_links_network.html"
create_directed_network(
    df, 
    feature1='healthcare_provider_type', 
    feature2='client_type', 
    title=title, 
    min_count=10_000, 
    output_file=output_file,
    length=1000
)

st.subheader(title)
st.components.v1.html(open(output_file, "r", encoding="utf-8").read(), height=750)

###################################################################################################

with st.sidebar:
    st.header("Chat with Apertus-70B")
    
    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "swiss-ai/Apertus-70B"

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("What is up?"):
        st.session_state.messages.append({"role": "user", "content": open(prompt_path).read() + "\n\n" + prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            stream = client.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            )
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})