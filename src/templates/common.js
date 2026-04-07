// See src/lib/templates.py
import * as SepPinyin from "SepPinyin";
import * as Config from "Config";

// utils
export const createButton = (id, innerHTML, onclick) => {
    const button = document.createElement("button");
    button.className = "quizButton";
    button.id = id;
    button.innerHTML = innerHTML;
    button.onclick = onclick;
    return button;
};

export function getTones(pinyin) {
    function getToneNumber(diac) {
        var allDiacs = ["āēīōūǖ", "áéíóúǘ", "ǎěǐǒǔǚ", "àèìòùǜ", "aeiouür"];
        for (var i = 0; i < allDiacs.length; i++) {
            if (allDiacs[i].includes(diac)) {
                return i + 1;
            }
        }
        return 0;
    }
    var a = "([aāáǎà])";
    var e = "([eēéěè])";
    var ae = "([aāáǎàeēéěè])";
    var i = "([iīíǐì])";
    var o = "([oōóǒò])";
    var u = "([uūúǔùüǖǘǚǜ])";
    var eu = "([eēéěèuūúǔù])";
    // prettier-ignore
    var regex=
         '(?:'
           +'(?:'
             +'mi'+u
             +'|[pm]'+o+'u'
             +'|[bpm](?:'
                 +o
                 +'|'+e+'(?:i|ng??)?'
                 +'|'+a+'(?:ng?|i|o)?'
                 +'|i(?:'+e+'|'+a+'[no])'
                 +'|'+i+'(?:ng?)?'
                 +'|'+u
               +')'
             +')'
           +'|(?:f(?:'+o+'u?|'+ae+'(?:ng?|i)?|'+u+'))'
           +'|(?:'
             +'d(?:'+e+'(?:i|ng?)|i(?:'+a+'[on]?|'+u+'))'
             +'|[dt](?:'
                 +a+'(?:i|ng?|o)?'
                 +'|'+e+'(?:i|ng)?'
                 +'|i(?:'+a+'[on]?|'+eu+')'
                 +'|'+i+'(?:ng)?'
                 +'|'+o+'(?:ng?|u)'
                 +'|u(?:'+o+'|'+i+'|'+a+'n?)'
                 +'|'+u+'n?'
               +')'
             +')'
           +'|(?:'
             +'n'+e+'ng?'
             +'|[ln](?:'
                 +a+'(?:i|ng?|o)?'
                 +'|'+e+'(?:i|ng)?'
                 +'|i(?:'+a+'ng|'+a+'[on]?|'+e+'|'+u+')'
                 +'|'+i+'(?:ng?)?'
                 +'|'+o+'(?:ng?|u)'
                 +'|u(?:'+o+'|'+a+'n?)'
                 +'|ü'+e+'?'
                 +'|'+u+'n?'
               +')'
             +')'
           +'|(?:[ghk](?:'+a+'(?:i|ng??|o)?|'+e+'(?:i|ng?)?|'+o+'(?:u|ng)|u(?:'+a+'(?:i|ng??)??|'+i+'|'+o+')|'+u+'n?))'
           +'|(?:zh?'+e+'i|[cz]h?(?:'+e+'(?:ng?)?|'+o+'(?:ng?|u)?|'+a+'o|u?'+a+'(?:i|ng?)?|u?(?:'+o+'|'+i+')|'+u+'n?))'
           +'|(?:'
             +'s'+o+'ng'
             +'|shu'+a+'(?:i|ng?)?'
             +'|sh'+e+'i'
             +'|sh?(?:'
                 +a+'(?:i|ng?|o)?'
                 +'|'+e+'n?g?'
                 +'|'+o+'u'
                 +'|u(?:'+a+'n|'+o+'|'+i+')'
                 +'|'+u+'n?'
                 +'|'+i
               +')'
             +')'
           +'|(?:'
             +'r(?:'
               +ae+'ng?'
               +'|'+i
               +'|'+e
               +'|'+a+'o'
               +'|'+o+'u'
               +'|'+o+'ng'
               +'|u(?:'+o+'|'+i+')'
               +'|u'+a+'n?'
               +'|'+u+'n?'
               +')'
             +'|(r)'
             +')'
           +'|(?:[jqx](?:i(?:'+a+'(o|ng??)?|(?:'+e+'|'+u+')|'+o+'ng)|'+i+'(?:ng?)??|u(?:'+e+'|'+a+'n)|'+u+'n??))'
           +'|(?:'
             +'(?:'
                 +a+'(?:i|o|ng?)?'
                 +'|'+o+'u?'
                 +'|'+e+'(?:i|ng?|r)?'
               +')'
             +')'
           +'|(?:w(?:'+a+'(?:i|ng??)?|'+o+'|'+e+'(?:i|ng?)?|'+u+'))'
           +'|y(?:'+a+'(?:o|ng??)?|'+e+'|'+i+'(?:ng?)?|'+o+'(?:u|ng)?|u(?:'+e+'|'+a+'n)|'+u+'n??)'
         +')'
         +'([12345])?';
    pinyin = pinyin.normalize().toLowerCase().trim();
    //pinyin = pinyin.split('/')[0];
    const re = new RegExp(regex, "g");
    const matches = pinyin.matchAll(re);
    var tones = Array.from(matches).map(function (match) {
        var m = match;
        m.shift();
        var diac = m.filter(function (v) {
            return v !== undefined;
        });
        if (diac.length > 0) {
            if (diac.length > 1 && "12345".includes(diac[1])) {
                return parseInt(diac[1]); // tone as pinyin number
            } else {
                return getToneNumber(diac[0]); // tone as pinyin diacritic
            }
        } else {
            return 0;
        }
    });
    return tones;
}

export function toneToColor(tone) {
    switch (tone) {
        case 1:
        case 2:
        case 3:
        case 4:
        case 5:
            return Config.dconfig.pinyin[`tone${tone}`];
        default:
            console.error("Invalid tone: " + tone);
    }
}

export function colorPinyin(pinyinElement, pinyin) {
    var res = "";
    var rest = pinyin;
    for (const syllable of SepPinyin.separatePinyinInSyllables(pinyin, false)) {
        const tone = getTones(syllable);
        var coloredSyllable = "";
        if (tone.length === 0) {
            coloredSyllable = syllable;
        } else {
            const color = toneToColor(tone[0]);
            coloredSyllable = `<span style="color:${color}">${syllable}</span>`;
        }

        const pos = rest.search(syllable);
        if (pos === -1) {
            throw new Error(
                `Syllable ${syllable} not found in pinyin ${rest}: `,
            );
        }
        const curr = rest.slice(0, pos + syllable.length);
        rest = rest.slice(pos + syllable.length);
        res += curr.replace(syllable, coloredSyllable);
    }

    pinyinElement.innerHTML = res;
}

export function colorPinyinSentenceElement(pinyin) {
    var pinyinElement = document.getElementById("exampleSentencePinyin");
    colorPinyin(pinyinElement, pinyin);
}
