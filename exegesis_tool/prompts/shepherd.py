"""Shepherd perspective: Practical application for modern audiences."""

PERSPECTIVE_NAME = "shepherd"
SECTION_TITLE = "Application"

SYSTEM_PROMPT = """You are a pastoral theologian helping bridge ancient Scripture to modern life.
Clarify the original meaning in terms a contemporary audience can understand.
Identify what changes in belief, attitude, or action the text calls for.
Provide practical, concrete ways to implement biblical principles.
Distinguish between the timeless meaning and the culturally-bound methods of application."""

QUESTIONS = [
    "Clarify the original meaning for a modern audience",
    "What attributes or actions, of the modern audience, must change according to this Word?",
    "When, where and how might we implement these changes?",
    "Meaning versus method: how might I accomplish these things?",
]


def build_prompt(passage: str) -> str:
    """Build the user prompt for practical application."""
    questions_formatted = "\n".join(f"* {q}" for q in QUESTIONS)
    return f"""Analyze the following biblical passage for practical application.

Passage: {passage}

Answer each of the following questions with detailed analysis:

{questions_formatted}

Format your response as markdown with each question as a ### heading, followed by your analysis.
Be specific and practical in your applications. Distinguish between the timeless principle
(meaning) and the various ways it might be implemented (method). If a question is not directly
applicable to this passage, explain why briefly."""
