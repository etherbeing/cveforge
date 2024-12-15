"""
Vaccine is the 3 challenge of the tier 2 on Hack the box platform
it is related to SQL injection through a search form once we gain access to the system.
As per this part of the CVE Forge was made because a problem in the 6 step we are going to assume the rest of the steps are
ready and start the exploit from there
Data collection we have:
Enumaration:
db: postgres
vulnerability: The website is vulnerable to SQL injection but doesnt have enabled the stacked
queries so we can successfuly enable run the stored procedure for spawning the shell, so now
what we are going to do is, create a SQL Injection tool that allow
us to use the database through the vulnerable website...
Credentials:
db credentials: postgres:md52d58e0637ec1e94cdfba3d1c26b67d01
website credentials: admin:qwerty789

"""
import argparse
from prompt_toolkit.completion import NestedCompleter


general_commands = [
    "SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "ALTER", "DROP", 
    "GRANT", "REVOKE", "COMMIT", "ROLLBACK", "SAVEPOINT", 
    "BEGIN", "END", "EXPLAIN", "ANALYZE", "VACUUM"
]
ddl_commands = [
    "CREATE TABLE", "CREATE DATABASE", "CREATE INDEX", 
    "DROP TABLE", "DROP DATABASE", "DROP INDEX", 
    "ALTER TABLE", "ALTER DATABASE", "RENAME TABLE", 
    "RENAME COLUMN", "TRUNCATE TABLE"
]
dml_commands = [
    "SELECT", "INSERT INTO", "VALUES", "UPDATE", 
    "DELETE FROM", "WHERE", "GROUP BY", "HAVING", 
    "ORDER BY", "LIMIT", "OFFSET", "DISTINCT"
]
stored_procedures = [
    "pg_read_file", "pg_write_file", "pg_stat_file", 
    "lo_import", "lo_export", 
    "pg_execute_from_file",  # Custom implementations
    "plpgsql_function"      # Example of stored PL/pgSQL
]
admin_commands = [
    "pg_dump", "pg_restore", "pg_basebackup", 
    "VACUUM FULL", "REINDEX", "CLUSTER", 
    "CHECKPOINT", "SHOW", "SET", "RESET"
]
functions = [
    "NOW()", "CURRENT_DATE", "CURRENT_TIME", "AGE()", 
    "EXTRACT()", "TO_CHAR()", "TO_DATE()", 
    "STRING_AGG()", "ARRAY_AGG()", 
    "CASE WHEN THEN END", "COALESCE()", "NULLIF()"
]
system_catalogs = [
    "pg_catalog.pg_tables", "pg_catalog.pg_indexes", "pg_catalog.pg_views", 
    "pg_catalog.pg_roles", "pg_catalog.pg_proc", 
    "pg_catalog.pg_stat_activity"
]

commands = {
    "SELECT": {"*": None, "FROM": None, "WHERE": None, "GROUP BY": None},
    "INSERT INTO": None,
    "CREATE": {"TABLE": None, "DATABASE": None},
    "DROP": {"TABLE": None, "DATABASE": None},
    "ALTER": {"TABLE": None, "DATABASE": None},
    "EXECUTE": {"pg_read_file": None, "pg_write_file": None},
}

completer = NestedCompleter.from_nested_dict(commands)


class web_sql_injection_parse(argparse.ArgumentParser):
    pass

def web_sql_injection(namespace: web_sql_injection_parse, *args, **kwargs):
    """
    Open an SQL section that proxy the 
    """
    pass