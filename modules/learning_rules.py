"""
Learning Rules - Record and apply learned rules for autonomous behavior.

Tracks:
- Email classification improvements
- Decision accuracy over time
- Autonomy unlock criteria
- Rule retirement when underperforming
"""

import sqlite3
from pathlib import Path
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta


class LearningRuleEngine:
    """Track and apply learning rules."""

    def __init__(self, db_path: Path):
        """
        Initialize learning rule engine.

        Args:
            db_path: Path to SQLite database
        """
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(str(db_path))

    def create_rule(
        self,
        rule_id: str,
        rule_type: str,
        pattern: str,
        action: str,
        confidence: float = 0.0,
        created_by: str = "system",
        notes: str = ""
    ) -> bool:
        """
        Create a new learning rule.

        Args:
            rule_id: Unique identifier for rule
            rule_type: Type of rule (email_triage, obligation_priority, etc)
            pattern: Description of pattern (e.g., "from:boss@company.com")
            action: Action to take when pattern matches
            confidence: Initial confidence score (0-1)
            created_by: Who/what created this rule
            notes: Notes about the rule

        Returns:
            True if successful
        """
        cursor = self.conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO learning_rules
                (rule_id, rule_type, pattern, action, confidence, created_by, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (rule_id, rule_type, pattern, action, confidence, created_by, notes))

            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def record_application(
        self,
        rule_id: str,
        outcome: str,
        was_correct: bool,
        feedback: Optional[str] = None
    ):
        """
        Record that a rule was applied and whether it was correct.

        Args:
            rule_id: ID of the rule that was applied
            outcome: What the rule decided
            was_correct: Whether the decision was correct
            feedback: Optional user feedback
        """
        cursor = self.conn.cursor()

        # Get current rule
        cursor.execute("""
            SELECT id, applications_count, correct_count, confidence
            FROM learning_rules
            WHERE rule_id = ?
        """, (rule_id,))

        result = cursor.fetchone()
        if not result:
            return

        rule_row_id, app_count, correct_count, confidence = result

        # Update counts
        new_app_count = app_count + 1
        new_correct_count = correct_count + (1 if was_correct else 0)

        # Recalculate confidence (simple Bayesian)
        new_confidence = new_correct_count / new_app_count if new_app_count > 0 else 0

        cursor.execute("""
            UPDATE learning_rules
            SET applications_count = ?, correct_count = ?, confidence = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (new_app_count, new_correct_count, new_confidence, rule_row_id))

        # Record feedback if provided
        if feedback:
            cursor.execute("""
                INSERT INTO rule_feedback (rule_id, outcome, correct, feedback, recorded_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (rule_row_id, outcome, was_correct, feedback))

        self.conn.commit()

    def get_rule_stats(self, rule_id: str) -> Optional[Dict[str, Any]]:
        """Get statistics for a rule."""
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT rule_id, rule_type, pattern, action, confidence,
                   applications_count, correct_count,
                   created_at, updated_at
            FROM learning_rules
            WHERE rule_id = ?
        """, (rule_id,))

        result = cursor.fetchone()
        if not result:
            return None

        return {
            "rule_id": result[0],
            "type": result[1],
            "pattern": result[2],
            "action": result[3],
            "confidence": result[4],
            "applications": result[5],
            "correct_applications": result[6],
            "created_at": result[7],
            "updated_at": result[8],
            "accuracy": result[6] / result[5] if result[5] > 0 else 0
        }

    def get_rules_by_type(self, rule_type: str) -> List[Dict[str, Any]]:
        """Get all rules of a specific type."""
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT rule_id, pattern, action, confidence, applications_count, correct_count
            FROM learning_rules
            WHERE rule_type = ? AND disabled_at IS NULL
            ORDER BY confidence DESC
        """, (rule_type,))

        return [
            {
                "rule_id": row[0],
                "pattern": row[1],
                "action": row[2],
                "confidence": row[3],
                "applications": row[4],
                "accuracy": row[5] / row[4] if row[4] > 0 else 0
            }
            for row in cursor.fetchall()
        ]

    def retire_rule(self, rule_id: str, reason: str = ""):
        """Disable a rule (mark as retired)."""
        cursor = self.conn.cursor()

        cursor.execute("""
            UPDATE learning_rules
            SET disabled_at = CURRENT_TIMESTAMP, disabled_reason = ?
            WHERE rule_id = ?
        """, (reason, rule_id))

        self.conn.commit()

    def check_autonomy_unlock(self, workflow_name: str) -> Dict[str, Any]:
        """
        Check if workflow is ready for autonomous execution.

        Returns:
            {
                "ready": bool,
                "reason": str,
                "metrics": {...}
            }
        """
        cursor = self.conn.cursor()

        # Get all rules for this workflow
        cursor.execute("""
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN confidence >= 0.95 THEN 1 ELSE 0 END) as high_confidence,
                   AVG(confidence) as avg_confidence,
                   SUM(applications_count) as total_applications
            FROM learning_rules
            WHERE rule_type = ? AND disabled_at IS NULL
        """, (workflow_name,))

        result = cursor.fetchone()
        if not result or result[3] is None:
            return {
                "ready": False,
                "reason": "Insufficient training data",
                "metrics": {
                    "total_rules": 0,
                    "high_confidence_rules": 0,
                    "total_applications": 0
                }
            }

        total_rules, high_conf_rules, avg_conf, total_apps = result

        ready = (
            total_apps >= 300 and
            avg_conf >= 0.95 and
            high_conf_rules >= (total_rules * 0.9)  # 90% of rules high confidence
        )

        return {
            "ready": ready,
            "reason": "Ready for autonomy" if ready else "Not yet ready",
            "metrics": {
                "total_rules": total_rules,
                "high_confidence_rules": high_conf_rules,
                "average_confidence": avg_conf,
                "total_applications": total_apps,
                "requirements": {
                    "minimum_applications": 300,
                    "minimum_confidence": 0.95,
                    "high_confidence_ratio": 0.9
                }
            }
        }

    def suggest_training_data(self, rule_type: str) -> List[Dict[str, Any]]:
        """Suggest what additional training data would help most."""
        cursor = self.conn.cursor()

        # Find rules with low confidence
        cursor.execute("""
            SELECT rule_id, pattern, confidence, applications_count
            FROM learning_rules
            WHERE rule_type = ? AND disabled_at IS NULL
            ORDER BY confidence ASC, applications_count ASC
            LIMIT 5
        """, (rule_type,))

        suggestions = []
        for row in cursor.fetchall():
            suggestions.append({
                "rule_id": row[0],
                "pattern": row[1],
                "current_confidence": row[2],
                "applications_so_far": row[3],
                "suggestion": f"This rule needs more training. Try 50+ more examples where '{row[1]}' applies."
            })

        return suggestions
