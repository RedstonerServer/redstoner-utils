import org.bukkit.generator.ChunkGenerator as ChunkGen
import org.bukkit.Material as Material

def get_generator():
    return Generator()

class Generator(ChunkGen):

    def __init__(self):
        pass

    def generateBlockSections(self, world, random, x, z, biomes):
        result = ''.join(None for x in range(world.getMaxHeight() / 16))
        for x in range(16):
            for z in range(16):
                self.set_block(result, x, 0, z, Material.BEDROCK.getId())
        return result

    def set_block(self, result, x, y, z, block_id):
        if result[y >> 4] == None:
            result[y >> 4] = ''.join(chr(0x00) for x in range(4096))
        result[y >> 4][((y & 0xF) << 8) | (z << 4) | x] = block_id
