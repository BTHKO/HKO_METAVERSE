'use strict';

// LAYER 0: ATOMS
const Atom_State = (initial = null) => {
  let v = initial;
  return { read: () => v, write: (x) => (v = x, v), reset: () => (v = initial, v) };
};

const Atom_Event = () => {
  const ls = [];
  return {
    emit: (d) => ls.forEach(f => f(d)),
    on: (f) => (ls.push(f), () => ls.splice(ls.indexOf(f), 1)),
    once: (f) => { const off = ls.push((d) => (f(d), off())) && (() => ls.pop()); return off; },
    clear: () => ls.length = 0
  };
};

const Atom_Lifecycle = () => {
  const h = { init: [], start: [], stop: [], destroy: [] };
  return { on: (phase, fn) => h[phase].push(fn), run: (phase) => h[phase]?.forEach(f => f()) };
};

const Atom_Transform = {
  pipe: (...fns) => (x) => fns.reduce((v, f) => f(v), x),
  compose: (...fns) => Atom_Transform.pipe(...fns.reverse())
};

const Atom_Guard = {
  validate: (rules) => (data) => {
    for (const [k, r] of Object.entries(rules)) if (!r(data[k])) return { ok: false, field: k };
    return { ok: true, data };
  },
  required: (v) => v != null && v !== '',
  type: (t) => (v) => typeof v === t
};

// LAYER 1: MOLECULES
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
    on: changed.on, reset: state.reset
  };
};

const Mol_Module = (name, cfg = {}) => {
  const lc = Atom_Lifecycle();
  const state = Atom_State({ status: 'idle', err: null });
  const evt = Atom_Event();
  return {
    name, cfg,
    init: async () => { lc.run('init'); state.write({ status: 'init', err: null }); evt.emit('init'); },
    start: async () => { lc.run('start'); state.write({ status: 'run', err: null }); evt.emit('start'); },
    stop: async () => { lc.run('stop'); state.write({ status: 'stop', err: null }); evt.emit('stop'); },
    status: () => state.read(),
    on: evt.on,
    onInit: (f) => lc.on('init', f),
    onStart: (f) => lc.on('start', f),
    onStop: (f) => lc.on('stop', f)
  };
};

const Mol_Pipeline = (...stages) => {
  const evt = Atom_Event();
  return {
    run: async (input) => {
      let curr = input;
      for (let i = 0; i < stages.length; i++) {
        try { evt.emit({ stage: i, status: 'run' }); curr = await stages[i](curr); evt.emit({ stage: i, status: 'ok' }); }
        catch (e) { evt.emit({ stage: i, status: 'fail', err: e.message }); throw e; }
      }
      return curr;
    },
    on: evt.on
  };
};

// LAYER 2: MODULES
const Module_Logger = () => {
  const mod = Mol_Module('logger');
  const logs = [];
  const evt = Atom_Event();
  const log = (level, ...msgs) => {
    const entry = { time: new Date().toISOString(), level, msg: msgs.join(' ') };
    logs.push(entry); if (logs.length > 1000) logs.shift();
    evt.emit(entry); console.log(`[${entry.time}] [${level}]`, ...msgs);
  };
  return { ...mod, info: (...m) => log('INFO', ...m), warn: (...m) => log('WARN', ...m),
    error: (...m) => log('ERROR', ...m), debug: (...m) => log('DEBUG', ...m),
    getLogs: () => [...logs], onLog: evt.on };
};

const Module_State = () => {
  const mod = Mol_Module('state');
  const store = Mol_Store({ app: { status: 'idle', version: '2.0.0' }, modules: {}, plugins: {} });
  return { ...mod, get: store.get, set: store.set, subscribe: store.on,
    update: (path, val) => {
      const state = store.get(); const keys = path.split('.'); let obj = state;
      for (let i = 0; i < keys.length - 1; i++) obj = obj[keys[i]];
      obj[keys[keys.length - 1]] = val; store.set({ ...state });
    }
  };
};

const Module_Config = () => {
  const mod = Mol_Module('config');
  const store = Mol_Store({ env: 'development', paths: {}, features: {} });
  mod.onInit(() => {
    const os = require('os'); const app = require('electron').app;
    store.set({ env: process.env.NODE_ENV || 'development',
      paths: { home: os.homedir(), userData: app.getPath('userData'), temp: app.getPath('temp'), desktop: app.getPath('desktop') },
      features: { devTools: true, autoUpdate: false }
    });
  });
  return { ...mod, get: (key) => key.split('.').reduce((o, k) => o?.[k], store.get()), set: (key, val) => store.update(key, val), getAll: store.get };
};

const Module_Window = () => {
  const mod = Mol_Module('window');
  const store = Mol_Store({ win: null, bounds: { w: 1200, h: 800 } });
  let BrowserWindow;
  mod.onInit(() => { BrowserWindow = require('electron').BrowserWindow; });
  mod.onStart(() => {
    const win = new BrowserWindow({ width: store.get().bounds.w, height: store.get().bounds.h,
      webPreferences: { contextIsolation: true, nodeIntegration: false }, show: false });
    win.once('ready-to-show', () => win.show());
    store.set({ ...store.get(), win });
  });
  mod.onStop(() => { const { win } = store.get(); if (win && !win.isDestroyed()) win.close(); });
  return { ...mod, getWindow: () => store.get().win, loadURL: (url) => store.get().win?.loadURL(url),
    loadFile: (file) => store.get().win?.loadFile(file), openDevTools: () => store.get().win?.webContents.openDevTools() };
};

const Module_IPC = () => {
  const mod = Mol_Module('ipc'); const handlers = new Map(); let ipcMain;
  mod.onInit(() => { ipcMain = require('electron').ipcMain; });
  mod.onStart(() => { handlers.forEach((h, ch) => { ipcMain.handle(ch, async (e, ...a) => { try { return await h(...a); } catch (e) { return { error: e.message }; } }); }); });
  mod.onStop(() => { handlers.forEach((_, ch) => ipcMain.removeHandler(ch)); });
  return { ...mod, register: (ch, h) => handlers.set(ch, h), unregister: (ch) => handlers.delete(ch) };
};

// LAYER 3: CORE
const HKO_HUB_Core = () => {
  const logger = Module_Logger(); const config = Module_Config(); const state = Module_State();
  const window = Module_Window(); const ipc = Module_IPC();
  const modules = new Map([['logger', logger], ['config', config], ['state', state], ['window', window], ['ipc', ipc]]);
  const init = async () => { for (const [n, m] of modules) { await m.init(); logger.info(`[HKO_HUB] Init: ${n}`); } };
  const start = async () => { for (const [n, m] of modules) { await m.start(); logger.info(`[HKO_HUB] Start: ${n}`); state.update(`modules.${n}`, 'running'); } state.update('app.status', 'running'); };
  const stop = async () => { for (const [n, m] of [...modules].reverse()) { await m.stop(); logger.info(`[HKO_HUB] Stop: ${n}`); } };
  return { init, start, stop, getModule: (n) => modules.get(n), getAllModules: () => [...modules] };
};

// LAYER 4: BOOTSTRAP
const HKO_HUB_Bootstrap = async () => {
  console.log('\n╔═══════════════════════════════════════════════════════════╗');
  console.log('║           HKO_HUB CRYSTALLINE v2.0                        ║');
  console.log('╚═══════════════════════════════════════════════════════════╝\n');
  const { app } = require('electron'); const path = require('path'); const core = HKO_HUB_Core();
  app.on('ready', async () => {
    console.log('[Bootstrap] Electron ready');
    try { await core.init(); await core.start(); core.getModule('window').loadFile(path.join(__dirname, 'index.html')); console.log('\n🚀 HKO_HUB IS RUNNING\n'); }
    catch (e) { console.error('[Bootstrap] FATAL:', e); app.quit(); }
  });
  app.on('window-all-closed', () => { if (process.platform !== 'darwin') app.quit(); });
};

if (require.main === module) HKO_HUB_Bootstrap().catch(console.error);
module.exports = { Core: HKO_HUB_Core, Bootstrap: HKO_HUB_Bootstrap,
  Atoms: { State: Atom_State, Event: Atom_Event, Lifecycle: Atom_Lifecycle, Transform: Atom_Transform, Guard: Atom_Guard },
  Molecules: { Store: Mol_Store, Module: Mol_Module, Pipeline: Mol_Pipeline }
};
