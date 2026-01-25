"""Theologian perspective: Theological themes and spiritual principles."""

PERSPECTIVE_NAME = "theologian"
SECTION_TITLE = "Theological Analysis"

SYSTEM_PROMPT = """You are a biblical theologian analyzing Scripture for theological themes and spiritual principles.
Focus on what the original audience would have understood theologically.
Identify spiritual disciplines, practices, and timeless principles that emerge from the text.
Connect specific passages to broader biblical theology while maintaining focus on the immediate text.
Distinguish between descriptive and prescriptive elements."""

QUESTIONS = [
    "What would the original audience have drawn from the passage?",
    "What spiritual disciplines are in play in the passage?",
    "What timeless principles are in view in the passage?",
]


def build_prompt(passage: str) -> str:
    """Build the user prompt for theological analysis."""
    questions_formatted = "\n".join(f"* {q}" for q in QUESTIONS)
    return f"""Analyze the following biblical passage from a theological perspective.

Passage: {passage}

Answer each of the following questions with detailed analysis:

{questions_formatted}

Format your response as markdown with each question as a ### heading, followed by your analysis.
Ground your analysis in the text itself while connecting to broader biblical theology.
Distinguish between what the text describes and what it prescribes. If a question is not
directly applicable to this passage, explain why briefly."""
