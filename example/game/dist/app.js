webpackJsonp([1],[/*!**********************!*\
  !*** ./src/index.js ***!
  \**********************/
function(t,e,n){"use strict";function a(){(0,i.mainLoad)()}var i=n(24),o=n(3);o.state.game=new Phaser.Game(0,0,Phaser.AUTO,"app",{create:a})},,,/*!**********************!*\
  !*** ./src/store.js ***!
  \**********************/
function(t,e){"use strict";Object.defineProperty(e,"__esModule",{value:!0});var n={position:[1,2,0],direction:"w",loadingVision:!1};e.state=n,window.s=n},,,/*!**********************!*\
  !*** ./src/utils.js ***!
  \**********************/
function(t,e){"use strict";function n(t){return Math.floor(Math.random()*t)}function a(t,e){var n=!0;for(var a in t)if(t[a]!=e[a]){n=!1;break}return n}function i(t){return t.split("_").map(function(t){return parseInt(t)})}function o(t){return t.join("_")}function r(t,e){return o(t)+"_"+e}function s(t,e){return Math.sqrt(Math.pow(t[0]-e[0],2)+Math.pow(t[1]-e[1],2)+Math.pow(t[2]-e[2],2))}function u(t){return"n"==t?"w":f[f.indexOf(t)-1]}function d(t){return"w"==t?"n":f[f.indexOf(t)+1]}function c(t){return u(u(t))}function l(t){return[t.x,t.y,t.width,t.height]}Object.defineProperty(e,"__esModule",{value:!0}),e.randInt=n,e.equalArrays=a,e.textToPos=i,e.posToText=o,e.posDirToText=r,e.posDist=s,e.rotLeft=u,e.rotRight=d,e.rot180=c,e.getBounds=l;var f=["n","e","s","w"]},,,,,,,,,/*!***********************!*\
  !*** ./src/vision.js ***!
  \***********************/
function(t,e,n){"use strict";function a(){var t=arguments.length<=0||void 0===arguments[0]?!1:arguments[0];t||(s.state.loadingVision=!1),s.state.img&&s.state.img.destroy(),s.state.img=s.state.game.add.image(0,0,(0,r.posDirToText)(s.state.position,s.state.direction));var e=Math.min(s.state.game.width/s.state.img.width,s.state.game.height/s.state.img.height);s.state.img.scale.setTo(e),s.state.img.x=(s.state.game.width-s.state.img.width)/2,s.state.img.y=(s.state.game.height-s.state.img.height)/2;var n=["x","y","width","height"];n.map(function(t){return s.state.img[t]=Math.round(s.state.img[t])}),s.state.onTap&&(s.state.img.inputEnabled=!0,s.state.img.events.onInputUp.add(s.state.onTap,this))}function i(t){var e=(0,r.posDirToText)(t.position,t.direction);t.game.cache.checkImageKey(e)?a():(t.loadingVision=!0,t.game.load.image(e,"assets/map/"+e+".jpg").onFileComplete.add(function(){return a()}),t.game.load.start())}function o(){s.state.game.scale.setGameSize(window.innerWidth,window.innerHeight),a(!0)}Object.defineProperty(e,"__esModule",{value:!0}),e.loadVision=i,e.resize=o;var r=n(6),s=n(3);window.addEventListener("resize",function(){return s.state.game.time.events.add(200,o)},!1)},,,,,,,/*!***************************!*\
  !*** ./assets/map/map.js ***!
  \***************************/
function(t,e){"use strict";Object.defineProperty(e,"__esModule",{value:!0});var n={"1_2_0":{s:[1,1,0]},"1_1_0":{s:[1,0,0],n:[1,2,0]},"1_0_0":{n:[1,1,0],w:[0,0,0]},"0_0_0":{e:[1,0,0]}};e["default"]=n,t.exports=e["default"]},/*!**********************!*\
  !*** ./src/input.js ***!
  \**********************/
function(t,e,n){"use strict";function a(t,e){var n=this,a=["UP","DOWN","LEFT","RIGHT"];a.map(function(e){return u.state.game.input.keyboard.addKey(Phaser.Keyboard[e]).onDown.add(t,n,null,e)}),u.state.game.input.keyboard.addKey(Phaser.Keyboard.SPACEBAR).onDown.add(e,this,null)}function i(t,e){u.state.onTap=function(n,a){return o(a,t,e)}}function o(t,e,n){var a=t.x,i=t.y,o=.28,d=(0,s.getBounds)(u.state.img),c=r(d,4),l=c[0],f=c[1],g=c[2],m=c[3],p=f+m*o,h=f+m*(1-o),v=l+g*o,y=l+g*(1-o);i>p&&h>i?v>a?e(null,"LEFT"):a>y?e(null,"RIGHT"):n():a>v&&y>a&&(p>i?e(null,"UP"):i>h&&e(null,"DOWN"))}Object.defineProperty(e,"__esModule",{value:!0});var r=function(){function t(t,e){var n=[],a=!0,i=!1,o=void 0;try{for(var r,s=t[Symbol.iterator]();!(a=(r=s.next()).done)&&(n.push(r.value),!e||n.length!==e);a=!0);}catch(u){i=!0,o=u}finally{try{!a&&s["return"]&&s["return"]()}finally{if(i)throw o}}return n}return function(e,n){if(Array.isArray(e))return e;if(Symbol.iterator in Object(e))return t(e,n);throw new TypeError("Invalid attempt to destructure non-iterable instance")}}();e.initKeyboardInput=a,e.initMouseInput=i;var s=n(6),u=n(3)},/*!***********************!*\
  !*** ./src/loader.js ***!
  \***********************/
function(t,e,n){"use strict";function a(){u.state.game.load.onLoadComplete.add(function(){u.state.game.load.onLoadComplete.removeAll(),i()},this);var t=(0,o.posDirToText)(u.state.position,u.state.direction);u.state.game.load.image(t,"assets/map/"+t+".jpg"),u.state.game.load.start(),console.log("Loading...")}function i(){console.log("Done loading"),u.state.game.stage.backgroundColor="#000000",(0,s.initKeyboardInput)(r.move,function(){return!0}),(0,s.initMouseInput)(r.move,function(){return!0}),(0,d.resize)()}Object.defineProperty(e,"__esModule",{value:!0}),e.mainLoad=a;var o=n(6),r=n(25),s=n(23),u=n(3),d=n(15)},/*!*************************!*\
  !*** ./src/movement.js ***!
  \*************************/
function(t,e,n){"use strict";function a(t){return t&&t.__esModule?t:{"default":t}}function i(t){var e=u["default"][(0,d.posToText)(l.state.position)][t];return e?(l.state.position=e,!0):!1}function o(t,e){if(!l.state.loadingVision){var n=!1,a=!1;switch(e){case"UP":n=i(l.state.direction);break;case"DOWN":n=i((0,d.rot180)(l.state.direction));break;case"LEFT":r(l.state,"left"),a=!0;break;case"RIGHT":r(l.state,"right"),a=!0}(a||n)&&(0,c.loadVision)(l.state),n&&l.state.onMoved&&l.state.onMoved()}}function r(t,e){"left"==e?t.direction=(0,d.rotLeft)(t.direction):t.direction=(0,d.rotRight)(t.direction)}Object.defineProperty(e,"__esModule",{value:!0}),e.move=o;var s=n(22),u=a(s),d=n(6),c=n(15),l=n(3)}]);
//# sourceMappingURL=app.js.map