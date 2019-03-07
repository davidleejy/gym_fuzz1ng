# gym-fuzz1ng

## Info for Collaborators

AFL (a popular fuzzer) is wrapped in an OpenAI gym environment. `dummy_simple_bits_v2.py` creates an environment that has AFL and a simple binary to be fuzzed, and picks random actions (bit flips, bit insertions, etc.) to mutate the input to be passed to the binary. 

`fuzz_simple_bits_env_v2.py` contains the environment that is used.

The RL agent is not implemented yet.

More info in google docs for now :)

## Install

Python version 3.5.x or 3.6.x

```
# Activate virtual environment if you're using one (generally speaking it's good practise to haha)
conda activate gymfuzz

# cd to where the setup.py file is
cd gym_fuzz1ng

# Install gym_fuzz1ng package. -e flag means editable. Editable means that modifying the code here will directly modify the gym_fuzz1ng package that is imported elsewhere.
pip install -e .

# Let's build AFL (a popular fuzzer) and toy binaries for fuzzing.
cd gym_fuzz1ng/mods
make clean
make all

# Turns out that AFL needs 2 things to be set: core pattern and cpu frequency scaling. You may need to run the following as superuser. If you cannot "sudo echo", try "sudo bash" to launch an elevated bash shell to run these commands.

echo core >/proc/sys/kernel/core_pattern

echo performance | tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# Run a dummy example.
python test/dummy_simple_bits_v2.py
```

## credits
Forked from https://github.com/spolu/gym_fuzz1ng and modified.

# README OF ORIGINAL REPO:

# gym-fuzz1ng

OpenAI Gym[0] environment for binary fuzzing of a variety of libraries (libpng
for now), executables, as well as simpler examples.

The environment's engine is based on american fuzzy lop[1] (afl) and capable of
thousands of executions per seconds for moderaltely sized executables.

The action space is the following:
```
Box(low=0, high=DICT_SIZE-1, shape=(INPUT_SIZE,), dtype='int32')
```

`DICT_SIZE` and `INPUT_SIZE` depend on the environnment and the underlying
program to fuzz:
- `DICT_SIZE` is the size of the dictionnary used to fuzz the program. `EOF` is
  represented by `DICT_SIZE-1` and accessible by the `eof()` method on the
  environment.
- `INPUT_SIZE` is the input submitted for fuzzing it is fixed for each
  environment and represents a maximal size for inputs to fuzz; smaller inputs
  can be represented using `EOF`.

The environment simulates the following game:

- each action submits a full input for fuzzing and returns the number of unique
  transitions executed as reward.
- if no new coverage is discovered by an input, the game is ended.

(It is possible to simply call `step` independently of whether the game is done
or not if you're just interested in easily executing binaries and retrieving
the associated coverage from Python. See also `step_raw`[2]).

The observation space is the following:
```
Box(low=0, high=255, shape=(256, 256), dtype='int32')
```

To compute coverage, the underlying excecution engine assigns a random integer
in `[0, 255]` to each simple block in the targeted binary.  The coverage is
then represented by a `256x256` matrix of `int8` representing the number of
time a transition was executed (note that this differs from how afl computes
coverage). Since `int8` are used for efficiency, the number of transitions can
only be within `[0, 255]` and wraps otherwise. This coverage matrix for the
last step execution is exactly what is returned as observation.

- [0] https://gym.openai.com/
- [1] http://lcamtuf.coredump.cx/afl/
- [2] https://github.com/spolu/gym_fuzz1ng/blob/master/gym_fuzz1ng/envs/fuzz_base_env.py

## Installation

```
# Note that running setup.py bdist_wheel takes a bit a time as it builds our
# afl mod as well as the available targets.
pip install .

# You may need to run the following commands as well as superuser.
echo core >/proc/sys/kernel/core_pattern

# You can then test that everything works by running our dummy example.
python dummy_simple_bits.py
```

## Available environments

### `FuzzLibPNGEnv`

Fuzzing environment for libpng-1.6.34 (recent).

- **action_space**: `Box(low=0, high=283, shape=(1024,))` dictionary composed
  of magic tokens, all 255 bytes and EOF. Maximum input size is 1024.

### `FuzzSimpleBits-v0`

Fuzzing environment for the `simple_bits` executable (see
[code](https://github.com/spolu/gym_fuzz1ng/blob/master/gym_fuzz1ng/mods/simple_bits-mod/simple_bits_afl.c)).

- **action_space**: `Box(low=0, high=256, shape=(64,))` dictionary composed
  all 256 bytes and EOF. Maximum input size is 64.

### `FuzzSimpleLoop-v0`

Fuzzing environment for the `simple_loop` executable (see
[code](https://github.com/spolu/gym_fuzz1ng/blob/master/gym_fuzz1ng/mods/simple_loop-mod/simple_loop_afl.c)).

- **action_space**: `Box(low=0, high=256, shape=(8,))` dictionary composed
  all 256 bytes and EOF. Maximum input size is 8.

### `FuzzChecksum_{2,4,8}_{2,4,8}-v0`

Fuzzing environment for the `checksum_k_n` executable (see
[code](https://github.com/spolu/gym_fuzz1ng/blob/master/gym_fuzz1ng/mods/checksum_k_n-mod/checksum_k_n_afl.c)).

- **action_space**: `Box(low=0, high=256, shape=(8,))` dictionary composed
  all 256 bytes and EOF. Maximum input size is 72.
