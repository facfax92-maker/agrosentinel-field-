import os
import json
import re
import base64
import requests
import streamlit as st

API_KEY = os.environ.get("META_MODEL_API_KEY", "")
API_URL = "https://api.meta.ai/v1/chat/completions"
MODEL = "muse-spark-1.2"

def call_model(messages, max_tokens=300):
    r = requests.post(
        API_URL,
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json={"model": MODEL, "messages": messages, "max_tokens": max_tokens},
        timeout=120,
    )
    r.raise_for_status()
    data = r.json()
    content = data["choices"][0]["message"].get("content")
    if not content:
        reason = data["choices"][0].get("finish_reason")
        raise ValueError(f"Model returned an empty reply (finish_reason={reason}). Try a higher max_tokens.")
    return content

def read_strip(image_bytes):
    b64 = base64.b64encode(image_bytes).decode()
    prompt = (
        "This is a lateral flow test strip for aflatoxin in grain. "
        "Look at the control line and the test line. "
        "Reply with ONLY this JSON, nothing else: "
        "{\"control_line\": \"present|absent|unclear\", \"test_line\": \"present|absent|unclear\"}. "
        "If the image is not a test strip, use unclear for both."
    )
    messages = [{"role": "user", "content": [
        {"type": "text", "text": prompt},
        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}},
    ]}]
    raw = call_model(messages, max_tokens=8000)
    m = re.search(r"\{.*\}", raw, re.S)
    if not m:
        raise ValueError(f"Model did not return JSON. Its reply was: {raw[:300]}")
    return json.loads(m.group(0))

def decide(strip, humidity, duration_months):
    if strip.get("control_line") != "present" or strip.get("test_line") == "unclear":
        return "retest"
    if strip.get("test_line") == "present":
        return "discard"
    if humidity == "high" or duration_months > 6:
        return "dry_and_recheck"
    return "safe"

def advice(decision, grain, humidity, duration_months):
    prompt = (
        f"Write 2 short sentences in Nepali, then 2 in English, for a farmer. "
        f"Grain: {grain}. Storage humidity: {humidity}. Stored for {duration_months} months. "
        f"Decision: {decision}. Say this is a screening aid, not a lab test."
    )
    return call_model([{"role": "user", "content": prompt}], max_tokens=8000)

st.title("AgroSentinel Field")
st.caption("Screening aid for aflatoxin in stored grain. Not a lab test.")

photo = st.file_uploader("Photo of test strip", type=["jpg", "jpeg", "png"])
grain = st.selectbox("Grain", ["Maize", "Rice", "Wheat", "Other"])
humidity = st.selectbox("Storage humidity", ["low", "medium", "high"])
duration = st.number_input("Months in storage", min_value=0, max_value=36, value=3)

if st.button("Check batch") and photo:
    try:
        strip = read_strip(photo.getvalue())
        decision = decide(strip, humidity, duration)
        st.write(f"Strip reading: {strip}")
        st.subheader(f"Decision: {decision.replace('_', ' ')}")
        st.write(advice(decision, grain, humidity, duration))
    except Exception as e:
        st.error(f"Something failed: {e}")

