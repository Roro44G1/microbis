/* Filtrul pe ani din pagina Presă (presa.html și en/presa.html).
   Barele graficului sunt butoane cu data-an; cardurile au tot data-an (data-year e rezervat în main.js pentru anul din subsol).
   Textul de stare vine gata scris în HTML (data-msg pe fiecare bară,
   data-all pe paragraful de stare), deci nu depinde de limbă. */
(function () {
  'use strict';

  var chart = document.querySelector('.presa-chart');
  if (!chart) return;

  var bars = chart.querySelectorAll('.presa-bar');
  var cards = document.querySelectorAll('.presa-card');
  var status = document.querySelector('.presa-filter__text');
  var reset = document.querySelector('.presa-filter__reset');
  var active = null;

  function show(year) {
    active = year;
    chart.classList.toggle('is-filtered', year !== null);

    bars.forEach(function (bar) {
      bar.setAttribute('aria-pressed', String(bar.dataset.an === year));
    });

    cards.forEach(function (card) {
      card.hidden = year !== null && card.dataset.an !== year;
    });

    reset.hidden = year === null;

    var pressed = chart.querySelector('.presa-bar[aria-pressed="true"]');
    status.textContent = pressed ? pressed.dataset.msg : status.dataset.all;
  }

  bars.forEach(function (bar) {
    bar.addEventListener('click', function () {
      show(active === bar.dataset.an ? null : bar.dataset.an);
    });
  });

  reset.addEventListener('click', function () {
    show(null);
  });
})();
