from datetime import datetime

from sqlalchemy import select

from app.models.project import Project


async def test_project_model_fields_and_defaults(app_session):
    project = Project(
        title="Portfolio Redesign",
        slug="portfolio-redesign",
        short_description="Modernized portfolio experience",
        description="A full redesign of the portfolio experience.",
        problem="The old site felt dated and did not highlight the work effectively.",
        solution="I rebuilt the portfolio with clearer messaging and improved content structure.",
        technical_details="FastAPI, SQLAlchemy, and a modern frontend stack.",
        technical_decisions="Used a modular backend and a component-driven frontend.",
        challenges="Balancing marketing goals with technical simplicity.",
        outcome="The new experience is clearer, faster, and easier to maintain.",
    )

    app_session.add(project)
    await app_session.flush()

    stored = await app_session.scalar(select(Project).where(Project.slug == "portfolio-redesign"))

    assert stored is not None
    assert stored.title == "Portfolio Redesign"
    assert stored.slug == "portfolio-redesign"
    assert stored.status == "planning"
    assert stored.publication_status == "draft"
    assert stored.is_featured is False
    assert stored.display_order == 0
    assert stored.created_at is not None
    assert isinstance(stored.created_at, datetime)
