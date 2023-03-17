import PIL
import numpy as np
from PIL import Image as Img, ImageOps
from nbtschematic import SchematicFile

from schempic_color import color


def gen_pics(path, scale, shade, light):
    sf = SchematicFile.load(path)
    fn = ''.join(path.split('/')[-1].split('.')[:-1])
    return gen_pic_schem(sf, fn, scale, shade, light)


def gen_pic_schem(schem, name, scale=16, shade=30, light=10):
    sf = schem
    fn = name
    if sf.shape[0] * sf.shape[1] * sf.shape[2] > 8000000:
        return -1
    data = np.zeros((sf.shape[1], sf.shape[2], 4), dtype=np.uint8)
    for y in range(0, sf.shape[0]):
        for z in range(0, sf.shape[1]):
            for x in range(0, sf.shape[2]):
                if sf.blocks[y, z, x] != 0:
                    if color(sf.blocks[y, z, x], sf.data[y, z, x]) != [0, 0, 0, 255]:
                        c = color(sf.blocks[y, z, x], sf.data[y, z, x])
                        if shade != 0:
                            c = np.multiply(c, (y + 1 + 100 / shade) / (sf.shape[0] + 100 / shade))
                        c = np.multiply(c, 1 + light / 100)
                        c[3] = 255
                        data[sf.shape[1] - z - 1, x] = c
    im = Img.fromarray(data)
    im = im.resize((data.shape[1] * scale, data.shape[0] * scale), PIL.Image.NEAREST)
    im = ImageOps.flip(im)
    im.save("pics/" + fn + "+y.png")

    data = np.zeros((sf.shape[1], sf.shape[2], 4), dtype=np.uint8)
    for y in range(sf.shape[0]-1, -1, -1):
        for z in range(0, sf.shape[1]):
            for x in range(0, sf.shape[2]):
                if sf.blocks[y, z, x] != 0:
                    if color(sf.blocks[y, z, x], sf.data[y, z, x]) != [0, 0, 0, 255]:
                        c = color(sf.blocks[y, z, x], sf.data[y, z, x])
                        if shade != 0:
                            c = np.multiply(c, (sf.shape[0] - y + 100 / shade) / (sf.shape[0] + 100 / shade))
                        c = np.multiply(c, 1 + light / 100)
                        c[3] = 255
                        data[sf.shape[1] - z - 1, x] = c
    im = Img.fromarray(data)
    im = im.resize((data.shape[1] * scale, data.shape[0] * scale), PIL.Image.NEAREST)
    im.save("pics/" + fn + "-y.png")

    data = np.zeros((sf.shape[0], sf.shape[2], 4), dtype=np.uint8)
    for z in range(0, sf.shape[1]):
        for y in range(0, sf.shape[0]):
            for x in range(0, sf.shape[2]):
                if sf.blocks[y, z, x] != 0 and sf.blocks[y, z, x] != -85:
                    if color(sf.blocks[y, z, x], sf.data[y, z, x]) != [0, 0, 0, 255]:
                        c = color(sf.blocks[y, z, x], sf.data[y, z, x])
                        if shade != 0:
                            c = np.multiply(c, (z + 1 + 100 / shade) / (sf.shape[1] + 100 / shade))
                        c = np.multiply(c, 1 + light / 100)
                        c[3] = 255
                        data[sf.shape[0] - y - 1, x] = c
    im = Img.fromarray(data)
    im = im.resize((data.shape[1] * scale, data.shape[0] * scale), PIL.Image.NEAREST)
    im = ImageOps.mirror(im)
    im.save("pics/" + fn + "+z.png")

    data = np.zeros((sf.shape[0], sf.shape[2], 4), dtype=np.uint8)
    for z in range(sf.shape[1] - 1, -1, -1):
        for y in range(0, sf.shape[0]):
            for x in range(0, sf.shape[2]):
                if sf.blocks[y, z, x] != 0 and sf.blocks[y, z, x] != -85:
                    if color(sf.blocks[y, z, x], sf.data[y, z, x]) != [0, 0, 0, 255]:
                        c = color(sf.blocks[y, z, x], sf.data[y, z, x])
                        if shade != 0:
                            c = np.multiply(c, (sf.shape[1] - z + 100 / shade) / (sf.shape[1] + 100 / shade))
                        c = np.multiply(c, 1 + light / 100)
                        c[3] = 255
                        data[sf.shape[0] - y - 1, x] = c
    im = Img.fromarray(data)
    im = im.resize((data.shape[1] * scale, data.shape[0] * scale), PIL.Image.NEAREST)
    im.save("pics/" + fn + "-z.png")

    data = np.zeros((sf.shape[0], sf.shape[1], 4), dtype=np.uint8)
    for x in range(0, sf.shape[2]):
        for y in range(0, sf.shape[0]):
            for z in range(0, sf.shape[1]):
                if sf.blocks[y, z, x] != 0 and sf.blocks[y, z, x] != -85:
                    if color(sf.blocks[y, z, x], sf.data[y, z, x]) != [0, 0, 0, 255]:
                        c = color(sf.blocks[y, z, x], sf.data[y, z, x])
                        if shade != 0:
                            c = np.multiply(c, (x + 1 + 100 / shade) / (sf.shape[2] + 100 / shade))
                        c = np.multiply(c, 1 + light / 100)
                        c[3] = 255
                        data[sf.shape[0] - y - 1, z] = c
    im = Img.fromarray(data)
    im = im.resize((data.shape[1] * scale, data.shape[0] * scale), PIL.Image.NEAREST)
    im = ImageOps.mirror(im)
    im.save("pics/" + fn + "+x.png")

    data = np.zeros((sf.shape[0], sf.shape[1], 4), dtype=np.uint8)
    for x in range(sf.shape[2] - 1, -1, -1):
        for y in range(0, sf.shape[0]):
            for z in range(0, sf.shape[1]):
                if sf.blocks[y, z, x] != 0 and sf.blocks[y, z, x] != -85:
                    if color(sf.blocks[y, z, x], sf.data[y, z, x]) != [0, 0, 0, 255]:
                        c = color(sf.blocks[y, z, x], sf.data[y, z, x])
                        if shade != 0:
                            c = np.multiply(c, (sf.shape[2] - x + 100 / shade) / (sf.shape[2] + 100 / shade))
                        c = np.multiply(c, 1 + light / 100)
                        c[3] = 255
                        data[sf.shape[0] - y - 1, z] = c
    im = Img.fromarray(data)
    im = im.resize((data.shape[1] * scale, data.shape[0] * scale), PIL.Image.NEAREST)
    im.save("pics/" + fn + "-x.png")

    data = np.zeros((sf.shape[1] + sf.shape[0] + 1, sf.shape[2], 4), dtype=np.uint8)
    for y in range(0, sf.shape[0]):
        for z in range(sf.shape[1] - 1, -1, -1):
            for x in range(0, sf.shape[2]):
                if sf.blocks[y, z, x] != 0:
                    ofs = int(sf.blocks[y, z, x] == -85)
                    if color(sf.blocks[y, z, x], sf.data[y, z, x]) != [0, 0, 0, 255]:
                        c = color(sf.blocks[y, z, x], sf.data[y, z, x])
                        c = np.multiply(c, 1 + light / 200)
                        top = c
                        top[3] = 255
                        side = np.multiply(c, 1 - shade / 100)
                        side[3] = 255
                        data[sf.shape[1] - z + (sf.shape[0] - y - 1), x] = side
                        data[sf.shape[1] - z + (sf.shape[0] - y - 2) + ofs, x] = top
    im = Img.fromarray(data)
    im = im.resize((data.shape[1] * scale, data.shape[0] * scale), PIL.Image.NEAREST)
    im.save("pics/" + fn + "+dz.png")

    data = np.zeros((sf.shape[1] + sf.shape[0] + 1, sf.shape[2], 4), dtype=np.uint8)
    for y in range(0, sf.shape[0]):
        for z in range(0, sf.shape[1]):
            for x in range(0, sf.shape[2]):
                if sf.blocks[y, z, x] != 0:
                    ofs = int(sf.blocks[y, z, x] == -85)
                    if color(sf.blocks[y, z, x], sf.data[y, z, x]) != [0, 0, 0, 255]:
                        c = color(sf.blocks[y, z, x], sf.data[y, z, x])
                        c = np.multiply(c, 1 + light / 200)
                        top = c
                        top[3] = 255
                        side = np.multiply(c, 1 - shade / 100)
                        side[3] = 255
                        data[z + 1 + (sf.shape[0] - y - 1), x] = side
                        data[z + 1 + (sf.shape[0] - y - 2) + ofs, x] = top
    im = Img.fromarray(data)
    im = im.resize((data.shape[1] * scale, data.shape[0] * scale), PIL.Image.NEAREST)
    im.save("pics/" + fn + "-dz.png")

    data = np.zeros((sf.shape[2] + sf.shape[0] + 1, sf.shape[1], 4), dtype=np.uint8)
    for y in range(0, sf.shape[0]):
        for x in range(sf.shape[2] - 1, -1, -1):
            for z in range(0, sf.shape[1]):
                if sf.blocks[y, z, x] != 0:
                    ofs = int(sf.blocks[y, z, x] == -85)
                    if color(sf.blocks[y, z, x], sf.data[y, z, x]) != [0, 0, 0, 255]:
                        c = color(sf.blocks[y, z, x], sf.data[y, z, x])
                        c = np.multiply(c, 1 + light / 200)
                        top = c
                        top[3] = 255
                        side = np.multiply(c, 1 - shade / 100)
                        side[3] = 255
                        data[sf.shape[2] - x + (sf.shape[0] - y - 1), z] = side
                        data[sf.shape[2] - x + (sf.shape[0] - y - 2) + ofs, z] = top
    im = Img.fromarray(data)
    im = im.resize((data.shape[1] * scale, data.shape[0] * scale), PIL.Image.NEAREST)
    im.save("pics/" + fn + "+dx.png")

    data = np.zeros((sf.shape[2] + sf.shape[0] + 1, sf.shape[1], 4), dtype=np.uint8)
    for y in range(0, sf.shape[0]):
        for x in range(0, sf.shape[2]):
            for z in range(0, sf.shape[1]):
                if sf.blocks[y, z, x] != 0:
                    ofs = int(sf.blocks[y, z, x] == -85)
                    if color(sf.blocks[y, z, x], sf.data[y, z, x]) != [0, 0, 0, 255]:
                        c = color(sf.blocks[y, z, x], sf.data[y, z, x])
                        c = np.multiply(c, 1 + light / 200)
                        top = c
                        top[3] = 255
                        side = np.multiply(c, 1 - shade / 100)
                        side[3] = 255
                        data[x + 1 + (sf.shape[0] - y - 1), z] = side
                        data[x + 1 + (sf.shape[0] - y - 2) + ofs, z] = top
    im = Img.fromarray(data)
    im = im.resize((data.shape[1] * scale, data.shape[0] * scale), PIL.Image.NEAREST)
    im.save("pics/" + fn + "-dx.png")
    return 0
