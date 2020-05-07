from bisect import bisect_left
from transform import lerp

class KeyFrames:
    """ Stores keyframe pairs for any value type with interpolation_function"""
    def __init__(self, time_value_pairs, interpolation_function=lerp):
        if isinstance(time_value_pairs, dict):  # convert to list of pairs
            time_value_pairs = time_value_pairs.items()
        keyframes = sorted(((key[0], key[1]) for key in time_value_pairs))
        self.times, self.values = zip(*keyframes)  # pairs list -> 2 lists
        self.interpolate = interpolation_function

    def value(self, time):
        """ Computes interpolated value from keyframes, for a given time """

        # 1. ensure time is within bounds else return boundary keyframe
        if time <= self.times[0] or time >= self.times[-1]:
            return self.values[0 if time <= self.times[0] else -1]

        # 2. search for closest index entry in self.times, using bisect_left function
        _i = bisect_left(self.times, time) # _i is the time index just before t

        # 3. using the retrieved index, interpolate between the two neighboring values
        # in self.values, using the initially stored self.interpolate function
        fraction = (time-self.times[_i-1]) / (self.times[_i]-self.times[_i-1])
        return self.interpolate(self.values[_i-1], self.values[_i], fraction)