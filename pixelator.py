from PIL import Image, ImageFilter, ImageStat, ImageDraw
import numpy as np


def showColorSample(color):
    Image.new(mode="RGB", size=(100, 100), color=color).show()


def createStripes():
    image = Image.new(mode="RGB", size=(180, 350), color=(0, 0, 0, 255))
    for w in range(image.width):
        if w % 20 >= 5:
            for h in range(image.height):
                image.putpixel((w, h), (255-h, 0+w, 255-w))
    image.show()


def randomColorGen():
    x = np.random.randint(low=0, high=256, size=(100, 100, 3), dtype=np.uint8)
    Image.fromarray(x).show()

# methods of finding the edges of the new blocks
# Used to visualize how the original image will be divided


def drawBlockEdgeWithArr(image, blockSide):
    # find edges by converting the image to an array of pixels
    # and setting the edge pixels to black
    arr = np.asarray(image)
    newarr = []
    for h in range(image.height):
        heightarr = []
        for w in range(image.width):
            if (h % blockSide == 0 or w % blockSide == 0):
                heightarr.append([0, 0, 0])
            else:
                heightarr.append(arr[h][w])
        newarr.append(heightarr)
    Image.fromarray(np.array(newarr, dtype=np.uint8)).show()


def drawBlockEdge(image, blockSide):
    # After doing it the array way, I realized I can pick the pixels
    # directly from the image and thought this was cleaner
    blackPixel = (0, 0, 0, 255)
    copy = image.copy()
    for h in range(image.height):
        for w in range(image.width):
            if (h % blockSide == 0 or w % blockSide == 0):
                copy.putpixel((w, h), blackPixel)
            copy.putpixel((w, image.height-1), blackPixel)  # bottom edge of image
        copy.putpixel((image.width-1, h), blackPixel)  # right edge of image

    copy.show()


# methods of finding the corners of the blocks and getting back a list

def getBlockCornersSequentially(image, blockSide):
    # returns list of tuples (top left coords, bottom right coords) of the blocks made
    h = 0
    w = 0
    corners = []  # list of 2tuple-tuples ((topleft), (bottomright)) -> ((w1, h1), (w2, h2))
    while h < image.height:
        w = 0
        while w < image.width:
            w2 = w + blockSide if w + blockSide <= image.width-1 else image.width-1
            h2 = h + blockSide if h + blockSide <= image.height-1 else image.height-1
            corners.append(((w, h), (w2, h2)))
            w += blockSide
        h += blockSide
    return corners


def getBlockCornersDiagonals(image, blockSide):
    # returns list of lists of tuples (w,h)

    diagonals = []  # contains the list of diagonals
    # Diagonals that start on the top right
    w = image.width - 1  # do this one backwards to minimize visible artifacts in the output image
    while w > 0:
        h = 0
        diagonal = [(w, h)]

        nextPixelW = w + blockSide
        nextPixelH = h + blockSide
        while nextPixelW < image.width and nextPixelH < image.height:
            diagonal.append((nextPixelW, nextPixelH))
            nextPixelW += blockSide
            nextPixelH += blockSide

        # wont include edges so add manually
        nextPixelW = nextPixelW if nextPixelW <= image.width-1 else image.width-1
        nextPixelH = nextPixelH if nextPixelH <= image.height-1 else image.height-1
        diagonal.append((nextPixelW, nextPixelH))

        diagonals.append(diagonal)
        w -= blockSide

    # Diagonals that start on the left
    h = 0
    while h < image.height:
        w = 0
        diagonal = [(w, h)]

        nextPixelW = w + blockSide
        nextPixelH = h + blockSide
        while nextPixelW < image.width and nextPixelH < image.height:
            diagonal.append((nextPixelW, nextPixelH))
            nextPixelW += blockSide
            nextPixelH += blockSide

        # wont include edges so add manually
        nextPixelW = nextPixelW if nextPixelW <= image.width-1 else image.width-1
        nextPixelH = nextPixelH if nextPixelH <= image.height-1 else image.height-1
        diagonal.append((nextPixelW, nextPixelH))

        diagonals.append(diagonal)
        h += blockSide

    return diagonals


# Visualize corners


def drawCornersSequentially(image, blockSide):
    # using getBlockCornersSequentially
    corners = getBlockCornersSequentially(image, blockSide)
    for corner in corners:
        topleft, bottomright = corner
        w1, h1 = topleft
        w2, h2 = bottomright
        image.putpixel((w1, h1), (0, 255, 0, 255))
        image.putpixel((w2, h2), (0, 255, 0, 255))
    image.show()


def drawCornersDiagonals(image, blockSide):
    # using diagonals
    diagonals = getBlockCornersDiagonals(image, blockSide)
    for diagonal in diagonals:
        for i, coord in enumerate(diagonal):
            if i+1 > len(diagonal)-1:
                break
            topleft = coord
            bottomright = diagonal[i+1]
            w1, h1 = topleft
            w2, h2 = bottomright
            image.putpixel((w1, h1), (0, 255, 0, 255))
            image.putpixel((w2, h2), (0, 255, 0, 255))
    image.show()


def getBlockColor(image, blockColorMethod="mean"):
    # default method is "mean". others: "median", "thumbnail"

    pixelValue = None
    if blockColorMethod == "mean":
        avg = ImageStat.Stat(image).mean
        pixelValue = tuple(map(lambda x: round(x), avg))
    elif blockColorMethod == "median":
        median = ImageStat.Stat(image).median
        pixelValue = tuple(map(lambda x: round(x), median))
    elif blockColorMethod == "thumbnail":  # this is basically the same as "mean"
        image.thumbnail((1, 1))
        pixelValue = image.getpixel((0, 0))
    else:
        raise ValueError("unknown block color method")

    return pixelValue


# Create pixelized image and helper methods

def pixelize(image, blockSide, blockColorMethod="mean", cornersMode="sequential"):
    # corners mode: "sequential" (getBlockCornersSequentially); "diagonal" (getBlockCornersDiagonals)

    if cornersMode == "sequential":
        return pixelizeSequentially(image, blockSide, blockColorMethod)
    elif cornersMode == "diagonal":
        return pixelizeDiagonal(image, blockSide, blockColorMethod)
    else:
        raise ValueError("unknown cornersMode " + cornersMode)


def pixelizeSequentially(image, blockSide, blockColorMethod="mean"):
    pixelized = Image.new(image.mode, (image.width, image.height))
    drawImage = ImageDraw.Draw(pixelized)

    corners = getBlockCornersSequentially(image, blockSide)
    for corner in corners:
        topleft, bottomright = corner
        w1, h1 = topleft
        w2, h2 = bottomright

        if w1 - w2 == 0 or h1 - h2 == 0:
            blockColor = image.getpixel((w1, h1))
        else:
            block = image.crop((w1, h1, w2, h2))
            blockColor = getBlockColor(block, blockColorMethod=blockColorMethod)

        drawImage.rectangle((w1, h1, w2, h2), blockColor)

    return pixelized


def pixelizeDiagonal(image, blockSide, blockColorMethod="mean"):
    pixelized = Image.new(image.mode, (image.width, image.height))
    drawImage = ImageDraw.Draw(pixelized)

    diagonals = getBlockCornersDiagonals(image, blockSide)
    for diagonal in diagonals:
        for i, coord in enumerate(diagonal):
            if i+1 > len(diagonal)-1:
                break
            topleft = coord
            bottomright = diagonal[i+1]
            w1, h1 = topleft
            w2, h2 = bottomright

            if w1 - w2 == 0 or h1 - h2 == 0:
                blockColor = image.getpixel((w1, h1))
            else:
                block = image.crop((w1, h1, w2, h2))
                blockColor = getBlockColor(block, blockColorMethod=blockColorMethod)

            drawImage.rectangle((w1, h1, w2, h2), blockColor)

    return pixelized


def main():
    # Change these values
    imageName = "sampleCornersImage.png"  # path to image
    blockSideSize = 8  # 8-16 is a good blockSideSize; 1 gives back original image
    blockColorMethod = "mean"  # "mean", "median", or "thumbnail"
    cornersMode = "sequential"  # "sequential" or "diagonal"

    image = Image.open(imageName)
    # See where edges of the blocks
    drawBlockEdge(image, blockSideSize)
    # create the pixelized version
    outputImage = pixelize(image, blockSideSize, blockColorMethod=blockColorMethod, cornersMode=cornersMode)
    outputImage.show()
    # To save the output image
    outputImage.save("output.png")


main()
