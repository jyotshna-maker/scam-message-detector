import re
import streamlit as st

st.set_page_config(page_title="Scam Message Detector", page_icon="🛡️")

# 1. THE RULES
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
    "Fake delivery or package notice": ["package", "delivery failed",
                                        "reschedule", "customs"],
}
LINK_PATTERN = r"https?://\S+|www\.\S+|bit\.ly\S*|tinyurl\S*"

# 2. THE BRAIN
def analyze(message):
    text = message.lower()
    score = 0
    reasons = []
    found_words = []

    for reason, words in RULES.items():
        matched = False
        for word in words:
            if re.search(r"\b" + re.escape(word) + r"\b", text):
                found_words.append(word)
                matched = True
        if matched:
            score += 20
            reasons.append(reason)

    links = re.findall(LINK_PATTERN, text)
    if links:
        score += 25
        reasons.append("Contains a link")
        found_words.extend(links)

    return min(score, 100), reasons, found_words

# 3. HIGHLIGHTER: wraps suspicious words in a red background
def highlight(message, words):
    result = message
    for w in sorted(set(words), key=len, reverse=True):
        result = re.sub(
            re.escape(w),
            lambda m: f"<mark style='background:#ffb3b3'>{m.group(0)}</mark>",
            result,
            flags=re.IGNORECASE,
        )
    return result

# 4. SAMPLE MESSAGES for live demos
SAMPLES = {
    "🏦 Fake bank alert": "URGENT: Your SBI account will be blocked within 24 hours. Complete KYC now: http://sbi-kyc-update.xyz and share the OTP.",
    "🎁 Fake prize": "Congratulations! You have won a prize of 25,00,000. Pay the registration fee to claim.",
    "📦 Fake delivery": "Your package delivery failed. Reschedule here: http://bit.ly/track-pkg",
    "💬 Normal message": "Hey, are we meeting at 6 for dinner today?",
}

if "text" not in st.session_state:
    st.session_state.text = ""

# 5. THE SCREEN
st.title("🛡️ Scam Message Detector")
st.caption("Paste any suspicious SMS or WhatsApp message and check it in seconds.")

st.write("**Try a sample:**")
cols = st.columns(len(SAMPLES))
for col, (label, msg) in zip(cols, SAMPLES.items()):
    if col.button(label):
        st.session_state.text = msg

message = st.text_area("Paste a suspicious message here:",
                       key="text", height=120)

if st.button("🔍 Check message", type="primary"):
    if message.strip() == "":
        st.warning("Please paste a message first.")
    else:
        score, reasons, found_words = analyze(message)

        if score >= 50:
            st.error(f"🚨 LIKELY SCAM (risk {score}/100)")
        elif score >= 20:
            st.warning(f"⚠️ SUSPICIOUS (risk {score}/100)")
        else:
            st.success(f"✅ Looks safe (risk {score}/100)")
        st.progress(score / 100)

        if reasons:
            st.subheader("Why we flagged it")
            for r in reasons:
                st.write("•", r)
            st.subheader("Suspicious parts highlighted")
            st.markdown(highlight(message, found_words), unsafe_allow_html=True)

        if score >= 50:
            st.subheader("What to do next")
            st.info(
                "- Do **not** click any link or share any OTP, PIN or password.\n"
                "- Banks never ask for OTP or PIN by SMS, call or WhatsApp.\n"
                "- Block the sender and report it at **cybercrime.gov.in** "
                "or call **1930** (India's cyber fraud helpline).\n"
                "- If you already lost money, call 1930 immediately."
            )
        elif score >= 20:
            st.info("Be careful. Verify with the company using its official "
                    "app or website, not the link in the message.")