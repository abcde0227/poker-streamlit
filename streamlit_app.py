import streamlit as st
import random
import pandas as pd
from datetime import datetime

deck_template = [r + s for r in '23456789TJQKA' for s in 'cdhs']
if "all_games" not in st.session_state:
    st.session_state.all_games = []
if "seed" not in st.session_state:
    st.session_state.seed = int(datetime.now().timestamp())
    st.session_state.rng = random.Random(st.session_state.seed)

st.title("🃏 撲克牌預測工具")

with st.form("new_game_form"):
    st.subheader("新增一局")
    hand_input = st.text_input("手牌（如：Ah Ks）")
    flop_input = st.text_input("翻牌（如：9d Jc Qs）")
    turn_input = st.text_input("轉牌（可空白）")
    river_input = st.text_input("河牌（可空白）")
    submitted = st.form_submit_button("新增一局")

    if submitted:
        hand = hand_input.strip().split()
        flop = flop_input.strip().split()
        turn = turn_input.strip() if turn_input else ""
        river = river_input.strip() if river_input else ""

        if len(hand) != 2 or len(flop) != 3:
            st.warning("請輸入正確格式的手牌與翻牌")
        else:
            used = hand + flop + ([turn] if turn else []) + ([river] if river else [])
            remaining = [c for c in deck_template if c not in used]
            st.session_state.rng.shuffle(remaining)
            pred_turn = remaining[0] if not turn else turn
            pred_river = remaining[1] if not river and len(remaining) > 1 else river

            st.session_state.all_games.append({
                "hand": hand,
                "flop": flop,
                "turn": turn if turn else None,
                "river": river if river else None,
                "pred_turn": pred_turn,
                "pred_river": pred_river
            })

            st.success(f"✅ 本局儲存成功！")
            st.write(f"預測的轉牌：{pred_turn}")
            if not river:
                st.write(f"預測的河牌：{pred_river}")

st.divider()
st.subheader("📋 所有紀錄")
if st.session_state.all_games:
    df = pd.DataFrame([{
        "手牌1": g['hand'][0],
        "手牌2": g['hand'][1],
        "翻牌1": g['flop'][0],
        "翻牌2": g['flop'][1],
        "翻牌3": g['flop'][2],
        "轉牌": g['turn'],
        "河牌": g['river'],
        "預測轉牌": g['pred_turn'],
        "預測河牌": g['pred_river'],
    } for g in st.session_state.all_games])
    st.dataframe(df)
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("💾 下載 CSV", data=csv, file_name="poker_log.csv")
else:
    st.info("尚無資料，請先新增一局。")

st.caption(f"目前的 MT 種子值：{st.session_state.seed}")
