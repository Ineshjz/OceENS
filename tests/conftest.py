"""Configuration commune des tests, appliquée avant tout import du code.

`oceens.core.database` crée son moteur SQLite à l'import, dans
`LOCAL_DATABASE_DIR` : on le pointe vers un dossier temporaire, pour qu'un test
ne touche jamais la base de développement.

Importer un module de `oceens.core` importe `oceens.core.auth`, qui arrête le
processus sans credentials Entra : les tests tournent en `AUTH_MODE=dev`.

`load_dotenv` est neutralisé avant le premier import du projet : la CI n'a pas
de `.env`, un test ne doit donc pas dépendre de celui du poste de développement.
"""

import os
import tempfile

import dotenv

dotenv.load_dotenv = lambda *args, **kwargs: False

os.environ["LOCAL_DATABASE_DIR"] = tempfile.mkdtemp(prefix="oceens-tests-")
os.environ["AUTH_MODE"] = "dev"
