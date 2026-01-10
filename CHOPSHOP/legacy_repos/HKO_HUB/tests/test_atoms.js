// HKO_HUB Atom Tests
console.log('=== ATOM TESTS ===');
let pass = 0, fail = 0;

// Atom_State
const Atom_State = (initial = null) => {
  let v = initial;
  return { read: () => v, write: (x) => (v = x, v), reset: () => (v = initial, v) };
};

const s = Atom_State(10);
console.log('State initial:', s.read() === 10 ? '✓ PASS' : '✗ FAIL'); s.read() === 10 ? pass++ : fail++;
console.log('State write:', s.write(20) === 20 ? '✓ PASS' : '✗ FAIL'); s.write(20) === 20 ? pass++ : fail++;
console.log('State reset:', s.reset() === 10 ? '✓ PASS' : '✗ FAIL'); s.reset() === 10 ? pass++ : fail++;

// Atom_Event
const Atom_Event = () => {
  const ls = [];
  return {
    emit: (d) => ls.forEach(f => f(d)),
    on: (f) => (ls.push(f), () => ls.splice(ls.indexOf(f), 1)),
    clear: () => ls.length = 0
  };
};

const e = Atom_Event();
let received = null;
e.on((d) => received = d);
e.emit('test');
console.log('Event emit:', received === 'test' ? '✓ PASS' : '✗ FAIL'); received === 'test' ? pass++ : fail++;

// Atom_Guard
const Atom_Guard = {
  validate: (rules) => (data) => {
    for (const [k, r] of Object.entries(rules)) {
      if (!r(data[k])) return { ok: false, field: k };
    }
    return { ok: true, data };
  },
  required: (v) => v != null && v !== '',
  type: (t) => (v) => typeof v === t
};

const validator = Atom_Guard.validate({ name: Atom_Guard.required });
console.log('Guard valid:', validator({ name: 'test' }).ok === true ? '✓ PASS' : '✗ FAIL'); validator({ name: 'test' }).ok ? pass++ : fail++;
console.log('Guard invalid:', validator({ name: '' }).ok === false ? '✓ PASS' : '✗ FAIL'); !validator({ name: '' }).ok ? pass++ : fail++;

console.log(`\n=== RESULTS: ${pass}/${pass+fail} PASSED ===`);
process.exit(fail > 0 ? 1 : 0);
