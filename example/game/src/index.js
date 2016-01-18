import {mainLoad} from './loader.js'
import {state} from './store.js'

function create() {
    mainLoad()
}

state.game = new Phaser.Game(0, 0, Phaser.AUTO, 'app',
                           { create: create })
