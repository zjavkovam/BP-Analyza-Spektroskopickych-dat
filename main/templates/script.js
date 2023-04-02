var thresholdSlider = document.getElementById("threshold");
var thresholdValue = document.getElementById("threshold-value");
thresholdValue.innerHTML = thresholdSlider.value;
thresholdSlider.oninput = function() {
  thresholdValue.innerHTML = this.value;
};

var distanceSlider = document.getElementById("distance");
var distanceValue = document.getElementById("distance-value");
distanceValue.innerHTML = distanceSlider.value;
distanceSlider.oninput = function() {
  distanceValue.innerHTML = this.value;
};

var ppmSlider = document.getElementById("ppm");
var ppmValue = document.getElementById("ppm-value");
ppmValue.innerHTML = ppmSlider.value;
ppmSlider.oninput = function() {
  ppmValue.innerHTML = this.value;
};