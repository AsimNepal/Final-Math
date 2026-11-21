'use strict';
// 4,000 drivers, fixed 45-minute outer links, and t(x)=x/k on busy links.
// All values are equilibrium travel times, not a claim about measured traffic.
const $ = (id) => document.getElementById(id);
const capacity = $('capacity');
const toggle = $('roadToggle');
const fmt = (n) => Number(n.toFixed(2)).toLocaleString('en-US', {maximumFractionDigits: 2});
function equilibrium(k, roadOn) {
  const before = 45 + 2000 / k;
  if (!roadOn || k <= 4000 / 90) return {before, after: before, upper: 2000, lower: 2000, middle: 0};
  if (k < 4000 / 45) {
    const outer = 4000 - 45 * k;
    return {before, after: 90, upper: outer, lower: outer, middle: 4000 - 2 * outer};
  }
  return {before, after: 8000 / k, upper: 0, lower: 0, middle: 4000};
}
function update() {
  const k = Number(capacity.value), on = toggle.checked;
  const result = equilibrium(k, on);
  $('capacityValue').textContent = k;
  $('before').innerHTML = `${fmt(result.before)} <small>min</small>`;
  $('after').innerHTML = `${fmt(result.after)} <small>min</small>`;
  $('upperCost').textContent = `x / ${k}`;
  $('lowerCost').textContent = `x / ${k}`;
  $('networkStatus').textContent = on ? 'New road ON' : 'New road OFF';
  $('networkStatus').style.color = on ? 'var(--mint)' : 'var(--muted)';
  $('newRoad').style.display = on ? '' : 'none';
  for (const [id, value] of [['upper', result.upper], ['lower', result.lower], ['middle', result.middle]]) {
    $(`${id}Flow`).textContent = Math.round(value).toLocaleString('en-US');
    $(`flowBar${id.charAt(0).toUpperCase() + id.slice(1)}`).style.width = `${100 * value / 4000}%`;
  }
  const delta = result.after - result.before;
  const out = $('outcome');
  if (!on) {out.textContent = 'The new road is closed. Both original routes take the same time.';out.className='outcome neutral';}
  else if (delta > 0.00001) {out.textContent = `Adding the road makes trips ${fmt(delta)} minutes longer.`;out.className='outcome';}
  else if (delta < -0.00001) {out.textContent = `Adding the road saves ${fmt(-delta)} minutes per driver.`;out.className='outcome good';}
  else {out.textContent='Adding the road makes no difference at equilibrium.';out.className='outcome neutral';}
}
capacity.addEventListener('input', update);
toggle.addEventListener('change', update);
document.querySelectorAll('[data-k]').forEach(button => button.addEventListener('click', () => {
  capacity.value = button.dataset.k;
  toggle.checked = true;
  update();
  document.getElementById('experiment').scrollIntoView({behavior:'smooth'});
}));
update();
