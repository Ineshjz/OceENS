"""File des synthèses : l'avancement de chaque sondage et son temps restant (#152).

La table `summaries` sert de file au daemon de génération, qui l'écrit. Ce
module est le seul endroit où l'application web la lit : la signification de
`http_status`, la règle « terminé » et l'estimation du temps restant ne vivent
qu'ici.

- en attente : `http_status = 0` ;
- faite : `http_status = 200` **et** un texte de synthèse ;
- en erreur : tout le reste, y compris un 200 sans texte. Le daemon ne
  réessaie jamais une ligne sortie de l'état 0 : l'attendre bloquerait le
  sondage pour toujours.

Le temps restant d'un sondage compte toutes les synthèses en attente de la
file, de tous les sondages : le daemon les traite une par une, sans ordre
défini. C'est donc un majorant pour chaque sondage, exact pour celui qui finira
le dernier. La durée d'une synthèse est fournie par l'appelant : ce module ne
lit pas l'horloge.
"""

from dataclasses import dataclass
from typing import Optional

from sqlalchemy import and_
from sqlmodel import case, func, select

from oceens.models import Summary


@dataclass(frozen=True)
class SurveyProgress:
    """Avancement de la génération des synthèses d'un sondage."""

    total: int
    done: int
    pending: int
    error: int
    # Secondes restantes estimées ; None une fois le sondage terminé.
    eta_seconds: Optional[int]

    @property
    def finished(self) -> bool:
        return self.pending == 0


def survey_progress(session, seconds_per_job) -> dict[int, SurveyProgress]:
    """Retourne l'avancement de chaque sondage qui a au moins une synthèse.

    Un sondage absent du résultat n'a encore rien demandé. Une erreur de lecture
    de la base remonte telle quelle à l'appelant : aucun compte partiel ou nul
    n'est inventé.
    """
    if seconds_per_job <= 0:
        raise ValueError(
            f"La durée d'une synthèse doit être positive (reçu : {seconds_per_job})."
        )

    is_pending = Summary.http_status == 0
    is_done = and_(Summary.http_status == 200, Summary.summary_text.is_not(None))

    rows = session.exec(
        select(
            Summary.survey_id,
            func.count(Summary.summary_id),
            func.sum(case((is_pending, 1), else_=0)),
            func.sum(case((is_done, 1), else_=0)),
        ).group_by(Summary.survey_id)
    ).all()

    queue_pending = sum(pending for _, _, pending, _ in rows)
    queue_eta_seconds = queue_pending * seconds_per_job

    return {
        survey_id: SurveyProgress(
            total=total,
            done=done,
            pending=pending,
            error=total - pending - done,
            eta_seconds=queue_eta_seconds if pending else None,
        )
        for survey_id, total, pending, done in rows
    }
