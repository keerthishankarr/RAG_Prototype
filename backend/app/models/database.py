"""
Database models and operations using SQLite.
"""
import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class Database:
    """SQLite database wrapper for application data."""

    def __init__(self):
        """Initialize database connection and create tables."""
        settings = get_settings()
        self.db_path = settings.get_database_path()

        # Ensure directory exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Initializing database at {self.db_path}")
        self.create_tables()

    def get_connection(self) -> sqlite3.Connection:
        """Get a database connection."""
        conn = sqlite3.Connection(self.db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        return conn

    def create_tables(self) -> None:
        """Create database tables if they don't exist."""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Datasets table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS datasets (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                enabled INTEGER DEFAULT 1,
                chunk_size INTEGER NOT NULL,
                chunk_overlap INTEGER NOT NULL,
                chunking_strategy TEXT DEFAULT 'sentences',
                num_chunks INTEGER DEFAULT 0,
                file_size INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """
        )

        # Evaluations table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS evaluations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                response TEXT NOT NULL,
                rating INTEGER,
                notes TEXT,
                num_chunks INTEGER,
                response_length INTEGER,
                avg_chunk_score REAL,
                config TEXT,
                observability_data TEXT,
                created_at TEXT NOT NULL
            )
        """
        )

        # Test questions table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS test_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                expected_keywords TEXT NOT NULL,
                expected_source TEXT,
                test_suite_id TEXT,
                created_at TEXT NOT NULL
            )
        """
        )

        conn.commit()
        conn.close()
        logger.info("Database tables created/verified")

    # Dataset operations
    def create_dataset(self, dataset: Dict) -> str:
        """Create a new dataset record."""
        conn = self.get_connection()
        cursor = conn.cursor()

        now = datetime.utcnow().isoformat()
        dataset_id = dataset.get("id", dataset["dataset_id"])

        cursor.execute(
            """
            INSERT INTO datasets
            (id, name, enabled, chunk_size, chunk_overlap, chunking_strategy,
             num_chunks, file_size, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                dataset_id,
                dataset["name"],
                1,  # enabled by default
                dataset.get("chunk_size", 500),
                dataset.get("chunk_overlap", 50),
                dataset.get("chunking_strategy", "sentences"),
                dataset.get("num_chunks", 0),
                dataset.get("file_size", 0),
                now,
                now,
            ),
        )

        conn.commit()
        conn.close()
        logger.info(f"Created dataset: {dataset_id}")
        return dataset_id

    def get_dataset(self, dataset_id: str) -> Optional[Dict]:
        """Get a dataset by ID."""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM datasets WHERE id = ?", (dataset_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return dict(row)
        return None

    def list_datasets(self) -> List[Dict]:
        """List all datasets."""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM datasets ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def update_dataset(self, dataset_id: str, updates: Dict) -> bool:
        """Update a dataset."""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Build update query dynamically
        set_clauses = []
        values = []

        for key, value in updates.items():
            if key in ["name", "enabled", "num_chunks", "file_size"]:
                set_clauses.append(f"{key} = ?")
                values.append(value)

        if not set_clauses:
            return False

        set_clauses.append("updated_at = ?")
        values.append(datetime.utcnow().isoformat())
        values.append(dataset_id)

        query = f"UPDATE datasets SET {', '.join(set_clauses)} WHERE id = ?"
        cursor.execute(query, values)

        conn.commit()
        success = cursor.rowcount > 0
        conn.close()

        logger.info(f"Updated dataset {dataset_id}: {success}")
        return success

    def delete_dataset(self, dataset_id: str) -> bool:
        """Delete a dataset."""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM datasets WHERE id = ?", (dataset_id,))
        conn.commit()

        success = cursor.rowcount > 0
        conn.close()

        logger.info(f"Deleted dataset {dataset_id}: {success}")
        return success

    # Evaluation operations
    def create_evaluation(self, evaluation: Dict) -> int:
        """Create a new evaluation record."""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO evaluations
            (query, response, rating, notes, num_chunks, response_length,
             avg_chunk_score, config, observability_data, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                evaluation["query"],
                evaluation["response"],
                evaluation.get("rating"),
                evaluation.get("notes"),
                evaluation.get("num_chunks"),
                evaluation.get("response_length"),
                evaluation.get("avg_chunk_score"),
                json.dumps(evaluation.get("config")) if evaluation.get("config") else None,
                json.dumps(evaluation.get("observability_data"))
                if evaluation.get("observability_data")
                else None,
                datetime.utcnow().isoformat(),
            ),
        )

        evaluation_id = cursor.lastrowid
        conn.commit()
        conn.close()

        logger.info(f"Created evaluation: {evaluation_id}")
        return evaluation_id

    def list_evaluations(self, limit: int = 100) -> List[Dict]:
        """List evaluations."""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM evaluations ORDER BY created_at DESC LIMIT ?", (limit,)
        )
        rows = cursor.fetchall()
        conn.close()

        evaluations = []
        for row in rows:
            eval_dict = dict(row)
            # Parse JSON fields
            if eval_dict.get("config"):
                eval_dict["config"] = json.loads(eval_dict["config"])
            if eval_dict.get("observability_data"):
                eval_dict["observability_data"] = json.loads(
                    eval_dict["observability_data"]
                )
            evaluations.append(eval_dict)

        return evaluations

    # Test question operations
    def create_test_question(self, question: Dict) -> int:
        """Create a test question."""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO test_questions
            (question, expected_keywords, expected_source, test_suite_id, created_at)
            VALUES (?, ?, ?, ?, ?)
        """,
            (
                question["question"],
                json.dumps(question.get("expected_keywords", [])),
                question.get("expected_source"),
                question.get("test_suite_id"),
                datetime.utcnow().isoformat(),
            ),
        )

        question_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return question_id

    def list_test_questions(self) -> List[Dict]:
        """List all test questions."""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM test_questions ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()

        questions = []
        for row in rows:
            q_dict = dict(row)
            # Parse JSON field
            if q_dict.get("expected_keywords"):
                q_dict["expected_keywords"] = json.loads(q_dict["expected_keywords"])
            questions.append(q_dict)

        return questions


# Global database instance
_database = None


def get_database() -> Database:
    """
    Get or create the global database instance.

    Returns:
        The singleton database instance.
    """
    global _database
    if _database is None:
        _database = Database()
    return _database
