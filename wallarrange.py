from __future__ import annotations

from collections import defaultdict
from typing import Any, SupportsFloat

import gymnasium as gym
import numpy as np
from gymnasium import spaces
from gymnasium.core import ObsType, ActType

from koming.battlefield import Village, UIVillage
from koming.objects import Cannon, Wall

ACTIONS = (
    (0, -1),  # n
    (0, 1),  # s
    (1, 0),  # e
    (-1, 0),  # w
    (0, 0),  # r
)


class WallArrangerEnv(gym.Env):
    def __init__(self, village: UIVillage, walls_count: int):
        self.sim = village
        self.cannon = self.sim.add_defence(Cannon, 1, (0.5, 0.5))
        self.walls = [self.sim.add_defence(Wall, 1) for _ in range(walls_count)]
        self.distances = self.distance()
        # self.barb = self.sim.add_troop(Barbarian, 1)

        self.action_space = spaces.MultiDiscrete([len(ACTIONS)] * walls_count)
        self.observation_space = spaces.Discrete(2)

    def observe(self):
        return tuple(w.hit_box.topleft for w in self.walls)

    def distance(self):
        return tuple(
            np.linalg.norm(np.array(self.cannon.hit_box.center) - np.array(w.hit_box.topleft)) for w in self.walls
        )

    def reset(
            self,
            *,
            seed: int | None = None,
            options: dict[str, Any] | None = None,
    ) -> tuple[ObsType, dict[str, Any]]:
        for wall in self.walls:
            self.sim.random_move_defence(wall)
        return self.observe(), {}

    def step(
            self, action: ActType
    ) -> tuple[ObsType, SupportsFloat, bool, bool, dict[str, Any]]:
        reward = 0
        terminated = truncated = False

        for i, a in enumerate(action):
            a_direction = ACTIONS[a]
            potential_rect = self.walls[i].hit_box.move(a_direction)
            #if not self.sim.test_hit_valid(potential_rect):
            if self.sim.out_of_range(potential_rect):
                terminated = True
            self.sim.move_defence(self.walls[i], potential_rect)

        reward = sum(np.array(self.distances) - np.array(self.distance()))
        print('Reward', reward)
        self.distances = self.distance()
        observation = self.observe()
        return observation, reward, terminated, truncated, {}


class Agent:
    def __init__(
        self,
        env: WallArrangerEnv,
        learning_rate: float,
        initial_epsilon: float,
        epsilon_decay: float,
        final_epsilon: float,
        discount_factor: float = 0.95,
    ):
        """Initialize a Reinforcement Learning agent with an empty dictionary
        of state-action values (q_values), a learning rate and an epsilon.

        Args:
            learning_rate: The learning rate
            initial_epsilon: The initial epsilon value
            epsilon_decay: The decay for epsilon
            final_epsilon: The final epsilon value
            discount_factor: The discount factor for computing the Q-value
        """
        self.env = env
        self.q_values = defaultdict(lambda: np.zeros(len(ACTIONS)))

        self.lr = learning_rate
        self.discount_factor = discount_factor

        self.epsilon = initial_epsilon
        self.epsilon_decay = epsilon_decay
        self.final_epsilon = final_epsilon

        self.training_error = []

    def get_action(self, obs: tuple[int, int, bool]) -> tuple[int]:
        """
        Returns the best action with probability (1 - epsilon)
        otherwise a random action with probability epsilon to ensure exploration.
        """
        # with probability epsilon return a random action to explore the environment
        if np.random.random() < self.epsilon:
            return self.env.action_space.sample()

        # with probability (1 - epsilon) act greedily (exploit)
        else:
            u = self.q_values[obs]
            return int(np.argmax(self.q_values[obs])) * np.ones(len(self.env.action_space), dtype=int)

    def update(
        self,
        obs: tuple[int, int, bool],
        action: int,
        reward: float,
        terminated: bool,
        next_obs: tuple[int, int, bool],
    ):
        """Updates the Q-value of an action."""
        print(action, self.q_values[obs])

        future_q_value = (not terminated) * np.max(self.q_values[next_obs])
        temporal_difference = (
            reward + self.discount_factor * future_q_value - self.q_values[obs][action]
        )

        self.q_values[obs][action] = (
            self.q_values[obs][action] + self.lr * temporal_difference
        )
        self.training_error.append(temporal_difference)

    def decay_epsilon(self):
        self.epsilon = max(self.final_epsilon, self.epsilon - self.epsilon_decay)
