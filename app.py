"""
生命科学・医学系研究 倫理指針適合性チェッカー (Streamlit App)
「人を対象とする生命科学・医学系研究に関する倫理指針」適合性自動診断・対話型チェックシステム
"""
import os
import streamlit as st
import pandas as pd

from ethics_rules import ETHICS_ITEMS, evaluate_compliance
from doc_parser import extract_text_from_file, load_ethics_guideline_from_docx
from ai_checker import run_ai_compliance_review
from styles import apply_custom_styles

# ページ基本設定
st.set_page_config(
    page_title="倫理指針適合性チェッカー | 生命科学・医学系研究",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# スタイル適用
apply_custom_styles()

def main():
    # ヘッダー描画
    st.markdown("""
        <div class="ethic-header">
            <h1>⚖️ 生命科学・医学系研究 倫理指針適合性チェッカー</h1>
            <p>「人を対象とする生命科学・医学系研究に関する倫理指針」（令和3年告示第1号、令和5年3月27日一部改正）対応</p>
        </div>
    """, unsafe_allow_html=True)

    # サイドバー設定
    st.sidebar.title("⚙️ 設定 & 研究区分")
    
    st.sidebar.subheader("1. 研究計画書の指定")
    input_method = st.sidebar.radio(
        "入力形式の選択",
        ["ファイルアップロード (.docx, .pdf, .txt)", "テキスト直接入力"]
    )
    
    plan_text = ""
    current_filename = ""
    
    if input_method == "ファイルアップロード (.docx, .pdf, .txt)":
        uploaded_file = st.sidebar.file_uploader(
            "研究実施計画書ファイルをアップロード",
            type=["docx", "pdf", "txt"],
            help="Word (.docx), PDF (.pdf), テキスト (.txt) ファイルをドラッグ＆ドロップしてください"
        )
        if uploaded_file is not None:
            file_bytes = uploaded_file.read()
            plan_text = extract_text_from_file(file_bytes, uploaded_file.name)
            current_filename = uploaded_file.name
            st.sidebar.success(f"ファイル読込完了: {uploaded_file.name}")
            
    else: # テキスト直接入力
        plan_text = st.sidebar.text_area(
            "研究計画書の本文を入力",
            height=250,
            placeholder="ここに研究実施計画書のテキストを貼り付けてください..."
        )
        current_filename = "直接入力テキスト"

    st.sidebar.markdown("---")
    st.sidebar.subheader("2. 研究設計・適用のフラグ設定")
    st.sidebar.caption("※フラグ設定に応じて不適用項目の自動判定・適合率スコアが調整されます")
    
    is_invasive = st.sidebar.checkbox("身体的・精神的侵襲を伴う研究", value=False)
    is_interventional = st.sidebar.checkbox("介入研究（通常の診療を超える医療行為等）", value=False)
    use_optout = st.sidebar.checkbox("オプトアウト（情報公開・拒否機会の保障）を利用", value=True)
    has_substitute = st.sidebar.checkbox("代諾者からのインフォームド・コンセントが含まれる", value=False)
    has_minors = st.sidebar.checkbox("未成年者・小児（アセント必要）が含まれる", value=False)
    has_outsourcing = st.sidebar.checkbox("外部への業務委託（CRO・検体検査等）を行う", value=False)

    flags = {
        "is_invasive": is_invasive,
        "is_interventional": is_interventional,
        "use_optout": use_optout,
        "has_substitute": has_substitute,
        "has_minors": has_minors,
        "has_outsourcing": has_outsourcing
    }

    st.sidebar.markdown("---")
    st.sidebar.subheader("3. AI詳細診断設定 (オプション)")
    api_provider = st.sidebar.selectbox(
        "AI診断エンジン",
        ["内蔵ルールベース診断 (APIキー不要)", "Google Gemini", "OpenAI"]
    )
    api_key = ""
    if api_provider in ["Google Gemini", "OpenAI"]:
        api_key = st.sidebar.text_input(f"{api_provider} API Key", type="password")

    # ファイル未読み込み時のガイド画面
    if not plan_text.strip():
        st.markdown("""
        <div class="ethic-card">
            <h3>📥 研究実施計画書をアップロードしてください</h3>
            <p>左側のサイドバーから <b>.docx (Word)</b>, <b>.pdf</b>, <b>.txt</b> ファイルをアップロードするか、直接テキストを貼り付けてください。<br>
            アップロード後、瞬時に指針適合率スコア、25必須項目の記載判定、及び修正文案が生成されます。</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 📋 チェック対象：倫理指針第7「研究計画書の記載事項」全25項目")
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("""
            **1. 基本情報・体制**
            - ① 研究の名称
            - ② 研究の実施体制
            - ⑪ 研究機関の長への報告内容及び方法
            - ㉓ 業務委託の内容及び監督方法
            - ㉕ モニタリング及び監査の実施体制

            **2. 研究目的・合理性**
            - ③ 研究の目的及び意義
            - ④ 研究の方法及び期間
            - ⑤ 研究対象者の選定方針
            - ⑥ 研究の科学的合理性の根拠

            **4. 個人情報・安全管理**
            - ⑧ 個人情報等の取扱い（加工・安全管理）
            - ⑩ 試料・情報の保管及び廃棄の方法
            """)
            
        with col_b:
            st.markdown("""
            **3. IC・対象者保護**
            - ⑦ インフォームド・コンセント(IC)の手続
            - ⑨ 負担・リスク・利益評価とリスク最小化対策
            - ⑮ 相談窓口体制の整備
            - ⑯ 代諾者等からのIC手続
            - ⑰ インフォームド・アセントの手続
            - ⑱ IC免除・要件充足の判断理由
            - ⑲ 経済的負担及び謝礼の有無・内容
            - ⑳ 重篤な有害事象発生時の対応体制
            - ㉑ 健康被害に対する補償の有無及び内容
            - ㉒ 研究終了後における医療の提供対応

            **5. リスク・COI・その他**
            - ⑫ 利益相反（COI）の管理状況
            - ⑬ 研究に関する情報公開の方法（jRCT/UMIN等）
            - ⑭ 研究により得られた結果等の取扱い
            - ㉔ 将来の研究利用・他機関提供の可能性
            """)
        return

    # ルールベース適合性評価の実行
    rules_eval = evaluate_compliance(plan_text, flags)

    # タブナビゲーション
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 適合性サマリー & 診断結果",
        "📝 対話型チェックリスト & メモ",
        "📄 計画書テキストビューアー",
        "📚 倫理指針ガイドライン検索",
        "📥 監査レポート出力"
    ])

    # ==========================================
    # TAB 1: 適合性サマリー & 診断結果
    # ==========================================
    with tab1:
        st.subheader("🏁 倫理指針適合性 総合診断サマリー")
        
        col1, col2, col3, col4 = st.columns([1.5, 1, 1, 1])
        
        with col1:
            st.markdown(f"""
                <div class="score-box">
                    <div class="score-number">{rules_eval['overall_score']}%</div>
                    <div class="score-label">総合指針適合率</div>
                </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.metric("適用対象項目", f"{rules_eval['applicable_count']} / 25 項目")
        with col3:
            cnt = rules_eval['compliant_count']
            cnt_str = str(int(cnt)) if cnt == int(cnt) else f"{cnt:.1f}"
            st.metric("適合判定項目", f"{cnt_str} 項目")
        with col4:
            missing_count = sum(1 for r in rules_eval['results'] if r['status'] == '未記載 (要対応)')
            st.metric("未記載・要対応", f"{missing_count} 項目",
                      delta=f"-{missing_count}" if missing_count > 0 else "なし",
                      delta_color="inverse")

        st.markdown("---")
        
        # カテゴリ別達成度スコア
        st.subheader("📈 カテゴリ別指針達成度")
        c_cols = st.columns(len(rules_eval['category_scores']))
        for idx, (cat_name, score) in enumerate(rules_eval['category_scores'].items()):
            with c_cols[idx]:
                st.write(f"**{cat_name}**")
                st.progress(score / 100.0)
                st.caption(f"適合率: {score}%")

        st.markdown("---")
        
        # AI高度診断結果・アドバイス
        st.subheader("💡 AI/LLM倫理審査アドバイス & 修正提案")
        with st.spinner("計画書の深層AI分析を実行中..."):
            ai_res = run_ai_compliance_review(plan_text, rules_eval, api_provider, api_key)
            if ai_res.get("success"):
                st.success(f"診断完了 ({ai_res.get('provider')})")
                st.markdown(ai_res["summary_analysis"])
            else:
                st.warning(ai_res.get("error"))

        st.markdown("---")

        # 全25項目の詳細評価カード
        st.subheader("📋 倫理指針第7「研究計画書の記載事項」詳細判定 (全25項目)")
        
        filter_status = st.multiselect(
            "ステータスフィルタ",
            ["適合 (記載あり)", "要確認 (記載不十分の可能性)", "未記載 (要対応)", "不適用"],
            default=["適合 (記載あり)", "要確認 (記載不十分の可能性)", "未記載 (要対応)", "不適用"]
        )

        for item in rules_eval["results"]:
            if item["status"] not in filter_status:
                continue

            # ステータスバッジスタイルの決定
            if item["status"] == "適合 (記載あり)":
                badge_html = f'<span class="badge-compliant">適合 ✔</span>'
            elif item["status"] == "要確認 (記載不十分の可能性)":
                badge_html = f'<span class="badge-warning">要確認 ⚠️</span>'
            elif item["status"] == "未記載 (要対応)":
                badge_html = f'<span class="badge-missing">未記載 ❌</span>'
            else:
                badge_html = f'<span class="badge-na">不適用 (適用外)</span>'

            with st.expander(f"【項目 {item['id']}】{item['title']} - {item['category']} | 判定: {item['status']}"):
                st.markdown(f"**判定ステータス**: {badge_html}", unsafe_allow_html=True)
                st.markdown(f"**指針要件**: {item['description']}")
                st.markdown(f"**アドバイス・改善案**: {item['advice']}")
                
                if item["matched_keywords"]:
                    st.markdown(f"**検出キーワード**: `{', '.join(item['matched_keywords'])}`")
                    
                if item["snippets"]:
                    st.markdown("**計画書内の該当箇所スニペット:**")
                    for snip in item["snippets"]:
                        st.markdown(f'<div class="snippet-box">{snip}</div>', unsafe_allow_html=True)

    # ==========================================
    # TAB 2: 対話型チェックリスト & メモ
    # ==========================================
    with tab2:
        st.subheader("📝 対話型セルフチェックリスト")
        st.caption("研究責任者・倫理審査申請担当者が各項目を手動点検・メモ書き入力できるインタラクティブシートです。")

        if "user_checks" not in st.session_state:
            st.session_state.user_checks = {item["id"]: False for item in ETHICS_ITEMS}
        if "user_notes" not in st.session_state:
            st.session_state.user_notes = {item["id"]: "" for item in ETHICS_ITEMS}

        checked_count = sum(1 for v in st.session_state.user_checks.values() if v)
        st.progress(checked_count / len(ETHICS_ITEMS))
        st.write(f"手動セルフチェック完了: **{checked_count} / {len(ETHICS_ITEMS)}** 項目")

        for item in ETHICS_ITEMS:
            col_ck, col_info, col_note = st.columns([0.5, 2.5, 2])
            with col_ck:
                st.session_state.user_checks[item["id"]] = st.checkbox(
                    f"項{item['id']}",
                    value=st.session_state.user_checks[item["id"]],
                    key=f"chk_{item['id']}"
                )
            with col_info:
                st.markdown(f"**{item['id']}. {item['title']}** ({item['category']})")
                st.caption(item["description"])
            with col_note:
                st.session_state.user_notes[item["id"]] = st.text_input(
                    "メモ・対応ノート",
                    value=st.session_state.user_notes[item["id"]],
                    key=f"note_{item['id']}",
                    placeholder="例: 第4章に追記完了"
                )

    # ==========================================
    # TAB 3: 計画書テキストビューアー
    # ==========================================
    with tab3:
        st.subheader(f"📄 アップロード済み研究実施計画書 ({current_filename})")
        
        search_kw = st.text_input("計画書内キーワード検索", placeholder="例: オプトアウト, インフォームド・コンセント, 個人情報")
        
        if search_kw:
            highlighted_text = plan_text.replace(search_kw, f"【{search_kw}】")
            st.info(f"キーワード『{search_kw}』の出現回数: {plan_text.count(search_kw)} 回")
            st.text_area("テキストプレビュー（検索結果ハイライト）", value=highlighted_text, height=500)
        else:
            st.text_area("テキスト全文プレビュー", value=plan_text, height=500)

    # ==========================================
    # TAB 4: 倫理指針ガイドライン検索（Word版）
    # ==========================================
    with tab4:
        st.subheader("📚 「人を対象とする生命科学・医学系研究に関する倫理指針」条文ナレッジベース")
        st.caption("文部科学省・厚生労働省・経済産業省（令和3年告示・令和5年改正） — Wordファイルより正確な条文を表示")

        # 倫理指針Wordを読み込む（キャッシュ利用で高速化）
        @st.cache_resource
        def get_guideline_sections():
            import os
            # app.py の所在ディレクトリを基準に倫理指針ファイルを探す
            base = os.path.dirname(os.path.abspath(__file__))
            docx_path = os.path.join(base, '人を対象とする生命科学・医学系研究に関する倫理指針.docx')
            return load_ethics_guideline_from_docx(docx_path)

        gl_sections = get_guideline_sections()

        if not gl_sections or (len(gl_sections) == 1 and gl_sections[0]['title'] == 'エラー'):
            st.error(gl_sections[0]['content'] if gl_sections else "倫理指針ファイルが見つかりません。")
        else:
            # キーワード検索
            gl_search = st.text_input(
                "🔍 条文キーワード検索",
                placeholder="例: インフォームド・コンセント, 個人情報, モニタリング, 代諾者",
                key="gl_search"
            )

            # 章フィルタ（Heading 1 のみ抽出してセレクトボックス化）
            h1_sections = [s for s in gl_sections if s['level'] == 1]
            chapter_options = ["すべての章を表示"] + [s['title'] for s in h1_sections]
            selected_chapter = st.selectbox("📂 表示する章を絞り込む", chapter_options, key="gl_chapter")

            st.markdown("---")

            # クイックジャンプボタン
            st.markdown("#### 🔖 クイックジャンプ（よく参照される条文）")
            qj_cols = st.columns(4)
            quick_jumps = [
                ("第７条: 研究計画書の記載事項（25項目）", "第７　研究計画書の記載事項"),
                ("第８条: IC手続等", "第８　インフォームド・コンセントを受ける手続等"),
                ("第12条: 利益相反の管理", "第12　利益相反の管理"),
                ("第14条: モニタリング及び監査", "第14　モニタリング及び監査"),
            ]
            for col, (label, target_title) in zip(qj_cols, quick_jumps):
                if col.button(label, use_container_width=True):
                    # セッション状態でジャンプ先を記録
                    st.session_state["gl_jump_target"] = target_title

            st.markdown("---")

            # 表示対象のセクションを絞り込む
            jump_target = st.session_state.get("gl_jump_target", None)
            display_sections = []
            in_chapter = False

            for sec in gl_sections:
                # 章フィルタの適用
                if selected_chapter != "すべての章を表示":
                    if sec['level'] == 1:
                        in_chapter = (sec['title'] == selected_chapter)
                    if not in_chapter:
                        continue

                # キーワード検索フィルタの適用
                if gl_search:
                    combined = sec['title'] + '\n' + sec['content']
                    if gl_search not in combined:
                        continue

                display_sections.append(sec)

            st.caption(f"表示中: {len(display_sections)} セクション")

            # セクションの表示
            for sec in display_sections:
                # 見出しレベルに応じてアイコンとインデントを変更
                if sec['level'] <= 1:
                    icon = "📕"
                    prefix = ""
                elif sec['level'] == 2:
                    icon = "📗"
                    prefix = "　"
                else:
                    icon = "📘"
                    prefix = "　　"

                title_display = f"{prefix}{icon} {sec['title']}"

                # クイックジャンプ対象は自動展開
                auto_expand = (jump_target is not None and jump_target in sec['title'])

                with st.expander(title_display, expanded=auto_expand):
                    content = sec['content']

                    # キーワードハイライト
                    if gl_search and content:
                        content_display = content.replace(gl_search, f"**【{gl_search}】**")
                        st.markdown(content_display)
                    elif content:
                        # 第7条の記載事項は番号リストをきれいに表示
                        if "研究計画書の記載事項" in sec['title']:
                            lines = content.split('\n')
                            for line in lines:
                                line = line.strip()
                                if line:
                                    if line.startswith(('①', '②', '③', '④', '⑤', '⑥', '⑦', '⑧',
                                                        '⑨', '⑩', '⑪', '⑫', '⑬', '⑭', '⑮',
                                                        '⑯', '⑰', '⑱', '⑲', '⑳', '㉑', '㉒', '㉓', '㉔', '㉕')):
                                        st.markdown(f"- {line}")
                                    else:
                                        st.markdown(line)
                        else:
                            st.markdown(content)
                    else:
                        st.caption("（本節の本文はありません）")

    # ==========================================
    # TAB 5: 監査レポート出力
    # ==========================================
    with tab5:
        st.subheader("📥 倫理指針適合性 監査レポートのエクスポート")
        st.caption("審査委員会提出前チェック用のサマリーレポートを出力できます。")

        # レポート文字列の生成
        report_md = f"""# 生命科学・医学系研究 倫理指針適合性審査レポート

- **評価対象ファイル**: {current_filename}
- **総合指針適合率**: {rules_eval['overall_score']}%
- **適合項目**: {rules_eval['compliant_count']} / {rules_eval['applicable_count']} 項目

---

## カテゴリ別評価スコア
"""
        for cat, score in rules_eval["category_scores"].items():
            report_md += f"- **{cat}**: {score}%\n"

        report_md += "\n---\n\n## 全25項目詳細結果一覧\n\n"
        report_md += "| 項番 | 項目名 | カテゴリ | 判定 | 検出キーワード |\n"
        report_md += "|---|---|---|---|---|\n"

        df_list = []
        for item in rules_eval["results"]:
            kws = ", ".join(item["matched_keywords"]) if item["matched_keywords"] else "-"
            report_md += f"| {item['id']} | {item['title']} | {item['category']} | {item['status']} | {kws} |\n"
            df_list.append({
                "項番": item["id"],
                "項目名": item["title"],
                "カテゴリ": item["category"],
                "判定": item["status"],
                "スコア": item["score"],
                "検出キーワード": kws,
                "アドバイス": item["advice"]
            })

        st.markdown(report_md)

        # CSV & MD ダウンロードボタン
        df_report = pd.DataFrame(df_list)
        csv_data = df_report.to_csv(index=False).encode('utf-8-sig')

        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            st.download_button(
                label="📄 Markdownレポートをダウンロード (.md)",
                data=report_md,
                file_name="ethics_compliance_report.md",
                mime="text/markdown"
            )
        with col_dl2:
            st.download_button(
                label="📊 CSVデータ一覧をダウンロード (.csv)",
                data=csv_data,
                file_name="ethics_compliance_data.csv",
                mime="text/csv"
            )

if __name__ == "__main__":
    main()
