var mrsl = {};
var indo = {};
var latin = {};
var engl = {};

let Table;

function preload(){
  table = loadTable('~/cs334/proj1/langfreq.csv', 'csv', 'header');
}


function setup() {
  print("Hello?");
  createCanvas(windowWidth, windowHeight);
}

function draw() {
  background(41, 40, 40);
}
