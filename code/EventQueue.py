import heapq
class EventQueue():
    def __init__(self):
        self.minq = []
    def push(self,event):
        heapq.heappush(self.minq,event)
        pass
    def pop(self):
        return heapq.heappop(self.minq)
    def len(self):
        return len(self.minq)