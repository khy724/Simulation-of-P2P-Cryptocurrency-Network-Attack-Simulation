import heapq
class TxnEvent():
    def __init__(self,eventTime,fromID,toID,object,at,receivedfrom):
        '''
            -Total three types of events:
                --Txn: A sends B 5 BTC
                --Block: sends block or receives block
                        
            -eventTime : Scheduled time of event
            -type: "Block" or "Txn"
            -use of at:
                Ea is being executed
                generate new event for node a when at==fromID
            -messgae: contains object of the Transaction
        '''
        self.eventTime = eventTime
        self.at = at
        self.fromID = fromID
        self.toID = toID
        self.message = object
        self.receivedfrom = receivedfrom
        pass
    def __lt__(self,other):
        return self.eventTime<other.eventTime