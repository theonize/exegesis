"""Disciple perspective: Hermeneutical methods and canonical interpretation."""

PERSPECTIVE_NAME = "disciple"
SECTION_TITLE = "Hermeneutic"

SYSTEM_PROMPT = """You are a biblical hermeneuticist analyzing Scripture within its canonical context.
Trace how themes, images, and ideas develop across the biblical canon.
Identify intertextual connections, wordplay, and idiomatic expressions.
Analyze both micro-structures (within the passage) and macro-structures (larger literary units).
Consider the dual authorship of Scripture (human and divine) and the plenary intent of the text."""

QUESTIONS = [
    "How does this passage fit within over-arching canonical threads and themes?",
    "What wordplay and/or idioms are in use?",
    "What are some notable micro and macro-structures in the passage?",
    "What are the human image-bearer elements of the passage? What are the wisdom elements?",
    "What is the plenary authorship intent in composing this text?",
]


def build_prompt(passage: str) -> str:
    """Build the user prompt for hermeneutical analysis."""
    questions_formatted = "\n".join(f"* {q}" for q in QUESTIONS)
    return f"""Analyze the following biblical passage from a hermeneutical perspective.

Passage: {passage}

Answer each of the following questions with detailed analysis:

{questions_formatted}

Format your response as markdown with each question as a ### heading, followed by your analysis.
Trace canonical connections with specific cross-references. Explain any wordplay or idiomatic
expressions in their original language context. If a question is not directly applicable to
this passage, explain why briefly."""
