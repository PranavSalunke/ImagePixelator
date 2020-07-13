# Pixelator


## Motivation

This project started as a way to play around with the PIL library. I experimented with how PIL works and what I can do. I kept all the experimenting here instead of removing it


Other tools like this exist already but I ended up with an Image Pixelator. Pixelate here means make a larger "pixel" (which I called a "block") with the average of the pixels that fall in that block in the original image. The end result is like a blur but each new block has a hard edge. See the examples directory


## Implementation details

The original image is broken up into blocks which act as the bigger "pixel". This block is a square with the size defined by `blockSideSize`. It is not required that the image be evenly divided. However, if it does not, the blocks on the bottom and right side of the image will be smaller. 

### Getting block boundaries

The boundaries of these blocks must be found in order to do the pixelation. I did this two ways in `drawBlockEdgeWithArr()` and `drawBlockEdge()`. Both these draw the edges and show it. This can be used to visualize how the original image will be divided. I did it with an array and then found that I can get that information directly. 

### Getting block corners 


I then needed the corners to create the blocks. I also did this two ways, both with their pros and cons. 

`getBlockCornersSequentially` gives back an easy to understand list of coordinates breaking the image into blocks. It goes horizontally and then down.

One problem with this is that the coordinates for a corner will be in the list multiple times. Once as the top left coordinate and then again as the bottom right. The good thing is that when this method is used, the pixelated image is built sequentially and no artifacts are visible in the final image. 


`getBlockCornersDiagonals` gives back an lists of lists. Each list corresponds to one diagonal at the blockSide multiples of the left side and top side of the image. See "sampleCornersImage.png" where the diagonals are red and corners are green. Each diagonal list contains the coords of the pixels on that diagonal. The pixel that comes next in the list is the "bottom right" pixel of the one that came before. The number of blocks a diagonal represents is one less than the number of coordinates in it.


One problem with this is that since the blocks are created in a diagonal pattern, some block edges will overlap. Which sometimes creates visible artifacts. The order in which the diagonals are calculated minimizes this. The good thing is that it only tracks one corner at a time. This is more "clever" but it doesn't mean it was necessary. The other method works well, is easier to understand, and has less visible artifacts. 


These corners can be visualized with the methods `drawCornersSequentially` and `drawCornersDiagonals`. The corners are hard to see though because they are one pixel

See `stripes.png` in the examples section which shows the artifacts. 

### Getting the color for the block

Once I had the blocks, I needed to know what color it had to be. I did this in three ways. Each is a mode that can be selected. 

Mean: the average color of the pixels that fall in that block

Median: the median color of the pixels that fall in that block

Thumbnail: Converted the image to a thumbnail of size 1x1 pixel and took that color. This is almost the same as mean. 

## Examples

I took some pictures off the internet. The original, edges, and pixelated images are included. The following show which options were used.

### stripes.png

Made using the method `createStripes`


This example shows how different mean and median can be as well as the visible artifacts of using the diagonal method. Also note how that the edges shows the image does not divide evenly. There are smaller than 8x8 pixels on the right hand side


blockSideSize = 8 

blockColorMethod = "mean"  and "median" 

cornersMode = "diagonal"  and "sequential"

mean + diagonal -> stripes_out_mean_diagonal.png

mean + sequential -> stripes_out_mean_sequential.png

median + sequential -> stripes_out_median_sequential.png


### landscape1.jpg

blockSideSize = 16

blockColorMethod = "mean"

cornersMode="sequential"


### thispersondoesnotexist.png

Image taken from https://thispersondoesnotexist.com/

blockSideSize = 32

blockColorMethod = "median"

cornersMode = "diagonal"

## Running this program


Change the variables in `main()` to fit your needs.  Use python3 to run this on the command line.


`python3 pixelator.py` or `py -3 pixelator.py` depending on your OS.