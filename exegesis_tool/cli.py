"""Command-line interface for exegesis tool."""

import asyncio
import click
from pathlib import Path
from dotenv import load_dotenv

# Load .env file before anything else
load_dotenv()

from .config import Config, setup_logging
from .database import Database
from .models import Passage, PassageStatus


@click.group()
@click.option("--db", default="exegesis.db", help="Database path", envvar="EXEGESIS_DB")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.pass_context
def cli(ctx, db: str, verbose: bool):
    """Exegesis research automation tool using Claude API."""
    ctx.ensure_object(dict)
    config = Config.from_env()
    config.db_path = db
    if verbose:
        config.log_level = "DEBUG"
    ctx.obj["config"] = config
    ctx.obj["db"] = Database(db)
    ctx.obj["logger"] = setup_logging(config)


@cli.command()
@click.argument("passage")
@click.pass_context
def run(ctx, passage: str):
    """Process a single passage.

    Example: exegesis run "GEN 01:26-31"
    """
    from .orchestrator import ExegesisOrchestrator

    config = ctx.obj["config"]
    db = ctx.obj["db"]
    logger = ctx.obj["logger"]

    try:
        p = Passage.from_reference(passage)
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)

    # Check if passage exists in DB, if not add it
    existing = db.get_passage_by_reference(p.book, p.chapter, p.verse_start, p.verse_end)
    if existing:
        if existing.status == PassageStatus.COMPLETED:
            click.echo(f"Passage {passage} already completed. Use --force to reprocess.")
            return
        p = existing
    else:
        p.id = db.upsert_passage(p)

    click.echo(f"Processing {p.reference}...")

    orchestrator = ExegesisOrchestrator(config, db, logger)
    result = asyncio.run(orchestrator.process_passage(p))

    if result.is_complete:
        click.echo(f"Completed: {result.passage.output_path}")
        click.echo(f"Tokens used: {result.total_tokens:,}")
    else:
        click.echo(f"Failed perspectives: {', '.join(result.failed_perspectives)}", err=True)
        raise SystemExit(1)


@cli.command()
@click.option("--count", "-n", default=5, help="Number of passages to process")
@click.option("--book", "-b", help="Filter by book (e.g., GEN)")
@click.pass_context
def batch(ctx, count: int, book: str):
    """Process multiple pending passages.

    Example: exegesis batch -n 10 --book GEN
    """
    from .orchestrator import ExegesisOrchestrator

    config = ctx.obj["config"]
    db = ctx.obj["db"]
    logger = ctx.obj["logger"]

    passages = db.get_pending_passages(limit=count, book=book)
    if not passages:
        click.echo("No pending passages found.")
        return

    click.echo(f"Processing {len(passages)} passages...")

    # Claim all passages atomically
    passage_ids = [p.id for p in passages]
    claimed = db.claim_passages(passage_ids)
    click.echo(f"Claimed {claimed} passages for processing.")

    orchestrator = ExegesisOrchestrator(config, db, logger)
    results = asyncio.run(orchestrator.process_batch(passages))

    completed = sum(1 for r in results if r.is_complete)
    failed = len(results) - completed

    click.echo(f"\nCompleted: {completed}/{len(passages)}")
    if failed:
        click.echo(f"Failed: {failed}")
        for r in results:
            if not r.is_complete:
                click.echo(f"  - {r.passage.reference}: {', '.join(r.failed_perspectives)}")


@cli.command()
@click.pass_context
def status(ctx):
    """Show processing status summary."""
    db = ctx.obj["db"]
    summary = db.get_status_summary()
    total_tokens = db.get_total_tokens_used()

    click.echo(str(summary))
    click.echo(f"\nTotal tokens used: {total_tokens:,}")


@cli.command("retry-failed")
@click.option("--perspective", "-p", help="Retry only specific perspective")
@click.option("--limit", "-n", default=10, help="Maximum passages to retry")
@click.pass_context
def retry_failed(ctx, perspective: str, limit: int):
    """Retry all failed passages or specific perspectives.

    Example: exegesis retry-failed -p historian
    """
    from .orchestrator import ExegesisOrchestrator

    config = ctx.obj["config"]
    db = ctx.obj["db"]
    logger = ctx.obj["logger"]

    failed_passages = db.get_failed_passages(limit=limit)
    if not failed_passages:
        click.echo("No failed passages found.")
        return

    click.echo(f"Retrying {len(failed_passages)} failed passages...")

    # Reset status to pending for retry
    for p in failed_passages:
        db.update_passage_status(p.id, PassageStatus.PENDING)

    orchestrator = ExegesisOrchestrator(config, db, logger)

    if perspective:
        click.echo(f"Retrying only '{perspective}' perspective...")
        results = asyncio.run(orchestrator.retry_perspectives(failed_passages, [perspective]))
    else:
        results = asyncio.run(orchestrator.process_batch(failed_passages))

    completed = sum(1 for r in results if r.is_complete)
    click.echo(f"\nRetried: {completed}/{len(failed_passages)} now complete")


@cli.command("import-todo")
@click.argument("todo_path", type=click.Path(exists=True))
@click.pass_context
def import_todo(ctx, todo_path: str):
    """Import passages from TODO.md file.

    Example: exegesis import-todo TODO.md
    """
    from .importer import import_from_todo

    db = ctx.obj["db"]
    count = import_from_todo(db, todo_path)
    click.echo(f"Imported {count} passages")

    summary = db.get_status_summary()
    click.echo(f"\nDatabase now contains:")
    click.echo(str(summary))


@cli.command("export-todo")
@click.argument("todo_path", type=click.Path())
@click.pass_context
def export_todo(ctx, todo_path: str):
    """Export passage status back to TODO.md format.

    Example: exegesis export-todo TODO_updated.md
    """
    from .importer import export_to_todo

    db = ctx.obj["db"]
    count = export_to_todo(db, todo_path)
    click.echo(f"Exported {count} passages to {todo_path}")


if __name__ == "__main__":
    cli()
