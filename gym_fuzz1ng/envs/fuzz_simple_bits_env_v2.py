import gym_fuzz1ng
import gym_fuzz1ng.coverage as coverage
from gym_fuzz1ng.envs.fuzz_base_env import FuzzBaseEnv
from random import randrange
from bitarray import bitarray
from gym import spaces


class FuzzSimpleBitsEnv(FuzzBaseEnv):
    def __init__(self):
        self._input_size = 64
        self._target_path = gym_fuzz1ng.simple_bits_target_path()
        self._args = []
        self._dict = coverage.Dictionary({
            'tokens': [b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x00',
                       b'\xde\xad\xbe\xef' ],
            'bytes': True,
        }) # Gather a bunch of tokens to be used later in fuzzing.
        
        super(FuzzSimpleBitsEnv, self).__init__()

        # Override action space.
        self.actions_available = ['bitflip',
                                  'insert',
                                  'delete',
                                  #'arithmetics',
                                  # 'crossover',
                                  'new',
                                  'run'
                                  ]
        self.action_space = spaces.Discrete(len(self.actions_available))

        # initialize data to be passed as input to binary for fuzzing.        
        self.input_data = self._dict.bytes(int(randrange(self._dict.eof())))


    def step_raw(self, action):
        raise Exception('Don''t use this function.')

    @staticmethod
    def flip_bits(data, n_flips):
        # data is like b'\x01\xef\x3d'.
        b = bitarray()
        b.frombytes(data)
        for _ in range(n_flips):
            i = randrange(len(b))
            b[i] = not b[i] # flip
        return b.tobytes()

    @staticmethod
    def insert_bits(data, n_inserts):
        # data is like b'\x01\xef\x3d'.
        b = bitarray()
        b.frombytes(data)
        for _ in range(n_inserts):
            i = randrange(len(b))
            b.insert(i, True)
        return b.tobytes()

    @staticmethod
    def delete_bits(data, n_deletes):
        # data is like b'\x01\xef\x3d'.
        b = bitarray()
        b.frombytes(data)
        for _ in range(n_deletes):
            i = randrange(len(b))
            b.pop(i)
        return b.tobytes()


    def step(self, action):
        input_data = self.input_data
        run_binary = False
        if 'bitflip' == self.actions_available[action]:
            # randomly flip bits. TODO can be improved. e.g. give choice of which bit to flip.
            n_flips = randrange(min(8, len(input_data)))
            input_data = self.flip_bits(input_data, n_flips)
        elif 'insert' == self.actions_available[action]:
            # randomly insert bits. TODO can be improved. e.g. give choice of where to insert bit.
            n_inserts = randrange(16)
            input_data = self.insert_bits(input_data, n_inserts)
        elif 'delete' == self.actions_available[action]:
            # randomly delete bits. TODO can be improved. e.g. give choice of where to delete.
            n_deletes = randrange(len(input_data))
            if n_deletes > 0:
                input_data = self.delete_bits(input_data, n_deletes)
        
        #elif 'arithmetics' == actions_available[action]:
            # what is arithmetics in AFL?

        # elif 'crossover' == self.actions_available[action]:
            # crossover with random candidate with random crossover point. TODO can be improved. e.g. give choice of crossover candidate and crossover point.
            
        elif 'new' == self.actions_available[action]:
            # replace with new random data. # TODO can be improved.
            input_data = self._dict.bytes(int(randrange(self._dict.eof())))

        elif 'run' == self.actions_available[action]:
            run_binary = True
        else:
            raise Exception('No such action.')
        
        # record mutated input_data
        self.input_data = input_data

        if run_binary:
            # Run the binary with the mutate input.
            c = self.engine.run(input_data)
        
            # Did you crash the binary? Congrats!
            if c.crash_count() > 0:
                print("CRASH {}".format(input_data))
        
            # Compute reward. Currently reward is based on code coverage
            # garnered by the input passed to the binary.
            reward = c.transition_count()

            # Are we done? We are done when no new edges are visited
            # compared to all edges visited by previous inputs.
            old_path_count = self.total_coverage.skip_path_count()
            self.total_coverage.add(c)
            new_path_count = self.total_coverage.skip_path_count()
            done = (old_path_count == new_path_count)

            # The environment also can give the agent
            # an observation and additional info.
            info = {'step_coverage': c,
                    'total_coverage' : self.total_coverage,
                    'input_data': input_data,
                    'action' : self.actions_available[action]
                    }
            obs = c.observation()

        else: # Don't run the binary this step.
            reward = -1
            done = False
            obs = None
            info = {'input_data': input_data,
                    'action': self.actions_available[action]
                    }

        return obs, reward, done, info

