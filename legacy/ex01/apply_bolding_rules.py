
import os
import re

def apply_rules(content):
    # Rule 1: Remove internal space: **Text (Text)** -> **Text(Text)**
    # Be careful not to match too greedy inside **
    # Pattern: ** followed by text, space, (, text, ), **
    content = re.sub(r'\*\*(.*?)\s+\((.*?)\)\*\*', r'**\1(\2)**', content)
    
    # Rule 2: Add external space: **Text(Text)**Suffix -> **Text(Text)** Suffix
    # Match **...)...** followed by a character that is NOT a space, newline, or punctuation
    # We'll use a positive lookahead.
    # We want to add space if the next char is a Korean/English character.
    # Let's say: if followed by non-whitespace and non-punctuation.
    # Punctuation to exclude from adding space: . , ) ] } ! ? : ;
    # But usually user wants space before particles like '가', '을', '는'.
    # So if it's followed by a Hangul or Alphabet, add space.
    content = re.sub(r'(\*\*[^*]+\)\*\*)(?=[가-힣a-zA-Z0-9])', r'\1 ', content)
    
    return content

def process_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            original = f.read()
        
        modified = apply_rules(original)
        
        if original != modified:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(modified)
            print(f"Updated: {filepath}")
        else:
            print(f"Skipped (No changes): {filepath}")
            
    except Exception as e:
        print(f"Error processing {filepath}: {e}")

def main():
    root_dir = "/Users/nomadlab/Desktop/김주혁/workspace/coding-study/ai-llm-rag/실습용/ex01"
    
    # Target files: README.md in root, and all guide.md in subdirectories
    target_files = []
    
    # 1. Root README.md
    readme_path = os.path.join(root_dir, "README.md")
    if os.path.exists(readme_path):
        target_files.append(readme_path)
    
    # 2. All guide.md files
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if "guide.md" in filenames:
            target_files.append(os.path.join(dirpath, "guide.md"))
            
    print(f"Found {len(target_files)} files to process.")
    
    for filepath in target_files:
        process_file(filepath)

if __name__ == "__main__":
    main()
