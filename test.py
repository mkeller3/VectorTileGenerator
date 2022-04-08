from tileGenerator import generator

tileGeneration = generator.GenerateTiles(1, 5, [-118, 34, -84, 50])

# Demo of generating tiles
print(tileGeneration.generate())