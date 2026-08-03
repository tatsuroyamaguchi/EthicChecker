"""
倫理指針適合性チェッカー Streamlitアプリ用 カスタムCSS & スタイルモジュール
"""
import streamlit as st

def apply_custom_styles():
    st.markdown("""
        <style>
        /* メインコンテナの幅とパディング設定 */
        .main .block-container {
            padding-top: 1.5rem;
            padding-bottom: 3rem;
            max-width: 1200px;
        }

        /* ヘッダーグラデーション */
        .ethic-header {
            background: linear-gradient(135deg, #1A365D 0%, #2B6CB0 50%, #2C5282 100%);
            color: #FFFFFF;
            padding: 24px 32px;
            border-radius: 16px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
            margin-bottom: 24px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .ethic-header h1 {
            color: #FFFFFF !important;
            font-weight: 700;
            font-size: 2.2rem;
            margin-bottom: 8px;
        }

        .ethic-header p {
            color: #E2E8F0 !important;
            font-size: 1.05rem;
            margin-bottom: 0;
        }

        /* カードコンポーネント */
        .ethic-card {
            background: #FFFFFF;
            border-radius: 12px;
            padding: 20px 24px;
            margin-bottom: 16px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
            border: 1px solid #E2E8F0;
            transition: transform 0.2s, box-shadow 0.2s;
        }

        .ethic-card:hover {
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
        }

        /* ステータスバッジ */
        .badge-compliant {
            background-color: #DEF7EC;
            color: #03543F;
            padding: 4px 12px;
            border-radius: 9999px;
            font-weight: 600;
            font-size: 0.85rem;
            display: inline-block;
        }

        .badge-warning {
            background-color: #FEF08A;
            color: #713F12;
            padding: 4px 12px;
            border-radius: 9999px;
            font-weight: 600;
            font-size: 0.85rem;
            display: inline-block;
        }

        .badge-missing {
            background-color: #FDE8E8;
            color: #9B1C1C;
            padding: 4px 12px;
            border-radius: 9999px;
            font-weight: 600;
            font-size: 0.85rem;
            display: inline-block;
        }

        .badge-na {
            background-color: #F3F4F6;
            color: #4B5563;
            padding: 4px 12px;
            border-radius: 9999px;
            font-weight: 500;
            font-size: 0.85rem;
            display: inline-block;
        }

        /* スコア大文字メトリクス */
        .score-box {
            text-align: center;
            background: linear-gradient(145deg, #F8FAFC, #EDF2F7);
            border-radius: 16px;
            padding: 24px;
            border: 1px solid #CBD5E0;
            box-shadow: inset 0 2px 4px rgba(255, 255, 255, 0.8);
        }

        .score-number {
            font-size: 3.5rem;
            font-weight: 800;
            line-height: 1;
            background: -webkit-linear-gradient(45deg, #2B6CB0, #319795);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .score-label {
            font-size: 1.1rem;
            color: #4A5568;
            font-weight: 600;
            margin-top: 8px;
        }

        /* スニペット表示エリア */
        .snippet-box {
            background-color: #F7FAFC;
            border-left: 4px solid #4299E1;
            padding: 10px 14px;
            font-size: 0.9rem;
            color: #2D3748;
            margin-top: 8px;
            border-radius: 0 8px 8px 0;
            font-family: monospace;
        }
        </style>
    """, unsafe_allow_html=True)
