import os
import json
import sqlite3
import unittest
from unittest.mock import MagicMock, patch
import db_manager

class MockPgCursor:
    def __init__(self, storage):
        # storage is a list of tuples: [position, tarea_id, record_json, updated_at]
        self.storage = storage
        self._last_query = ""

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def execute(self, query, params=None):
        self._last_query = query
        q_upper = query.upper().strip()

        if q_upper.startswith("SELECT POSITION, TAREA_ID, RECORD, UPDATED_AT FROM ENJOY_RECORDS"):
            # Return all rows ordered by position
            sorted_storage = sorted(self.storage, key=lambda x: (x[0], str(x[3])))
            self._results = list(sorted_storage)
            return

        if q_upper.startswith("SELECT POSITION, TAREA_ID FROM ENJOY_RECORDS"):
            self._results = [(row[0], row[1]) for row in self.storage]
            return

        if q_upper.startswith("UPDATE ENJOY_RECORDS SET RECORD = %S, UPDATED_AT = NOW() WHERE TAREA_ID = %S"):
            rec_json, tid = params
            for i, row in enumerate(self.storage):
                if row[1] == tid:
                    self.storage[i] = (row[0], tid, rec_json, "2026-08-07 18:00:00")
                    break
            return

        if q_upper.startswith("INSERT INTO ENJOY_RECORDS"):
            pos, tid, rec_json = params
            self.storage.append((pos, tid, rec_json, "2026-08-07 18:00:00"))
            return

        if "DELETE FROM ENJOY_RECORDS" in q_upper:
            raise AssertionError("DELETE FROM enjoy_records no debe ser ejecutado!")

    def fetchall(self):
        return getattr(self, "_results", [])

    def close(self):
        pass

class MockPgConnection:
    def __init__(self, storage):
        self.storage = storage
        self.cursor_obj = MockPgCursor(storage)

    def cursor(self):
        return self.cursor_obj

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def close(self):
        pass

class TestConsolaEnjoyPersistence(unittest.TestCase):

    def setUp(self):
        # Mock initial storage with 2 existing tasks
        self.initial_storage = [
            (
                0,
                "2026_RI020_001",
                json.dumps({
                    "proyecto_id": "2026_RI020",
                    "unidad_nombre": "Enjoy Rinconada",
                    "proyecto_nombre": "PROYECTO RINCONADA",
                    "tarea_id": "2026_RI020_001",
                    "tarea_nombre": "Tarea Original 1",
                    "tarea_estado": "en desarrollo",
                    "fecha_inicio_proy": "28/07/2026",
                    "fecha_fin_real": None,
                    "fecha_legacy": None
                }),
                "2026-08-01 10:00:00"
            ),
            (
                1,
                "2026_RI020_002",
                json.dumps({
                    "proyecto_id": "2026_RI020",
                    "unidad_nombre": "Enjoy Rinconada",
                    "proyecto_nombre": "PROYECTO RINCONADA",
                    "tarea_id": "2026_RI020_002",
                    "tarea_nombre": "Tarea Original 2 (No incluida en update)",
                    "tarea_estado": "en desarrollo",
                    "fecha_inicio_proy": "29/07/2026",
                    "fecha_fin_real": None
                }),
                "2026-08-01 11:00:00"
            )
        ]
        self.mock_conn = MockPgConnection(self.initial_storage)

    def test_01_insert_new_task(self):
        """1. Verifica la inserción de una tarea nueva asignando una posición válida sin conflictos."""
        new_payload = [
            {
                "proyecto_id": "2026_RI020",
                "unidad_nombre": "Enjoy Rinconada",
                "proyecto_nombre": "PROYECTO RINCONADA",
                "tarea_id": "2026_RI020_003",
                "tarea_nombre": "Nueva Tarea 3",
                "tarea_estado": "en desarrollo",
                "fecha_inicio_proy": "07/08/2026",
                "fecha_fin_real": ""
            }
        ]

        count = db_manager._save_to_postgresql(new_payload, custom_conn=self.mock_conn)
        self.assertEqual(count, 1)

        # Check that storage now contains 3 records
        self.assertEqual(len(self.mock_conn.storage), 3)
        inserted_row = next(r for r in self.mock_conn.storage if r[1] == "2026_RI020_003")
        self.assertEqual(inserted_row[0], 2)  # Position incremented to 2
        self.assertEqual(inserted_row[1], "2026_RI020_003")

    def test_02_update_existing_task(self):
        """2. Verifica la actualización de una tarea existente sin cambiar su posición original."""
        update_payload = [
            {
                "proyecto_id": "2026_RI020",
                "unidad_nombre": "Enjoy Rinconada",
                "proyecto_nombre": "PROYECTO RINCONADA",
                "tarea_id": "2026_RI020_001",
                "tarea_nombre": "Tarea 1 Modificada",
                "tarea_estado": "terminada",
                "tarea_pct": 100,
                "fecha_inicio_proy": "28/07/2026",
                "fecha_fin_real": "07/08/2026"
            }
        ]

        count = db_manager._save_to_postgresql(update_payload, custom_conn=self.mock_conn)
        self.assertEqual(count, 1)

        # Position must remain 0
        updated_row = next(r for r in self.mock_conn.storage if r[1] == "2026_RI020_001")
        self.assertEqual(updated_row[0], 0)
        rec_data = json.loads(updated_row[2])
        self.assertEqual(rec_data["tarea_nombre"], "Tarea 1 Modificada")
        self.assertEqual(rec_data["tarea_estado"], "terminada")

    def test_03_preservation_of_unincluded_records(self):
        """3. Comprueba que registros existentes no incluidos en el payload se conservan intactos."""
        # Only update 2026_RI020_001. 2026_RI020_002 is NOT in the payload.
        partial_payload = [
            {
                "proyecto_id": "2026_RI020",
                "unidad_nombre": "Enjoy Rinconada",
                "proyecto_nombre": "PROYECTO RINCONADA",
                "tarea_id": "2026_RI020_001",
                "tarea_nombre": "Tarea 1",
                "tarea_estado": "en desarrollo"
            }
        ]

        db_manager._save_to_postgresql(partial_payload, custom_conn=self.mock_conn)

        # Verify 2026_RI020_002 is still in storage
        unincluded_row = next((r for r in self.mock_conn.storage if r[1] == "2026_RI020_002"), None)
        self.assertIsNotNone(unincluded_row)
        self.assertEqual(unincluded_row[0], 1)
        self.assertIn("Tarea Original 2", unincluded_row[2])

    def test_04_null_and_none_normalization(self):
        """4. Carga registros con null / None y comprueba que se normalizan a cadena vacía '' sin 'None'."""
        loaded_records = db_manager._load_from_postgresql(custom_conn=self.mock_conn)

        for rec in loaded_records:
            self.assertEqual(rec["fecha_fin_real"], "")
            self.assertEqual(rec["fecha_legacy"], "")
            self.assertNotEqual(rec["fecha_fin_real"], "None")
            self.assertNotEqual(rec["fecha_legacy"], "None")

    def test_05_reject_empty_tarea_id(self):
        """5. Rechaza payloads con tarea_id vacío informando error explícito."""
        invalid_payload = [
            {
                "proyecto_id": "2026_RI020",
                "tarea_id": "",
                "tarea_nombre": "Tarea Sin ID"
            }
        ]

        res = db_manager.save_central_data(invalid_payload)
        self.assertEqual(res["status"], "error")
        self.assertIn("vacío", res["message"].lower())

    def test_06_reject_duplicate_tarea_id(self):
        """6. Rechaza payloads con tarea_id duplicado informando error explícito."""
        duplicate_payload = [
            {
                "proyecto_id": "2026_RI020",
                "tarea_id": "2026_RI020_DUP",
                "tarea_nombre": "Tarea 1"
            },
            {
                "proyecto_id": "2026_RI020",
                "tarea_id": "2026_RI020_DUP",
                "tarea_nombre": "Tarea 2"
            }
        ]

        res = db_manager.save_central_data(duplicate_payload)
        self.assertEqual(res["status"], "error")
        self.assertIn("duplicado", res["message"].lower())

    def test_07_valid_positions_without_conflict(self):
        """7. Verifica asignación de posiciones secuenciales sin solapamiento."""
        multi_payload = [
            {"tarea_id": "2026_T1", "tarea_nombre": "Task 1"},
            {"tarea_id": "2026_T2", "tarea_nombre": "Task 2"},
            {"tarea_id": "2026_T3", "tarea_nombre": "Task 3"}
        ]

        db_manager._save_to_postgresql(multi_payload, custom_conn=self.mock_conn)
        positions = [r[0] for r in self.mock_conn.storage]
        self.assertEqual(len(positions), len(set(positions)))  # All positions unique

    def test_08_connection_error_handling(self):
        """8. Manejo controlado de fallos de conexión."""
        with patch.object(db_manager, "get_pg_dsn", return_value="postgresql://dummy:5432/db"):
            with patch.object(db_manager, "_get_pg_connection", return_value=(None, None)):
                res = db_manager.load_central_data()
                self.assertEqual(res["status"], "error")
                self.assertEqual(res["source"], "postgresql_vps")

if __name__ == "__main__":
    print("==================================================")
    print("EJECUTANDO PRUEBAS DE PERSISTENCIA EN PYTHON")
    print("==================================================")
    unittest.main(verbosity=2)
