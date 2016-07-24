from PIL import Image
from os import system, remove


def extractor(name):
    im = Image.open(name)

    im2 = Image.new("P", im.size, 255)

    currentNumber = 0
#                  top bot left right
    numbers = {"1": [500, 0, 0, 0],
               "2": [500, 0, 0, 0],
               "3": [500, 0, 0, 0],
               "4": [500, 0, 0, 0],
               "5": [500, 0, 0, 0],
               "6": [500, 0, 0, 0]}

    spaces = [0] * 6
    gotBlackPixel = False
    lastRowEmpty = True
    emptyXSpace = []

    # clean image and get measurements about numbers
    for x in range(im.size[0]):
        for y in range(im.size[1]):
            pix = im.getpixel((x, y))
            if 2 < x < im.size[0] - 2 and 2 < y < im.size[1] - 2:
                if pix == 16:
                    im2.putpixel((x, y), 0)
                    if lastRowEmpty and currentNumber != 6:
                        currentNumber += 1
                    if not gotBlackPixel and lastRowEmpty:  # get left most pixel of number
                        numbers[str(currentNumber)][2] = x
                    if y < numbers[str(currentNumber)][0]:  # get top most pixel of number
                        numbers[str(currentNumber)][0] = y
                    if y > numbers[str(currentNumber)][1]:  # new get lowest pixel of number
                        numbers[str(currentNumber)][1] = y
                    gotBlackPixel = True
                    lastRowEmpty = False
                else:
                    if not lastRowEmpty and not gotBlackPixel:  # get the far right x pixel of number
                        numbers[str(currentNumber)][3] = x - 1
        if not gotBlackPixel:
            lastRowEmpty = True
            spaces[currentNumber - 1] += 1
            emptyXSpace.append(x)  # recording empty x coordinates
        gotBlackPixel = False

    im2.save("alignNumbers.gif")

    im3 = Image.new("P", im.size, 255)

    currentNumber = 0
    gotBlackPixel = False
    lastRowEmpty = True
    dy = 0  # how many pixels to move up
    dx = 0  # how many pixels to move left
    line = 4  # line where all numbers to align up on
    row = 10  # the row from where to start drawing numbers
    newNumber = True

    for x in range(im2.size[0]):
        for y in range(im2.size[1]):
            pix = im2.getpixel((x, y))
            if pix == 0:
                if lastRowEmpty and currentNumber != 6:
                    currentNumber += 1
                    dy = numbers[str(currentNumber)][0] - line
                if newNumber:
                    newNumber = False
                    if currentNumber == 1:
                        dx = (im2.size[0] - row) - (im2.size[0] - x)
                    else:
                        dx += 3

                im3.putpixel((dx, y - dy), 0)
                gotBlackPixel = True
                lastRowEmpty = False

        if x in emptyXSpace:
            newNumber = True
        if gotBlackPixel:
            dx += 1
        if not gotBlackPixel:
            lastRowEmpty = True
        gotBlackPixel = False

    im3.save("output.gif")

    system("tesseract output.gif result -psm 8")

    # read in numbers from output file
    result = open("result.txt", 'r').readline().strip()

    if len(result) == 6 and result.isdigit():
        # do some cleaning up
        try:
            remove("alignNumbers.gif")
            remove("output.gif")
            remove("result.txt")
        except IOError, e:
            print e.message
        return result
    else:
        return -1
