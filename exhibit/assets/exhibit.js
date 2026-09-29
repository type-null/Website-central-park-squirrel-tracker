/* The archive uses classic local scripts so it also works when index.html is opened directly. */
(() => {
  'use strict';
  const records = window.SQUIRREL_CENSUS;
  const $ = id => document.getElementById(id);
  const fields = ['search', 'fur', 'age', 'shift', 'activity', 'date'];
  const pageSize = 12;
  const colors = {Gray: '#7b918d', Cinnamon: '#bb7b48', Black: '#434e59', Unknown: '#b9a052'};
  const dateFormat = new Intl.DateTimeFormat('en-US', {month: 'short', day: 'numeric', year: 'numeric', timeZone: 'UTC'});
  const formatDate = value => dateFormat.format(new Date(value + 'T12:00:00Z'));
  const number = value => value.toLocaleString('en-US');
  if (!Array.isArray(records) || !records.length) {
    $('result-count').textContent = 'The census could not be loaded. Download the original CSV below.';
    return;
  }
  const searchText = records.map(r => [r.id, r.hectare, r.fur, r.age, r.location, ...Object.values(r.notes)].join(' ').toLocaleLowerCase());
  const byKey = new Map(records.map(r => [r.key, r]));
  const idCounts = new Map();
  records.forEach(r => idCounts.set(r.id, (idCounts.get(r.id) || 0) + 1));
  let matching = records.slice(), page = 0, selected = null;
  for (const day of [...new Set(records.map(r => r.date))].sort()) {
    const option = document.createElement('option');
    option.value = day;
    option.textContent = formatDate(day);
    $('date').append(option);
  }
  function node(tag, text, className) {
    const el = document.createElement(tag);
    if (text !== undefined) el.textContent = text;
    if (className) el.className = className;
    return el;
  }
  function showDetail(record, focus = false) {
    selected = record ? record.key : null;
    const target = $('detail');
    target.replaceChildren(node('p', 'SIGHTING FIELD NOTE', 'eyebrow'));
    const title = node('h3', record ? record.id : 'No matching sightings');
    title.id = 'detail-heading';
    target.append(title);
    if (!record) {
      target.append(node('p', 'Try a broader search or reset the filters to return to the collection.'));
      drawMap();
      return;
    }
    target.append(node('p', formatDate(record.date) + ' · ' + record.shift + ' observation', 'detail-date'));
    const tags = node('div', undefined, 'tags');
    [record.fur === 'Unknown' ? 'Unknown fur color' : record.fur + ' fur', record.age === 'Unknown' ? 'Unknown age' : record.age].forEach(text => tags.append(node('span', text, 'tag')));
    target.append(tags);
    const facts = node('dl');
    [['Location', record.location], ['Hectare', record.hectare], ['Coordinates', record.lat.toFixed(6) + ', ' + record.lon.toFixed(6)], ['Source row', number(record.key + 1)]].forEach(([label, value]) => facts.append(node('dt', label), node('dd', value)));
    target.append(facts, node('h4', 'WHAT WAS OBSERVED'));
    const activities = Object.entries(record.behaviors).filter(([, value]) => value === true).map(([name]) => name);
    target.append(node('p', activities.length ? activities.join(' · ') : 'No behavior flags were marked for this sighting.'));
    const unrecorded = Object.entries(record.behaviors).filter(([, value]) => value === null).map(([name]) => name);
    if (unrecorded.length) target.append(node('p', 'Not recorded: ' + unrecorded.join(', ')));
    const notes = Object.entries(record.notes).filter(([key, value]) => key !== 'Above Ground Sighter Measurement' || value !== 'FALSE');
    if (notes.length) target.append(node('h4', 'FROM THE OBSERVER’S NOTES'));
    notes.forEach(([label, value]) => {
      target.append(node('p', label === 'Above Ground Sighter Measurement' ? 'Recorded height (units not specified in source)' : label, 'note-label'));
      target.append(node('blockquote', value));
    });
    if (!notes.length) target.append(node('p', 'No additional written notes were recorded.', 'detail-footer'));
    if (idCounts.get(record.id) > 1) target.append(node('p', 'This ID appears more than once in the original census, with different coordinates. Each source row is preserved separately.', 'detail-footer'));
    document.querySelectorAll('.sighting-card').forEach(button => button.setAttribute('aria-pressed', String(Number(button.dataset.key) === selected)));
    drawMap();
    if (focus) target.focus({preventScroll: true});
  }
  function renderList() {
    const start = page * pageSize;
    const fragment = document.createDocumentFragment();
    matching.slice(start, start + pageSize).forEach(record => {
      const button = node('button', undefined, 'sighting-card');
      button.type = 'button';
      button.dataset.key = record.key;
      button.setAttribute('aria-pressed', String(record.key === selected));
      button.setAttribute('aria-label', `${record.id}, ${record.fur} fur, ${record.age}, source row ${record.key + 1}. Open field note`);
      const top = node('span', undefined, 'card-top');
      top.append(node('span', undefined, 'fur-dot ' + record.fur.toLowerCase()), node('span', record.fur + ' · ' + record.age));
      button.append(top, node('strong', record.id), node('small', formatDate(record.date) + ' · ' + record.shift), node('small', 'Source row ' + number(record.key + 1)), node('span', '↗', 'card-arrow'));
      fragment.append(button);
    });
    $('sighting-list').replaceChildren(fragment);
    $('empty').hidden = matching.length > 0;
    $('list-range').textContent = matching.length ? `${number(start + 1)}–${number(Math.min(start + pageSize, matching.length))} of ${number(matching.length)} sightings` : 'No matches';
    $('page-label').textContent = matching.length ? `${page + 1} / ${Math.ceil(matching.length / pageSize)}` : '0 / 0';
    $('previous').disabled = page === 0;
    $('next').disabled = start + pageSize >= matching.length;
  }
  function applyFilters() {
    const values = Object.fromEntries(fields.map(key => [key, $(key).value.trim()]));
    const terms = values.search.toLocaleLowerCase().split(/\s+/).filter(Boolean);
    matching = records.filter(r => (!values.fur || r.fur === values.fur) && (!values.age || r.age === values.age) && (!values.shift || r.shift === values.shift) && (!values.date || r.date === values.date) && (!values.activity || r.behaviors[values.activity] === true) && terms.every(term => searchText[r.key].includes(term)));
    page = 0;
    const count = node('strong', number(matching.length));
    $('result-count').replaceChildren(count, document.createTextNode(' of ' + number(records.length) + ' sightings'));
    const stats = [
      [matching.filter(r => r.age === 'Juvenile').length, 'juvenile sightings'],
      [matching.filter(r => r.behaviors.Foraging).length, 'seen foraging'],
      [matching.filter(r => r.behaviors.Climbing).length, 'seen climbing'],
      [new Set(matching.map(r => r.date)).size, 'observation dates']
    ];
    $('summary').replaceChildren(...stats.map(([value, label]) => {
      const box = node('div', undefined, 'stat');
      box.append(node('strong', number(value)), node('span', label));
      return box;
    }));
    const retained = matching.find(r => r.key === selected);
    // A colorful verbatim note makes the first view inviting without inventing an animal profile.
    const featured = matching.find(r => r.id === '39B-PM-1014-05');
    showDetail(retained || featured || matching[0] || null);
    renderList();
  }
  $('filters').addEventListener('submit', event => event.preventDefault());
  let searchTimer;
  $('search').addEventListener('input', () => { clearTimeout(searchTimer); searchTimer = setTimeout(applyFilters, 100); });
  fields.slice(1).forEach(id => $(id).addEventListener('change', applyFilters));
  $('filters').addEventListener('reset', () => { clearTimeout(searchTimer); setTimeout(applyFilters, 0); });
  $('sighting-list').addEventListener('click', event => {
    const button = event.target.closest('[data-key]');
    if (!button) return;
    showDetail(byKey.get(Number(button.dataset.key)), true);
    $('detail').scrollIntoView({behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth', block: 'nearest'});
  });
  [['previous', -1], ['next', 1]].forEach(([id, direction]) => $(id).addEventListener('click', () => {
    page += direction;
    renderList();
    $('sighting-list').querySelector('button')?.focus({preventScroll: true});
  }));

  const canvas = $('map'), ctx = canvas.getContext('2d');
  const width = 640, height = 680;
  const polygons = window.PARK_BOUNDARY.features.flatMap(feature => feature.geometry.type === 'MultiPolygon' ? feature.geometry.coordinates : [feature.geometry.coordinates]);
  const allPoints = records.map(r => [r.lon, r.lat]).concat(polygons.flat(2));
  const minLon = Math.min(...allPoints.map(p => p[0])), maxLon = Math.max(...allPoints.map(p => p[0]));
  const minLat = Math.min(...allPoints.map(p => p[1])), maxLat = Math.max(...allPoints.map(p => p[1]));
  const longitudeScale = Math.cos((minLat + maxLat) / 2 * Math.PI / 180);
  const scale = Math.min((width - 95) / ((maxLon - minLon) * longitudeScale), (height - 100) / (maxLat - minLat));
  function project(lon, lat) {
    return [width / 2 + (lon - (minLon + maxLon) / 2) * longitudeScale * scale, height / 2 - (lat - (minLat + maxLat) / 2) * scale];
  }
  const locations = new Map(records.map(r => [r.key, project(r.lon, r.lat)]));
  function drawMap() {
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    if (canvas.width !== width * dpr) { canvas.width = width * dpr; canvas.height = height * dpr; }
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, width, height);
    ctx.fillStyle = '#f7faf5'; ctx.fillRect(0, 0, width, height);
    ctx.strokeStyle = '#e3e9df'; ctx.lineWidth = 1;
    ctx.fillStyle = '#809182'; ctx.font = '10px Lato, sans-serif';
    for (let lat = Math.ceil(minLat * 100) / 100; lat < maxLat; lat += .01) {
      const y = project(minLon, lat)[1];
      ctx.beginPath(); ctx.moveTo(25, y); ctx.lineTo(width - 25, y); ctx.stroke();
      ctx.fillText(lat.toFixed(2) + '° N', 15, y - 7);
    }
    for (let lon = Math.ceil(minLon * 100) / 100; lon < maxLon; lon += .01) {
      const x = project(lon, minLat)[0];
      ctx.beginPath(); ctx.moveTo(x, 25); ctx.lineTo(x, height - 25); ctx.stroke();
      ctx.fillText(Math.abs(lon).toFixed(2) + '° W', x + 4, height - 15);
    }
    ctx.fillStyle = '#e6efda'; ctx.strokeStyle = '#aabc9b'; ctx.lineWidth = 1.5;
    polygons.forEach(polygon => {
      ctx.beginPath();
      polygon.forEach(ring => {
        ring.forEach(([lon, lat], index) => { const [x, y] = project(lon, lat); index ? ctx.lineTo(x, y) : ctx.moveTo(x, y); });
        ctx.closePath();
      });
      ctx.fill('evenodd'); ctx.stroke();
    });
    ctx.globalAlpha = .75;
    matching.forEach(record => {
      const [x, y] = locations.get(record.key);
      ctx.beginPath(); ctx.arc(x, y, matching.length < 100 ? 4.5 : 2.6, 0, Math.PI * 2); ctx.fillStyle = colors[record.fur]; ctx.fill();
    });
    ctx.globalAlpha = 1;
    if (selected !== null) {
      const [x, y] = locations.get(selected);
      ctx.beginPath(); ctx.arc(x, y, 9, 0, Math.PI * 2); ctx.fillStyle = '#fff'; ctx.fill(); ctx.lineWidth = 2.5; ctx.strokeStyle = '#246ba6'; ctx.stroke();
      ctx.beginPath(); ctx.arc(x, y, 4.5, 0, Math.PI * 2); ctx.fillStyle = colors[byKey.get(selected).fur]; ctx.fill();
    }
    canvas.setAttribute('aria-label', `Geographic map of ${number(matching.length)} matching sightings, north up. ${selected !== null ? 'Selected sighting ' + byKey.get(selected).id + '.' : ''} All sightings can also be selected from the list below.`);
  }
  canvas.addEventListener('click', event => {
    const box = canvas.getBoundingClientRect();
    const x = (event.clientX - box.left) / box.width * width, y = (event.clientY - box.top) / box.height * height;
    let closest, distance = (16 * width / box.width) ** 2;
    matching.forEach(record => {
      const [px, py] = locations.get(record.key), d = (px - x) ** 2 + (py - y) ** 2;
      if (d < distance) { closest = record; distance = d; }
    });
    if (closest) showDetail(closest);
  });
  applyFilters();
  if (document.fonts) document.fonts.ready.then(drawMap);
  // A fixed acknowledgement lets an embedding article distinguish the exhibit from an error page.
  window.addEventListener('message', event => {
    if (window.parent === window || event.source !== window.parent || event.data?.type !== 'type-null:embed-ping') return;
    window.parent.postMessage({type: 'type-null:embed-ready'}, event.origin === 'null' ? '*' : event.origin);
  });
})();
