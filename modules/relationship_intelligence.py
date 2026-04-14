"""
Relationship Intelligence - Track and predict relationship needs.

Maintains:
- Last contact dates
- Interaction history and sentiment
- Communication preferences
- Relationship insights (gaps, opportunities, changes)
- Predicted next-best-contact-time
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional


class RelationshipIntelligence:
    """Manage and predict relationship needs."""

    def __init__(self, db_path: Path):
        """
        Initialize relationship intelligence.

        Args:
            db_path: Path to SQLite database
        """
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(str(db_path))

    def record_interaction(
        self,
        person_id: int,
        interaction_type: str,
        sentiment: str = "neutral",
        summary: str = "",
        context: str = ""
    ):
        """
        Record an interaction with a person.

        Args:
            person_id: ID of person
            interaction_type: email, call, meeting, message, etc
            sentiment: positive, neutral, negative
            summary: Brief summary of interaction
            context: Detailed context
        """
        cursor = self.conn.cursor()

        # Record interaction
        cursor.execute("""
            INSERT INTO relationship_history
            (person_id, interaction_type, sentiment, summary, context, date_at)
            VALUES (?, ?, ?, ?, ?, DATE('now'))
        """, (person_id, interaction_type, sentiment, summary, context))

        # Update last_contact in relationships
        cursor.execute("""
            UPDATE relationships
            SET last_contact = DATE('now')
            WHERE person_id = ?
        """, (person_id,))

        self.conn.commit()

    def get_relationship_summary(self, person_id: int) -> Optional[Dict[str, Any]]:
        """Get summary of relationship with a person."""
        cursor = self.conn.cursor()

        # Get relationship data
        cursor.execute("""
            SELECT p.name, p.organization, r.relationship_type,
                   r.preferred_contact_mode, r.contact_frequency_days,
                   r.last_contact, r.topics_of_interest
            FROM people p
            LEFT JOIN relationships r ON p.id = r.person_id
            WHERE p.id = ?
        """, (person_id,))

        result = cursor.fetchone()
        if not result:
            return None

        name, org, rel_type, contact_mode, freq_days, last_contact, topics = result

        # Get recent interactions
        cursor.execute("""
            SELECT interaction_type, sentiment, summary, date_at
            FROM relationship_history
            WHERE person_id = ?
            ORDER BY date_at DESC
            LIMIT 5
        """, (person_id,))

        recent_interactions = [
            {
                "type": row[0],
                "sentiment": row[1],
                "summary": row[2],
                "date": row[3]
            }
            for row in cursor.fetchall()
        ]

        # Calculate days since last contact
        days_since = None
        if last_contact:
            last_date = datetime.fromisoformat(last_contact).date()
            days_since = (datetime.now().date() - last_date).days

        return {
            "person_id": person_id,
            "name": name,
            "organization": org,
            "relationship_type": rel_type,
            "preferred_contact_mode": contact_mode,
            "expected_contact_frequency_days": freq_days,
            "last_contact_date": last_contact,
            "days_since_contact": days_since,
            "overdue": days_since and freq_days and days_since > freq_days,
            "topics_of_interest": topics,
            "recent_interactions": recent_interactions
        }

    def get_overdue_contacts(self) -> List[Dict[str, Any]]:
        """Get relationships that are overdue for contact."""
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT p.id, p.name, r.relationship_type,
                   JULIANDAY('now') - JULIANDAY(r.last_contact) as days_since,
                   r.contact_frequency_days
            FROM people p
            JOIN relationships r ON p.id = r.person_id
            WHERE r.last_contact IS NOT NULL
              AND (JULIANDAY('now') - JULIANDAY(r.last_contact)) > r.contact_frequency_days
            ORDER BY days_since DESC
        """)

        return [
            {
                "person_id": row[0],
                "name": row[1],
                "relationship_type": row[2],
                "days_overdue": int(row[3] - row[4]),
                "suggested_contact_mode": self._suggest_contact_mode(row[0])
            }
            for row in cursor.fetchall()
        ]

    def get_upcoming_birthdays(self, days_ahead: int = 30) -> List[Dict[str, Any]]:
        """Get upcoming birthdays."""
        cursor = self.conn.cursor()

        # This would require birthday field in people table
        # For now, return empty list as placeholder
        return []

    def suggest_next_contact_time(self, person_id: int) -> Dict[str, Any]>:
        """Suggest when and how to next contact this person."""
        cursor = self.conn.cursor()

        # Get relationship details
        cursor.execute("""
            SELECT p.name, r.relationship_type, r.preferred_contact_mode,
                   r.last_contact, r.contact_frequency_days
            FROM people p
            LEFT JOIN relationships r ON p.id = r.person_id
            WHERE p.id = ?
        """, (person_id,))

        result = cursor.fetchone()
        if not result:
            return {}

        name, rel_type, pref_mode, last_contact, freq_days = result

        if not last_contact or not freq_days:
            return {
                "person_id": person_id,
                "name": name,
                "suggested_action": f"Add contact frequency preference for {name}"
            }

        last_date = datetime.fromisoformat(last_contact).date()
        next_contact = last_date + timedelta(days=freq_days)
        days_until = (next_contact - datetime.now().date()).days

        return {
            "person_id": person_id,
            "name": name,
            "relationship_type": rel_type,
            "last_contact": last_contact,
            "suggested_next_contact": next_contact.isoformat(),
            "days_until_suggested": max(0, days_until),
            "overdue": days_until < 0,
            "suggested_mode": pref_mode or "email",
            "suggested_context": self._suggest_context(person_id)
        }

    def _suggest_contact_mode(self, person_id: int) -> str:
        """Suggest best contact mode based on history."""
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT preferred_contact_mode FROM relationships WHERE person_id = ?
        """, (person_id,))

        result = cursor.fetchone()
        if result and result[0]:
            return result[0]

        # Default based on most recent interaction
        cursor.execute("""
            SELECT interaction_type FROM relationship_history
            WHERE person_id = ?
            ORDER BY date_at DESC
            LIMIT 1
        """, (person_id,))

        result = cursor.fetchone()
        return result[0] if result else "email"

    def _suggest_context(self, person_id: int) -> str:
        """Suggest what to talk about."""
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT topics_of_interest FROM relationships WHERE person_id = ?
        """, (person_id,))

        result = cursor.fetchone()
        if result and result[0]:
            return f"Topics: {result[0]}"

        return "Catch up on work/life"

    def record_relationship_insight(
        self,
        person_id: int,
        insight_type: str,
        description: str,
        suggested_action: str
    ):
        """
        Record an insight about a relationship.

        Args:
            person_id: ID of person
            insight_type: gap, opportunity, milestone, change
            description: What the insight is
            suggested_action: What to do about it
        """
        cursor = self.conn.cursor()

        cursor.execute("""
            INSERT INTO relationship_insights
            (person_id, insight_type, description, suggested_action, created_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (person_id, insight_type, description, suggested_action))

        self.conn.commit()

    def get_relationship_insights(self) -> List[Dict[str, Any]]:
        """Get all active relationship insights."""
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT p.name, ri.insight_type, ri.description, ri.suggested_action
            FROM relationship_insights ri
            JOIN people p ON ri.person_id = p.id
            WHERE DATE(ri.created_at) >= DATE('now', '-30 days')
            ORDER BY ri.created_at DESC
        """)

        return [
            {
                "person": row[0],
                "type": row[1],
                "description": row[2],
                "suggested_action": row[3]
            }
            for row in cursor.fetchall()
        ]
