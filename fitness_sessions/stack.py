# sessions/stack.py
# Manual stack implementation for tracking recently viewed sessions
# Last In First Out (LIFO) - most recent item is on top


class RecentSessionsStack:
    """
    Stack data structure for tracking recently viewed sessions
    Uses LIFO (Last In First Out) ordering

    Operations:
    - push(item): Add item to top of stack
    - pop(): Remove and return item from top of stack
    - is_empty(): Check if stack has no items
    - size(): Get number of items in stack
    - peek(): View top item without removing it
    """

    def __init__(self, max_size=5):
        """
        Initialize empty stack with maximum size limit

        Args:
            max_size: Maximum number of items to store (default 5)
        """
        self.items = []
        self.max_size = max_size

    def push(self, item):
        """
        Add an item to the top of the stack
        If stack exceeds max_size, remove the oldest item (bottom)

        Args:
            item: The session ID to add
        """
        # Add to top of stack
        self.items.append(item)

        # If over max size, remove bottom item (oldest)
        if len(self.items) > self.max_size:
            self.items.pop(0)

    def pop(self):
        """
        Remove and return the item from the top of the stack

        Returns:
            The most recent item, or None if empty
        """
        if not self.is_empty():
            # pop() without index removes from end (top of stack)
            return self.items.pop()
        return None

    def is_empty(self):
        """
        Check if the stack is empty

        Returns:
            True if stack has no items, False otherwise
        """
        return len(self.items) == 0

    def size(self):
        """
        Get the number of items in the stack

        Returns:
            Integer count of items
        """
        return len(self.items)

    def peek(self):
        """
        View the top item without removing it

        Returns:
            The most recent item, or None if empty
        """
        if not self.is_empty():
            return self.items[-1]  # Last item is top of stack
        return None

    def get_all(self):
        """
        Get all items in the stack (from most recent to oldest)

        Returns:
            List of items in LIFO order
        """
        # Return reversed to show most recent first
        return list(reversed(self.items))
