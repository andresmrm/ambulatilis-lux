## Check online

[Here](https://andresmrm.github.io/ambulatilis-lux/example/game)

## To render the map

From inside the `blender` folder run:

(change `/path/to/a/store/folder` so it points to an empty folder where LuxRender FLMs files will be stored, allowing to resume the render later)

(the `-t 6` is the number of threads, don't use more than the number of cores in your box)

```
blender example.blend -b -P ../../src/amblux.py -- /path/to/a/store/folder ../game/assets/map -T 60 -w 60 -t 6 -j -f
```

Observe the `-f` in the end. This should delete the files inside the store folder, export the map and start rendering from zero.
If you want to use the already exported files, resuming FLMs, don't add the `-f` in the end.

Use this for a help with the parameters:

```
blender example.blend -b -P ../../src/amblux.py -- --help
```


## To run the example locally

From inside the `game` folder run:

```
npm install
npm run dev
```

Then open `localhost:5001` in a browser.
