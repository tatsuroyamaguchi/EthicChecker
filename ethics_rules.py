"""
人を対象とする生命科学・医学系研究に関する倫理指針 (第7 研究計画書の記載事項) 25項目の定義およびルールベース適合性解析モジュール
"""
from typing import Dict, List, Any
import re

ETHICS_ITEMS = [
    {
        "id": 1,
        "title": "研究の名称",
        "category": "1. 基本情報・体制",
        "keywords": ["研究の名称", "研究課題名", "題名", "タイトル", "研究名", "Registry", "レジストリ"],
        "description": "研究の内容を正確かつ具体的に表す名称が記載されているか。",
        "required": True,
        "advice": "研究目的や対象疾患、研究デザイン（観察研究、介入研究等）が明確に分かる名称を設定してください。"
    },
    {
        "id": 2,
        "title": "研究の実施体制",
        "category": "1. 基本情報・体制",
        "keywords": ["研究責任者", "研究代表者", "共同研究機関", "研究協力機関", "実施体制", "研究者", "所属機関", "役割"],
        "description": "すべての研究機関、研究協力機関の名称、研究者等の氏名・所属・役割が明記されているか。",
        "required": True,
        "advice": "多機関共同研究の場合は、研究代表者、共同研究機関、研究協力機関、試料・情報のみ提供する機関等を区別して明記してください。"
    },
    {
        "id": 3,
        "title": "研究の目的及び意義",
        "category": "2. 研究目的・合理性",
        "keywords": ["研究の目的", "目的", "意義", "背景", "学術的背景", "臨床的意義", "臨床的背景"],
        "description": "研究の学術的・社会的背景、目的、期待される科学的・臨床的意義が明確に記載されているか。",
        "required": True,
        "advice": "先行研究のエビデンスと課題、本研究によって解決される学術的・社会的意義を論理的に記述してください。"
    },
    {
        "id": 4,
        "title": "研究の方法及び期間",
        "category": "2. 研究目的・合理性",
        "keywords": ["研究期間", "研究方法", "研究デザイン", "観察期間", "スケジュール", "登録期間", "解析手法", "主要評価項目"],
        "description": "研究のデザイン、具体的な実施方法、対象期間（実施期間・登録期間）が明確に定められているか。",
        "required": True,
        "advice": "研究デザイン（前向き/後向き、観察/介入等）、研究期間（全期間・登録期間・追跡期間）を具体的に記載してください。"
    },
    {
        "id": 5,
        "title": "研究対象者の選定方針",
        "category": "2. 研究目的・合理性",
        "keywords": ["選択基準", "除外基準", "インクルージョン", "エクスクルージョン", "対象者", "選定基準", "目標症例数"],
        "description": "選択基準・除外基準、目標症例数およびその設定根拠が科学的・倫理的に適正に設定されているか。",
        "required": True,
        "advice": "対象者の選定において不当な差別や偏りが生じないよう、明確な選択基準・除外基準を設定してください。"
    },
    {
        "id": 6,
        "title": "研究の科学的合理性の根拠",
        "category": "2. 研究目的・合理性",
        "keywords": ["科学的根拠", "科学的合理性", "統計学的根拠", "サンプルサイズ", "目標症例数の根拠", "統計解析"],
        "description": "目標症例数の統計学的算出根拠や、研究計画の科学的妥当性が裏付けられているか。",
        "required": True,
        "advice": "主要評価項目に基づき、パワー計算や統計学的根拠に基づく目標症例数の算出理由を明記してください。"
    },
    {
        "id": 7,
        "title": "インフォームド・コンセント(IC)の手続等",
        "category": "3. IC・対象者保護",
        "keywords": ["インフォームド・コンセント", "IC", "説明と同意", "オプトアウト", "オプトイン", "同意書", "説明文書", "文書による同意"],
        "description": "ICを取得する手続（説明文書・同意書の使用、オプトアウト手続き等）が指針第8に従って規定されているか。",
        "required": True,
        "advice": "文書によるIC取得、またはオプトアウト（適切な通知・公開と拒否機会の保障）の手続を具体的に記載してください。"
    },
    {
        "id": 8,
        "title": "個人情報等の取扱い",
        "category": "4. 個人情報・安全管理",
        "keywords": ["個人情報", "仮名加工", "匿名化", "対応表", "安全管理", "ID管理", "保護", "個人識別符号", "漏えい"],
        "description": "個人情報等の加工方法（仮名加工・匿名化・対応表管理）、安全管理措置および漏えい防止対策が明記されているか。",
        "required": True,
        "advice": "対応表の管理方法、ID化の手順、データの外部送信・クラウド保存時のセキュリティ対策を明記してください。"
    },
    {
        "id": 9,
        "title": "負担・リスク・利益評価とリスク最小化対策",
        "category": "3. IC・対象者保護",
        "keywords": ["リスク", "負担", "利益", "不利益", "予測されるリスク", "最小化", "総合的評価", "安全対策"],
        "description": "対象者に生じる心理的・身体的負担やリスク、期待される利益、及びリスクを最小化する対策が評価されているか。",
        "required": True,
        "advice": "予想されるリスク（個人情報漏えい、身体的負担等）と、それを予防・最小化するための具体的対策を記載してください。"
    },
    {
        "id": 10,
        "title": "試料・情報の保管及び廃棄の方法",
        "category": "4. 個人情報・安全管理",
        "keywords": ["保管", "廃棄", "保存期間", "保管場所", "シュレッダー", "消去", "保管期間", "ロックダウン"],
        "description": "試料や情報の保管場所、保管期間（原則論文公表後一定期間）、廃棄の手順が具体的に規定されているか。",
        "required": True,
        "advice": "保管期間（例: 研究終了報告から5年/10年間）や保管責任者、廃棄時の完全消去・無効化方法を規定してください。"
    },
    {
        "id": 11,
        "title": "研究機関の長への報告内容及び方法",
        "category": "1. 基本情報・体制",
        "keywords": ["研究機関の長", "報告", "進捗報告", "年次報告", "終了報告", "不適合報告", "定期報告"],
        "description": "進捗状況、研究終了、不適合・重大な有害事象発生時の研究機関の長への報告規定が含まれているか。",
        "required": True,
        "advice": "年に1回の定期報告や、重大な不適合発生時の緊急報告手続について記載してください。"
    },
    {
        "id": 12,
        "title": "利益相反（COI）の管理状況",
        "category": "5. リスク・COI・その他",
        "keywords": ["利益相反", "COI", "Conflict of Interest", "資金源", "研究費", "企業COI", "利益相反委員会"],
        "description": "研究の資金源、研究機関・研究者個人の利益相反状況および管理方法が明示されているか。",
        "required": True,
        "advice": "研究費の出所（公的資金、企業奨学寄付金等）および利益相反審査委員会での自己申告・承認状況を明記してください。"
    },
    {
        "id": 13,
        "title": "研究に関する情報公開の方法",
        "category": "5. リスク・COI・その他",
        "keywords": ["情報公開", "データベース", "jRCT", "UMIN", "公開データベース", "臨床研究登録", "研究の登録"],
        "description": "研究概要の公開データベース（jRCT, UMIN-CTR, JRCT等）への登録・公開方法が規定されているか。",
        "required": True,
        "advice": "原則として研究開始前に公的データベース（jRCT, UMIN等）に登録・公開する方針を記載してください。"
    },
    {
        "id": 14,
        "title": "研究により得られた結果等の取扱い",
        "category": "5. リスク・COI・その他",
        "keywords": ["結果の開示", "結果の取扱い", "偶発的所見", "開示方針", "研究結果の公表", "学会発表", "論文発表"],
        "description": "研究対象者本人への結果・偶発的所見（Informed Findings）の開示方針および結果の論文・学会公表方針が示されているか。",
        "required": True,
        "advice": "臨床的意義のある個別結果や偶発的所見の開示基準・対応方針について明記してください。"
    },
    {
        "id": 15,
        "title": "相談窓口体制の整備",
        "category": "3. IC・対象者保護",
        "keywords": ["相談窓口", "問い合わせ", "連絡先", "苦情", "遺伝カウンセリング", "問合せ先", "電話番号"],
        "description": "研究対象者や家族からの相談、問い合わせ、苦情等に対応する窓口・連絡先が設置されているか。",
        "required": True,
        "advice": "研究対象者等が気軽に質問や相談ができる問い合わせ窓口（担当者、電話番号、メール等）を設けてください。"
    },
    {
        "id": 16,
        "title": "代諾者等からのIC手続",
        "category": "3. IC・対象者保護",
        "condition_flag": "has_substitute",
        "keywords": ["代諾", "代諾者", "法定代理人", "配偶者", "親権者", "選定方針"],
        "description": "対象者が意思決定能力を欠く場合に、代諾者を選定する方針及びIC手続が定められているか。",
        "required": False,
        "advice": "未成年者や認知症患者等が含まれる場合、代諾者の選定順位（親権者、配偶者等）と説明同意手続を明記してください。"
    },
    {
        "id": 17,
        "title": "インフォームド・アセントの手続",
        "category": "3. IC・対象者保護",
        "condition_flag": "has_minors",
        "keywords": ["アセント", "インフォームド・アセント", "小児", "わかりやすい説明", "アセント文書"],
        "description": "未成年者等の対象者から年齢・理解力に応じたアセント（賛同）を得る手続が定められているか。",
        "required": False,
        "advice": "7歳〜15歳程度の小児が対象に含まれる場合、平易な表現を用いたアセント文書と説明手続を用意してください。"
    },
    {
        "id": 18,
        "title": "IC免除・要件充足の判断理由",
        "category": "3. IC・対象者保護",
        "condition_flag": "use_optout",
        "keywords": ["IC不要", "ICの免除", "要件を満たす", "オプトアウト", "拒否の機会", "学術研究機関"],
        "description": "ICを受けないで研究を実施する場合（オプトアウト等）、指針第8の7の要件を満たす判断根拠が示されているか。",
        "required": False,
        "advice": "オプトアウトを適用する場合、研究の必要性、社会的重要度、対象者への危険性のなさ等の適用理由を明記してください。"
    },
    {
        "id": 19,
        "title": "経済的負担及び謝礼の有無・内容",
        "category": "3. IC・対象者保護",
        "keywords": ["経済的負担", "謝礼", "クオカード", "交通費", "負担額", "謝金", "無償"],
        "description": "研究対象者に生じる経済的負担（検査費自費等）や謝礼（交通費補助、電子マネー等）の有無と具体的な内容。",
        "required": True,
        "advice": "対象者の自己負担の有無、謝礼の有無・金額・支給基準を明確に記載してください。"
    },
    {
        "id": 20,
        "title": "重篤な有害事象発生時の対応体制",
        "category": "3. IC・対象者保護",
        "condition_flag": "is_invasive",
        "keywords": ["重篤な有害事象", "有害事象", "SAE", "副作用", "緊急対応", "報告体制"],
        "description": "侵襲を伴う研究において、重篤な有害事象（SAE）が発生した際の医療対応および緊急報告手続が整備されているか。",
        "required": False,
        "advice": "侵襲を伴う研究では、SAE発生時の迅速な救急処置体制および倫理委員会・長への緊急報告フローを記載してください。"
    },
    {
        "id": 21,
        "title": "健康被害に対する補償の有無及び内容",
        "category": "3. IC・対象者保護",
        "condition_flag": "is_invasive",
        "keywords": ["補償", "健康被害", "臨床研究保険", "損害賠償", "医療費給付"],
        "description": "侵襲を伴う研究において、研究に起因する健康被害が発生した場合の補償（保険加入等）の有無と内容が示されているか。",
        "required": False,
        "advice": "侵襲を伴う介入研究等では、補償保険の加入状況や医療費・医療手当の給付規定について明記してください。"
    },
    {
        "id": 22,
        "title": "研究終了後における医療の提供対応",
        "category": "3. IC・対象者保護",
        "condition_flag": "is_interventional",
        "keywords": ["研究終了後", "医療の提供", "継続投与", "後治療", "最善の治療"],
        "description": "通常の診療を超える医療行為を伴う研究において、研究終了後に対象者が継続して最善の医療を受けられる対応。",
        "required": False,
        "advice": "試験薬・試験治療の終了後、対象者に継続して適切な診療・後治療を提供する方針を記載してください。"
    },
    {
        "id": 23,
        "title": "業務委託の内容及び監督方法",
        "category": "1. 基本情報・体制",
        "condition_flag": "has_outsourcing",
        "keywords": ["委託", "業務委託", "CRO", "受託機関", "監督", "再委託", "委託契約"],
        "description": "研究業務の一部を外部委託する場合（データ解析、検査受託等）、業務内容と委託先への監督方法が定められているか。",
        "required": False,
        "advice": "外部受託機関（CRO、検査会社等）を利用する場合、委託内容、個人情報保護措置、立入検査等の監督規定を記載してください。"
    },
    {
        "id": 24,
        "title": "将来の研究利用・他機関提供の可能性",
        "category": "5. リスク・COI・その他",
        "keywords": ["将来の研究", "二次利用", "他機関への提供", "バンク", "バイオバンク", "分譲"],
        "description": "取得した試料・情報が将来の特定されない研究に利用される可能性や、他機関へ提供される可能性についての明記。",
        "required": True,
        "advice": "将来の二次利用や他機関提供の可能性がある場合、同意時点で想定される研究内容や提供先情報の確認方法を記載してください。"
    },
    {
        "id": 25,
        "title": "モニタリング及び監査の実施体制・手順",
        "category": "1. 基本情報・体制",
        "keywords": ["モニタリング", "監査", "品質保証", "データの信頼性", "モニター", "監査担当者"],
        "description": "研究の品質保証およびデータの信頼性確保のため、モニタリングや監査の実施体制・手順が規定されているか。",
        "required": True,
        "advice": "侵襲や介入を伴う研究を中心に、研究の進捗やデータ正確性を確認するモニタリング・監査計画を明示してください。"
    }
]

def evaluate_compliance(text: str, flags: Dict[str, bool]) -> Dict[str, Any]:
    """
    研究実施計画書のテキストと各種研究フラグ（侵襲有無、介入有無等）を入力として受け取り、
    全25項目の適合性を自動評価する。
    """
    results = []
    applicable_count = 0
    compliant_count = 0
    category_scores = {}

    for item in ETHICS_ITEMS:
        item_id = item["id"]
        title = item["title"]
        category = item["category"]
        keywords = item["keywords"]
        cond_flag = item.get("condition_flag")

        # 適用区分の判定
        is_applicable = True
        if cond_flag:
            if cond_flag == "is_invasive" and not flags.get("is_invasive", False):
                is_applicable = False
            elif cond_flag == "is_interventional" and not flags.get("is_interventional", False):
                is_applicable = False
            elif cond_flag == "has_substitute" and not flags.get("has_substitute", False):
                is_applicable = False
            elif cond_flag == "has_minors" and not flags.get("has_minors", False):
                is_applicable = False
            elif cond_flag == "use_optout" and not flags.get("use_optout", False):
                is_applicable = False
            elif cond_flag == "has_outsourcing" and not flags.get("has_outsourcing", False):
                is_applicable = False

        if not is_applicable:
            results.append({
                "id": item_id,
                "title": title,
                "category": category,
                "status": "不適用",
                "score": None,
                "matched_keywords": [],
                "description": item["description"],
                "advice": "本研究区分では適用外（不適用）項目として扱われます。",
                "snippets": []
            })
            continue

        applicable_count += 1

        # テキスト検索とキーワード抽出
        matched_kw = []
        snippets = []

        for kw in keywords:
            pattern = re.compile(re.escape(kw), re.IGNORECASE)
            matches = list(pattern.finditer(text))
            if matches:
                matched_kw.append(kw)
                for m in matches[:2]:
                    start = max(0, m.start() - 40)
                    end = min(len(text), m.end() + 80)
                    snippet = text[start:end].replace("\n", " ")
                    snippets.append(f"...{snippet}...")

        snippets = list(dict.fromkeys(snippets))[:3]

        # ステータス判定ロジック
        if len(matched_kw) >= 2 or (len(matched_kw) >= 1 and len(snippets) >= 2):
            status = "適合 (記載あり)"
            score = 100
            compliant_count += 1
            advice = "指針の要求項目が計画書内に十分に記載されています。"
        elif len(matched_kw) == 1:
            status = "要確認 (記載不十分の可能性)"
            score = 50
            compliant_count += 0.5
            advice = f"キーワード『{matched_kw[0]}』が検出されましたが、記載内容が不十分な可能性があります。より具体的な記述を追加することを検討してください。"
        else:
            status = "未記載 (要対応)"
            score = 0
            advice = f"【注意】本項目に関する明確な記述が検出されませんでした。倫理審査で指摘を受ける可能性があるため、以下の記述の追加を強く推奨します：{item['advice']}"

        if category not in category_scores:
            category_scores[category] = {"total_applicable": 0, "total_score": 0}

        category_scores[category]["total_applicable"] += 1
        category_scores[category]["total_score"] += score

        results.append({
            "id": item_id,
            "title": title,
            "category": category,
            "status": status,
            "score": score,
            "matched_keywords": matched_kw,
            "description": item["description"],
            "advice": advice,
            "snippets": snippets
        })

    # カテゴリ別達成率算出
    cat_summary = {}
    for cat, data in category_scores.items():
        if data["total_applicable"] > 0:
            cat_summary[cat] = round(data["total_score"] / data["total_applicable"], 1)
        else:
            cat_summary[cat] = 100.0

    overall_score = round((compliant_count / applicable_count * 100), 1) if applicable_count > 0 else 100.0

    return {
        "overall_score": overall_score,
        "applicable_count": applicable_count,
        "compliant_count": compliant_count,  # floatのまま返す（0.5単位の半適合を正確に維持）
        "results": results,
        "category_scores": cat_summary
    }
