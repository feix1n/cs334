var mrsl = {};
var indo = {};
var latin = {};
var engl = {};

const lngColors = {
  engl: { hue: 0, sat: 40, light: 40, max: 85 },   // red
  mrsl: { hue: 124, sat: 38, light: 20, max: 60 }, // green
  indo: { hue: 222, sat: 60, light: 35, max: 60 },  // blue
  latin: { hue: 47, sat: 90, light: 51, max: 71 }    // yellow
};

let Table;

// load csv values into table
function preload() {
  Table = loadTable('langfreq.csv', 'csv', 'header');
}

// populate each dictionary with necessary values
function calculate_values() {
  // load marshallese
  let mletters = Table.getColumn('LetterM');
  let mfreq = Table.getColumn('FreqM');

  for (let i = 0; i < mletters.length; i++) {
    if (mletters[i] == "") continue;
    let freqm = round(parseFloat(mfreq[i]), 5);
    let infom = round(-Math.log2(freqm), 5);
    let wetpm = round(freqm * infom, 5);

    mrsl[mletters[i]] = { freq: freqm, info: infom, wetp: wetpm, angle: 0 };
  }

  // load indonesian
  let iletter = Table.getColumn('LetterI');
  let ifreq = Table.getColumn('FreqI');

  for (let i = 0; i < iletter.length; i++) {
    if (iletter[i] == "") continue;
    let freqi = round(parseFloat(ifreq[i]), 5);
    let infoi = round(-Math.log2(freqi), 5);
    let wetpi = round(freqi * infoi, 5);

    indo[iletter[i]] = { freq: freqi, info: infoi, wetp: wetpi, angle: 0 };
  }

  // load Latin
  let lletters = Table.getColumn('LetterL');
  let lfreq = Table.getColumn('FreqL');

  for (let i = 0; i < lletters.length; i++) {
    if (lletters[i] == "") continue;
    let freq_l = round(parseFloat(lfreq[i]), 5);
    let info_l = round(-Math.log2(freq_l), 5);
    let wetp_l = round(freq_l * info_l, 5);

    latin[lletters[i]] = { freq: freq_l, info: info_l, wetp: wetp_l, angle: 0 };
  }

  // load English
  let eletters = Table.getColumn('LetterE');
  let efreq = Table.getColumn('FreqE');

  for (let i = 0; i < eletters.length; i++) {
    let freq_e = round(parseFloat(efreq[i]), 5);
    let info_e = round(-Math.log2(freq_e), 5);
    let wetp_e = round(freq_e * info_e, 5);

    engl[eletters[i]] = { freq: freq_e, info: info_e, wetp: wetp_e, angle: 0 };
  }

  let entropy_mrsl = 0.0;
  let entropy_indo = 0.0;
  let entropy_latin = 0.0;
  let entropy_engl = 0.0;

  // sum entropy for each language up
  for (let symbm in mrsl) {
    entropy_mrsl += mrsl[symbm].wetp;
  }

  for (let symbi in indo) {
    entropy_indo += indo[symbi].wetp;
  }

  for (let symbl in latin) {
    entropy_latin += latin[symbl].wetp;
  }

  for (let symbe in engl) {
    entropy_engl += engl[symbe].wetp;
  }

  mrsl["entropy"] = round(entropy_mrsl, 5);
  indo["entropy"] = round(entropy_indo, 5);
  latin["entropy"] = round(entropy_latin, 5)
  engl["entropy"] = round(entropy_engl, 5);
}


function setup() {
  colorMode(HSL);
  calculate_values();
  print(engl, indo, latin, mrsl);

  createCanvas(windowWidth, windowHeight);
}

function windowResized() {
  resizeCanvas(windowWidth, windowHeight);
}

function drawCodes(lang, slang, yoffset, yheight) {
  let symb = Object.keys(lang).filter(key => key !== "entropy");
  let spacing = windowWidth / (symb.length - 1) * 0.9;
  let maxfreq = Math.max(...symb.map(k => lang[k].freq));
  let maxinfo = Math.max(...symb.map(k => lang[k].info));
  let maxwetp = Math.max(...symb.map(k => lang[k].wetp));
  let entropy = lang.entropy || 1;

  let x = 5;

  for (let i = 0; i < symb.length; i++) {
    let letter = lang[symb[i]];

    // ypos
    let freqhalf = maxfreq / 2;
    let freqOffset = (freqhalf - letter.freq) * entropy * yheight;
    // bobbin?
    let boboffset = sin((letter.angle + frameCount) * 0.03) * letter.wetp * 100;
    // let chaos = random(-(windowHeight * 0.50), windowHeight * 0.46);
    let y = (yoffset + yheight / 2) + freqOffset - (yheight * 0.05) + boboffset;

    // size
    let h = map(letter.info, 0, maxinfo, yheight * 0.05, yheight * 0.12);
    if (y + h / 2 >= yheight + yoffset) h = yheight - y - 10;
    if (y - h / 2 < yoffset) h = h - yheight * 0.02;
    let w = map(letter.wetp, 0, maxwetp, windowWidth * 0.02, windowWidth * 0.04);
    if (x + w / 2 >= windowWidth) w = windowWidth - x - 5;
    if (x - w / 2 < 0) w = x * 0.02;

    // color
    let lightcolor = map(letter.freq, 0, maxfreq, lngColors[slang].light, lngColors[slang].max);
    fill(lngColors[slang].hue, lngColors[slang].sat, lightcolor, 0.80);
    noStroke();
    rect(x, y, w, h);

    // update x pos after drawing
    x += spacing + (entropy);
    x = constrain(x, 0, (windowWidth - 5));

  }
}

function draw() {
  background(0, 1, 16);

  drawCodes(mrsl, 'mrsl', 20, windowHeight * 0.9);
  drawCodes(indo, 'indo', 20, windowHeight * 0.9);
  drawCodes(latin, 'latin', 20, windowHeight * 0.9);
  drawCodes(engl, 'engl', 20, windowHeight * 0.9);

  // let symbolsorted_mrsl = Object.fromEntries(Object.entries(mrsl).filter(key => key !== "entropy").sort(([, a], [, b]) => a.info - b.info));
  // let symbolsorted_indo = Object.fromEntries(Object.entries(indo).filter(key => key !== "entropy").sort(([, a], [, b]) => a.info - b.info));
  // let symbolsorted_latin = Object.fromEntries(Object.entries(latin).filter(key => key !== "entropy").sort(([, a], [, b]) => a.info - b.info));
  // let symbolsorted_engl = Object.fromEntries(Object.entries(engl).filter(key => key !== "entropy").sort(([, a], [, b]) => a.info - b.info));

  // let wetpsorted_mrsl = Object.fromEntries(Object.entries(mrsl).filter(key => key !== "entropy").sort(([, a], [, b]) => a.wtep - b.wetp));
  // let wetpsorted_indo = Object.fromEntries(Object.entries(indo).filter(key => key !== "entropy").sort(([, a], [, b]) => a.wetp - b.wetp));
  // let wetpsorted_latin = Object.fromEntries(Object.entries(latin).filter(key => key !== "entropy").sort(([, a], [, b]) => a.wetp - b.wetp));
  // let wetpsorted_engl = Object.fromEntries(Object.entries(engl).filter(key => key !== "entropy").sort(([, a], [, b]) => a.wetp - b.wetp));

  // drawCodes(symbolsorted_mrsl, 'mrsl', 0, windowHeight / 4);
  // drawCodes(symbolsorted_indo, 'indo', 0, windowHeight / 4);
  // drawCodes(symbolsorted_latin, 'latin', 0, windowHeight / 4);
  // drawCodes(symbolsorted_engl, 'engl', 0, windowHeight / 4);

  // drawCodes(wetpsorted_mrsl, 'mrsl', 2 * (windowHeight / 3), windowHeight / 3);
  // drawCodes(wetpsorted_indo, 'indo', 2 * (windowHeight / 3), windowHeight / 3);
  // drawCodes(wetpsorted_latin, 'latin', 2 * (windowHeight / 3), windowHeight / 3);
  // drawCodes(wetpsorted_engl, 'engl', 2 * (windowHeight / 3), windowHeight / 3);


}

