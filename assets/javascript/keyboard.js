/*!
 * 
 *   simple-keyboard v2.27.56
 *   https://github.com/hodgef/simple-keyboard
 * 
 *   Copyright (c) Francisco Hodge (https://github.com/hodgef)
 * 
 *   This source code is licensed under the MIT license found in the
 *   LICENSE file in the root directory of this source tree.
 *   
 */

!function (t, e) {
    "object" === typeof exports && "object" === typeof module ? module.exports = e() : "function" === typeof define && define.amd ? define("SimpleKeyboard", [], e) : "object" === typeof exports ? exports.SimpleKeyboard = e() : t.SimpleKeyboard = e()
}(window, (function () {
    return function (t) {
        var e = {};

        function __webpack_require__(n) {
            if (e[n]) return e[n].exports;
            var o = e[n] = {i: n, l: !1, exports: {}};
            return t[n].call(o.exports, o, o.exports, __webpack_require__), o.l = !0, o.exports
        }

        return __webpack_require__.m = t, __webpack_require__.c = e, __webpack_require__.d = function (t, e, n) {
            __webpack_require__.o(t, e) || Object.defineProperty(t, e, {enumerable: !0, get: n})
        }, __webpack_require__.r = function (t) {
            "undefined" !== typeof Symbol && Symbol.toStringTag && Object.defineProperty(t, Symbol.toStringTag, {value: "Module"}), Object.defineProperty(t, "__esModule", {value: !0})
        }, __webpack_require__.t = function (t, e) {
            if (1 & e && (t = __webpack_require__(t)), 8 & e) return t;
            if (4 & e && "object" === typeof t && t && t.__esModule) return t;
            var n = Object.create(null);
            if (__webpack_require__.r(n), Object.defineProperty(n, "default", {
                enumerable: !0,
                value: t
            }), 2 & e && "string" != typeof t) for (var o in t) __webpack_require__.d(n, o, function (e) {
                return t[e]
            }.bind(null, o));
            return n
        }, __webpack_require__.n = function (t) {
            var e = t && t.__esModule ? function () {
                return t.default
            } : function () {
                return t
            };
            return __webpack_require__.d(e, "a", e), e
        }, __webpack_require__.o = function (t, e) {
            return Object.prototype.hasOwnProperty.call(t, e)
        }, __webpack_require__.p = "", __webpack_require__(__webpack_require__.s = 0)
    }([function (t, e, n) {
        t.exports = n(2)
    }, function (t, e, n) {
    }, function (t, e, n) {
        "use strict";
        n.r(e);
        n(1);

        function _typeof(t) {
            return (_typeof = "function" === typeof Symbol && "symbol" === typeof Symbol.iterator ? function (t) {
                return typeof t
            } : function (t) {
                return t && "function" === typeof Symbol && t.constructor === Symbol && t !== Symbol.prototype ? "symbol" : typeof t
            })(t)
        }

        function _defineProperties(t, e) {
            for (var n = 0; n < e.length; n++) {
                var o = e[n];
                o.enumerable = o.enumerable || !1, o.configurable = !0, "value" in o && (o.writable = !0), Object.defineProperty(t, o.key, o)
            }
        }

        var o = function () {
            function Utilities(t) {
                var e = t.getOptions, n = t.getCaretPosition, o = t.dispatch;
                !function (t, e) {
                    if (!(t instanceof e)) throw new TypeError("Cannot call a class as a function")
                }(this, Utilities), this.getOptions = e, this.getCaretPosition = n, this.dispatch = o, Utilities.bindMethods(Utilities, this)
            }

            var t, e, n;
            return t = Utilities, n = [{
                key: "bindMethods", value: function (t, e) {
                    var n = !0, o = !1, i = void 0;
                    try {
                        for (var s, a = Object.getOwnPropertyNames(t.prototype)[Symbol.iterator](); !(n = (s = a.next()).done); n = !0) {
                            var r = s.value;
                            "constructor" === r || "bindMethods" === r || (e[r] = e[r].bind(e))
                        }
                    } catch (u) {
                        o = !0, i = u
                    } finally {
                        try {
                            n || null == a.return || a.return()
                        } finally {
                            if (o) throw i
                        }
                    }
                }
            }], (e = [{
                key: "getButtonClass", value: function (t) {
                    var e = t.includes("{") && t.includes("}") && "{//}" !== t ? "functionBtn" : "standardBtn",
                        n = t.replace("{", "").replace("}", ""), o = "";
                    return "standardBtn" !== e && (o = " hg-button-".concat(n)), "hg-".concat(e).concat(o)
                }
            }, {
                key: "getDefaultDiplay", value: function () {
                    return {
                        "{bksp}": "backspace",
                        "{backspace}": "backspace",
                        "{enter}": "< enter",
                        "{shift}": "shift",
                        "{shiftleft}": "shift",
                        "{shiftright}": "shift",
                        "{alt}": "alt",
                        "{s}": "shift",
                        "{tab}": "tab",
                        "{lock}": "caps",
                        "{capslock}": "caps",
                        "{accept}": "Submit",
                        "{space}": " ",
                        "{//}": " ",
                        "{esc}": "esc",
                        "{escape}": "esc",
                        "{f1}": "f1",
                        "{f2}": "f2",
                        "{f3}": "f3",
                        "{f4}": "f4",
                        "{f5}": "f5",
                        "{f6}": "f6",
                        "{f7}": "f7",
                        "{f8}": "f8",
                        "{f9}": "f9",
                        "{f10}": "f10",
                        "{f11}": "f11",
                        "{f12}": "f12",
                        "{numpaddivide}": "/",
                        "{numlock}": "lock",
                        "{arrowup}": "\u2191",
                        "{arrowleft}": "\u2190",
                        "{arrowdown}": "\u2193",
                        "{arrowright}": "\u2192",
                        "{prtscr}": "print",
                        "{scrolllock}": "scroll",
                        "{pause}": "pause",
                        "{insert}": "ins",
                        "{home}": "home",
                        "{pageup}": "up",
                        "{delete}": "del",
                        "{end}": "end",
                        "{pagedown}": "down",
                        "{numpadmultiply}": "*",
                        "{numpadsubtract}": "-",
                        "{numpadadd}": "+",
                        "{numpadenter}": "enter",
                        "{period}": ".",
                        "{numpaddecimal}": ".",
                        "{numpad0}": "0",
                        "{numpad1}": "1",
                        "{numpad2}": "2",
                        "{numpad3}": "3",
                        "{numpad4}": "4",
                        "{numpad5}": "5",
                        "{numpad6}": "6",
                        "{numpad7}": "7",
                        "{numpad8}": "8",
                        "{numpad9}": "9"
                    }
                }
            }, {
                key: "getButtonDisplayName", value: function (t, e, n) {
                    return (e = n ? Object.assign({}, this.getDefaultDiplay(), e) : e || this.getDefaultDiplay())[t] || t
                }
            }, {
                key: "getUpdatedInput", value: function (t, e, n, o) {
                    var i = this.getOptions(), s = e;
                    return ("{bksp}" === t || "{backspace}" === t) && s.length > 0 ? s = this.removeAt(s, n, o) : "{space}" === t ? s = this.addStringAt(s, " ", n, o) : "{tab}" !== t || "boolean" === typeof i.tabCharOnTab && !1 === i.tabCharOnTab ? "{enter}" !== t && "{numpadenter}" !== t || !i.newLineOnEnter ? t.includes("numpad") && Number.isInteger(Number(t[t.length - 2])) ? s = this.addStringAt(s, t[t.length - 2], n, o) : "{numpaddivide}" === t ? s = this.addStringAt(s, "/", n, o) : "{numpadmultiply}" === t ? s = this.addStringAt(s, "*", n, o) : "{numpadsubtract}" === t ? s = this.addStringAt(s, "-", n, o) : "{numpadadd}" === t ? s = this.addStringAt(s, "+", n, o) : "{numpaddecimal}" === t ? s = this.addStringAt(s, ".", n, o) : "{" === t || "}" === t ? s = this.addStringAt(s, t, n, o) : t.includes("{") || t.includes("}") || (s = this.addStringAt(s, t, n, o)) : s = this.addStringAt(s, "\n", n, o) : s = this.addStringAt(s, "\t", n, o), s
                }
            }, {
                key: "updateCaretPos", value: function (t, e) {
                    var n = this.updateCaretPosAction(t, e);
                    this.dispatch((function (t) {
                        t.caretPosition = n
                    }))
                }
            }, {
                key: "updateCaretPosAction", value: function (t, e) {
                    var n = this.getOptions(), o = this.getCaretPosition();
                    return e ? o > 0 && (o -= t) : o += t, n.debug && console.log("Caret at:", o, "(".concat(this.keyboardDOMClass, ")")), o
                }
            }, {
                key: "addStringAt", value: function (t, e, n, o) {
                    var i;
                    return n || 0 === n ? (i = [t.slice(0, n), e, t.slice(n)].join(""), this.isMaxLengthReached() || o && this.updateCaretPos(e.length)) : i = t + e, i
                }
            }, {
                key: "removeAt", value: function (t, e, n) {
                    var o;
                    if (0 === this.getCaretPosition()) return t;
                    var i = /([\uD800-\uDBFF][\uDC00-\uDFFF])/g;
                    return e && e >= 0 ? t.substring(e - 2, e).match(i) ? (o = t.substr(0, e - 2) + t.substr(e), n && this.updateCaretPos(2, !0)) : (o = t.substr(0, e - 1) + t.substr(e), n && this.updateCaretPos(1, !0)) : t.slice(-2).match(i) ? (o = t.slice(0, -2), n && this.updateCaretPos(2, !0)) : (o = t.slice(0, -1), n && this.updateCaretPos(1, !0)), o
                }
            }, {
                key: "handleMaxLength", value: function (t, e) {
                    var n = this.getOptions(), o = n.maxLength, i = t[n.inputName], s = e.length - 1 >= o;
                    if (e.length <= i.length) return !1;
                    if (Number.isInteger(o)) return n.debug && console.log("maxLength (num) reached:", s), s ? (this.maxLengthReached = !0, !0) : (this.maxLengthReached = !1, !1);
                    if ("object" === _typeof(o)) {
                        var a = i.length === o[n.inputName];
                        return n.debug && console.log("maxLength (obj) reached:", a), a ? (this.maxLengthReached = !0, !0) : (this.maxLengthReached = !1, !1)
                    }
                }
            }, {
                key: "isMaxLengthReached", value: function () {
                    return Boolean(this.maxLengthReached)
                }
            }, {
                key: "isTouchDevice", value: function () {
                    return "ontouchstart" in window || navigator.maxTouchPoints
                }
            }, {
                key: "pointerEventsSupported", value: function () {
                    return window.PointerEvent
                }
            }, {
                key: "camelCase", value: function (t) {
                    return !!t && t.toLowerCase().trim().split(/[.\-_\s]/g).reduce((function (t, e) {
                        return e.length ? t + e[0].toUpperCase() + e.slice(1) : t
                    }))
                }
            }]) && _defineProperties(t.prototype, e), n && _defineProperties(t, n), Utilities
        }();

        function PhysicalKeyboard_defineProperties(t, e) {
            for (var n = 0; n < e.length; n++) {
                var o = e[n];
                o.enumerable = o.enumerable || !1, o.configurable = !0, "value" in o && (o.writable = !0), Object.defineProperty(t, o.key, o)
            }
        }

        var i = function () {
            function PhysicalKeyboard(t) {
                var e = t.dispatch, n = t.getOptions;
                !function (t, e) {
                    if (!(t instanceof e)) throw new TypeError("Cannot call a class as a function")
                }(this, PhysicalKeyboard), this.dispatch = e, this.getOptions = n, o.bindMethods(PhysicalKeyboard, this)
            }

            var t, e, n;
            return t = PhysicalKeyboard, (e = [{
                key: "handleHighlightKeyDown", value: function (t) {
                    var e = this.getOptions(), n = this.getSimpleKeyboardLayoutKey(t);
                    this.dispatch((function (t) {
                        var o = t.getButtonElement(n) || t.getButtonElement("{".concat(n, "}"));
                        o && (o.style.backgroundColor = e.physicalKeyboardHighlightBgColor || "#9ab4d0", o.style.color = e.physicalKeyboardHighlightTextColor || "white")
                    }))
                }
            }, {
                key: "handleHighlightKeyUp", value: function (t) {
                    var e = this.getSimpleKeyboardLayoutKey(t);
                    this.dispatch((function (t) {
                        var n = t.getButtonElement(e) || t.getButtonElement("{".concat(e, "}"));
                        n && n.removeAttribute && n.removeAttribute("style")
                    }))
                }
            }, {
                key: "getSimpleKeyboardLayoutKey", value: function (t) {
                    var e;
                    return ((e = t.code.includes("Numpad") || t.code.includes("Shift") || t.code.includes("Space") || t.code.includes("Backspace") || t.code.includes("Control") || t.code.includes("Alt") || t.code.includes("Meta") ? t.code : t.key) !== e.toUpperCase() || "F" === t.code[0] && Number.isInteger(Number(t.code[1])) && t.code.length <= 3) && (e = e.toLowerCase()), e
                }
            }]) && PhysicalKeyboard_defineProperties(t.prototype, e), n && PhysicalKeyboard_defineProperties(t, n), PhysicalKeyboard
        }();

        function KeyboardLayout_defineProperties(t, e) {
            for (var n = 0; n < e.length; n++) {
                var o = e[n];
                o.enumerable = o.enumerable || !1, o.configurable = !0, "value" in o && (o.writable = !0), Object.defineProperty(t, o.key, o)
            }
        }

        var s = function () {
            function KeyboardLayout() {
                !function (t, e) {
                    if (!(t instanceof e)) throw new TypeError("Cannot call a class as a function")
                }(this, KeyboardLayout)
            }

            var t, e, n;
            return t = KeyboardLayout, n = [{
                key: "getDefaultLayout", value: function () {
                    return {
                        default: ["` 1 2 3 4 5 6 7 8 9 0 - = {bksp}", "{tab} q w e r t y u i o p [ ] \\", "{lock} a s d f g h j k l ; ' {enter}", "{shift} z x c v b n m , . / {shift}", ".com @ {space}"],
                        shift: ["~ ! @ # $ % ^ & * ( ) _ + {bksp}", "{tab} Q W E R T Y U I O P { } |", '{lock} A S D F G H J K L : " {enter}', "{shift} Z X C V B N M < > ? {shift}", ".com @ {space}"]
                    }
                }
            }], (e = null) && KeyboardLayout_defineProperties(t.prototype, e), n && KeyboardLayout_defineProperties(t, n), KeyboardLayout
        }();

        function _toConsumableArray(t) {
            return function (t) {
                if (Array.isArray(t)) {
                    for (var e = 0, n = new Array(t.length); e < t.length; e++) n[e] = t[e];
                    return n
                }
            }(t) || function (t) {
                if (Symbol.iterator in Object(t) || "[object Arguments]" === Object.prototype.toString.call(t)) return Array.from(t)
            }(t) || function () {
                throw new TypeError("Invalid attempt to spread non-iterable instance")
            }()
        }

        function Keyboard_typeof(t) {
            return (Keyboard_typeof = "function" === typeof Symbol && "symbol" === typeof Symbol.iterator ? function (t) {
                return typeof t
            } : function (t) {
                return t && "function" === typeof Symbol && t.constructor === Symbol && t !== Symbol.prototype ? "symbol" : typeof t
            })(t)
        }

        function Keyboard_defineProperties(t, e) {
            for (var n = 0; n < e.length; n++) {
                var o = e[n];
                o.enumerable = o.enumerable || !1, o.configurable = !0, "value" in o && (o.writable = !0), Object.defineProperty(t, o.key, o)
            }
        }

        function _defineProperty(t, e, n) {
            return e in t ? Object.defineProperty(t, e, {
                value: n,
                enumerable: !0,
                configurable: !0,
                writable: !0
            }) : t[e] = n, t
        }

        var a = function () {
            function SimpleKeyboard() {
                var t = this;
                !function (t, e) {
                    if (!(t instanceof e)) throw new TypeError("Cannot call a class as a function")
                }(this, SimpleKeyboard), _defineProperty(this, "getOptions", (function () {
                    return t.options
                })), _defineProperty(this, "getCaretPosition", (function () {
                    return t.caretPosition
                })), _defineProperty(this, "registerModule", (function (e, n) {
                    t.modules[e] || (t.modules[e] = {}), n(t.modules[e])
                }));
                var e = "string" === typeof (arguments.length <= 0 ? void 0 : arguments[0]) ? arguments.length <= 0 ? void 0 : arguments[0] : ".simple-keyboard",
                    n = "object" === Keyboard_typeof(arguments.length <= 0 ? void 0 : arguments[0]) ? arguments.length <= 0 ? void 0 : arguments[0] : arguments.length <= 1 ? void 0 : arguments[1];
                if (n || (n = {}), this.utilities = new o({
                    getOptions: this.getOptions,
                    getCaretPosition: this.getCaretPosition,
                    dispatch: this.dispatch
                }), this.caretPosition = null, this.keyboardDOM = document.querySelector(e), this.options = n, this.options.layoutName = this.options.layoutName || "default", this.options.theme = this.options.theme || "hg-theme-default", this.options.inputName = this.options.inputName || "default", this.options.preventMouseDownDefault = this.options.preventMouseDownDefault || !1, this.keyboardPluginClasses = "", o.bindMethods(SimpleKeyboard, this), this.input = {}, this.input[this.options.inputName] = "", this.keyboardDOMClass = e.split(".").join(""), this.buttonElements = {}, window.SimpleKeyboardInstances || (window.SimpleKeyboardInstances = {}), this.currentInstanceName = this.utilities.camelCase(this.keyboardDOMClass), window.SimpleKeyboardInstances[this.currentInstanceName] = this, this.allKeyboardInstances = window.SimpleKeyboardInstances, this.keyboardInstanceNames = Object.keys(window.SimpleKeyboardInstances), this.isFirstKeyboardInstance = this.keyboardInstanceNames[0] === this.currentInstanceName, this.physicalKeyboard = new i({
                    dispatch: this.dispatch,
                    getOptions: this.getOptions
                }), !this.keyboardDOM) throw console.warn('"'.concat(e, '" was not found in the DOM.')), new Error("KEYBOARD_DOM_ERROR");
                this.render(), this.modules = {}, this.loadModules()
            }

            var t, e, n;
            return t = SimpleKeyboard, (e = [{
                key: "handleButtonClicked", value: function (t) {
                    var e = this.options.debug;
                    if ("{//}" === t) return !1;
                    "function" === typeof this.options.onKeyPress && this.options.onKeyPress(t), this.input[this.options.inputName] || (this.input[this.options.inputName] = "");
                    var n = this.utilities.getUpdatedInput(t, this.input[this.options.inputName], this.caretPosition);
                    if (this.input[this.options.inputName] !== n && (!this.options.inputPattern || this.options.inputPattern && this.inputPatternIsValid(n))) {
                        if (this.options.maxLength && this.utilities.handleMaxLength(this.input, n)) return !1;
                        this.input[this.options.inputName] = this.utilities.getUpdatedInput(t, this.input[this.options.inputName], this.caretPosition, !0), e && console.log("Input changed:", this.input), this.options.syncInstanceInputs && this.syncInstanceInputs(), "function" === typeof this.options.onChange && this.options.onChange(this.input[this.options.inputName]), "function" === typeof this.options.onChangeAll && this.options.onChangeAll(this.input)
                    }
                    e && console.log("Key pressed:", t)
                }
            }, {
                key: "handleButtonMouseDown", value: function (t, e) {
                    var n = this;
                    this.options.preventMouseDownDefault && e.preventDefault(), this.options.stopMouseDownPropagation && e.stopPropagation(), e && e.target.classList.add(this.activeButtonClass), this.isMouseHold = !0, this.holdInteractionTimeout && clearTimeout(this.holdInteractionTimeout), this.holdTimeout && clearTimeout(this.holdTimeout), this.options.disableButtonHold || (this.holdTimeout = setTimeout((function () {
                        !n.isMouseHold || (t.includes("{") || t.includes("}")) && "{delete}" !== t && "{backspace}" !== t && "{bksp}" !== t && "{space}" !== t && "{tab}" !== t || (n.options.debug && console.log("Button held:", t), n.handleButtonHold(t, e)), clearTimeout(n.holdTimeout)
                    }), 500))
                }
            }, {
                key: "handleButtonMouseUp", value: function (t) {
                    var e = this;
                    this.recurseButtons((function (t) {
                        t.classList.remove(e.activeButtonClass)
                    })), this.isMouseHold = !1, this.holdInteractionTimeout && clearTimeout(this.holdInteractionTimeout), t && "function" === typeof this.options.onKeyReleased && this.options.onKeyReleased(t)
                }
            }, {
                key: "handleKeyboardContainerMouseDown", value: function (t) {
                    this.options.preventMouseDownDefault && t.preventDefault()
                }
            }, {
                key: "handleButtonHold", value: function (t) {
                    var e = this;
                    this.holdInteractionTimeout && clearTimeout(this.holdInteractionTimeout), this.holdInteractionTimeout = setTimeout((function () {
                        e.isMouseHold ? (e.handleButtonClicked(t), e.handleButtonHold(t)) : clearTimeout(e.holdInteractionTimeout)
                    }), 100)
                }
            }, {
                key: "syncInstanceInputs", value: function () {
                    var t = this;
                    this.dispatch((function (e) {
                        e.replaceInput(t.input), e.caretPosition = t.caretPosition
                    }))
                }
            }, {
                key: "clearInput", value: function (t) {
                    t = t || this.options.inputName, this.input[t] = "", this.caretPosition = 0, this.options.syncInstanceInputs && this.syncInstanceInputs()
                }
            }, {
                key: "getInput", value: function (t) {
                    return t = t || this.options.inputName, this.options.syncInstanceInputs && this.syncInstanceInputs(), this.input[t]
                }
            }, {
                key: "setInput", value: function (t, e) {
                    e = e || this.options.inputName, this.input[e] = t, this.options.syncInstanceInputs && this.syncInstanceInputs()
                }
            }, {
                key: "replaceInput", value: function (t) {
                    this.input = t
                }
            }, {
                key: "setOptions", value: function (t) {
                    t = t || {}, this.options = Object.assign(this.options, t), this.onSetOptions(t), this.render()
                }
            }, {
                key: "onSetOptions", value: function (t) {
                    t.inputName && (this.options.debug && console.log("inputName changed. caretPosition reset."), this.caretPosition = null)
                }
            }, {
                key: "clear", value: function () {
                    this.keyboardDOM.innerHTML = "", this.keyboardDOM.className = this.keyboardDOMClass, this.buttonElements = {}
                }
            }, {
                key: "dispatch", value: function (t) {
                    if (!window.SimpleKeyboardInstances) throw console.warn("SimpleKeyboardInstances is not defined. Dispatch cannot be called."), new Error("INSTANCES_VAR_ERROR");
                    return Object.keys(window.SimpleKeyboardInstances).forEach((function (e) {
                        t(window.SimpleKeyboardInstances[e], e)
                    }))
                }
            }, {
                key: "addButtonTheme", value: function (t, e) {
                    var n = this;
                    if (!e || !t) return !1;
                    t.split(" ").forEach((function (o) {
                        e.split(" ").forEach((function (e) {
                            n.options.buttonTheme || (n.options.buttonTheme = []);
                            var i = !1;
                            n.options.buttonTheme.map((function (t) {
                                if (t.class.split(" ").includes(e)) {
                                    i = !0;
                                    var n = t.buttons.split(" ");
                                    n.includes(o) || (i = !0, n.push(o), t.buttons = n.join(" "))
                                }
                                return t
                            })), i || n.options.buttonTheme.push({class: e, buttons: t})
                        }))
                    })), this.render()
                }
            }, {
                key: "removeButtonTheme", value: function (t, e) {
                    var n = this;
                    if (!t && !e) return this.options.buttonTheme = [], this.render(), !1;
                    t && Array.isArray(this.options.buttonTheme) && this.options.buttonTheme.length && (t.split(" ").forEach((function (t, o) {
                        n.options.buttonTheme.map((function (o, i) {
                            if (e && e.includes(o.class) || !e) {
                                var s = o.buttons.split(" ").filter((function (e) {
                                    return e !== t
                                }));
                                s.length ? o.buttons = s.join(" ") : (n.options.buttonTheme.splice(i, 1), o = null)
                            }
                            return o
                        }))
                    })), this.render())
                }
            }, {
                key: "getButtonElement", value: function (t) {
                    var e, n = this.buttonElements[t];
                    return n && (e = n.length > 1 ? n : n[0]), e
                }
            }, {
                key: "inputPatternIsValid", value: function (t) {
                    var e, n = this.options.inputPattern;
                    if ((e = n instanceof RegExp ? n : n[this.options.inputName]) && t) {
                        var o = e.test(t);
                        return this.options.debug && console.log('inputPattern ("'.concat(e, '"): ').concat(o ? "passed" : "did not pass!")), o
                    }
                    return !0
                }
            }, {
                key: "setEventListeners", value: function () {
                    !this.isFirstKeyboardInstance && this.allKeyboardInstances || (this.options.debug && console.log("Caret handling started (".concat(this.keyboardDOMClass, ")")), document.addEventListener("keyup", this.handleKeyUp), document.addEventListener("keydown", this.handleKeyDown), document.addEventListener("mouseup", this.handleMouseUp), document.addEventListener("touchend", this.handleTouchEnd))
                }
            }, {
                key: "handleKeyUp", value: function (t) {
                    this.caretEventHandler(t), this.options.physicalKeyboardHighlight && this.physicalKeyboard.handleHighlightKeyUp(t)
                }
            }, {
                key: "handleKeyDown", value: function (t) {
                    this.options.physicalKeyboardHighlight && this.physicalKeyboard.handleHighlightKeyDown(t)
                }
            }, {
                key: "handleMouseUp", value: function (t) {
                    this.caretEventHandler(t)
                }
            }, {
                key: "handleTouchEnd", value: function (t) {
                    this.caretEventHandler(t)
                }
            }, {
                key: "caretEventHandler", value: function (t) {
                    var e;
                    t.target.tagName && (e = t.target.tagName.toLowerCase()), this.dispatch((function (n) {
                        n.isMouseHold && (n.isMouseHold = !1), "textarea" !== e && "input" !== e || n.options.disableCaretPositioning ? n.options.disableCaretPositioning && (n.caretPosition = null) : (n.caretPosition = t.target.selectionStart, n.options.debug && console.log("Caret at: ", t.target.selectionStart, t.target.tagName.toLowerCase(), "(".concat(n.keyboardDOMClass, ")")))
                    }))
                }
            }, {
                key: "recurseButtons", value: function (t) {
                    var e = this;
                    if (!t) return !1;
                    Object.keys(this.buttonElements).forEach((function (n) {
                        return e.buttonElements[n].forEach(t)
                    }))
                }
            }, {
                key: "destroy", value: function () {
                    this.options.debug && console.log("Destroying simple-keyboard instance: ".concat(this.currentInstanceName)), document.removeEventListener("keyup", this.handleKeyUp), document.removeEventListener("keydown", this.handleKeyDown), document.removeEventListener("mouseup", this.handleMouseUp), document.removeEventListener("touchend", this.handleTouchEnd), document.onpointerup = null, document.ontouchend = null, document.ontouchcancel = null, document.onmouseup = null;
                    var deleteButton = function (t) {
                        t.onpointerdown = null, t.onpointerup = null, t.onpointercancel = null, t.ontouchstart = null, t.ontouchend = null, t.ontouchcancel = null, t.onclick = null, t.onmousedown = null, t.onmouseup = null, t.remove(), t = null
                    };
                    this.recurseButtons(deleteButton), this.recurseButtons = null, deleteButton = null, this.keyboardDOM.onpointerdown = null, this.keyboardDOM.ontouchstart = null, this.keyboardDOM.onmousedown = null, this.clear(), window.SimpleKeyboardInstances[this.currentInstanceName] = null, delete window.SimpleKeyboardInstances[this.currentInstanceName], this.initialized = !1
                }
            }, {
                key: "getButtonThemeClasses", value: function (t) {
                    var e = this.options.buttonTheme, n = [];
                    return Array.isArray(e) && e.forEach((function (e) {
                        if (e.class && "string" === typeof e.class && e.buttons && "string" === typeof e.buttons) {
                            var o = e.class.split(" ");
                            e.buttons.split(" ").includes(t) && (n = [].concat(_toConsumableArray(n), _toConsumableArray(o)))
                        } else console.warn('Incorrect "buttonTheme". Please check the documentation.', e)
                    })), n
                }
            }, {
                key: "setDOMButtonAttributes", value: function (t, e) {
                    var n = this.options.buttonAttributes;
                    Array.isArray(n) && n.forEach((function (n) {
                        n.attribute && "string" === typeof n.attribute && n.value && "string" === typeof n.value && n.buttons && "string" === typeof n.buttons ? n.buttons.split(" ").includes(t) && e(n.attribute, n.value) : console.warn('Incorrect "buttonAttributes". Please check the documentation.', n)
                    }))
                }
            }, {
                key: "onTouchDeviceDetected", value: function () {
                    this.processAutoTouchEvents(), this.disableContextualWindow()
                }
            }, {
                key: "disableContextualWindow", value: function () {
                    window.oncontextmenu = function (t) {
                        if (t.target.classList.contains("hg-button")) return t.preventDefault(), t.stopPropagation(), !1
                    }
                }
            }, {
                key: "processAutoTouchEvents", value: function () {
                    this.options.autoUseTouchEvents && (this.options.useTouchEvents = !0, this.options.debug && console.log("autoUseTouchEvents: Touch device detected, useTouchEvents enabled."))
                }
            }, {
                key: "onInit", value: function () {
                    this.options.debug && console.log("".concat(this.keyboardDOMClass, " Initialized")), this.setEventListeners(), "function" === typeof this.options.onInit && this.options.onInit()
                }
            }, {
                key: "beforeFirstRender", value: function () {
                    this.utilities.isTouchDevice() && this.onTouchDeviceDetected(), "function" === typeof this.options.beforeFirstRender && this.options.beforeFirstRender(), this.isFirstKeyboardInstance && this.utilities.pointerEventsSupported() && !this.options.useTouchEvents && !this.options.useMouseEvents && this.options.debug && console.log("Using PointerEvents as it is supported by this browser"), this.options.useTouchEvents && this.options.debug && console.log("useTouchEvents has been enabled. Only touch events will be used.")
                }
            }, {
                key: "beforeRender", value: function () {
                    "function" === typeof this.options.beforeRender && this.options.beforeRender()
                }
            }, {
                key: "onRender", value: function () {
                    "function" === typeof this.options.onRender && this.options.onRender()
                }
            }, {
                key: "onModulesLoaded", value: function () {
                    "function" === typeof this.options.onModulesLoaded && this.options.onModulesLoaded()
                }
            }, {
                key: "loadModules", value: function () {
                    var t = this;
                    Array.isArray(this.options.modules) && (this.options.modules.forEach((function (e) {
                        var n = new e;
                        if (n.constructor.name && "Function" !== n.constructor.name) {
                            var o = "module-".concat(t.utilities.camelCase(n.constructor.name));
                            t.keyboardPluginClasses = t.keyboardPluginClasses + " ".concat(o)
                        }
                        n.init(t)
                    })), this.keyboardPluginClasses = this.keyboardPluginClasses + " modules-loaded", this.render(), this.onModulesLoaded())
                }
            }, {
                key: "getModuleProp", value: function (t, e) {
                    return !!this.modules[t] && this.modules[t][e]
                }
            }, {
                key: "getModulesList", value: function () {
                    return Object.keys(this.modules)
                }
            }, {
                key: "parseRowDOMContainers", value: function (t, e, n, o) {
                    var i = this, s = Array.from(t.children), a = 0;
                    return s.length && n.forEach((function (n, r) {
                        var u = o[r];
                        if (!u || !(u > n)) return !1;
                        var c = n - a, l = u - a, h = document.createElement("div");
                        h.className += "hg-button-container";
                        var d = "".concat(i.options.layoutName, "-r").concat(e, "c").concat(r);
                        h.setAttribute("data-skUID", d);
                        var p = s.splice(c, l - c + 1);
                        a = l - c, p.forEach((function (t) {
                            return h.appendChild(t)
                        })), s.splice(c, 0, h), t.innerHTML = "", s.forEach((function (e) {
                            return t.appendChild(e)
                        })), i.options.debug && console.log("rowDOMContainer", p, c, l, a + 1)
                    })), t
                }
            }, {
                key: "render", value: function () {
                    var t = this;
                    this.clear(), this.initialized || this.beforeFirstRender(), this.beforeRender();
                    var e = "hg-layout-".concat(this.options.layoutName),
                        n = this.options.layout || s.getDefaultLayout(), o = this.options.useTouchEvents || !1,
                        i = o ? "hg-touch-events" : "", a = this.options.useMouseEvents || !1,
                        r = this.options.disableRowButtonContainers;
                    this.keyboardDOM.className += " ".concat(this.options.theme, " ").concat(e, " ").concat(this.keyboardPluginClasses, " ").concat(i), n[this.options.layoutName].forEach((function (e, n) {
                        var i = e.split(" "), s = document.createElement("div");
                        s.className += "hg-row";
                        var u = [], c = [];
                        i.forEach((function (e, i) {
                            var l, h = !r && e.includes("[") && e.length > 1, d = !r && e.includes("]") && e.length > 1;
                            h && (u.push(i), e = e.replace(/\[/g, "")), d && (c.push(i), e = e.replace(/\]/g, ""));
                            var p = t.utilities.getButtonClass(e),
                                f = t.utilities.getButtonDisplayName(e, t.options.display, t.options.mergeDisplay),
                                y = t.options.useButtonTag ? "button" : "div", b = document.createElement(y);
                            b.className += "hg-button ".concat(p), (l = b.classList).add.apply(l, _toConsumableArray(t.getButtonThemeClasses(e))), t.setDOMButtonAttributes(e, (function (t, e) {
                                b.setAttribute(t, e)
                            })), t.activeButtonClass = "hg-activeButton", !t.utilities.pointerEventsSupported() || o || a ? o ? (b.ontouchstart = function (n) {
                                t.handleButtonClicked(e), t.handleButtonMouseDown(e, n)
                            }, b.ontouchend = function () {
                                t.handleButtonMouseUp(e)
                            }, b.ontouchcancel = function () {
                                t.handleButtonMouseUp(e)
                            }) : (b.onclick = function () {
                                t.isMouseHold = !1, t.handleButtonClicked(e)
                            }, b.onmousedown = function (n) {
                                t.handleButtonMouseDown(e, n)
                            }, b.onmouseup = function () {
                                t.handleButtonMouseUp(e)
                            }) : (b.onpointerdown = function (n) {
                                t.handleButtonClicked(e), t.handleButtonMouseDown(e, n)
                            }, b.onpointerup = function () {
                                t.handleButtonMouseUp(e)
                            }, b.onpointercancel = function () {
                                t.handleButtonMouseUp(e)
                            }), b.setAttribute("data-skBtn", e);
                            var m = "".concat(t.options.layoutName, "-r").concat(n, "b").concat(i);
                            b.setAttribute("data-skBtnUID", m);
                            var g = document.createElement("span");
                            g.innerHTML = f, b.appendChild(g), t.buttonElements[e] || (t.buttonElements[e] = []), t.buttonElements[e].push(b), s.appendChild(b)
                        })), s = t.parseRowDOMContainers(s, n, u, c), t.keyboardDOM.appendChild(s)
                    })), this.onRender(), this.initialized || (this.initialized = !0, !this.utilities.pointerEventsSupported() || o || a ? o ? (document.ontouchend = function () {
                        return t.handleButtonMouseUp()
                    }, document.ontouchcancel = function () {
                        return t.handleButtonMouseUp()
                    }, this.keyboardDOM.ontouchstart = function (e) {
                        return t.handleKeyboardContainerMouseDown(e)
                    }) : o || (document.onmouseup = function () {
                        return t.handleButtonMouseUp()
                    }, this.keyboardDOM.onmousedown = function (e) {
                        return t.handleKeyboardContainerMouseDown(e)
                    }) : (document.onpointerup = function () {
                        return t.handleButtonMouseUp()
                    }, this.keyboardDOM.onpointerdown = function (e) {
                        return t.handleKeyboardContainerMouseDown(e)
                    }), this.onInit())
                }
            }]) && Keyboard_defineProperties(t.prototype, e), n && Keyboard_defineProperties(t, n), SimpleKeyboard
        }();
        e.default = a
    }])
}));
