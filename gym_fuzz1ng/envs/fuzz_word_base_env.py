import gym
import numpy as np

from gym import spaces

import gym_fuzz1ng.coverage as coverage


class FuzzWordBaseEnv(gym.Env):
    def __init__(self):
        # Classes that inherit FuzzWordBase must define before calling this
        # constructor:
        # - self.max_input_size
        # - self.dict
        # - self.target_path
        self.engine = coverage.Afl(
            self.target_path, launch_afl_forkserver=True,
        )
        self.observation_space = spaces.Box(
            0, np.inf, shape=(2, coverage.PATH_MAP_SIZE), dtype='int32',
        )
        self.action_space = spaces.Box(
            0, self.dict.size(), shape=(self.max_input_size,), dtype='int32',
        )
        self.reset()

    def reset(self):
        self.total_coverage = coverage.Coverage()

        return np.stack([
            self.total_coverage.observation(),
            coverage.Coverage().observation(),
        ])

    def step(self, action):
        assert self.action_space.contains(action)

        reward = 0.0
        done = False

        input_data = b""

        for i in range(self.max_input_size):
            if int(action[i]) == self.dict.eof():
                break
            input_data += self.dict.bytes(int(action[i]))

        c = self.engine.run(input_data)

        old_path_count = self.total_coverage.path_count()
        self.total_coverage.add(c)
        new_path_count = self.total_coverage.path_count()

        if old_path_count == new_path_count:
            done = True

        reward = c.transition_count()

        if c.crash_count() > 0:
            print("CRASH {}".format(input_data))

        return np.stack([
            self.total_coverage.observation(),
            c.observation(),
        ]), reward, done, {
            "step_coverage": c,
            "total_coverage": self.total_coverage,
            "input_data": input_data,
        }

    def render(self, mode='human', close=False):
        pass
