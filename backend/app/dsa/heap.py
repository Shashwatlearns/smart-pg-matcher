class MaxHeap:
    """Heap where the item with the HIGHEST score (first tuple value) is on top."""

    def __init__(self):
        self.heap = []

    def push(self, item):
        self.heap.append(item)
        self._heapify_up(len(self.heap) - 1)

    def pop(self):
        if not self.heap:
            raise IndexError("pop from empty heap")

        if len(self.heap) == 1:
            return self.heap.pop()

        max_item = self.heap[0]
        self.heap[0] = self.heap.pop()
        self._heapify_down(0)
        return max_item

    def peek(self):
        if not self.heap:
            raise IndexError("peek from empty heap")
        return self.heap[0]

    def _heapify_up(self, index):
        parent_index = (index - 1) // 2
        while index > 0 and self.heap[index][0] > self.heap[parent_index][0]:
            self.heap[index], self.heap[parent_index] = self.heap[parent_index], self.heap[index]
            index = parent_index
            parent_index = (index - 1) // 2

    def _heapify_down(self, index):
        length = len(self.heap)
        while True:
            largest = index
            left_child = 2 * index + 1
            right_child = 2 * index + 2

            if left_child < length and self.heap[left_child][0] > self.heap[largest][0]:
                largest = left_child
            if right_child < length and self.heap[right_child][0] > self.heap[largest][0]:
                largest = right_child

            if largest != index:
                self.heap[index], self.heap[largest] = self.heap[largest], self.heap[index]
                index = largest
            else:
                break

    def __len__(self):
        return len(self.heap)


class MinHeap:
    """Heap where the item with the LOWEST score (first tuple value) is on top."""

    def __init__(self):
        self.heap = []

    def push(self, item):
        self.heap.append(item)
        self._heapify_up(len(self.heap) - 1)

    def pop(self):
        if not self.heap:
            raise IndexError("pop from empty heap")

        if len(self.heap) == 1:
            return self.heap.pop()

        min_item = self.heap[0]
        self.heap[0] = self.heap.pop()
        self._heapify_down(0)
        return min_item

    def peek(self):
        if not self.heap:
            raise IndexError("peek from empty heap")
        return self.heap[0]

    def _heapify_up(self, index):
        parent_index = (index - 1) // 2
        while index > 0 and self.heap[index][0] < self.heap[parent_index][0]:
            self.heap[index], self.heap[parent_index] = self.heap[parent_index], self.heap[index]
            index = parent_index
            parent_index = (index - 1) // 2

    def _heapify_down(self, index):
        length = len(self.heap)
        while True:
            smallest = index
            left_child = 2 * index + 1
            right_child = 2 * index + 2

            if left_child < length and self.heap[left_child][0] < self.heap[smallest][0]:
                smallest = left_child
            if right_child < length and self.heap[right_child][0] < self.heap[smallest][0]:
                smallest = right_child

            if smallest != index:
                self.heap[index], self.heap[smallest] = self.heap[smallest], self.heap[index]
                index = smallest
            else:
                break

    def __len__(self):
        return len(self.heap)


class TopKHeap:
    """
    Keeps only the K best items out of a stream of N items.

    Analogy: a leaderboard with K seats. The person in the LAST seat (the
    weakest of the top K) is the only one you ever compare a newcomer
    against. If the newcomer beats them, the weakest is kicked out.

    Inside, it uses a MinHeap so the weakest of the K is always on top.
    Items are tuples like (score, data). Only the score is compared.

    Time: O(N log K) for N pushes. Memory: O(K).
    """

    def __init__(self, k: int):
        self.k = k
        self.min_heap = MinHeap()

    def push(self, item):
        if self.k <= 0:
            return

        if len(self.min_heap) < self.k:
            # Leaderboard not full yet, so just add the item
            self.min_heap.push(item)
        elif item[0] > self.min_heap.peek()[0]:
            # Full leaderboard, and this item beats the weakest one
            self.min_heap.pop()
            self.min_heap.push(item)

    def get_sorted_desc(self):
        """
        Returns the K items sorted from best to worst.
        Note: this empties the heap.
        """
        result = []
        while len(self.min_heap) > 0:
            result.append(self.min_heap.pop())  # comes out worst to best
        result.reverse()
        return result

    def __len__(self):
        return len(self.min_heap)