###############################################################################
#  Copyright 2019, by the California Institute of Technology. ALL RIGHTS RESERVED. 
#  United States Government Sponsorship acknowledged. Any commercial use must be 
#  negotiated with the Office of Technology Transfer at the 
#  California Institute of Technology.
#
#  This software may be subject to U.S. export control laws. By accepting this software, 
#  the user agrees to comply with all applicable U.S. export laws and regulations. 
#  User has the responsibility to obtain export licenses, or other export authority 
#  as may be required before exporting such information to foreign countries or providing 
#  access to foreign persons.
#
#  file:	dhmpubsub.py
#  author:	S. Felipe Fregoso
#  description:	Publish/subscribe class specifically done for the DHM software.
#              
###############################################################################
class PubSub(object):

    def __init__(self):
        self._subscribers = {}
        pass

    def subscribe(self, identifier, q, datatype=None):
        try:
            self._subscribers[identifier]['set'].add(q)
        except KeyError as e:
            self._subscribers[identifier] = {'set':set(), 'datatype':datatype}
            self._subscribers[identifier]['set'].add(q)

    def publish(self, identifier, data=None):
        try:
            for v in self._subscribers[identifier]['set']:
                v.put_nowait(data)
        except KeyError as e:
            raise(e)

