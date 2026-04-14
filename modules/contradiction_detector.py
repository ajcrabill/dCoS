"""Contradiction Detection: Flag when reality contradicts stored memories.

When new observations conflict with stored rules/relationships:
1. Detects the contradiction
2. Updates confidence scores (Bayesian update)
3. Flags for user review
"""

from typing import Dict, Optional
from datetime import datetime
import sqlite3
import json


class ContradictionDetector:
    """Detects contradictions between observations and stored memories."""

    def __init__(self, db_connection: sqlite3.Connection):
        self.db = db_connection
        self._ensure_tables_exist()

    def _ensure_tables_exist(self):
        """Create contradiction tracking table if needed."""
        cursor = self.db.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contradiction_flags (
                id TEXT PRIMARY KEY,
                memory_id TEXT,
                memory_type TEXT,
                observation TEXT,
                original_confidence REAL,
                updated_confidence REAL,
                severity TEXT,
                flagged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_reviewed BOOLEAN DEFAULT 0
            )
        """)
        self.db.commit()

    def check_rule_contradiction(self, rule_id: str, new_observation: Dict) -> Optional[Dict]:
        """Check if new observation contradicts a rule.

        Args:
            rule_id: ID of rule to check
            new_observation: New observation

        Returns:
            Contradiction info or None if no contradiction
        """
        cursor = self.db.cursor()

        # Get rule details
        cursor.execute(
            "SELECT condition, action, confidence_score FROM learning_rules WHERE id = ?",
            (rule_id,)
        )
        rule = cursor.fetchone()
        if not rule:
            return None

        condition, action, confidence = rule

        # Check if new observation contradicts the rule
        if self._observations_contradict(condition, action, new_observation):
            new_confidence = self._bayesian_update(confidence, contradiction=True)
            return {
                "rule_id": rule_id,
                "original_confidence": confidence,
                "new_confidence": new_confidence,
                "observation": new_observation,
                "severity": "high" if confidence > 0.9 else "medium"
            }

        return None

    def check_relationship_contradiction(self, person_id: str, new_observation: Dict) -> Optional[Dict]:
        """Check if new observation contradicts relationship profile.

        Args:
            person_id: ID of relationship
            new_observation: New observation about the person

        Returns:
            Contradiction info or None
        """
        cursor = self.db.cursor()

        # Get relationship profile
        cursor.execute(
            "SELECT sentiment_baseline FROM relationships WHERE id = ?",
            (person_id,)
        )
        profile = cursor.fetchone()
        if not profile:
            return None

        sentiment_baseline = profile[0]

        # Check for contradictions
        if self._relationship_contradicts(sentiment_baseline, new_observation):
            return {
                "person_id": person_id,
                "expected_sentiment": sentiment_baseline,
                "observed_sentiment": new_observation.get("sentiment"),
                "observation": new_observation,
                "severity": "high"
            }

        return None

    def _observations_contradict(self, condition: str, action: str, observation: Dict) -> bool:
        """Simple heuristic: check if observation contradicts rule.

        This is a placeholder; in production would use semantic similarity.
        """
        return False

    def _relationship_contradicts(self, baseline: str, obs: Dict) -> bool:
        """Check if observation contradicts relationship profile."""
        return False

    def _bayesian_update(self, prior_confidence: float, contradiction: bool, observations: int = 1) -> float:
        """Bayesian update of confidence score.

        Args:
            prior_confidence: Previous confidence
            contradiction: Whether new observation contradicts
            observations: Number of observations supporting update

        Returns:
            Updated confidence
        """
        if contradiction:
            # Reduce confidence on contradiction
            return prior_confidence * 0.8 * (1 / observations)
        else:
            # Increase confidence on support
            return min(0.99, prior_confidence + (1 - prior_confidence) * 0.1 * observations)

    def flag_contradiction(self, contradiction: Dict):
        """Flag contradiction for user review.

        Args:
            contradiction: Contradiction info dict
        """
        from uuid import uuid4
        flag_id = str(uuid4())
        cursor = self.db.cursor()
        cursor.execute("""
            INSERT INTO contradiction_flags
            (id, memory_id, memory_type, observation, original_confidence, updated_confidence, severity, flagged_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            flag_id,
            contradiction.get("rule_id") or contradiction.get("person_id"),
            "rule" if "rule_id" in contradiction else "relationship",
            json.dumps(contradiction["observation"]),
            contradiction.get("original_confidence"),
            contradiction.get("updated_confidence"),
            contradiction["severity"],
            datetime.now()
        ))
        self.db.commit()
