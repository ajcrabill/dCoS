"""Memory Decay: Ebbinghaus-inspired forgetting curve.

Memories fade over time unless reinforced. Implements exponential decay:
importance(t) = initial_importance * 2^(-t/half_life)
"""

from datetime import datetime
from typing import Dict
import sqlite3


class EbbinghausDecay:
    """Applies Ebbinghaus decay curve to memories."""

    def __init__(self, half_life_days: float = 5.0):
        """Initialize decay curve.

        Args:
            half_life_days: Days for memory to lose 50% importance
        """
        self.half_life_days = half_life_days

    def calculate_decay(self, created_at: datetime, current_time: datetime = None) -> float:
        """Calculate decay factor for a memory.

        Args:
            created_at: When memory was created
            current_time: Current time (default: now)

        Returns:
            Decay factor (0.0 to 1.0). 1.0 = no decay, 0.0 = completely forgotten.
        """
        if current_time is None:
            current_time = datetime.now()

        days_elapsed = (current_time - created_at).days
        if days_elapsed < 0:
            return 1.0

        # Exponential decay: 2^(-t/half_life)
        decay = 2 ** (-days_elapsed / self.half_life_days)
        return max(0.0, min(1.0, decay))

    def should_delete(self, created_at: datetime, threshold: float = 0.05) -> bool:
        """Check if memory should be deleted (below threshold).

        Args:
            created_at: When memory was created
            threshold: Importance below this triggers deletion (default: 5%)

        Returns:
            True if memory should be deleted
        """
        return self.calculate_decay(created_at) < threshold

    def apply_decay_to_scores(self, scores: Dict[str, float], created_at: datetime) -> Dict[str, float]:
        """Apply decay factor to a dict of scores.

        Args:
            scores: Dictionary of {name: score}
            created_at: When this batch was created

        Returns:
            Decayed scores
        """
        decay_factor = self.calculate_decay(created_at)
        return {k: v * decay_factor for k, v in scores.items()}


class MemoryDecayScheduler:
    """Manages decay and deletion of old memories."""

    def __init__(self, db_connection: sqlite3.Connection, decay_engine: EbbinghausDecay):
        self.db = db_connection
        self.decay = decay_engine

    def prune_old_memories(self, table: str, timestamp_field: str = "created_at") -> int:
        """Delete memories below decay threshold.

        Args:
            table: Table name
            timestamp_field: Column name for creation timestamp

        Returns:
            Number of memories deleted
        """
        cursor = self.db.cursor()

        # Get all memories with timestamps
        cursor.execute(f"SELECT id, {timestamp_field} FROM {table}")
        rows = cursor.fetchall()

        deleted_count = 0
        for row_id, created_at in rows:
            if self.decay.should_delete(created_at):
                cursor.execute(f"DELETE FROM {table} WHERE id = ?", (row_id,))
                deleted_count += 1

        self.db.commit()
        return deleted_count

    def apply_decay_to_importance(
        self,
        table: str,
        importance_field: str,
        timestamp_field: str
    ) -> None:
        """Apply decay factor to importance scores.

        Args:
            table: Table name
            importance_field: Column with importance scores
            timestamp_field: Column with creation timestamps
        """
        cursor = self.db.cursor()
        cursor.execute(f"SELECT id, {timestamp_field}, {importance_field} FROM {table}")
        rows = cursor.fetchall()

        for row_id, created_at, original_importance in rows:
            decayed = original_importance * self.decay.calculate_decay(created_at)
            cursor.execute(
                f"UPDATE {table} SET {importance_field} = ? WHERE id = ?",
                (decayed, row_id)
            )

        self.db.commit()
