from enum import Enum
from queue import Queue

import numpy as np
from nbtschematic import SchematicFile

from schempic import gen_pic_schem


class SchemBlock(Enum):
    AIR = 0
    EXTERNAL = 1
    INTERNAL = 2


flammables = [5, 17,
              85, 107, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192,
              35, 171, 173]


class Ship:
    def __init__(self, path):
        self.path = path
        st = SchematicFile.load(self.path)
        self.schem = SchematicFile(shape=(st.shape[0] + 2, st.shape[1] + 2, st.shape[2] + 2))
        self.name = ''.join(path.split('/')[-1].split('.')[:-1])
        self.types = np.full((self.schem.shape[0], self.schem.shape[1], self.schem.shape[2]), 2)
        self.depths = np.full((self.schem.shape[0], self.schem.shape[1], self.schem.shape[2]), 0)

    def map(self):
        st = SchematicFile.load(self.path)
        for y in range(0, st.shape[0]):
            for z in range(0, st.shape[1]):
                for x in range(0, st.shape[2]):
                    self.schem.blocks[y + 1, z + 1, x + 1] = st.blocks[y, z, x]
                    self.schem.data[y + 1, z + 1, x + 1] = st.data[y, z, x]
        s = self.schem

        # --Mark block types--
        aq = Queue(0)
        eq = Queue(0)
        for y in (0, s.shape[0] - 1):
            for z in (0, s.shape[1] - 1):
                for x in (0, s.shape[2] - 1):
                    aq.put((y, z, x))
        # Recursively mark air blocks
        while not aq.empty():
            coord = aq.get()
            if coord[0] < 0 or s.shape[0] <= coord[0]:
                continue
            if coord[1] < 0 or s.shape[1] <= coord[1]:
                continue
            if coord[2] < 0 or s.shape[2] <= coord[2]:
                continue
            if self.types[coord[0], coord[1], coord[2]] != 2:
                continue
            block = s.blocks[coord[0], coord[1], coord[2]]
            if block == 0:
                self.types[coord[0], coord[1], coord[2]] = 0
                aq.put((coord[0] + 1, coord[1], coord[2]))
                aq.put((coord[0] - 1, coord[1], coord[2]))
                aq.put((coord[0], coord[1] + 1, coord[2]))
                aq.put((coord[0], coord[1] - 1, coord[2]))
                aq.put((coord[0], coord[1], coord[2] + 1))
                aq.put((coord[0], coord[1], coord[2] - 1))
            elif block in flammables:
                eq.put((coord[0], coord[1], coord[2], 0))
        # Recursively mark exterior flammable blocks
        while not eq.empty():
            coord = eq.get()
            depth = coord[3]
            if coord[0] < 0 or s.shape[0] <= coord[0]:
                continue
            if coord[1] < 0 or s.shape[1] <= coord[1]:
                continue
            if coord[2] < 0 or s.shape[2] <= coord[2]:
                continue
            if self.types[coord[0], coord[1], coord[2]] == 1:
                if depth < self.depths[coord[0], coord[1], coord[2]]:
                    self.depths[coord[0], coord[1], coord[2]] = depth
            if self.types[coord[0], coord[1], coord[2]] != 2:
                continue
            block = s.blocks[coord[0], coord[1], coord[2]]
            if block in flammables or block == 0:
                self.types[coord[0], coord[1], coord[2]] = 1
                self.depths[coord[0], coord[1], coord[2]] = depth
                if block != 0:
                    depth += 1
                eq.put((coord[0] + 1, coord[1], coord[2], depth))
                eq.put((coord[0] - 1, coord[1], coord[2], depth))
                eq.put((coord[0], coord[1] + 1, coord[2], depth))
                eq.put((coord[0], coord[1] - 1, coord[2], depth))
                eq.put((coord[0], coord[1], coord[2] + 1, depth))
                eq.put((coord[0], coord[1], coord[2] - 1, depth))

    def size(self):
        n = 0
        for y in range(0, self.schem.shape[0]):
            for z in range(0, self.schem.shape[1]):
                for x in range(0, self.schem.shape[2]):
                    if self.types[y, z, x] != 0:
                        if self.schem.blocks[y, z, x] != 0:
                            n += 1
        return n

    def lift(self):
        n = 0
        w = 0
        for y in range(0, self.schem.shape[0]):
            for z in range(0, self.schem.shape[1]):
                for x in range(0, self.schem.shape[2]):
                    if self.schem.blocks[y, z, x] == 35:
                        w += 1
                    if self.schem.blocks[y, z, x] != 0:
                        n += 1
        return w / n

    def internal_lift(self):
        n = 0
        w = 0
        for y in range(0, self.schem.shape[0]):
            for z in range(0, self.schem.shape[1]):
                for x in range(0, self.schem.shape[2]):
                    if self.types[y, z, x] == 2:
                        if self.schem.blocks[y, z, x] == 35:
                            w += 1
                        if self.schem.blocks[y, z, x] != 0:
                            n += 1
        return w / n

    def engines(self):
        n = 0
        w = 0
        a = []
        for y in range(0, self.schem.shape[0]):
            for z in range(0, self.schem.shape[1]):
                for x in range(0, self.schem.shape[2]):
                    if self.types[y, z, x] != 0:
                        if self.schem.blocks[y, z, x] == -104:
                            w += 1
                        if self.schem.blocks[y, z, x] != 0:
                            n += 1
        return w / n

    def fire_depth(self):
        depth = 0
        for y in range(0, self.schem.shape[0]):
            for z in range(0, self.schem.shape[1]):
                for x in range(0, self.schem.shape[2]):
                    if self.types[y, z, x] == 1 and self.schem.blocks[y, z, x] != 0:
                        if self.depths[y, z, x] > depth:
                            depth = self.depths[y, z, x]
        return depth

    def fire_test(self):
        sf = SchematicFile(shape=(self.schem.shape[0] - 2, self.schem.shape[1] - 2, self.schem.shape[2] - 2))
        for y in range(1, self.schem.shape[0] - 1):
            for z in range(1, self.schem.shape[1] - 1):
                for x in range(1, self.schem.shape[2] - 1):
                    if self.types[y, z, x] == 1 and self.schem.blocks[y, z, x] != 0:
                        if 0 < self.depths[y, z, x] < 5:
                            sf.blocks[y - 1, z - 1, x - 1] = 251
                            sf.data[y - 1, z - 1, x - 1] = 1
                            if 2 < self.depths[y, z, x]:
                                sf.data[y - 1, z - 1, x - 1] = 14
        gen_pic_schem(sf, self.name + "-firetest")
        se = SchematicFile(shape=(self.schem.shape[0] - 2, self.schem.shape[1] - 2, self.schem.shape[2] - 2))
        for y in range(1, self.schem.shape[0] - 1):
            for z in range(1, self.schem.shape[1] - 1):
                for x in range(1, self.schem.shape[2] - 1):
                    se.blocks[y - 1, z - 1, x - 1] = self.schem.blocks[y, z, x]
                    se.data[y - 1, z - 1, x - 1] = self.schem.data[y, z, x]
                    if self.types[y, z, x] == 1 and self.schem.blocks[y, z, x] != 0:
                        if 0 < self.depths[y, z, x]:
                            se.blocks[y - 1, z - 1, x - 1] = 95
                            se.data[y - 1, z - 1, x - 1] = 1
                            if 2 < self.depths[y, z, x]:
                                se.data[y - 1, z - 1, x - 1] = 14
                            if 5 < self.depths[y, z, x]:
                                se.data[y - 1, z - 1, x - 1] = 15
        se.save('temp/-firetest.schematic')

    def hole_test(self):
        hl = 0
        sf = SchematicFile(shape=(self.schem.shape[0] - 2, self.schem.shape[1] - 2, self.schem.shape[2] - 2))
        for y in range(1, self.schem.shape[0] - 1):
            for z in range(1, self.schem.shape[1] - 1):
                for x in range(1, self.schem.shape[2] - 1):
                    if self.types[y, z, x] == 2 and self.schem.blocks[y, z, x] == 0:
                        sf.blocks[y - 1, z - 1, x - 1] = 251
                        sf.data[y - 1, z - 1, x - 1] = 3
                        hl += 1
        gen_pic_schem(sf, self.name + "-holetest", light=15)
        sf = SchematicFile(shape=(self.schem.shape[0] - 2, self.schem.shape[1] - 2, self.schem.shape[2] - 2))
        for y in range(1, self.schem.shape[0] - 1):
            for z in range(1, self.schem.shape[1] - 1):
                for x in range(1, self.schem.shape[2] - 1):
                    sf.blocks[y - 1, z - 1, x - 1] = self.schem.blocks[y, z, x]
                    sf.data[y - 1, z - 1, x - 1] = self.schem.data[y, z, x]
                    if self.types[y, z, x] == 2 and self.schem.blocks[y, z, x] == 0:
                        sf.blocks[y - 1, z - 1, x - 1] = 95
                        sf.data[y - 1, z - 1, x - 1] = 3
        sf.save('temp/-holetest.schematic')
        return hl
