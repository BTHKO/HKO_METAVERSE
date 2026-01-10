// HKO_HUB Molecule Tests
console.log('=== MOLECULE TESTS ===');
let pass = 0, fail = 0;

// Atoms
const Atom_State = (initial = null) => {
  let v = initial;
  return { read: () => v, write: (x) => (v = x, v), reset: () => (v = initial, v) };
};

const Atom_Event = () => {
  const ls = [];
  return {
    emit: (d) => ls.forEach(f => f(d)),
    on: (f) => (ls.push(f), () => ls.splice(ls.indexOf(f), 1)),
    clear: () => ls.length = 0
  };
};

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

// Mol_Store
const Mol_Store = (init = {}, schema = {}) => {
  const state = Atom_State(init);
  const changed = Atom_Event();
  const validator = Object.keys(schema).length ? Atom_Guard.validate(schema) : null;
  return {
    get: state.read,
    set: (v) => {
      if (validator) { const r = validator(v); if (!r.ok) throw new Error(`Invalid: ${r.field}`); }
      state.write(v); changed.emit(v); return v;
    },
    on: changed.on,
    reset: state.reset
  };
};

const store = Mol_Store({ count: 0 });
console.log('Store get:', store.get().count === 0 ? '✓ PASS' : '✗ FAIL'); store.get().count === 0 ? pass++ : fail++;
store.set({ count: 5 });
console.log('Store set:', store.get().count === 5 ? '✓ PASS' : '✗ FAIL'); store.get().count === 5 ? pass++ : fail++;

let emitted = false;
store.on(() => emitted = true);
store.set({ count: 10 });
console.log('Store emit:', emitted ? '✓ PASS' : '✗ FAIL'); emitted ? pass++ : fail++;

// Mol_Pipeline
const Mol_Pipeline = (...stages) => ({
  run: async (input) => {
    let curr = input;
    for (let i = 0; i < stages.length; i++) curr = await stages[i](curr);
    return curr;
  }
});

const pipeline = Mol_Pipeline(x => x + 1, x => x * 2, x => x - 3);

(async () => {
  const result = await pipeline.run(5);
  console.log('Pipeline:', result === 9 ? '✓ PASS' : '✗ FAIL'); result === 9 ? pass++ : fail++;
  console.log(`\n=== RESULTS: ${pass}/${pass+fail} PASSED ===`);
  process.exit(fail > 0 ? 1 : 0);
})();
