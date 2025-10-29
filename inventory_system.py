"""
Inventory Management System.

A simple inventory tracking system that manages stock levels,
provides logging of all operations, and supports data persistence.
"""

import json
from datetime import datetime
from typing import Dict, List, Optional


class InventoryManager:
    """Manages inventory stock and activity logging."""

    def __init__(self):
        """Initialize inventory manager with empty stock and log."""
        self.stock_data: Dict[str, int] = {}
        self.activity_log: List[str] = []

    def add_item(
        self,
        item: str = "default",
        qty: int = 0,
        logs: Optional[List[str]] = None
    ) -> None:
        """Add items to inventory."""
        # Validate types and values
        if not isinstance(item, str) or not isinstance(qty, int):
            raise TypeError(
                "Item must be a string and qty must be an integer"
            )
        if not item.strip():
            raise ValueError("Item name cannot be empty")
        if qty < 0:
            raise ValueError("Quantity to add cannot be negative")

        # Use provided logs list or default to instance activity_log
        target_logs = logs if logs is not None else self.activity_log

        # Update stock
        self.stock_data[item] = self.stock_data.get(item, 0) + qty

        # Log action
        timestamp = datetime.now().isoformat(timespec='seconds')
        target_logs.append(f"{timestamp}: Added {qty} of {item}")

    def remove_item(
        self,
        item: str,
        qty: int,
        logs: Optional[List[str]] = None
    ) -> None:
        """Remove items from inventory."""
        if not isinstance(item, str) or not isinstance(qty, int):
            raise TypeError(
                "Item must be a string and qty must be an integer"
            )
        if qty < 0:
            raise ValueError("Quantity to remove cannot be negative")

        # Use provided logs list or default to instance activity_log
        target_logs = logs if logs is not None else self.activity_log

        current = self.stock_data.get(item, 0)
        if current == 0:
            # Silently ignore removal of non-existent items
            return

        # Calculate actual quantity removed
        actual_qty_removed = min(qty, current)
        new_qty = current - actual_qty_removed

        if new_qty > 0:
            self.stock_data[item] = new_qty
        else:
            # Remove item when depleted
            del self.stock_data[item]

        timestamp = datetime.now().isoformat(timespec='seconds')
        target_logs.append(
            f"{timestamp}: Removed {actual_qty_removed} of {item}"
        )

    def get_qty(self, item: str) -> int:
        """Get quantity of an item."""
        if not isinstance(item, str):
            raise TypeError("Item must be a string")
        # Return 0 for missing items to avoid KeyError
        return self.stock_data.get(item, 0)

    def load_data(self, file: str = "inventory.json") -> None:
        """Load inventory data from JSON file."""
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                raise ValueError("Invalid inventory file format")
            # Coerce values to int safely
            cleaned: Dict[str, int] = {}
            for k, v in data.items():
                if not isinstance(k, str):
                    continue
                try:
                    cleaned[k] = int(v)
                except (TypeError, ValueError):
                    continue
            self.stock_data = cleaned
            timestamp = datetime.now().isoformat(timespec='seconds')
            self.activity_log.append(
                f"{timestamp}: Loaded inventory from {file}"
            )
        except FileNotFoundError:
            # Start with empty inventory if file missing
            self.stock_data = {}
            timestamp = datetime.now().isoformat(timespec='seconds')
            self.activity_log.append(
                f"{timestamp}: Inventory file not found; initialized empty"
            )
        except json.JSONDecodeError as e:
            # Keep existing data if corrupt
            timestamp = datetime.now().isoformat(timespec='seconds')
            self.activity_log.append(
                f"{timestamp}: Failed to parse {file}: {e}"
            )

    def save_data(self, file: str = "inventory.json") -> None:
        """Save inventory data to JSON file."""
        with open(file, "w", encoding="utf-8") as f:
            json.dump(self.stock_data, f, ensure_ascii=False, indent=2)
        timestamp = datetime.now().isoformat(timespec='seconds')
        self.activity_log.append(
            f"{timestamp}: Saved inventory to {file}"
        )

    def print_data(self) -> None:
        """Print current inventory."""
        print("Items Report")
        if not self.stock_data:
            print("(no items)")
            return
        for item, qty in self.stock_data.items():
            print(f"{item} -> {qty}")

    def check_low_items(self, threshold: int = 5) -> List[str]:
        """Check items below threshold."""
        if not isinstance(threshold, int) or threshold < 0:
            raise ValueError("Threshold must be a non-negative integer")
        return [i for i, q in self.stock_data.items() if q < threshold]

    def print_log(self, logs: Optional[List[str]] = None) -> None:
        """Print activity log."""
        target_logs = logs if logs is not None else self.activity_log
        print("Activity Log")
        if not target_logs:
            print("(no activity)")
            return
        for entry in target_logs:
            print(entry)


def main() -> None:
    """Main function to demonstrate inventory operations."""
    # Create inventory manager instance
    inventory = InventoryManager()

    # Fresh start: load existing data if any
    inventory.load_data()

    # Valid operations
    inventory.add_item("apple", 10)
    inventory.add_item("banana", 2)

    inventory.remove_item("apple", 3)
    # Removing a non-existent item is a no-op
    inventory.remove_item("orange", 1)

    print("Apple stock:", inventory.get_qty("apple"))
    print("Low items:", inventory.check_low_items())

    inventory.save_data()
    inventory.print_data()
    inventory.print_log()


if __name__ == "__main__":
    main()
