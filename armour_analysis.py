from nbtschematic import SchematicFile
import math
import ship_stats
from ship_stats import Ship
import numpy as np
import PIL
from PIL import Image as Img, ImageOps

tnt_r = [8, 10, 13, 13, 10, 8, 0]
armour_blocks = [121, -50, 8, 9, 10, 11]
non_solid_blocks = [0, 55, 75, 76, 93, 94, -107, -106, 69, 77, -113, 50, -85, 70, 72, -109, -108,
                    8, 9, 10, 11, 63, 68]
liquids = [8, 9, 10, 11]


def sq_dist(a, b):
    return ((a[0] - b[0]) ** 2) + ((a[1] - b[1]) ** 2)


def blast(by, bz, bx):
    blast_list = []
    for y in range(0, 7):
        for z in range(0, 7):
            for x in range(0, 7):
                if sq_dist((x, z), (3, 3)) <= tnt_r[y]:
                    blast_list.append((by + y - 3, bz + z - 3, bx + x - 3))
    return blast_list


def score_color(score):
    if score < 2:
        return (192, 192, 192, 255)
    elif score < 3:
        return (105, 179, 76, 255)
    elif score < 5:
        return (172, 179, 52, 255)
    elif score < 7:
        return (250, 183, 51, 255)
    elif score < 8:
        return (255, 142, 21, 255)
    elif score < 9:
        return (255, 78, 17, 255)
    else:
        return (255, 13, 13, 255)

async def armour_test(ship: Ship):
    sf = ship.schem
    strength = np.full((sf.shape[0], sf.shape[1], sf.shape[2]), 3)
    # X+ hitscan
    in_liquid = False
    for z in range(0, sf.shape[1]):
        for y in range(0, sf.shape[0]):
            for x in range(0, sf.shape[2]):
                if ship.types[y, z, x] == 2 and ship.types[y, z, x] not in non_solid_blocks and not in_liquid:
                    x -= 1
                    for block in blast(y, z, x):
                        if 0 <= block[0] < sf.shape[0] and 0 <= block[1] < sf.shape[1] and 0 <= block[2] < sf.shape[2]:
                            if sf.blocks[y, z, x] not in [8, 9, 10, 11]:
                                strength[block[0], block[1], block[2]] = 2
                    break
                in_liquid = ship.types[y, z, x] in liquids
    # X- hitscan
    in_liquid = False
    for z in range(0, sf.shape[1]):
        for y in range(0, sf.shape[0]):
            for x in range(sf.shape[2] - 1, -1, -1):
                if ship.types[y, z, x] == 2 and ship.types[y, z, x] not in non_solid_blocks and not in_liquid:
                    x += 1
                    for block in blast(y, z, x):
                        if 0 <= block[0] < sf.shape[0] and 0 <= block[1] < sf.shape[1] and 0 <= block[2] < sf.shape[2]:
                            if sf.blocks[y, z, x] not in [8, 9, 10, 11]:
                                strength[block[0], block[1], block[2]] = 2
                    break
                in_liquid = ship.types[y, z, x] in liquids
    # Z+ hitscan
    in_liquid = False
    for x in range(0, sf.shape[2]):
        for y in range(0, sf.shape[0]):
            for z in range(0, sf.shape[1]):
                if ship.types[y, z, x] == 2 and ship.types[y, z, x] not in non_solid_blocks and not in_liquid:
                    z -= 1
                    for block in blast(y, z, x):
                        if 0 <= block[0] < sf.shape[0] and 0 <= block[1] < sf.shape[1] and 0 <= block[2] < sf.shape[2]:
                            if sf.blocks[y, z, x] not in [8, 9, 10, 11]:
                                strength[block[0], block[1], block[2]] = 2
                    break
                in_liquid = ship.types[y, z, x] in liquids
    # Z- hitscan
    in_liquid = False
    for x in range(0, sf.shape[2]):
        for y in range(0, sf.shape[0]):
            for z in range(sf.shape[1] - 1, -1, -1):
                if ship.types[y, z, x] == 2 and ship.types[y, z, x] not in non_solid_blocks and not in_liquid:
                    z += 1
                    for block in blast(y, z, x):
                        if 0 <= block[0] < sf.shape[0] and 0 <= block[1] < sf.shape[1] and 0 <= block[2] < sf.shape[2]:
                            strength[block[0], block[1], block[2]] = 2
                    break
                in_liquid = ship.types[y, z, x] in liquids
    # Render X axis armour
    data = np.zeros((sf.shape[0] - 2, sf.shape[1] - 2, 4), dtype=np.uint8)
    for z in range(1, sf.shape[1] - 1):
        for y in range(1, sf.shape[0] - 1):
            score = -1
            for x in range(0, sf.shape[2]):
                if ship.types[y, z, x] == 2 and score == -1:
                    score = 0
                if ship.types[y, z, x] == 2 and sf.blocks[y, z, x] in armour_blocks:
                    score += strength[y, z, x]
            if score != -1:
                data[sf.shape[0] - y - 2, sf.shape[1] - z - 2] = score_color(score / 2)
    im = Img.fromarray(data)
    im = im.resize((data.shape[1] * 16, data.shape[0] * 16), PIL.Image.NEAREST)
    im.save("temp/armour_x.png")
    # Render Z axis armour
    data = np.zeros((sf.shape[0] - 2, sf.shape[2] - 2, 4), dtype=np.uint8)
    for x in range(1, sf.shape[2] - 1):
        for y in range(1, sf.shape[0] - 1):
            score = -1
            for z in range(0, sf.shape[1]):
                if ship.types[y, z, x] == 2 and score == -1:
                    score = 0
                if ship.types[y, z, x] == 2 and sf.blocks[y, z, x] in armour_blocks:
                    score += strength[y, z, x]
            if score != -1:
                data[sf.shape[0] - y - 2, sf.shape[2] - x - 2] = score_color(score / 2)
    im = Img.fromarray(data)
    im = im.resize((data.shape[1] * 16, data.shape[0] * 16), PIL.Image.NEAREST)
    im.save("temp/armour_z.png")
    # Render Y axis armour
    data = np.zeros((sf.shape[1] - 2, sf.shape[2] - 2, 4), dtype=np.uint8)
    for x in range(1, sf.shape[2] - 1):
        for z in range(1, sf.shape[1] - 1):
            score = -1
            for y in range(0, sf.shape[0]):
                if ship.types[y, z, x] == 2 and score == -1:
                    score = 0
                if ship.types[y, z, x] == 2 and sf.blocks[y, z, x] in armour_blocks:
                    score += strength[y, z, x]
            if score != -1:
                data[z - 1, x - 1] = score_color(score / 2)
    im = Img.fromarray(data)
    im = im.resize((data.shape[1] * 16, data.shape[0] * 16), PIL.Image.NEAREST)
    im.save("temp/armour_y.png")

    # Generate weak armour schem
    sa = SchematicFile(shape=(sf.shape[0] - 2, sf.shape[1] - 2, sf.shape[2] - 2))
    for y in range(1, sf.shape[0] - 1):
        for z in range(1, sf.shape[1] - 1):
            for x in range(1, sf.shape[2] - 1):
                sa.blocks[y - 1, z - 1, x - 1] = sf.blocks[y, z, x]
                sa.data[y - 1, z - 1, x - 1] = sf.data[y, z, x]
                if sf.blocks[y, z, x] in armour_blocks and strength[y, z, x] < 3:
                    sa.blocks[y - 1, z - 1, x - 1] = 95
                    sa.data[y - 1, z - 1, x - 1] = 14
    sa.save('temp/-armourtest.schematic')