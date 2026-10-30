import re
import streamlit as st

# 1. THE RULES: each red flag has a reason and a list of trigger words
RULES = {
    "Asks for OTP, PIN or password": ["otp", "pin", "password", "cvv"],
    "Creates urgency or fear": ["urgent", "immediately", "blocked", "suspended",
                                "expires", "last chance", "within 24 hours"],
    "Promises money or prizes": ["lottery", "winner", "prize", "cashback",
                                 "free gift", "you have won"],
    "Pushes KYC / account verification": ["kyc", "verify your account",
                                          "update your pan", "aadhaar"],
    "Looks like a fake job offer": ["work from home", "earn daily",
                                    "registration fee", "part time job"],
}

# 2. THE BRAIN: takes a message, returns a score and reasons
def analyze(message):
    text = message.lower()
    score = 0
    reasons = []

    for reason, words in RULES.items():
        for word in words:
            if re.search(r"\b" + re.escape(word) + r"\b", text):
                score += 20
                reasons.append(reason)
                break  # count each reason only once

    if re.search(r"https?://|www\.|bit\.ly|tinyurl", text):
        score += 25
        reasons.append("Contains a link")

    return min(score, 100), reasons

# 3. THE SCREEN: what the user sees
st.title("🛡️ Scam Message Detector")
message = st.text_area("Paste a suspicious message here:")

if st.button("Check"):
    if message.strip() == "":
        st.warning("Please paste a message first.")
    else:
        score, reasons = analyze(message)

        if score >= 50:
            st.error(f"🚨 LIKELY SCAM (risk {score}/100)")
        elif score >= 20:
            st.warning(f"⚠️ SUSPICIOUS (risk {score}/100)")
        else:
            st.success(f"✅ Looks safe (risk {score}/100)")

        st.progress(score / 100)

        if reasons:
            st.subheader("Why we flagged it:")
            for r in reasons:
                st.write("•", r)