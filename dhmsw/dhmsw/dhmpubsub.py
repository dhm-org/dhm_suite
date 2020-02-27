"""
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
"""
class PubSub():
    """
    Publish/Subscribe Class

    Implemented as a dictionary of message queues
    """
    def __init__(self):
        """
        Constructor
        """
        self._subscribers = {}

    def subscribe(self, identifier, sub_q, datatype=None):
        """
        Subscribe (add) a queue to a list of subscriber:w
        """
        try:
            self._subscribers[identifier]['set'].add(sub_q)
        except KeyError:
            self._subscribers[identifier] = {'set':set(), 'datatype':datatype}
            self._subscribers[identifier]['set'].add(sub_q)

    def publish(self, identifier, data=None):
        """
        Publish data to all subscriber of 'identifier'
        """
        for sub_q in self._subscribers[identifier]['set']:
            sub_q.put_nowait(data)
