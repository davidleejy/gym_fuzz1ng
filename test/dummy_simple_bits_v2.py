import gym
import gym_fuzz1ng.coverage as coverage
import numpy as np
from random import randrange

def main():
    env = gym.make('FuzzSimpleBits-v0')
    print("dict_size={} eof={}".format(env.dict_size(), env.eof()))

    MAX_STEPS = 5000



    env.reset()
    c = coverage.Coverage()
    for _ in range(MAX_STEPS):
        
        # take a random action. If there's an RL agent, the agent would control
        # action selection.
        obs, reward, done, info = env.step(env.action_space.sample())
        # print('obs coords where > 0: ', np.where(np.array(obs) > 0)) # debug
        print('input_data used:', info['input_data'])
        if info['action'] == 'run':
            c.add(info['step_coverage']) # update records
            print(("STEP: reward={} done={} " +
                "step={}/{}/{} total={}/{}/{} " +
                "sum={}/{}/{} action={}").format(
                    reward, done,
                    info['step_coverage'].skip_path_count(),
                    info['step_coverage'].transition_count(),
                    info['step_coverage'].crash_count(),
                    info['total_coverage'].skip_path_count(),
                    info['total_coverage'].transition_count(),
                    info['total_coverage'].crash_count(),
                    c.skip_path_count(),
                    c.transition_count(),
                    c.crash_count(),
                    info['action'],
                ))
        else:
            print(("STEP: reward={} done={} action={}").format(
                    reward, done, info['action']
                ))
        if done:
            env.reset()
            print("ENV RESET")


if __name__ == "__main__":
    main()
