"""
LLM (Gemini, OpenAI, Anthropic) を用いた高度倫理適合性診断・修正提案生成モジュール
"""
import os
from typing import Dict, Any, List

def run_ai_compliance_review(
    text: str,
    rules_result: Dict[str, Any],
    api_provider: str = "None",
    api_key: str = ""
) -> Dict[str, Any]:
    """
    倫理指針適合性のAIレビューを実行する。
    APIキーが設定されている場合は各プロバイダのLLMを呼び出し、
    そうでない場合はスマートルールベースで高度なレビュー文案・改善アドバイスを生成する。
    """
    
    # 欠陥または要確認の項目を抽出（不適用=None のスコアを除外してTypeErrorを防ぐ）
    flagged_items = [
        item for item in rules_result["results"]
        if item["score"] is not None and item["score"] < 100
    ]
    
    if api_provider == "Google Gemini" and api_key:
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            prompt = f"""
あなたは医学系研究の倫理審査委員会（REC）のベテラン審査員です。
以下の研究実施計画書について、「人を対象とする生命科学・医学系研究に関する倫理指針」への適合性を審査してください。

【計画書テキスト抜粋】
{text[:4000]}

【特に確認すべき不十分な項目】
{', '.join([item['title'] for item in flagged_items])}

上記をもとに、以下の構成で日本語で審査結果と具体的改善アドバイスを出力してください：
1. 総合評価と倫理的妥当性（要約）
2. 指摘事項と具体的な修正・加筆文案（上記項目について計画書に書き加えるべき具体的文章）
3. 倫理審査承認に向けたアドバイス
"""
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            return {
                "success": True,
                "provider": "Google Gemini (gemini-2.5-flash)",
                "summary_analysis": response.text
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Gemini API 呼び出しエラー: {str(e)}",
                "summary_analysis": generate_fallback_ai_analysis(flagged_items, text)
            }
            
    elif api_provider == "OpenAI" and api_key:
        try:
            import openai
            client = openai.OpenAI(api_key=api_key)
            prompt = f"""
あなたは生命科学・医学系研究倫理の専門家です。
「人を対象とする生命科学・医学系研究に関する倫理指針」に基づき、以下の研究計画書の不十分な点をレビューし、具体的な修正文案を提示してください。

【計画書テキスト抜粋】
{text[:4000]}

【不十分な項目】
{', '.join([item['title'] for item in flagged_items])}
"""
            res = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "あなたは医学倫理審査委員会の審査員です。"},
                    {"role": "user", "content": prompt}
                ]
            )
            return {
                "success": True,
                "provider": "OpenAI (gpt-4o-mini)",
                "summary_analysis": res.choices[0].message.content
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"OpenAI API 呼び出しエラー: {str(e)}",
                "summary_analysis": generate_fallback_ai_analysis(flagged_items, text)
            }
            
    # APIキーが指定されていない場合、またはフォールバック時
    return {
        "success": True,
        "provider": "内蔵倫理評価AIエンジン (ルールベース診断)",
        "summary_analysis": generate_fallback_ai_analysis(flagged_items, text)
    }


def generate_fallback_ai_analysis(flagged_items: List[Dict[str, Any]], text: str) -> str:
    """
    APIキーなしで動作する高品質な内蔵倫理診断エンジン
    """
    analysis = "### 📋 内蔵倫理診断AIによる詳細レビューレポート\n\n"
    
    if not flagged_items:
        analysis += "🎉 **素晴らしい研究計画書です！**\n\n"
        analysis += "倫理指針第7に定められた全25の必須記載事項において、必要な要素が網羅されています。倫理審査委員会（REC）への提出にあたり、主要な要件を満たしていると評価されます。\n"
        return analysis
        
    analysis += f"本研究計画書には、倫理審査において追加の確認または記載の充実が推奨される項目が **{len(flagged_items)} 件** 検出されました。\n\n"
    analysis += "--- \n\n"
    analysis += "#### 重点修正・追記が推奨される項目と文案例\n\n"
    
    for item in flagged_items:
        analysis += f"##### 🔹 【項目 {item['id']}】{item['title']} （判定: {item['status']}）\n"
        analysis += f"- **指針要件**: {item['description']}\n"
        analysis += f"- **アドバイス**: {item['advice']}\n"
        analysis += f"- **計画書への追記文案（テンプレート例）**:\n"
        
        # 項目に応じた文案テンプレートの提供
        if item['id'] == 8: # 個人情報
            analysis += "  > *「本研究で取得されたデータはすべて匿名化IDにより管理され、対応表は研究責任者が施錠可能な保管庫（または暗号化ストレージ）にて厳重に保管する。解析データおよび試料には個人の氏名・住所・カルテ番号等の個人識別符号は含めない。」*\n\n"
        elif item['id'] == 10: # 保管・廃棄
            analysis += "  > *「本研究で得られた試料およびデータ（対応表を含む）は、研究結果の最終公表（論文発表）報告から5年間、研究責任者の責任のもと鍵のかかる保管庫にて厳重に保管する。保存期間経過後は、シュレッダー裁断または電子データの復元不能な消去により確実に廃棄する。」*\n\n"
        elif item['id'] == 12: # COI
            analysis += "  > *「本研究の実施にあたり、研究責任者および研究分担者は所属機関の利益相反管理委員会へ申告を行い、適正に管理・承認された状態で研究を実施する。特定企業からの直接的な資金提供や研究結果に影響を与える利害関係は存在しない。」*\n\n"
        elif item['id'] == 13: # 情報公開
            analysis += "  > *「本研究は研究開始前に、国立大学附属病院長会議臨床研究推進データベース（UMIN-CTR）または厚生労働省jRCT等の公的データベースに研究概要を登録し、進捗に応じて遅滞なく更新を行う。」*\n\n"
        elif item['id'] == 14: # 結果取扱い・偶発的所見
            analysis += "  > *「研究により判明した個人の健康に関する重要な偶発的所見（Informed Findings）については、対象者が希望し、かつ臨床的妥当性・有効性が認められる場合に限り、専門医・遺伝カウンセラーの関与のもとで適切な開示と説明を行う。」*\n\n"
        elif item['id'] == 24: # 将来利用・他機関提供
            analysis += "  > *「取得された試料・情報は、本研究の目的達成後も将来の新たな生命科学・医学研究に利用される可能性がある。その場合、倫理審査委員会の審査および研究機関の長の許可を得た上で行い、対象者の拒否の機会（オプトアウト）を確保する。」*\n\n"
        elif item['id'] == 25: # モニタリング
            analysis += "  > *「本研究の信頼性と対象者の安全を確保するため、研究責任者が指定するモニターにより、研究計画書への準拠性、データ入力の正確性、及び有害事象発生時の手続遵守に関する定期的なモニタリングを実施する。」*\n\n"
        else:
            analysis += f"  > *「【{item['title']}に関する追記】本研究における{item['title']}については、関係法令及び『人を対象とする生命科学・医学系研究に関する倫理指針』に則り、適切に実施・管理を行う。」*\n\n"
            
    analysis += "--- \n"
    analysis += "💡 **倫理審査委員会（REC）申請時のワンポイントアドバイス**:\n"
    analysis += "上記の追記文案を研究実施計画書および説明文書・オプトアウト文書に組み込み、倫理審査申請書を作成してください。\n"
    
    return analysis
