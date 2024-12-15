from unittest import TestCase

from core.database.models.cve import CVE


class DatabaseTestCase(TestCase):
    def test_database_ok(self):
        model = CVE()
        self.assertEqual(model.__tablename__, "CVE")