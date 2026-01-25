"""Perspective execution with API calls and retry logic."""

import asyncio
import time
import logging
from typing import Optional

import anthropic

from .config import Config
from .models import Passage, PerspectiveResult, PerspectiveStatus
from .prompts import get_prompt_module


class PerspectiveRunner:
    """Runs individual perspective analyses against the Claude API."""

    def __init__(
        self,
        config: Config,
        logger: Optional[logging.Logger] = None,
    ):
        self.config = config
        self.client = anthropic.AsyncAnthropic()
        self.logger = logger or logging.getLogger("exegesis.perspectives")

    async def run_perspective(
        self,
        passage: Passage,
        perspective: str,
        semaphore: Optional[asyncio.Semaphore] = None,
    ) -> PerspectiveResult:
        """Run a single perspective analysis with retry logic.

        Args:
            passage: The passage to analyze
            perspective: Name of the perspective (historian, linguist, etc.)
            semaphore: Optional semaphore for rate limiting

        Returns:
            PerspectiveResult with the analysis or error information
        """
        prompt_module = get_prompt_module(perspective)

        async def _execute():
            return await self._call_api(passage, prompt_module)

        # Use semaphore if provided for rate limiting
        if semaphore:
            async with semaphore:
                return await self._run_with_retry(passage, perspective, _execute)
        else:
            return await self._run_with_retry(passage, perspective, _execute)

    async def _run_with_retry(
        self,
        passage: Passage,
        perspective: str,
        execute_fn,
    ) -> PerspectiveResult:
        """Execute with exponential backoff retry."""
        last_error = None

        for attempt in range(1, self.config.max_retries + 1):
            try:
                start_time = time.time()

                response = await execute_fn()

                duration_ms = int((time.time() - start_time) * 1000)

                result = PerspectiveResult(
                    perspective=perspective,
                    status=PerspectiveStatus.COMPLETED,
                    content=response.content[0].text,
                    input_tokens=response.usage.input_tokens,
                    output_tokens=response.usage.output_tokens,
                    duration_ms=duration_ms,
                    attempt_number=attempt,
                )

                self.logger.info(
                    f"Completed {perspective} for {passage.reference}",
                    extra={
                        "passage_id": passage.id,
                        "perspective": perspective,
                        "duration_ms": duration_ms,
                        "tokens": result.total_tokens,
                    },
                )

                return result

            except anthropic.RateLimitError as e:
                last_error = e
                wait_time = self.config.base_retry_delay * (2 ** (attempt - 1))
                self.logger.warning(
                    f"Rate limited on {perspective} for {passage.reference}, "
                    f"waiting {wait_time}s (attempt {attempt}/{self.config.max_retries})"
                )
                await asyncio.sleep(wait_time)

            except anthropic.APIConnectionError as e:
                # Connection error, retry
                last_error = e
                wait_time = self.config.base_retry_delay * (2 ** (attempt - 1))
                self.logger.warning(
                    f"Connection error on {perspective} for {passage.reference}, "
                    f"waiting {wait_time}s (attempt {attempt}/{self.config.max_retries})"
                )
                await asyncio.sleep(wait_time)

            except anthropic.APIStatusError as e:
                last_error = e
                if e.status_code >= 500:
                    # Server error, retry
                    wait_time = self.config.base_retry_delay * (2 ** (attempt - 1))
                    self.logger.warning(
                        f"API error {e.status_code} on {perspective} for {passage.reference}, "
                        f"waiting {wait_time}s (attempt {attempt}/{self.config.max_retries})"
                    )
                    await asyncio.sleep(wait_time)
                else:
                    # Client error, don't retry
                    break

            except Exception as e:
                last_error = e
                self.logger.error(
                    f"Unexpected error on {perspective} for {passage.reference}: {e}"
                )
                break

        # All retries exhausted or unrecoverable error
        error_msg = str(last_error) if last_error else "Unknown error"
        self.logger.error(
            f"Failed {perspective} for {passage.reference} after {attempt} attempts: {error_msg}"
        )

        return PerspectiveResult(
            perspective=perspective,
            status=PerspectiveStatus.FAILED,
            error_message=error_msg,
            attempt_number=attempt,
        )

    async def _call_api(self, passage: Passage, prompt_module) -> anthropic.types.Message:
        """Make the actual API call."""
        return await self.client.messages.create(
            model=self.config.model,
            max_tokens=self.config.max_tokens,
            system=prompt_module.SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": prompt_module.build_prompt(passage.reference),
                }
            ],
        )
