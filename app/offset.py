import numpy as np
# Provided coordinates
ground = [
    (33.60387497714889, -79.03585510826689),
    (33.60388575665613, -79.03582104187062),
    (33.60389388588512, -79.03582375649621),
    (33.60392338512367, -79.03569553047166),
    (33.60386354920544, -79.03564470547535),
    (33.60378260978639, -79.03563977719969),
    (33.60374856752868, -79.03578743284498),
    (33.6037504603331, -79.03580478399826),
    (33.60387497714889, -79.03585510826689)
]

calculated = [
    (29.739503313069974, -95.5456817173678),
    (29.739472244821783, -95.54566929006852),
    (29.739474907814486, -95.54566041342618),
    (29.73935773613561, -95.54562579452106),
    (29.73930980226699, -95.54569059401014),
    (29.739303588617357, -95.5457793604335),
    (29.739438513580893, -95.54581930532404),
    (29.739454491537103, -95.54581752999556),
    (29.739503313069974, -95.5456817173678)
]

# Check if both lists have the same length
if len(ground) != len(calculated):
    print("Error: Lists have different lengths")
else:
    # Convert coordinates to numpy arrays for easy calculation
    ground_array = np.array(ground)
    calculated_array = np.array(calculated)

    # Calculate differences between corresponding pairs
    differences = coordinates_array2 - coordinates_array1

    # Print the differences
    print("Differences between corresponding pairs:")
    print(differences)
