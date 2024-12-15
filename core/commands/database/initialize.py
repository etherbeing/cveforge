import os
import json
from sqlalchemy.exc import OperationalError
from core.context import Context
from core.database.base import engine, Base, SessionLocal
from core.database.types.cve import TypedCVE
from core.io import OUT
from core.database.models.cve import CVE


def load_cves():
    """Load into DB all of the CVEs for faster search"""
    for year in os.listdir(Context().CVE_FOLDER):
        year_folder = Context().CVE_FOLDER / year
        if year_folder.is_dir():
            for folder in os.listdir(year_folder):
                cve_folder = year_folder / folder
                for cve_file in os.listdir(cve_folder):
                    cve_file = cve_folder / cve_file
                    with open(cve_file, "r", encoding="utf8") as file:
                        cve = TypedCVE(**json.loads(file.read()))
                        yield cve

def store_cve_in_db():
    """Store all the cve returned by the load cves function into the configured db"""
    for cve in load_cves():
        with SessionLocal() as session:
            session.add(
                CVE(
                    **cve
                )
            )


def init_db():
    """Initialize the DB with all of the needed data"""
    try:
        Base.metadata.create_all(engine)
        OUT.print("[green]Database successfully created and initialized[/green]")
        OUT.print(f"[green]Database path {Context().db_path}[/green]")
        OUT.print(f"[green]Data path {Context().db_path.parent}[/green]")
    except OperationalError as err:
        OUT.print(f"[red]Error on database creation {err}[/red]")
        OUT.print(f"[yellow]Database URI {Context().DB_URI}[/yellow]")
        OUT.print(
            f"[yellow]Database path {os.listdir(Context().db_path.parent)}[/yellow]"
        )
        OUT.print(
            f"[yellow]Database path is file {Context().db_path.is_file()}[/yellow]"
        )
        if not Context().db_path.is_file():
            os.rmdir(Context().db_path)
