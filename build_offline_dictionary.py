import json
import os
import sqlite3
import sys

OUTPUT_DB = "offline_dictionary.db"


def extract_primary_entry(word_data: dict):
    etymologies = word_data.get("etymologies") or []
    primary_pos = ""
    primary_sense = ""
    primary_example = ""
    extra_senses = []

    for ety in etymologies:
        for pos_block in ety.get("partsOfSpeech") or []:
            pos = pos_block.get("partOfSpeech", "")
            for sense_block in pos_block.get("senses") or []:
                sense_text = (sense_block.get("sense") or "").strip()
                if not sense_text:
                    continue
                if not primary_sense:
                    primary_pos = pos
                    primary_sense = sense_text
                    examples = sense_block.get("examples") or []
                    if examples:
                        primary_example = examples[0]
                else:
                    extra_senses.append(sense_text)

    return primary_pos, primary_sense, primary_example, extra_senses


def main():
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python build_offline_dictionary.py <path-to-api-folder>")

    api_dir = sys.argv[1]
    if not os.path.isdir(api_dir):
        raise SystemExit(f"Not a directory: {api_dir}")

    if os.path.exists(OUTPUT_DB):
        os.remove(OUTPUT_DB)

    conn = sqlite3.connect(OUTPUT_DB)
    conn.execute("""
        CREATE TABLE words (
            word TEXT PRIMARY KEY,
            part_of_speech TEXT,
            definition TEXT NOT NULL,
            example TEXT,
            extra_senses TEXT
        )
    """)

    json_files = []
    for root, _dirs, files in os.walk(api_dir):
        for name in files:
            if name.endswith(".json"):
                json_files.append(os.path.join(root, name))

    total_words = 0
    rows = []

    for i, path in enumerate(json_files):
        with open(path, encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                continue

        for word, word_data in data.items():
            if not isinstance(word_data, dict):
                continue
            pos, sense, example, extra = extract_primary_entry(word_data)
            if not sense:
                continue
            clean_word = word.strip().upper()
            if not clean_word:
                continue
            extra_joined = " | ".join(extra[:4])
            rows.append((clean_word, pos, sense, example, extra_joined))
            total_words += 1

        if (i + 1) % 100 == 0:
            print(f"Processed {i + 1}/{len(json_files)} files, {total_words} words so far...")

    conn.executemany(
        "INSERT OR REPLACE INTO words (word, part_of_speech, definition, example, extra_senses) "
        "VALUES (?, ?, ?, ?, ?)",
        rows,
    )
    conn.execute("CREATE INDEX idx_word ON words(word)")
    conn.commit()
    conn.close()

    print(f"Built {OUTPUT_DB} with {total_words} words.")


if __name__ == "__main__":
    main()
