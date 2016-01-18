import map from '../assets/map/map.js'
import {randInt, posToText, posDist, getBounds, rotLeft, rotRight, rot180} from './utils.js'
import {loadVision} from './vision.js'
import {state} from './store.js'


var walk = {
    e: [1, 0, 0],
    s: [0, -1, 0],
    w: [-1, 0, 0],
    n: [0, 1, 0],
}


function tryChangePos(direction) {
    let newPos = map[posToText(state.position)][direction]
    if (newPos) {
        state.position = newPos
        return true
    }
    return false
}

export function move(event, key) {
    if (!state.loadingVision) {
        var moved = false
        var rotated = false
        switch (key) {
        case 'UP':
            moved = tryChangePos(state.direction)
            break
        case 'DOWN':
            moved = tryChangePos(rot180(state.direction))
            break
        case 'LEFT':
            rotatePlayer(state, 'left')
            rotated = true
            break
        case 'RIGHT':
            rotatePlayer(state, 'right')
            rotated = true
            break
        }
        if (rotated || moved) loadVision(state)
        if (moved && state.onMoved) state.onMoved()
    }
}

function rotatePlayer(state, type) {
    if (type == 'left') state.direction = rotLeft(state.direction)
    else state.direction = rotRight(state.direction)
}
