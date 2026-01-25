"""Historian perspective: Historical and cultural background analysis."""

PERSPECTIVE_NAME = "historian"
SECTION_TITLE = "Historical & Cultural Analysis"

SYSTEM_PROMPT = """You are a biblical scholar specializing in ancient Near Eastern history and culture.
Provide detailed, academically rigorous analysis while remaining accessible to educated non-specialists.
Support claims with references to primary sources, archaeological evidence, and scholarly consensus where applicable.
When there is scholarly debate, acknowledge multiple positions and explain the evidence for each."""

QUESTIONS = [
    "Who was the author?",
    "What was the original audience?",
    "When was it originally composed?",
    "When did the events take place?",
    "What are some notable practices of the day?",
    "What archaeology and external histories are associated with the passage?",
    "What was the political-socio-economic milieu of that time? What were the social structures?",
    "What were the circumstantial social norms, practices and issues of the day?",
    "What geography is associated with the passage?",
]


def build_prompt(passage: str) -> str:
    """Build the user prompt for historical/cultural analysis."""
    questions_formatted = "\n".join(f"* {q}" for q in QUESTIONS)
    return f"""Analyze the following biblical passage from a historical and cultural perspective.

Passage: {passage}

Answer each of the following questions with detailed analysis:

{questions_formatted}

Format your response as markdown with each question as a ### heading, followed by your analysis.
Use scholarly citations and references where appropriate. If a question is not directly applicable
to this passage, explain why briefly and provide any relevant tangential information."""
