from threading import Thread
from time import sleep
import numpy as np
import sys
from particle import Particle
from mayavi import mlab
import matplotlib.pyplot as plt

phi = np.linspace(0, 2*np.pi, 100)
theta = np.linspace(0, np.pi, 100)

class MainCycle:

    def __init__(self, particle_count, delta_t):
        self.particle_count = int(particle_count)
        self.delta_t = float(delta_t)
        self.counter = np.array([0])
        self.total_potential_energy = []
        self.min_potential_energy_pos = []
        self.make_particle_list()

    def call_at_interval(self, period, callback, args):
        while self.counter[-1] < int(args):
            current_counter = round(self.counter[-1] + period, 3)
            self.counter = np.append(self.counter, current_counter)
            #sleep(period)
            callback(args)
        #print('done')
        print(self.total_potential_energy[-1])

    def set_interval(self, period, callback, *args):
        Thread(target=self.call_at_interval, args=(period, callback, args)).start()
        #mlab.show()

    def make_particle_list(self):  # makes list of N particles
        particle_list = []
        for i in range(int(self.particle_count)):
            particle_list.append(Particle(self.delta_t))
        self.particle_list = particle_list

    def get_particle_list(self):
        return self.particle_list

    def set_positions(self):  # sets random INITIAL positions of particles
        for i in range(len(self.particle_list)):
            set_pos = [np.random.rand(3)]
            self.particle_list[i].pos = (set_pos/np.linalg.norm(set_pos))*1
        self.calc_potential_energy(self.particle_list)

    def plot_sphere(self):
        x = 1 * np.outer(np.cos(phi), np.sin(theta))
        y = 1 * np.outer(np.sin(phi), np.sin(theta))
        z = 1 * np.outer(np.ones(np.size(phi)), np.cos(theta))
        mlab.mesh(x, y, z, colormap="Spectral")

    def plot_particles(self): # plots INITIAL positions of particles
        particle_plots = []
        force_plots = []
        for i in range(len(self.particle_list)):
            x = 0.05 * np.outer(np.cos(phi), np.sin(theta)) + self.particle_list[i].pos[0][0]
            y = 0.05 * np.outer(np.sin(phi), np.sin(theta)) + self.particle_list[i].pos[0][1]
            z = 0.05 * np.outer(np.ones(np.size(phi)), np.cos(theta)) + self.particle_list[i].pos[0][2]
            if i == 0:
                particle_plots.append(mlab.mesh(x, y, z, colormap="PuBu"))
            else:
                particle_plots.append(mlab.mesh(x, y, z, colormap="autumn"))
        self.particle_plots = particle_plots

    def calc_forces(self, particle_list):
        for i in range(len(particle_list)):
            total_force = 0
            for j in range(len(particle_list)):
                sep = particle_list[i].pos[-1] - particle_list[j].pos[-1]
                radius = particle_list[i].pos[-1]
                if i!=j:
                    force = particle_list[j].charge * particle_list[i].charge * sep / (np.linalg.norm(sep)) ** 3
                    total_force = total_force + (force - np.dot(force, radius)*(radius/np.linalg.norm(radius)))
            particle_list[i].force = np.vstack((particle_list[i].force, total_force))

    def calc_potential_energy(self, particle_list):
        total_potential_energy = 0
        for i in range(len(particle_list)):
            for j in range(i+1, len(particle_list)):
                sep = particle_list[i].pos[-1] - particle_list[j].pos[-1]
                potential_energy = 1/np.linalg.norm(sep)
                total_potential_energy += potential_energy
        self.total_potential_energy.append(total_potential_energy)

    def get_potential_energy(self):
        return self.total_potential_energy[-1]

    def update_plot(self):
        for i in range(len(self.particle_list)):
            x = 0.05 * np.outer(np.cos(phi), np.sin(theta)) + self.particle_list[i].pos[-1][0]
            y = 0.05 * np.outer(np.sin(phi), np.sin(theta)) + self.particle_list[i].pos[-1][1]
            z = 0.05 * np.outer(np.ones(np.size(phi)), np.cos(theta)) + self.particle_list[i].pos[-1][2]
            self.particle_plots[i].mlab_source.trait_set(x=x, y=y, z=z)

    def iterate_cycle(self, time_duration):
        self.calc_forces(self.particle_list)
        self.calc_potential_energy(self.particle_list)
        for i in range(self.particle_count):
            self.particle_list[i].update()
        print(self.total_potential_energy[-1])
        #self.update_plot()

    def start_cycle(self, time_duration):
        self.set_positions()
        #self.plot_sphere()
        #self.plot_particles()
        #self.set_interval(self.delta_t, self.iterate_cycle, time_duration)
        self.call_at_interval(self.delta_t, self.iterate_cycle, time_duration)
        plt.plot(self.counter, self.total_potential_energy)
        plt.show()

if __name__ == "__main__":
    # first arg will be number of particles and second arg will be delta T in seconds and third arg will be total duration in seconds
    MainCycle(sys.argv[1], sys.argv[2]).start_cycle(sys.argv[3])
