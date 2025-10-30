import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time

# Pagina-configuratie
st.set_page_config(page_title="BonsAI Replay Detectie Demo", layout="wide")

st.markdown("""
<style>
    .replay-alert {
        animation: blink 1s infinite;
        font-size: 18px;
        font-weight: bold;
        color: red;
    }
    @keyframes blink {
        0% { opacity: 1; }
        50% { opacity: 0.1; }
        100% { opacity: 1; }
    }
</style>
""", unsafe_allow_html=True)

st.title("🔌 Live stroommetingen bij TenneT – Replay-aanval detectie met BonsAI-sleutel")

st.markdown("""
In deze demo zie je het verschil tussen een **standaard NOC-dashboard** en een dashboard dat werkt met de **BonsAI-sleutel**.  
De meetwaarden lijken betrouwbaar, maar worden **stiekem hergebruikt** door een aanvaller.  
👉 Alleen het systeem met sleutel herkent dit als herhaling.
""")

# Initialiseer sessiestatus
if "metingen" not in st.session_state:
    st.session_state.metingen = []
if "replay" not in st.session_state:
    st.session_state.replay = False
if "replay_data" not in st.session_state:
    st.session_state.replay_data = []
if "animating" not in st.session_state:
    st.session_state.animating = False
if "replay_started" not in st.session_state:
    st.session_state.replay_started = None

# Genereer nieuwe meetwaarde
def nieuwe_meting(t):
    return np.sin(t / 3) + np.random.normal(0, 0.1)

# Bediening
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("▶️ Start animatie"):
        st.session_state.animating = True
        st.session_state.replay = False
        st.session_state.replay_started = None
with col2:
    if st.button("🛑 Stop"):
        st.session_state.animating = False
with col3:
    if st.button("🎭 Start Replay"):
        st.session_state.replay = True
        st.session_state.replay_data = st.session_state.metingen.copy()
        st.session_state.replay_started = len(st.session_state.metingen)

# Plotfunctie
def plot_grafieken(ts, waarden, replay_start=None, detecteer=False):
    colL, colR = st.columns(2)

    with colL:
        st.subheader("🔓 Normale detectie (zonder sleutel)")
        fig, ax = plt.subplots(figsize=(6, 3))
        ax.plot(ts, waarden, color="green")
        if replay_start is not None:
            ax.axvline(replay_start, color="gray", linestyle="--")
            ax.text(replay_start + 0.5, max(waarden), "Replay gestart", color="gray")
        ax.set_xlabel("Tijd")
        ax.set_ylabel("Stroomsterkte (A)")
        st.pyplot(fig)
        if replay_start is not None:
            st.info("Replay-aanval **niet herkend**.")

    with colR:
        st.subheader("🔐 TenneT-dashboard met BonsAI-sleutel")
        fig2, ax2 = plt.subplots(figsize=(6, 3))
        ax2.plot(ts, waarden, color="blue")
        if replay_start is not None:
            ax2.axvline(replay_start, color="red", linestyle="--")
            ax2.text(replay_start + 0.5, max(waarden), "⚠️ Replay gedetecteerd!", color="red", fontsize=10)
        ax2.set_xlabel("Tijd")
        ax2.set_ylabel("Stroomsterkte (A)")
        st.pyplot(fig2)
        if replay_start is not None and detecteer:
            st.markdown('<div class="replay-alert">🚨 BonsAI herkent hergebruik van een meetpatroon!</div>', unsafe_allow_html=True)

# Animeren
placeholder = st.empty()
if st.session_state.animating:
    for t in range(100):  # Looptijd demo
        if not st.session_state.animating:
            break

        nieuwe = nieuwe_meting(t)
        st.session_state.metingen.append(nieuwe)
        ts = list(range(len(st.session_state.metingen)))
        waarden = st.session_state.metingen.copy()
        detecteer = False
        replay_start = None

        # Voeg replay toe
        if st.session_state.replay and t > 20:
            waarden += st.session_state.replay_data
            ts += list(range(len(ts), len(ts) + len(st.session_state.replay_data)))
            replay_start = st.session_state.replay_started
            detecteer = True

        with placeholder.container():
            plot_grafieken(ts, waarden, replay_start, detecteer)

        time.sleep(0.3)

# Achtergronduitleg
st.markdown("""---  
### Waarom dit relevant is voor TenneT  
In het hoogspanningsnet zijn stroommetingen cruciaal – voor sturing, veiligheid en verrekening.  
Een slimme aanvaller kan echter eerdere meetreeksen opnieuw versturen.  

📉 **Traditionele detectie** controleert alleen of de waarden ‘kloppen’.  
🧠 **BonsAI** herkent dat een exact patroon **al eerder is gebruikt** – zelfs als de data zelf geldig lijkt.

**Zo krijg je zekerheid over authenticiteit én actualiteit van metingen.**
""")
