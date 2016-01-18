import {posDirToText} from './utils.js'
import {move} from './movement.js'
import {initKeyboardInput, initMouseInput} from './input.js'
import {state} from './store.js'
import {resize} from './vision.js'


export function mainLoad() {
    state.game.load.onLoadComplete.add(function () {
            state.game.load.onLoadComplete.removeAll()
            mainInit()
    }, this)

    var firstImg = posDirToText(state.position, state.direction)
    state.game.load.image(firstImg, `assets/map/${firstImg}.jpg`)

    state.game.load.start()
    console.log('Loading...')
}

// First init called. Should be called only once, and before any level.
function mainInit() {
    console.log('Done loading')

    state.game.stage.backgroundColor = '#000000'

    resize()

    initKeyboardInput(move, () => true)
    initMouseInput(move, () => true)
}
