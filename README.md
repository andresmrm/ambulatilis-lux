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


## Examples

[Here](https://github.com/andresmrm/ambulatilis-lux/tree/master/example) there is a simple example, good to use has a base for new maps. 

And [here](https://github.com/andresmrm/labyrimental) something more complex that maybe can be called a game.


## Install

To model the map and render it you'll need to install [Blender](https://www.blender.org/download), [LuxRender](http://www.luxrender.net/en_GB/standalone) and [LuxBlend](http://www.luxrender.net/en_GB/blender_2_5) (LuxRender exporter for Blender).

For the browser part you will need [Node.js](https://nodejs.org), which should come with [npm](https://docs.npmjs.com/getting-started/installing-node).
Check the [example](https://github.com/andresmrm/ambulatilis-lux/tree/master/example) to see more info.
The Phaser app is only an example of what can be done with the rendered images.

To install Ambulatilis Lux clone or download this repository. It should require Python +3.1.


## Usage

As stated before, this is a proof of concept, so some stuff are not well documented or need to be set in the source code...

### Modeling

Your modeled map (.blend file) should have objects to mark the places where the camera/player can stay.
The ID of such objects should start with `position` (e.g.: `position`, `position.001`, `position.049`).
This name can be configured in the source code.
Using `Alt+D` or `SHIFT+D` in Blender you should be able to copy objects in a manner that the beginning of the ID won't change.

You'll also need objects to mark the links between this positions: from which positions the player can go to which positions.
The ID of such objects should start with `path`.
It can also be configured in source code.

The best way to understand how use these "mark objects" is to check the [example](https://github.com/andresmrm/ambulatilis-lux/tree/master/example/blender).
And use it as a base for new maps, or at least import a `position` and a `path` in your existing scene.

The position of the `position`s is relevant, and they cannot be placed anywhere.
Imagine your map as a tilemap, tiles with a `position` are walk-able tiles.
In the current source code config the tiles are 5x5 units (`SCALE = 5`).
So the `position`s should be spaced 5 units and centered in the center of a tile.
For example, the a `position` x=2.5 y=2.5 (in Blender coords) is in the center of the tile x=[0..5] y=[0..5]. Since the `SCALE = 5` this is the tile 0,0 in game coords, and will become the images 0\_0\_0\_e, 0\_0\_0\_n, 0\_0\_0\_w, 0\_0\_0\_s (east, north, west, south).

The third 0 is the z, it can vary in one or more steps of 0.5 Blender units.
The z of the linking `path` should be in the middle of the z variation.
Erm... Again, check the [example](https://github.com/andresmrm/ambulatilis-lux/tree/master/example/blender).


### Rendering

Go to the folder of the .blend file and run a command like this:

```
blender <your-blend>.blend -b -P <amblux-folder>/amblux.py -- /path/to/a/store/folder /path/to/final/folder -T 60 -w 60 -t 6 -j
```

Adjust the paths and parameters. See the help for more info:

```
blender example.blend -b -P <amblux-folder>/amblux.py -- --help
```

This should save the resulting PNGs images (4 images for each `position`) and FLMs files in the store folder. And also save the converted JPGs images and a `map.js` file in the final folder. We are using JPGs for the final version to reduce size.
The `map.js` has info about the links between the `position`s.

To resume the rendering, you only need to call the script again. If it finds previous exported files it should resume, if not it should export all again and start from zero.

If you modified the .blend file and want to render it, you will need to call the script with a `--force-export` parameter or delete the files stored in the store folder manually.

#### Zone files

It's possible to divide your map into zones, so it would be easier to render only part of a .blend file.
It's useful when some parts need more time to render than others.
So you can render the "hard" zone for 1h and the "easy" zone for 15min.

A zone is little more than a group of Blender layers.
For an example of a zone file, check the blend package in [Labyrimental](https://github.com/andresmrm/labyrimental).


### Viewing

Once the rendering is complete, the JPGs and `map.js` should be in the final folder (if the path was set correctly).
If using the app from the [example](https://github.com/andresmrm/ambulatilis-lux/tree/master/example/blender), it should be a matter of restarting `npm run dev` and reloading the browser to check it.


## Tips

### Avoid light to change from image to image

Select the camera object and in object data tab set:

- LuxRender Camera > Exposure: Absolute
- LuxRender Film > Tonemapper: Linear (manual)

Then try some rendering to adjust "LuxRender Camera > Close" to a good value for your ambient.

### Reduce the effect of discrete rotation

Select the camera object and in object data tab, in the Lens section, change the Focal Length from millimeters to Field of View, and set it to something broader, like 90º.


## Name

The name should mean something like [walking/moving](http://www.latin-dictionary.net/definition/2956/ambulatilis-ambulatilis-ambulatile) light in Latin.
It's somehow a reference to LuxRender.
