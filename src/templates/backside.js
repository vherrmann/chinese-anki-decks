import * as Common from "Common";
import * as AnkiHanziQuiz from "AnkiHanziQuiz";
import * as Config from "Config";

function scrollDistanceToTopOfElement(elem) {
    const viewportHeight = Math.max(
        document.documentElement.clientHeight || 0,
        window.innerHeight || 0,
    );
    const elemTop = elem.getBoundingClientRect().top;
    return elemTop - viewportHeight;
}

export async function initializeCharsTargetQuiz(
    chinese,
    pinyin,
    showOutline,
    colorp,
) {
    const frameEl = document.getElementById("characters-target-div-quiz");

    const openDicWordBtn = Common.createButton("openDicWordBtn", "📘", () => {
        if (Config.mobilep) {
            window.open("plecoapi://x-callback-url/df?hw=" + chinese);
        } else {
            window.open(
                "https://www.mdbg.net/chinese/dictionary?page=worddict&wdqb=" +
                    chinese,
            );
        }
    });
    frameEl.appendChild(openDicWordBtn);

    let shownChars = {};
    const infoElement = document.getElementById("info");
    const changeExSentenceDisplay = (c, val) => {
        shownChars[c] = val;
        if (!showOutline && Object.values(shownChars).includes(false)) {
            infoElement.style.display = "none";
        } else {
            infoElement.style.display = "block";
            // Only scroll into view, if there was a proper quiz
            if (
                !showOutline &&
                scrollDistanceToTopOfElement(infoElement) < 100
            ) {
                // Scroll to the element if it is not fully visible
                infoElement.scrollIntoView({
                    behavior: "smooth",
                    block: "end",
                });
            }
        }
    };

    frameEl?.appendChild(
        await AnkiHanziQuiz.createQuizzesString({
            quizSize: Config.dconfig.quizSize,
            chinese,
            // TODO: give options from dconf
            onComplete: (c) => changeExSentenceDisplay(c, true),
            onUncomplete: (c) => changeExSentenceDisplay(c, false),
            extraWriterOptions: {
                showOutline,
                charDataLoader: async function (char, onLoad, onError) {
                    const res = await fetch(`_hanzi_writer_${char}.json`);
                    if (res.ok) {
                        onLoad(await res.json());
                    } else {
                        onError(res);
                    }
                },
            },
            extraQuizOptions: {
                leniency: Config.dconfig.leniency,
                averageDistanceThreshold:
                    Config.dconfig.averageDistanceThreshold,
            },
        }),
    );
}
