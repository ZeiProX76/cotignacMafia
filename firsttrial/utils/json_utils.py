"""JSON utilities for parsing, cleaning, and saving responses."""

import json
from pathlib import Path
from typing import Any, Dict, Union


def clean_json_response(response_text: str) -> str:
    """
    Clean JSON response by removing markdown code blocks.

    Args:
        response_text: Raw response text that may contain ```json``` blocks

    Returns:
        Cleaned JSON string

    Examples:
        >>> clean_json_response('```json\\n{"key": "value"}\\n```')
        '{"key": "value"}'
    """
    cleaned = response_text.strip()

    # Remove markdown code blocks
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]

    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]

    return cleaned.strip()


def save_json(
    data: Union[Dict, str],
    output_path: Union[str, Path],
    indent: int = 2,
    ensure_ascii: bool = False
) -> Path:
    """
    Save data to JSON file.

    Args:
        data: Dictionary or JSON string to save
        output_path: Output file path
        indent: JSON indentation level
        ensure_ascii: Whether to escape non-ASCII characters

    Returns:
        Path object of saved file
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # If data is already a string (JSON), parse it first to validate
    if isinstance(data, str):
        data = json.loads(data)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii)

    return output_path


def load_json(input_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Load JSON from file.

    Args:
        input_path: Path to JSON file

    Returns:
        Parsed JSON as dictionary

    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file contains invalid JSON
    """
    input_path = Path(input_path)

    if not input_path.exists():
        raise FileNotFoundError(f"JSON file not found: {input_path}")

    with open(input_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def parse_and_save_json(
    response_text: str,
    output_path: Union[str, Path],
    validate_schema: bool = True
) -> Dict[str, Any]:
    """
    Clean, parse, and save JSON response in one step.

    Args:
        response_text: Raw response text
        output_path: Output file path
        validate_schema: Whether to validate JSON structure

    Returns:
        Parsed JSON dictionary

    Raises:
        json.JSONDecodeError: If response is not valid JSON
    """
    cleaned = clean_json_response(response_text)

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse JSON response:")
        print(f"   {cleaned[:500]}...")
        raise e

    if validate_schema and not isinstance(parsed, dict):
        raise ValueError(f"Expected JSON object (dict), got {type(parsed)}")

    save_json(parsed, output_path)
    return parsed


def pretty_print_json(data: Union[Dict, str], max_depth: int = 3) -> None:
    """
    Pretty print JSON data to console.

    Args:
        data: Dictionary or JSON string
        max_depth: Maximum depth to display (None for unlimited)
    """
    if isinstance(data, str):
        data = json.loads(data)

    print(json.dumps(data, indent=2, ensure_ascii=False))
