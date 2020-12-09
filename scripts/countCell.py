import json
import pyvips
import numpy as np

roiPath = elements
filePath = in_path
cellSize = 20
output = {}

print in_path
print elements
image = pyvips.Image.new_from_file(filePath, access='sequential')

for element in elements:

    type = element['type']
    if type == 'rectangle':
        pixelX, pixelY, pixelZ = element['center']
        height = round(element['height'])
        width = round(element['width'])
        left = round(pixelX) - width//2
        top = round(pixelY)- height//2
        tile = image.crop(left, top, width, height)
        tileInArray = np.ndarray(buffer=tile.write_to_memory(),dtype=np.uint8,shape=[tile.height, tile.width])
        NumOfCell = round(np.count_nonzero(tileInArray)/cellSize)
        element['Num_of_Cell'] = NumOfCell
        output[element['id']] = element
#         # tileNum = libtiff_ctypes.libtiff.TIFFComputeTile(img, round(pixelX), round(pixelY), 0, 0).value

elementsWithCell = json.dumps(output)
