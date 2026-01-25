"""Author perspective: Literary analysis of biblical texts."""

PERSPECTIVE_NAME = "author"
SECTION_TITLE = "Literary Analysis"

SYSTEM_PROMPT = """You are a literary scholar specializing in biblical literature.
Analyze texts for genre, structure, rhetorical and literary devices, characterization, and symbolism.
Identify chiastic structures, inclusios, and other macro-structural features.
Pay attention to narrative techniques, poetic devices, and the author's craft.
Connect literary observations to meaning and theological significance."""

QUESTIONS = [
    "What is the genre (and sub-genres) of the passage?",
    "What is the literary structure of the immediate and surrounding context?",
    "What is the voice, mood and style of the passage?",
    "What rhetorical devices are used in the text?",
    "What literary devices are used in the text?",
    "What are the characters and images in use, and their purpose in the passage?",
    "What numerology is in play here?",
    "What colors, items, et cetera have significance?",
]


def build_prompt(passage: str) -> str:
    """Build the user prompt for literary analysis."""
    questions_formatted = "\n".join(f"* {q}" for q in QUESTIONS)
    return f"""Analyze the following biblical passage from a literary perspective.

Passage: {passage}

Answer each of the following questions with detailed analysis:

{questions_formatted}

Format your response as markdown with each question as a ### heading, followed by your analysis.
Identify specific literary techniques with examples from the text. Diagram any chiastic or
parallel structures you identify. If a question is not directly applicable to this passage,
explain why briefly."""
