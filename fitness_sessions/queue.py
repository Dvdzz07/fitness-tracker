# sessions/queue.py
# Manual queue implementation for processing join requests in FIFO order
# First In First Out (FIFO) - requests are processed in the order they arrive


class SessionJoinQueue:
    """
    Queue data structure for processing session join requests
    Uses FIFO (First In First Out) ordering

    Operations:
    - enqueue(item): Add item to back of queue
    - dequeue(): Remove and return item from front of queue
    - is_empty(): Check if queue has no items
    - size(): Get number of items in queue
    - peek(): View front item without removing it
    """

    def __init__(self):
        """Initialize empty queue using a list"""
        self.items = []

    def enqueue(self, item):
        """
        Add an item to the back of the queue

        Args:
            item: The join request object to add
        """
        self.items.append(item)

    def dequeue(self):
        """
        Remove and return the item from the front of the queue

        Returns:
            The first item in the queue, or None if empty
        """
        if not self.is_empty():
            # pop(0) removes from index 0 (front of queue)
            return self.items.pop(0)
        return None

    def is_empty(self):
        """
        Check if the queue is empty

        Returns:
            True if queue has no items, False otherwise
        """
        return len(self.items) == 0

    def size(self):
        """
        Get the number of items in the queue

        Returns:
            Integer count of items
        """
        return len(self.items)

    def peek(self):
        """
        View the front item without removing it

        Returns:
            The first item in the queue, or None if empty
        """
        if not self.is_empty():
            return self.items[0]
        return None
