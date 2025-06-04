# Streamlit 撲克預測工具（圖片點選手牌 + 自動預測翻牌/轉牌/河牌 + 玩家數）
import streamlit as st
import random
import pandas as pd
from datetime import datetime

# 初始化牌組與狀態
deck_template = [r + s for r in '23456789TJQKA' for s in 'cdhs']
suit_map = {'s': '♠', 'h': '♥', 'd': '♦', 'c': '♣'}
if "all_games" not in st.session_state:
    st.session_state.all_games = []
if "seed" not in st.session_state:
    st.session_state.seed = int(datetime.now().timestamp())
    st.session_state.rng = random.Random(st.session_state.seed)

st.title("🃏 撲克牌預測工具（圖片選牌 + 玩家數 + 自動預測）")

# UI 選牌用的函數
def card_button(label):
    col1, col2 = st.columns(2)
    with col1:
        rank = st.selectbox(f"{label} 點數", list('23456789TJQKA'), key=f"{label}_rank")
    with col2:
        suit = st.selectbox(f"{label} 花色", ["♠ (s)", "♥ (h)", "♦ (d)", "♣ (c)"], key=f"{label}_suit")
    suit_letter = suit[suit.find("(") + 1]
    return rank + suit_letter

with st.form("new_game_form"):
    st.subheader("🔢 玩家資訊與選牌")
    num_players = st.number_input("請輸入本局玩家人數（含你自己）", min_value=2, max_value=9, value=6, step=1)

    st.markdown("### 👤 你的兩張手牌")
    card1 = card_button("手牌1")
    card2 = card_button("手牌2")

    st.markdown("### 🃏 公牌區")
    flop1 = card_button("翻牌1")
    flop2 = card_button("翻牌2")
    flop3 = card_button("翻牌3")
    turn = st.text_input("轉牌（如未發牌可空白）")
    river = st.text_input("河牌（如未發牌可空白）")

    submitted = st.form_submit_button("✅ 新增一局")

    if submitted:
        hand = [card1, card2]
        flop = [flop1, flop2, flop3]
        used = hand + flop
        if turn:
            used.append(turn)
        if river:
            used.append(river)

        remaining = [c for c in deck_template if c not in used]
        st.session_state.rng.shuffle(remaining)

        # 預測翻牌（如果使用者輸入為空）
        if not flop1 or not flop2 or not flop3:
            flop = remaining[:3]
            used += flop
            remaining = remaining[3:]

        # 預測轉牌與河牌
        predict_turn = turn if turn else remaining[0]
        predict_river = river if river else remaining[1]

        st.session_state.all_games.append({
            "players": num_players,
            "hand": hand,
            "flop": flop,
            "turn": turn if turn else None,
            "river": river if river else None,
            "pred_flop": flop,
            "pred_turn": predict_turn,
            "pred_river": predict_river
        })

        st.success("✅ 本局已儲存！")
        if not turn:
            st.write(f"➡ 預測轉牌：{predict_turn}")
        if not river:
            st.write(f"➡ 預測河牌：{predict_river}")

st.divider()

st.subheader("📋 所有牌局紀錄")
if st.session_state.all_games:
    df = pd.DataFrame([{
        "玩家數": g['players'],
        "手牌1": g['hand'][0],
        "手牌2": g['hand'][1],
        "翻牌1": g['flop'][0],
        "翻牌2": g['flop'][1],
        "翻牌3": g['flop'][2],
        "轉牌": g['turn'],
        "河牌": g['river'],
        "預測轉牌": g['pred_turn'],
        "預測河牌": g['pred_river']
    } for g in st.session_state.all_games])
    st.dataframe(df)
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("💾 下載 CSV", data=csv, file_name="poker_log.csv")
else:
    st.info("尚未輸入任何資料。")

st.caption(f"🔐 本次 MT19937 種子：{st.session_state.seed}")
