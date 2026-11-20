// 無頭瀏覽器端對端測試：一個裁判＋多個玩家，實際透過 PeerJS 連線，把三種玩法各跑一輪。
// 用法：cd tools/e2e && npm install && node run.mjs      （加 HEADED=1 可以看畫面）
import { chromium } from 'playwright-core';
import http from 'node:http';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const server = http.createServer((req, res) => {
  res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
  res.end(readFileSync(path.join(ROOT, 'index.html')));
}).listen(0, '127.0.0.1');
await new Promise(r => server.once('listening', r));
const BASE = `http://127.0.0.1:${server.address().port}/`;

const browser = await chromium.launch({ channel: 'chrome', headless: !process.env.HEADED });
let pass = 0, fail = 0; const fails = [];
const ok = (cond, name, extra = '') => { if (cond) { pass++; console.log('  ✓ ' + name); } else { fail++; fails.push(name); console.log('  ✗ ' + name + (extra ? '  → ' + extra : '')); } };
const sleep = ms => new Promise(r => setTimeout(r, ms));

const state = page => page.evaluate(() => JSON.parse(localStorage.getItem('wwj-state-v1')).S);
const net = page => page.evaluate(() => JSON.parse(localStorage.getItem('wwj-net-v1')));
const text = page => page.evaluate(() => document.querySelector('#app').innerText.replace(/\n+/g, ' | '));
const act = (page, a, p) => page.evaluate(([a, p]) => {
  const e = [...document.querySelectorAll('[data-a="' + a + '"]')].find(e => p == null || e.dataset.p === String(p));
  if (!e) throw new Error('找不到按鈕 ' + a + ':' + p + ' @ ' + document.querySelector('#app').innerText.slice(0, 160));
  if (e.disabled) throw new Error('按鈕停用中 ' + a + ':' + p); e.click();
}, [a, p]);
const nact = (page, a, p) => page.evaluate(([a, p]) => {
  const e = [...document.querySelectorAll('[data-n="' + a + '"]')].find(e => p == null || e.dataset.p === String(p));
  if (!e) throw new Error('找不到按鈕 n:' + a + ':' + p + ' @ ' + document.querySelector('#app').innerText.slice(0, 160)); e.click();
}, [a, p]);
const stepName = page => page.evaluate(() => (document.querySelector('.steps li.on') || {}).innerText || '');
/** 裁判一路按下一步，直到停在指定步驟 */
async function gotoStep(host, name) { for (let i = 0; i < 14; i++) { if (await stepName(host) === name) return; await act(host, 'next'); } throw new Error('走不到步驟 ' + name); }
/** 玩家在行動面板點一個選項（用文字找） */
const pact = (page, label) => page.evaluate(label => {
  const e = [...document.querySelectorAll('[data-n="pact"]')].find(e => e.innerText.includes(label));
  if (!e) throw new Error('玩家畫面沒有選項「' + label + '」 @ ' + document.querySelector('#app').innerText.slice(0, 200));
  if (e.disabled) throw new Error('選項停用中「' + label + '」'); e.click();
}, label);
const hasPanel = page => page.evaluate(() => !!document.querySelector('.actc'));
const pacts = page => page.evaluate(() => document.querySelectorAll('[data-n="pact"]').length);
const until = async (fn, what, ms = 8000) => { const t = Date.now(); for (;;) { try { if (await fn()) return true; } catch (e) {} if (Date.now() - t > ms) { console.log('    （等不到：' + what + '）'); return false; } await sleep(120); } };

async function newHost(board, { sheriff = false } = {}) {
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 } }); const page = await ctx.newPage();
  page.on('pageerror', e => { fail++; fails.push('裁判頁面錯誤：' + e.message); console.log('  ✗ 裁判頁面錯誤：' + e.message); });
  await page.goto(BASE);
  if (board != null) await act(page, 'board', board);
  if (!sheriff) await page.selectOption('#r-sheriff', 'false');
  await act(page, 'toAssign'); await act(page, 'open', 'room'); await nact(page, 'hostOpen');
  await page.waitForFunction(() => /已開啟/.test((document.querySelector('.sheet h2') || {}).innerText || ''), null, { timeout: 20000 });
  return { ctx, page, code: (await net(page)).code };
}
async function newPlayer(code, name) {
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 } }); const page = await ctx.newPage();
  page.on('pageerror', e => { fail++; fails.push(name + ' 頁面錯誤：' + e.message); console.log('  ✗ ' + name + ' 頁面錯誤：' + e.message); });
  await page.goto(BASE + '?room=' + code);
  await page.waitForSelector('[data-n="pseat"]', { timeout: 20000 });
  await page.fill('#p-nm', name); await page.dispatchEvent('#p-nm', 'change');
  return { ctx, page, name };
}
const sit = async (pl, seat) => { await nact(pl.page, 'pseat', seat); await pl.page.waitForFunction(s => document.querySelector('#app').innerText.includes('你是 ' + s + '號'), seat, { timeout: 8000 }); pl.seat = seat; };
const closeAll = async (...xs) => { for (const x of xs) await x.ctx.close(); };
const HEI = 5; // 板子：黑商狼兄弟・預女獵黑（12 人）

/* ───────── 1. 現場有牌 ───────── */
async function testCards() {
  console.log('\n【現場有牌】手機只顯示階段，不顯示身份');
  const h = await newHost(null); await nact(h.page, 'mode', 'cards'); await act(h.page, 'close');
  const p = await newPlayer(h.code, '小明'); await sit(p, 1);
  ok((await state(h.page)).players[0].name === '小明', '玩家入座後，裁判座位表出現名字');
  await act(h.page, 'start');
  ok(await until(async () => (await text(p.page)).includes('第 1 夜'), '玩家看到第 1 夜'), '裁判開始後，玩家手機顯示「第 1 夜」');
  const t = await text(p.page);
  ok(t.includes('實體牌'), '玩家手機提示這局用實體牌');
  ok(!(await p.page.$('.c3d')), '玩家手機沒有牌卡');
  ok(await pacts(p.page) === 0 && !(await hasPanel(p.page)), '玩家手機沒有任何選項');
  await closeAll(h, p);
}

/* ───────── 2. 現場沒牌 ───────── */
async function testPhone() {
  console.log('\n【現場沒牌】手機看牌、跟著階段走，不顯示選項');
  const h = await newHost(HEI); await nact(h.page, 'mode', 'phone'); await act(h.page, 'close'); await act(h.page, 'deal');
  const S0 = await state(h.page), seatOf = r => S0.players.find(p => p.role === r).id;
  const wolf = await newPlayer(h.code, '狼'), seer = await newPlayer(h.code, '預'), witch = await newPlayer(h.code, '巫');
  await sit(wolf, seatOf('wolf')); await sit(seer, seatOf('seer')); await sit(witch, seatOf('witch'));
  ok(!(await wolf.page.$('.c3d')), '開始前玩家還看不到牌');
  await act(h.page, 'start');
  for (const [pl, role] of [[wolf, 'wolf'], [seer, 'seer'], [witch, 'witch']])
    ok(await until(() => pl.page.$('.cf.av-' + role), pl.name + ' 的牌'), '開始第一夜後，' + pl.name + ' 的手機自動收到正確的牌（' + role + '）');
  ok(await wolf.page.evaluate(() => getComputedStyle(document.querySelector('.pinfo')).visibility) === 'hidden', '牌預設背面朝上，角色說明隱藏');
  await wolf.page.click('.stage3d');
  ok(await until(() => wolf.page.evaluate(() => getComputedStyle(document.querySelector('.pinfo')).visibility === 'visible'), '翻面'), '點一下卡片翻到正面，顯示角色說明');
  await gotoStep(h.page, '狼人'); await sleep(500);
  ok(!(await hasPanel(wolf.page)) && await pacts(wolf.page) === 0, '輪到狼人時，狼人手機沒有出現選項');
  ok(!(await text(wolf.page)).includes('夜晚進行中'), '手機不顯示目前輪到哪個角色');
  const victim = S0.players.find(p => p.role === 'villager').id;
  await act(h.page, 'kill', victim); ok((await state(h.page)).nt.kill === victim, '裁判在裁判台點選刀口');
  await gotoStep(h.page, '天亮'); await act(h.page, 'dawn');
  ok(await until(async () => (await text(seer.page)).includes('第 1 天'), '天亮'), '天亮後玩家手機切到「第 1 天」');
  ok(!(await state(h.page)).players[victim - 1].alive, '結算正確：被刀的人出局');
  await closeAll(h, wolf, seer, witch);
}

/* ───────── 3. 線上玩 ───────── */
async function testOnline() {
  console.log('\n【線上玩】輪到的人在手機上選，結果回到裁判台');
  const h = await newHost(HEI); await nact(h.page, 'mode', 'online'); await act(h.page, 'close'); await act(h.page, 'deal');
  const S0 = await state(h.page), ids = r => S0.players.filter(p => p.role === r).map(p => p.id);
  const [w1, w2] = ids('wolf'), [v1, v2] = ids('villager');
  const seat = { wolf: w1, bro: ids('wolfbro')[0], yb: ids('wolfyb')[0], seer: ids('seer')[0], witch: ids('witch')[0], hunter: ids('hunter')[0], merchant: ids('merchant')[0], vil: v1 };
  const P = {}; for (const k of Object.keys(seat)) { P[k] = await newPlayer(h.code, k); await sit(P[k], seat[k]); }
  ok(Object.keys((await net(h.page)).seats).length === 8, '八位玩家都入座');
  await act(h.page, 'start');
  ok(await until(() => P.seer.page.$('.cf.av-seer'), '收到牌'), '開始後玩家收到自己的牌');

  console.log('  — 第 1 夜');
  await gotoStep(h.page, '兄弟');
  ok(await until(async () => (await text(P.bro.page)).includes('你的兄弟是 ' + seat.yb + '號'), '兄弟互認'), '狼兄手機顯示兄弟是幾號');
  ok((await text(P.yb.page)).includes('你的兄弟是 ' + seat.bro + '號'), '狼弟手機顯示兄弟是幾號');
  ok(!(await hasPanel(P.seer.page)) && (await text(P.seer.page)).includes('夜晚進行中'), '沒輪到的人只看到「夜晚進行中」');

  await gotoStep(h.page, '狼人');
  ok(await until(() => hasPanel(P.wolf.page), '狼人面板'), '狼人手機跳出行動面板');
  const wt = await text(P.wolf.page);
  ok(wt.includes('狼隊友') && wt.includes(w2 + '號') && wt.includes(seat.bro + '號') && !wt.split('狼隊友')[1].split('|')[0].includes(seat.yb + '號'), '狼人看到隊友（含狼兄，不含未覺醒的狼弟）');
  ok(!(await hasPanel(P.yb.page)), '未覺醒的狼弟沒有行動面板');
  ok(!(await hasPanel(P.witch.page)), '女巫此時看不到狼人的選項');
  await pact(P.wolf.page, v2 + '號');
  ok(await until(async () => (await state(h.page)).nt.kill === v2, '刀口'), '狼人選的刀口出現在裁判台');
  await pact(P.bro.page, seat.vil + '號');
  ok(await until(async () => (await state(h.page)).nt.kill === seat.vil, '改刀口'), '狼兄改刀口，以最後選的為準');
  await pact(P.wolf.page, v2 + '號'); await until(async () => (await state(h.page)).nt.kill === v2, '刀口改回');

  await gotoStep(h.page, '商人');
  ok(await until(() => hasPanel(P.merchant.page), '商人面板'), '黑市商人手機跳出行動面板');
  await pact(P.merchant.page, '查驗'); await pact(P.merchant.page, seat.vil + '號');
  ok(await until(async () => { const n = (await state(h.page)).nt; return n.titem === 'crystal' && n.tpid === seat.vil; }, '交易'), '商人選的技能和對象出現在裁判台');

  await gotoStep(h.page, '女巫');
  ok(await until(async () => (await text(P.witch.page)).includes('今晚 ' + v2 + '號 被襲擊'), '女巫資訊'), '女巫手機顯示今晚誰被襲擊');
  await pact(P.witch.page, '用解藥救');
  ok(await until(async () => (await state(h.page)).nt.save === v2, '解藥'), '女巫用解藥，裁判台收到');

  await gotoStep(h.page, '預言家');
  await until(() => hasPanel(P.seer.page), '預言家面板');
  await pact(P.seer.page, seat.yb + '號'); await sleep(300);
  ok((await state(h.page)).nt.check == null && (await text(P.seer.page)).includes('再點一次確認'), '預言家第一次點只是預選，要再點一次確認');
  await pact(P.seer.page, seat.yb + '號');
  ok(await until(async () => (await text(P.seer.page)).includes(seat.yb + '號是好人'), '查驗結果'), '預言家查驗未覺醒的狼弟：顯示好人');
  ok(await P.seer.page.evaluate(() => [...document.querySelectorAll('[data-n="pact"]')].every(e => e.disabled)), '查驗確認後選項鎖住，不能再驗別人');
  ok(!(await text(P.wolf.page)).includes('是好人'), '查驗結果只有預言家看得到');

  await gotoStep(h.page, '獵人');
  ok(await until(async () => (await text(P.hunter.page)).includes('可以開槍'), '獵人狀態'), '獵人手機顯示「可以開槍」');
  await gotoStep(h.page, '天亮'); await act(h.page, 'dawn');
  let S = await state(h.page);
  ok(S.phase === 'day' && S.players.every(p => p.alive), '第 1 夜結算：解藥救回，平安夜');
  ok(S.lucky && S.lucky.pid === seat.vil && S.lucky.item === 'crystal', '交易成立：平民成為幸運兒，持有查驗');
  ok(await until(async () => (await text(P.vil.page)).includes('你是幸運兒'), '幸運兒通知'), '幸運兒的手機收到通知');
  ok(!(await text(P.wolf.page)).includes('幸運兒'), '其他人不知道誰是幸運兒');

  console.log('  — 第 1 天：放逐狼兄');
  await act(h.page, 'pickOpen', 'exile'); await act(h.page, 'pickdo', seat.bro);
  S = await state(h.page);
  ok(!S.players[seat.bro - 1].alive && !!S.yb, '狼兄出局，狼弟覺醒');
  ok(await until(() => P.yb.page.$('.cf.av-wolfyb2'), '覺醒卡'), '狼弟手機上的牌換成覺醒版');
  ok(await until(async () => (await text(P.bro.page)).includes('你已出局'), '出局提示'), '狼兄手機顯示「你已出局」');
  await act(h.page, 'toNight');

  console.log('  — 第 2 夜');
  await gotoStep(h.page, '狼人');
  ok(await until(async () => (await text(P.yb.page)).includes('狼弟的額外一刀'), '額外刀口'), '覺醒的狼弟手機出現「額外一刀」');
  ok(!(await hasPanel(P.bro.page)), '已出局的狼兄沒有行動面板');
  await pact(P.wolf.page, v2 + '號'); await until(async () => (await state(h.page)).nt.kill === v2, '刀口');
  await gotoStep(h.page, '商人');
  ok(await until(async () => (await text(P.merchant.page)).includes('已經交易過了'), '商人'), '商人手機顯示已交易過，沒有選項') ;
  ok(await pacts(P.merchant.page) === 0, '已交易的商人沒有可點的選項');
  await gotoStep(h.page, '女巫');
  ok(await until(async () => (await text(P.witch.page)).includes('解藥已用完'), '女巫'), '解藥用掉後，女巫不再知道誰被襲擊');
  ok(!/今晚 \d+號/.test(await text(P.witch.page)) && !(await P.witch.page.$('.actc .big')), '女巫畫面沒有透露刀口');
  await pact(P.witch.page, seat.wolf + '號');
  ok(await until(async () => (await state(h.page)).nt.poison === seat.wolf, '毒'), '女巫下毒，裁判台收到');
  await gotoStep(h.page, '預言家'); await until(() => hasPanel(P.seer.page), '預言家面板');
  await pact(P.seer.page, seat.yb + '號'); await pact(P.seer.page, seat.yb + '號');
  ok(await until(async () => (await text(P.seer.page)).includes(seat.yb + '號是狼人'), '查驗'), '狼弟覺醒後，預言家查驗他：顯示狼人');
  await gotoStep(h.page, '幸運兒');
  ok(await until(() => hasPanel(P.vil.page), '幸運兒面板'), '幸運兒手機跳出行動面板');
  ok(!(await hasPanel(P.seer.page)), '幸運兒階段，預言家沒有面板');
  await pact(P.vil.page, seat.merchant + '號'); await pact(P.vil.page, seat.merchant + '號');
  ok(await until(async () => (await text(P.vil.page)).includes(seat.merchant + '號是好人'), '幸運兒查驗'), '幸運兒用交易來的查驗，看到結果');
  await gotoStep(h.page, '獵人');
  ok(await until(async () => (await text(P.hunter.page)).includes('可以開槍'), '獵人'), '獵人排在最後，顯示開槍狀態');
  await gotoStep(h.page, '天亮'); await act(h.page, 'dawn');
  S = await state(h.page);
  ok(!S.players[v2 - 1].alive && !S.players[seat.wolf - 1].alive && S.players[seat.wolf - 1].death.c === '毒殺', '第 2 夜結算：被刀的平民、被毒的狼人出局');

  console.log('  — 第 2 天：放逐獵人，獵人在手機上開槍');
  await act(h.page, 'pickOpen', 'exile'); await act(h.page, 'pickdo', seat.hunter);
  ok(await until(async () => (await text(P.hunter.page)).includes('開槍帶走誰'), '開槍面板'), '獵人手機出現開槍選項');
  await pact(P.hunter.page, seat.yb + '號');
  ok(await until(async () => { const s = await state(h.page); return !s.players[seat.yb - 1].alive && s.players[seat.yb - 1].death.c === '獵人開槍'; }, '開槍結果'), '獵人選人後，裁判台記錄「獵人開槍」');
  ok(await until(async () => !(await hasPanel(P.hunter.page)), '面板消失'), '開槍後選項消失');

  console.log('  — 斷線重連');
  await h.page.reload();
  ok(await until(async () => (await text(P.seer.page)).includes('第 2 天') && !(await text(P.seer.page)).includes('重新連線'), '重連', 25000), '裁判重新整理後，玩家自動接回');
  await P.seer.page.reload();
  ok(await until(() => P.seer.page.$('.cf.av-seer'), '玩家重連', 25000), '玩家重新整理後，接回原座位並看到自己的牌');
  await closeAll(h, ...Object.values(P));
}

const only = process.argv[2];
try {
  if (!only || only === 'cards') await testCards();
  if (!only || only === 'phone') await testPhone();
  if (!only || only === 'online') await testOnline();
} catch (e) { fail++; fails.push('測試中斷：' + e.message); console.log('\n✗ 測試中斷：' + e.message); }
await browser.close(); server.close();
console.log(`\n結果：${pass} 項通過，${fail} 項失敗`); if (fail) { console.log('失敗項目：\n - ' + fails.join('\n - ')); process.exit(1); }
