import re

from utils.constants import DEFAULT_SECTION_NAMES

section_aliases = {
    "治療内容": "治療経過",
    "その他": "備考",
    "補足": "備考",
    "メモ": "備考"
}


def format_output_summary(summary_text):
    processed_text = (
        summary_text.replace('*', '')
        .replace('＊', '')
        .replace('#', '')
        .replace(' ', '')
    )

    return processed_text


def parse_output_summary(summary_text):
    sections = {section: "" for section in DEFAULT_SECTION_NAMES}
    lines = summary_text.split('\n')
    current_section = None

    all_section_names = list(sections.keys()) + list(section_aliases.keys())

    for line in lines:
        line = line.strip()
        if not line:
            continue

        found_section = False
        detected_section = None
        remaining_content = ""

        for section in all_section_names:
            # パターン1: 行頭から始まり、セクション名の後に「:」「：」「】」「」または行末が続く
            # パターン2: 「【」「■」「●」などの記号で始まる
            patterns = [
                rf'^[【\[■●\s]*{re.escape(section)}[】\]\s]*[:：]?\s*(.*)$',  # 【治療経過】: 内容 など
                rf'^{re.escape(section)}\s*[:：]\s*(.*)$',  # 治療経過: 内容
                rf'^{re.escape(section)}\s*$',  # 治療経過（行全体がセクション名のみ）
            ]

            for pattern in patterns:
                match = re.match(pattern, line)
                if match:
                    if section in section_aliases:
                        detected_section = section_aliases[section]
                    else:
                        detected_section = section

                    if match.groups():
                        remaining_content = match.group(1).strip()
                    else:
                        remaining_content = ""

                    found_section = True
                    break

            if found_section:
                break

        if found_section:
            current_section = detected_section
            if remaining_content:
                sections[current_section] = remaining_content
        elif current_section and line:
            # セクションヘッダーではない行を現在のセクションに追加
            if sections[current_section]:
                sections[current_section] += "\n" + line
            else:
                sections[current_section] = line

    return {k: sections.get(k, "") for k in DEFAULT_SECTION_NAMES}