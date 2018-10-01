# (C) Datadog, Inc. 2018
# All rights reserved
# Licensed under Simplified BSD License (see LICENSE)


class Limiter(object):
    """
    Limiter implements a simple cut-off capping logic for object count.
    It is used by the AgentCheck class to limit the number of sets of tags
    that can be set by an instance.
    """

    def __init__(self, object_name, object_limit, warning_func=None):
        """
        :param object_name: (plural) name of counted objects for warning wording
        :param object_limit: maximum number of objects to accept before limiting
        :param warning_func: callback function, called with a string when limit is exceeded
        """
        self.warning = warning_func
        self.name = object_name
        self.limit = object_limit

        self.reached_limit = False
        self.count = 0
        self.seen = set()

    def reset(self):
        """
        Resets state and uid set. To be called asap to free memory
        """
        self.reached_limit = False
        self.count = 0
        self.seen.clear()

    def is_reached(self, uid=None):
        """
        is_reached is to be called for every object that counts towards the limit.
        - When called with no uid, the Limiter assumes this is a new object and
        unconditionally increments the counter (less CPU and memory usage).
        - When a given object can be passed multiple times, a uid must be provided to
        deduplicate calls. Only the first occurrence of a uid will increment the counter.

        :param uid: (optional) unique identifier of the object, to deduplicate calls
        :returns: boolean, true if limit exceeded
        """
        if self.reached_limit:
            return True

        if uid:
            if uid in self.seen:
                return False
            self.count += 1
            self.seen.add(uid)
        else:
            self.count += 1

        if self.count > self.limit:
            if self.warning:
                self.warning("Exceeded limit of {} {}, ignoring next ones".format(self.limit, self.name))
            self.reached_limit = True
            return True
        return False

    def get_status(self):
        """
        Returns the internal state of the limiter for unit tests
        """
        return (self.count, self.limit, self.reached_limit)