import time

import pygame.event
from tqdm import tqdm

from koming.battlefield import UIVillage
from koming.data import Database
from wallarrange import WallArrangerEnv, Agent

import gymnasium as gym

VILLAGE_SIDE_LEN = 6


if __name__ == '__main__':
    db = Database('koming.sqlite')
    sim = UIVillage(VILLAGE_SIDE_LEN, db, 'resources', True)
    env = WallArrangerEnv(sim, 2)

    learning_rate = 0.01
    n_episodes = 100_000
    start_epsilon = 1.0
    epsilon_decay = start_epsilon / (n_episodes / 2)  # reduce the exploration over time
    final_epsilon = 0.1

    agent = Agent(
        env,
        learning_rate=learning_rate,
        initial_epsilon=start_epsilon,
        epsilon_decay=epsilon_decay,
        final_epsilon=final_epsilon,
    )

    env = gym.wrappers.RecordEpisodeStatistics(env, deque_size=n_episodes)
    for episode in tqdm(range(n_episodes)):
        obs, info = env.reset()
        sim.redraw_defences()
        sim.render()
        done = False

        # play one episode
        while not done:
            action = agent.get_action(obs)
            next_obs, reward, terminated, truncated, info = env.step(action)

            perfect = True
            for obs in next_obs:
                perfect = perfect and obs == env.cannon.hit_box.center

            # update the agent
            agent.update(obs, action, reward, terminated, next_obs)
            sim.redraw_defences()
            sim.render()
            #time.sleep(1/3)
            pygame.event.pump()

            if perfect:
                input('All reached center')

            # update if the environment is done and the current obs
            done = terminated or truncated
            obs = next_obs

        agent.decay_epsilon()

    #sim.run()
    input('Completed')
