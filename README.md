# AgroSentinel Field

Theme: Build for Your World · Indie developer · Meta Global AI Developer Hackathon

A phone-photo screening aid for aflatoxin in stored grain. A farmer or small trader uploads a photo of a lateral flow test strip, picks the grain and storage conditions, and gets a plain-language answer in Nepali and English.

**This is a screening aid, not a lab test.**

## Why
Mycotoxin contamination in stored grain is a real risk in Nepal, and farmers and small traders have no cheap, quick way to check a batch. This project explores whether a phone and a multimodal model can close part of that gap.

## How it works
Read the strip. The uploaded photo is sent to Muse Spark 1.2 through the Meta Model API. The model is asked to return only JSON describing the control line and test line (present, absent or unclear).

Apply a simple rule. A transparent, hand-written rule maps the reading and the storage inputs to a decision:
- control line missing or test line unclear → retest
- test line present → discard
- high humidity or more than 6 months in storage → dry and recheck
- otherwise → no contamination line detected(safe)

Explain it. The model writes two short sentences in Nepali and two in English for the farmer, and always states that this is a screening aid, not a lab test.

Stack: Python, Streamlit, requests, Meta Model API (muse-spark-1.2).

## Run it (Windows PowerShell)
```powershell
pip install -r requirements.txt
$env:META_MODEL_API_KEY="YOUR_KEY"
streamlit run app.py
```

Then open http://localhost:8501. Never commit your API key; it only lives in the environment variable.

Note: Muse Spark uses hidden reasoning tokens, so max_tokens is set to 8000 for strip reading and 8000 for advice. With low limits the model can return an empty reply.

## Demo video
[https://youtu.be/87PeO7saXTg?si=0qqcqSRKd_6RbVPs]

## Test log
Tested on 4 sample images (Maize, low humidity, 3 months in storage).

| Image | Expected | control_line | test_line | Decision | Match |
|---|---|---|---|---|---|
| sample_neg | negative | present | absent | no contamination line detected | Yes (one other run returned retest) |
| sample_med | positive | present | present | discard | Yes |
| sample_high | positive | present | present | discard | Yes |
| blank | invalid | unclear | unclear | retest | Yes |

On this kit, a negative strip shows only the control line, so the model reports test_line absent.

Source of the sample images: [https://github.com/jackievaleri/lateral_flow_quantification_app]

Tiny test set. Four images, not photos of strips from a real aflatoxin kit. Strip-reading accuracy has not been validated.

**Inconsistent once.** The negative sample returned retest on one run, so repeated readings can differ.

**Placeholder rule.** The decision rule is a transparent placeholder, not a validated threshold. Medium and high positives both map to discard; the app does not grade contamination levels.

Kit format matters. Many aflatoxin kits use a competitive format where the test line fades as toxin increases, which is the opposite of this rule. The rule here assumes a stronger test line means more contamination, which fits the sample images but must be checked against your kit's manual before any real use.

Language not reviewed. The Nepali advice has not yet been reviewed by a native speaker or an agronomist.

Data handling. While free API credits are in use, Meta's billing page notes that content may be used for product improvement. Use sample images only, not private farm data.

## Future work
- SAM 3.1 segmentation to isolate the strip and lines from a phone photo in real-world lighting
- Validation against real kits and lab results, with a proper threshold
- Contamination-level grading, not just present/absent
- Review of the Nepali advice by native speakers and agronomists
- Field testing with farmers and small traders

## Author
Suman Shrestha, Kathmandu, Nepal
