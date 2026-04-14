"""
Predictive Planning - Proactive recommendations to help user succeed.

Analyzes:
- Upcoming deadlines
- Dependency chains (what's blocking what)
- Time crunch situations
- Relationship gaps
- Value/goal alignment

Generates actionable recommendations with deadlines.
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional


class PredictivePlanner:
    """Generate proactive recommendations."""

    def __init__(self, db_path: Path, user_values: Optional[Dict] = None):
        """
        Initialize predictive planner.

        Args:
            db_path: Path to SQLite database
            user_values: Dictionary with user's values/goals for prioritization
        """
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(str(db_path))
        self.user_values = user_values or {}

    def generate_daily_plan(self) -> List[Dict[str, Any]]:
        """
        Generate today's predictive plan.

        Returns:
            List of recommendations prioritized by importance
        """
        recommendations = []

        # 1. Check for deadline approaching in next 3 days
        recommendations.extend(self._find_approaching_deadlines(days_ahead=3))

        # 2. Check for dependency blockages
        recommendations.extend(self._find_blocking_dependencies())

        # 3. Check for time crunch situations
        recommendations.extend(self._identify_time_crunch())

        # 4. Check calendar for optimization opportunities
        recommendations.extend(self._suggest_calendar_optimizations())

        # 5. Check for relationship gaps
        recommendations.extend(self._surface_relationship_gaps())

        # Sort by priority score
        recommendations.sort(key=lambda x: x.get('priority_score', 0), reverse=True)

        return recommendations[:10]  # Top 10 recommendations

    def _find_approaching_deadlines(self, days_ahead: int = 3) -> List[Dict]:
        """Find obligations with approaching deadlines."""
        cursor = self.conn.cursor()

        # Get obligations due in next N days
        today = datetime.now().date()
        cutoff = today + timedelta(days=days_ahead)

        cursor.execute("""
            SELECT o.id, o.title, o.due_at, o.importance_score, o.urgency_score
            FROM obligations o
            WHERE o.status = 'open'
              AND o.due_at IS NOT NULL
              AND DATE(o.due_at) BETWEEN DATE('now') AND DATE(?)
            ORDER BY o.due_at ASC
        """, (cutoff.isoformat(),))

        recommendations = []
        for row in cursor.fetchall():
            rec = {
                "type": "deadline_approaching",
                "obligation_id": row[0],
                "title": row[1],
                "due_date": row[2],
                "days_remaining": (datetime.fromisoformat(row[2]).date() - today).days,
                "priority_score": row[3] * 100 + row[4] * 50,
                "suggested_action": f"Review and prepare for '{row[1]}' due on {row[2]}"
            }

            # Check for dependencies that might block completion
            cursor.execute("""
                SELECT COUNT(*) FROM obligation_dependencies
                WHERE obligation_id = ? AND constraint_type = 'must_complete_first'
            """, (row[0],))

            blocking_count = cursor.fetchone()[0]
            if blocking_count > 0:
                rec["suggested_action"] += f" ({blocking_count} dependencies to complete first)"

            recommendations.append(rec)

        return recommendations

    def _find_blocking_dependencies(self) -> List[Dict]:
        """Find obligations that are blocking others."""
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT od.obligation_id, od.depends_on_obligation_id,
                   o_blocker.title as blocker_title,
                   o_blocked.title as blocked_title,
                   o_blocker.due_at
            FROM obligation_dependencies od
            JOIN obligations o_blocker ON od.depends_on_obligation_id = o_blocker.id
            JOIN obligations o_blocked ON od.obligation_id = o_blocked.id
            WHERE o_blocker.status = 'open'
              AND o_blocked.status = 'open'
              AND o_blocked.due_at IS NOT NULL
              AND DATE(o_blocked.due_at) <= DATE(DATE('now', '+3 days'))
        """)

        recommendations = []
        for row in cursor.fetchall():
            rec = {
                "type": "dependency_blocking",
                "blocking_obligation_id": row[1],
                "blocked_obligation_id": row[0],
                "blocker_title": row[2],
                "blocked_title": row[3],
                "priority_score": 80,
                "suggested_action": f"Complete '{row[2]}' first—it's blocking '{row[3]}'"
            }
            recommendations.append(rec)

        return recommendations

    def _identify_time_crunch(self) -> List[Dict]:
        """Identify when too many obligations are due same day."""
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT DATE(due_at) as due_date, COUNT(*) as count
            FROM obligations
            WHERE status = 'open' AND due_at IS NOT NULL
            GROUP BY DATE(due_at)
            HAVING count > 2
            ORDER BY due_date ASC
        """)

        recommendations = []
        for row in cursor.fetchall():
            rec = {
                "type": "time_crunch",
                "due_date": row[0],
                "obligation_count": row[1],
                "priority_score": row[1] * 25,
                "suggested_action": f"{row[1]} obligations due on {row[0]}. Consider reprioritizing or redistributing deadlines."
            }
            recommendations.append(rec)

        return recommendations

    def _suggest_calendar_optimizations(self) -> List[Dict]:
        """Suggest calendar improvements (deep work blocks, no back-to-back, etc)."""
        recommendations = []

        # Check if user has calendar pattern data
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT COUNT(*) FROM calendar_patterns WHERE impact_assessment = 'high'
        """)

        if cursor.fetchone()[0] == 0:
            return recommendations

        # Suggest deep work blocks
        rec = {
            "type": "calendar_optimization",
            "priority_score": 50,
            "suggested_action": "Your calendar shows fragmented time blocks. Create 2-hour deep work blocks on Tue/Thu mornings."
        }
        recommendations.append(rec)

        return recommendations

    def _surface_relationship_gaps(self) -> List[Dict]:
        """Surface relationships that need attention."""
        cursor = self.conn.cursor()

        # Find key people not contacted recently
        cursor.execute("""
            SELECT p.id, p.name, r.contact_frequency_days,
                   JULIANDAY('now') - JULIANDAY(r.last_contact) as days_since
            FROM people p
            JOIN relationships r ON p.id = r.person_id
            WHERE r.relationship_type IN ('direct_report', 'manager', 'client')
              AND (r.last_contact IS NULL
                   OR JULIANDAY('now') - JULIANDAY(r.last_contact) > r.contact_frequency_days)
            ORDER BY days_since DESC
            LIMIT 5
        """)

        recommendations = []
        for row in cursor.fetchall():
            days_overdue = int(row[3] - row[2]) if row[3] and row[2] else 0

            rec = {
                "type": "relationship_gap",
                "person_id": row[0],
                "person_name": row[1],
                "days_overdue": max(0, days_overdue),
                "priority_score": 40 + (days_overdue * 2),
                "suggested_action": f"Reach out to {row[1]}—last contact was {int(row[3] or 0)} days ago"
            }
            recommendations.append(rec)

        return recommendations

    def record_recommendation(
        self,
        rec_type: str,
        target_entity_type: str,
        target_entity_id: str,
        priority_score: float,
        description: str,
        suggested_action: str,
        action_deadline: Optional[str] = None
    ):
        """Record a recommendation to database."""
        cursor = self.conn.cursor()

        if action_deadline is None:
            action_deadline = (datetime.now() + timedelta(days=1)).isoformat()

        cursor.execute("""
            INSERT INTO predictive_recommendations
            (recommendation_type, target_entity_type, target_entity_id,
             priority_score, description, suggested_action, action_deadline)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (rec_type, target_entity_type, target_entity_id, priority_score,
              description, suggested_action, action_deadline))

        self.conn.commit()

    def get_unacknowledged_recommendations(self) -> List[Dict]:
        """Get recommendations pending user acknowledgement."""
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT id, recommendation_type, description, suggested_action, priority_score
            FROM predictive_recommendations
            WHERE status = 'pending'
            ORDER BY priority_score DESC
            LIMIT 10
        """)

        return [
            {
                "id": row[0],
                "type": row[1],
                "description": row[2],
                "action": row[3],
                "priority": row[4]
            }
            for row in cursor.fetchall()
        ]

    def acknowledge_recommendation(self, rec_id: int):
        """Mark recommendation as acknowledged."""
        cursor = self.conn.cursor()

        cursor.execute("""
            UPDATE predictive_recommendations
            SET status = 'acknowledged', updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (rec_id,))

        self.conn.commit()
