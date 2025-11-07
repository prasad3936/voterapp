import re

def fix_json_page_breaks(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Replace pattern: ] followed by <!-- Page Break --> and json [
    # with a comma to merge arrays
    fixed = re.sub(
        r'\]\s*<!-- Page Break - Batch \d+ -->\s*json\s*\[',
        ',',
        content,
        flags=re.IGNORECASE
    )

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(fixed)

    print(f"Cleaned JSON saved to {output_file}")

# Example usage
fix_json_page_breaks("voters.json", "voter_data.json")