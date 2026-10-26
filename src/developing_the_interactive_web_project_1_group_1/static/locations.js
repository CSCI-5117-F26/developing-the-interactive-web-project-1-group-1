function showBuildingsMap(elementId, buildings, scrollZoom) {
  var map = L.map(elementId, { scrollWheelZoom: scrollZoom });
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  }).addTo(map);

  var pins = [];
  var markers = {};
  buildings.forEach(function (building) {
    var popup = document.createElement('div');
    var name = document.createElement('strong');
    name.textContent = building.building_name;
    popup.append(name, document.createElement('br'), building.address);

    markers[building.location_id] = L.marker([building.latitude, building.longitude]).addTo(map).bindPopup(popup);
    pins.push([building.latitude, building.longitude]);
  });

  document.querySelectorAll('.location-card').forEach(function (card) {
    card.addEventListener('click', function (event) {
      var marker = markers[card.dataset.locationId];
      map.flyTo(marker.getLatLng(), 18);
      marker.openPopup();

      // on phones the map is at the top of the page, so scroll up to it (but not when copying an address)
      if (window.innerWidth <= 700 && !event.target.classList.contains('copy-address')) {
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
    });
  });

  if (pins.length == 1) {
    map.setView(pins[0], 17);
  } else {
    map.fitBounds(pins, { padding: [30, 30] });
  }
}

document.querySelectorAll('.copy-address').forEach(function (button) {
  button.addEventListener('click', function () {
    navigator.clipboard.writeText(button.dataset.address).then(function () {
      button.textContent = 'Copied!';
      setTimeout(function () { button.textContent = 'Copy address'; }, 2000);
    });
  });
});
