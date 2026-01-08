# trainer_bookings/min_heap.py
# Manual min-heap implementation for priority queue
# Lower priority score = higher priority (processed first)


class MinHeap:
    """
    Min-Heap data structure for priority queue
    Parent node has smaller value than children

    Array representation:
    - Parent of index i is at (i-1)//2
    - Left child of index i is at 2*i + 1
    - Right child of index i is at 2*i + 2

    Operations:
    - insert(item): Add item and maintain heap property
    - extract_min(): Remove and return minimum (root)
    - heapify_up(index): Fix heap upward from index
    - heapify_down(index): Fix heap downward from index
    - get_min(): View minimum without removing
    """

    def __init__(self):
        """Initialize empty heap"""
        self.heap = []

    def size(self):
        """Get number of items in heap"""
        return len(self.heap)

    def is_empty(self):
        """Check if heap is empty"""
        return len(self.heap) == 0

    def get_parent_index(self, index):
        """Get index of parent node"""
        return (index - 1) // 2

    def get_left_child_index(self, index):
        """Get index of left child"""
        return 2 * index + 1

    def get_right_child_index(self, index):
        """Get index of right child"""
        return 2 * index + 2

    def has_parent(self, index):
        """Check if node has a parent"""
        return self.get_parent_index(index) >= 0

    def has_left_child(self, index):
        """Check if node has left child"""
        return self.get_left_child_index(index) < len(self.heap)

    def has_right_child(self, index):
        """Check if node has right child"""
        return self.get_right_child_index(index) < len(self.heap)

    def parent(self, index):
        """Get parent node value"""
        return self.heap[self.get_parent_index(index)]

    def left_child(self, index):
        """Get left child value"""
        return self.heap[self.get_left_child_index(index)]

    def right_child(self, index):
        """Get right child value"""
        return self.heap[self.get_right_child_index(index)]

    def swap(self, index1, index2):
        """Swap two elements in heap"""
        self.heap[index1], self.heap[index2] = self.heap[index2], self.heap[index1]

    def get_min(self):
        """
        View minimum element without removing it

        Returns:
            Minimum element (root), or None if empty
        """
        if self.is_empty():
            return None
        return self.heap[0]

    def insert(self, item):
        """
        Insert new item into heap and maintain heap property

        Args:
            item: Tuple of (priority_score, booking_object)

        Process:
        1. Add item to end of array
        2. Heapify up to restore heap property
        """
        self.heap.append(item)
        self.heapify_up(len(self.heap) - 1)

    def heapify_up(self, index):
        """
        Fix heap property by moving element up
        Compare with parent and swap if needed

        Args:
            index: Index of element to heapify up
        """
        # While element has parent and is smaller than parent
        while self.has_parent(index) and self.heap[index][0] < self.parent(index)[0]:
            # Swap with parent
            parent_index = self.get_parent_index(index)
            self.swap(index, parent_index)
            index = parent_index

    def extract_min(self):
        """
        Remove and return minimum element (root)

        Returns:
            Minimum element, or None if empty

        Process:
        1. Save root element
        2. Move last element to root
        3. Heapify down to restore heap property
        """
        if self.is_empty():
            return None

        # Save minimum
        min_item = self.heap[0]

        # Move last element to root
        self.heap[0] = self.heap[len(self.heap) - 1]
        self.heap.pop()

        # Restore heap property
        if not self.is_empty():
            self.heapify_down(0)

        return min_item

    def heapify_down(self, index):
        """
        Fix heap property by moving element down
        Compare with children and swap with smaller child if needed

        Args:
            index: Index of element to heapify down
        """
        # While element has at least one child
        while self.has_left_child(index):
            # Find smaller child
            smaller_child_index = self.get_left_child_index(index)

            # Check if right child exists and is smaller than left
            if (self.has_right_child(index) and
                self.right_child(index)[0] < self.left_child(index)[0]):
                smaller_child_index = self.get_right_child_index(index)

            # If current element is smaller than smaller child, heap property is satisfied
            if self.heap[index][0] < self.heap[smaller_child_index][0]:
                break

            # Swap with smaller child
            self.swap(index, smaller_child_index)
            index = smaller_child_index

    def get_all(self):
        """
        Get all elements in heap order (for debugging/display)

        Returns:
            List of all items in heap
        """
        return self.heap.copy()
