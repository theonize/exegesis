"""Orchestration of exegesis processing with parallel execution."""

import asyncio
import logging
from pathlib import Path
from typing import List, Optional

from .config import Config
from .database import Database
from .models import (
    Passage, PassageStatus, PerspectiveResult, PerspectiveStatus, CompilationResult
)
from .perspectives import PerspectiveRunner
from .compiler import compile_perspectives
from .prompts import PERSPECTIVES


class ExegesisOrchestrator:
    """Orchestrates exegesis processing with parallel perspective execution."""

    def __init__(
        self,
        config: Config,
        db: Database,
        logger: Optional[logging.Logger] = None,
    ):
        self.config = config
        self.db = db
        self.logger = logger or logging.getLogger("exegesis.orchestrator")
        self.perspective_runner = PerspectiveRunner(config, logger)
        self.semaphore = asyncio.Semaphore(config.max_concurrent_requests)

    async def process_passage(self, passage: Passage) -> CompilationResult:
        """Process a single passage through all 6 perspectives.

        Args:
            passage: The passage to analyze

        Returns:
            CompilationResult with all perspective analyses compiled
        """
        self.logger.info(f"Starting processing of {passage.reference}")

        # Mark as in_progress
        self.db.update_passage_status(passage.id, PassageStatus.IN_PROGRESS)

        # Run all perspectives in parallel
        tasks = [
            self.perspective_runner.run_perspective(passage, perspective, self.semaphore)
            for perspective in PERSPECTIVES
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results, handling any exceptions
        perspective_results: List[PerspectiveResult] = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.error(f"Exception in {PERSPECTIVES[i]}: {result}")
                perspective_results.append(
                    PerspectiveResult(
                        perspective=PERSPECTIVES[i],
                        status=PerspectiveStatus.FAILED,
                        error_message=str(result),
                    )
                )
            else:
                perspective_results.append(result)

        # Save all perspective runs to database
        for result in perspective_results:
            self.db.save_perspective_run(passage.id, result)

        # Compile results
        compilation = self._compile_and_save(passage, perspective_results)

        return compilation

    async def process_batch(self, passages: List[Passage]) -> List[CompilationResult]:
        """Process multiple passages.

        Args:
            passages: List of passages to process

        Returns:
            List of CompilationResults
        """
        self.logger.info(f"Starting batch processing of {len(passages)} passages")

        results = []
        for passage in passages:
            try:
                result = await self.process_passage(passage)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Error processing {passage.reference}: {e}")
                # Mark as failed
                self.db.update_passage_status(passage.id, PassageStatus.FAILED)
                results.append(
                    CompilationResult(
                        passage=passage,
                        perspectives=[],
                        is_complete=False,
                        failed_perspectives=PERSPECTIVES.copy(),
                    )
                )

        self.logger.info(
            f"Batch complete: {sum(1 for r in results if r.is_complete)}/{len(results)} successful"
        )

        return results

    async def retry_perspectives(
        self,
        passages: List[Passage],
        perspectives: List[str],
    ) -> List[CompilationResult]:
        """Retry specific perspectives for passages.

        Args:
            passages: List of passages to retry
            perspectives: List of perspective names to retry

        Returns:
            List of CompilationResults
        """
        self.logger.info(
            f"Retrying {len(perspectives)} perspectives for {len(passages)} passages"
        )

        results = []
        for passage in passages:
            # Get existing successful runs
            existing_runs = self.db.get_latest_perspective_runs(passage.id)
            existing_by_name = {r.perspective: r for r in existing_runs}

            # Mark as in_progress
            self.db.update_passage_status(passage.id, PassageStatus.IN_PROGRESS)

            # Run only the specified perspectives
            tasks = [
                self.perspective_runner.run_perspective(passage, p, self.semaphore)
                for p in perspectives
            ]

            new_results = await asyncio.gather(*tasks, return_exceptions=True)

            # Merge with existing results
            all_results: List[PerspectiveResult] = []
            for perspective in PERSPECTIVES:
                if perspective in perspectives:
                    # Find the new result for this perspective
                    idx = perspectives.index(perspective)
                    result = new_results[idx]
                    if isinstance(result, Exception):
                        all_results.append(
                            PerspectiveResult(
                                perspective=perspective,
                                status=PerspectiveStatus.FAILED,
                                error_message=str(result),
                            )
                        )
                    else:
                        all_results.append(result)
                        self.db.save_perspective_run(passage.id, result)
                elif perspective in existing_by_name:
                    all_results.append(existing_by_name[perspective])

            compilation = self._compile_and_save(passage, all_results)
            results.append(compilation)

        return results

    def _compile_and_save(
        self,
        passage: Passage,
        perspective_results: List[PerspectiveResult],
    ) -> CompilationResult:
        """Compile perspective results and save to file if complete."""
        # Check for failures
        failed = [r.perspective for r in perspective_results if not r.is_success]

        # Compile markdown
        compiled_content = compile_perspectives(passage, perspective_results)

        # Determine if complete (all perspectives succeeded)
        is_complete = len(failed) == 0

        if is_complete:
            # Write output file
            output_path = self._write_output(passage, compiled_content)
            self.db.update_passage_status(
                passage.id, PassageStatus.COMPLETED, output_path
            )
            self.logger.info(f"Completed {passage.reference} -> {output_path}")
        else:
            self.db.update_passage_status(passage.id, PassageStatus.FAILED)
            self.logger.warning(
                f"Incomplete {passage.reference}, failed perspectives: {', '.join(failed)}"
            )

        return CompilationResult(
            passage=passage,
            perspectives=perspective_results,
            compiled_content=compiled_content,
            is_complete=is_complete,
            failed_perspectives=failed,
        )

    def _write_output(self, passage: Passage, content: str) -> str:
        """Write compiled content to output file."""
        output_dir = Path(self.config.content_dir) / passage.book / f"{passage.chapter:02d}"
        output_dir.mkdir(parents=True, exist_ok=True)

        output_path = output_dir / passage.filename
        output_path.write_text(content, encoding="utf-8")

        return str(output_path)
