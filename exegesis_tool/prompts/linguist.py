"""Linguist perspective: Hebrew, Greek, and Aramaic linguistic analysis."""

PERSPECTIVE_NAME = "linguist"
SECTION_TITLE = "Linguistic Analysis"

SYSTEM_PROMPT = """You are a biblical linguist specializing in Hebrew, Greek, and Aramaic.
Provide detailed linguistic analysis including morphology, syntax, semantics, and discourse features.
When discussing original language terms, include transliteration and translation.
Reference textual variants from major manuscript traditions (MT, LXX, DSS, etc.) where relevant.
Explain technical linguistic concepts in accessible terms."""

QUESTIONS = [
    "What was the original language of this writing?",
    "What are the lexical semantics and range of the passage?",
    "What are some notable morphological and grammatical features of the passage?",
    "What are the lexical-syntactical and discourse features of the passage?",
    "What is the etymology of key terms?",
    "What are some notable translation decisions associated with this passage?",
    "What notable textual variants are there?",
]


def build_prompt(passage: str) -> str:
    """Build the user prompt for linguistic analysis."""
    questions_formatted = "\n".join(f"* {q}" for q in QUESTIONS)
    return f"""Analyze the following biblical passage from a linguistic perspective.

Passage: {passage}

Answer each of the following questions with detailed analysis:

{questions_formatted}

Format your response as markdown with each question as a ### heading, followed by your analysis.
Include transliteration of Hebrew/Greek/Aramaic terms in parentheses. Reference manuscript traditions
and textual critical issues where relevant. If a question is not directly applicable to this passage,
explain why briefly."""
