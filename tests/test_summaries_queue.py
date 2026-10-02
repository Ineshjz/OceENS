"""La file des synthèses donne à chaque sondage un temps restant estimé (#152).

Le chiffre vient du Design Document (#111) : un soir de campagne, 10 sondages
(C) de 45 synthèses (A) attendent, à 20 s chacune (B). Le dernier sondage de
la file doit alors annoncer 2 h 30 ± 10 % (D).
"""

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from oceens.models import Summary
from oceens.services.summaries_queue import survey_progress

SURVEYS_ON_A_CAMPAIGN_EVENING = 10  # C
JOBS_PER_SURVEY = 45  # A
SECONDS_PER_JOB = 20  # B


@pytest.fixture
def session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def queue_pending(session, survey_id, jobs):
    for _ in range(jobs):
        session.add(Summary(survey_id=survey_id, http_status=0))
    session.commit()


def test_last_survey_of_a_campaign_evening_is_estimated_at_2h30(session):
    for survey_id in range(1, SURVEYS_ON_A_CAMPAIGN_EVENING + 1):
        queue_pending(session, survey_id, JOBS_PER_SURVEY)
    last_survey = SURVEYS_ON_A_CAMPAIGN_EVENING

    progress = survey_progress(session, seconds_per_job=SECONDS_PER_JOB)

    # 2 h 30 = 9 000 s, ± 10 %.
    assert 8_100 <= progress[last_survey].eta_seconds <= 9_900
