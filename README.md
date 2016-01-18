**Warning: Proof of concept**

# Ambulatilis Lux

This a kind of [2.5D](https://en.wikipedia.org/wiki/2.5D) game engine for browsers using [Blender](https://www.blender.org) to model the map, [LuxRender](http://www.luxrender.net) to render the images and [Phaser](http://phaser.io) to display them.

## Why?

LuxRender is an open source unbiased render that can do [amazing stuff](http://www.luxrender.net/forum/gallery2.php).
But it can also take days to render a single image, making difficult to use it for real time rendering.

Pre-rendering the images and displaying them in the correct moment it's possible to create the illusion of a 3D ambient, with the render quality of LuxRender.
And running this ambient on a browser makes easier for anyone the see it, without the need to install anything.
That's were Phaser helps.

## Work flow

1. Use Blender to model your ambient/map/scenario.
2. Place some objects with special IDs (like IDs starting with `position` and `path`) to mark walk-able positions and links between this positions.
3. Call Ambulatilis Lux script: it will render the images for each position, in four directions and export a JSON file with the links between this positions.
4. View your ambient in a browser. The JSON file will be used to know from which positions the player can walk to which positions.

## Limitations

As stated before, this *engine* is based on pre-rendering all the images that the player will be able to see in game.
So, unless you have unlimited processing power/time to render infinite images and unlimited space to store them, you'll have to use a limited number of images.

Currently the engine is configured to render 4 images (north, east, west, south) for each walk-able position. This means that for a small map, where the player can walk to 5 different positions, 20 images (4*5) will need to be rendered.

We can enumerate a few limitations:

- Render time: in the example above, if each image takes 1h to render, the whole map will take 20h to render. A big ambient, with hundreds of positions, can take weeks...
- Discrete ambient: Currently the engine renders only 4 angles/directions for each position. This means that if the player wants to rotate only 45º, instead of 90º, it won't be possible. The engine can be modified to render more directions for each position, but this means more images to render/store. The player can only walk from positions to position, so it's more like a teleport. Closer positions make waking transition more continuous, but also require more images...
- Bandwidth: Currently images are downloaded on-demand. This reduces the total download size if a player doesn't see all directions from all positions, but adds a delay before any non-cached image is displayed. Anyway, downloading lots of images can cost lots of bandwidth.
- Immutable images: Generally in games the ambient changes and you can see moving objects. Given the pre-rendered nature of this engine, such things are not easy to do here.

## Example



## Install

To model the map and render it you'll need to install [Blender](https://www.blender.org/download), [LuxRender](http://www.luxrender.net/en_GB/standalone) and [LuxBlend](http://www.luxrender.net/en_GB/blender_2_5) (LuxRender exporter for Blender).


## Tips

### Avoid light to change from image to image

Select the camera object and in object data tab set:

- LuxRender Camera > Exposure: Absolute
- LuxRender Film > Tonemapper: Linear (manual)

Then try some rendering to adjust "LuxRender Camera > Close" to a good value for your ambient.


## Name

The name should mean something like [walking/moving](http://www.latin-dictionary.net/definition/2956/ambulatilis-ambulatilis-ambulatile) light in Latin.
It's somehow a reference to LuxRender.
