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
const shot = async (page, name) => { if (process.env.SHOTS) { await sleep(2900); await page.screenshot({ path: process.env.SHOTS + '/' + name + '.png', fullPage: true }); } };
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
  await nact(p.page, 'noteOpen'); await p.page.fill('[data-nt="text"]', '3號跳預言家\n我覺得是假的');
  await p.page.selectOption('[data-nt="g"][data-p="3"]', '狼人');
  await p.page.focus('[data-nt="text"]'); await act(h.page, 'next'); await sleep(600);
  ok(await p.page.evaluate(() => document.activeElement.tagName === 'TEXTAREA' && document.activeElement.value.includes('3號跳預言家')), '打筆記時裁判推進流程，輸入框不會被重畫打斷');
  ok(JSON.stringify(await state(h.page)).indexOf('跳預言家') < 0 && JSON.stringify(await net(h.page)).indexOf('跳預言家') < 0, '筆記不會送到裁判那邊');
  await p.page.reload(); await p.page.waitForSelector('[data-n="noteOpen"]', { timeout: 20000 });
  ok((await text(p.page)).includes('已記 1 人、有文字'), '重新整理後筆記還在，收起時只顯示摘要');
  await nact(p.page, 'noteOpen');
  ok(await p.page.evaluate(() => document.querySelector('[data-nt="text"]').value.includes('我覺得是假的') && document.querySelector('[data-nt="g"][data-p="3"]').value === '狼人'), '打開後文字和「3號＝狼人」都還在');
  await nact(p.page, 'noteClear'); await nact(p.page, 'noteClear');
  ok(await p.page.evaluate(() => document.querySelector('[data-nt="text"]').value === '' && document.querySelector('[data-nt="g"][data-p="3"]').value === ''), '清空筆記要點兩次，清完是空的');
  await closeAll(h, p);
}

/* ───────── 座位名字不殘留 ───────── */
async function testNames() {
  console.log('\n【座位名字】離開、關房、開新房後不留舊名字');
  const h = await newHost(null);
  const names = async () => (await state(h.page)).players.map(p => p.name).filter(Boolean).join(',');
  let a = await newPlayer(h.code, '阿明'), b = await newPlayer(h.code, '小華'); await sit(a, 1); await sit(b, 2);
  ok(await until(async () => await names() === '阿明,小華', '入座'), '兩人入座，裁判座位表出現名字');
  await nact(a.page, 'leave');
  ok(await until(async () => await names() === '小華', '離開'), '玩家按離開，他的座位名字清掉');
  await act(h.page, 'close'); await act(h.page, 'start');
  await nact(b.page, 'leave');
  ok(await until(async () => await names() === '', '開始後離開'), '遊戲開始後才離開，名字一樣清掉');
  await a.ctx.close();
  // 同一支手機（同一個瀏覽器環境）再加入：先重新入座，再關房開新房
  await b.page.goto(BASE + '?room=' + h.code); await b.page.waitForSelector('#app');
  await act(h.page, 'menu'); await act(h.page, 'endGame').catch(() => {});
  await h.page.evaluate(() => { localStorage.removeItem('wwj-state-v1'); }); await h.page.reload();
  await act(h.page, 'toAssign'); await act(h.page, 'open', 'room');
  await b.page.waitForSelector('[data-n="pseat"]:not([disabled])', { timeout: 25000 }); await sit(b, 3);
  ok(await until(async () => await names() === '小華', '重新入座'), '同一支手機重新入座');
  await nact(h.page, 'hostClose');
  ok(await names() === '', '裁判關閉房間，座位名字全部清掉');
  await h.page.evaluate(() => { const d = JSON.parse(localStorage.getItem('wwj-state-v1')); d.S.players[5].name = '舊名字'; localStorage.setItem('wwj-state-v1', JSON.stringify(d)); }); await h.page.reload();
  await act(h.page, 'open', 'room'); await nact(h.page, 'hostOpen');
  await h.page.waitForFunction(() => /已開啟/.test((document.querySelector('.sheet h2') || {}).innerText || ''), null, { timeout: 20000 });
  ok(await names() === '', '開新房間時，之前殘留在座位上的名字被清空');
  const code2 = (await net(h.page)).code;
  await b.page.goto(BASE + '?room=' + code2); await b.page.waitForSelector('[data-n="pseat"]', { timeout: 25000 });
  ok(await b.page.evaluate(() => [...document.querySelectorAll('[data-n="pseat"] .nm')].every(e => e.innerText === '空位')), '同一支手機加入新房間：所有座位都是空位');
  ok(await b.page.inputValue('#p-nm') === '小華', '名字欄仍記得上次填的名字，方便直接用');
  await closeAll(h, b);
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
  const faceUp = pl => pl.page.evaluate(() => getComputedStyle(document.querySelector('.pinfo')).visibility === 'visible');
  await sleep(10800);
  ok(!(await faceUp(wolf)), '牌翻開 10 秒後自動蓋回');
  ok(await wolf.page.evaluate(() => getComputedStyle(document.querySelector('.stage3d')).touchAction) === 'pan-y', '卡片區域允許上下滑動捲頁面');
  const orient = (b, g) => wolf.page.evaluate(([b, g]) => window.dispatchEvent(Object.assign(new Event('deviceorientation'), { beta: b, gamma: g })), [b, g]);
  const rx = () => wolf.page.evaluate(() => parseFloat((document.querySelector('.c3d').style.transform.match(/rotateX\(([-\d.]+)deg/) || [0, 0])[1]));
  await orient(40, 0); await orient(55, 0);
  ok(await rx() === 0, '晃動連動預設關閉：手機傾斜時卡片不動');
  await wolf.page.click('[data-m="on"]'); await wolf.page.waitForSelector('[data-m="off"]');
  await orient(40, 0); await orient(55, 0); const r1 = await rx();
  ok(r1 !== 0, '開啟後卡片跟著手機傾斜', 'rx=' + r1);
  await wolf.page.click('.stage3d'); await sleep(200); await orient(55, 0); const r2 = await rx();
  ok(Math.abs(r2 - r1) < 0.01, '傾斜狀態下翻面，基準角度不會跑掉', 'before=' + r1 + ' after=' + r2);
  await wolf.page.click('[data-m="off"]'); await wolf.page.waitForSelector('[data-m="on"]'); await orient(70, 20);
  ok(await rx() === 0, '可以關閉晃動連動，關掉後卡片回正且不再跟著動');
  await sleep(10800);
  await gotoStep(h.page, '狼人'); await sleep(500);
  ok(!(await hasPanel(wolf.page)) && await pacts(wolf.page) === 0, '輪到狼人時，狼人手機沒有出現選項');
  ok(!(await text(wolf.page)).includes('夜晚進行中'), '手機不顯示目前輪到哪個角色');
  const victim = S0.players.find(p => p.role === 'villager').id;
  await act(h.page, 'kill', victim); ok((await state(h.page)).nt.kill === victim, '裁判在裁判台點選刀口');
  await gotoStep(h.page, '天亮');
  await seer.page.click('.stage3d'); await until(() => faceUp(seer), '翻開');
  await act(h.page, 'dawn');
  ok(await until(async () => (await text(seer.page)).includes('第 1 天'), '天亮'), '天亮後玩家手機切到「第 1 天」');
  ok(await until(async () => !(await faceUp(seer)), '換階段蓋牌', 3000), '換階段時，翻開的牌馬上蓋回');
  ok(!(await state(h.page)).players[victim - 1].alive, '結算正確：被刀的人出局');
  await witch.page.close(); await sleep(4000);
  ok(!(await h.page.$('.veil.pz')), '現場沒牌：有人離線不會暫停遊戲');
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
  const nextBtn = () => h.page.evaluate(() => { const b = document.querySelector('.foot .btn.pri'); return { dis: b.disabled, t: b.innerText }; });
  await pact(P.merchant.page, seat.vil + '號'); await until(async () => (await state(h.page)).nt.tpid === seat.vil, '只選對象');
  let nb = await nextBtn();
  ok(nb.dis && nb.t.includes('還沒選要給的技能'), '商人只選了對象沒選技能：裁判不能按下一步', JSON.stringify(nb));
  await pact(P.merchant.page, seat.vil + '號'); await until(async () => (await state(h.page)).nt.tpid == null, '取消對象');
  ok(!(await nextBtn()).dis, '取消已選的對象（＝不交易）：可以下一步');
  await pact(P.merchant.page, '查驗'); await until(async () => (await state(h.page)).nt.titem === 'crystal', '只選技能');
  nb = await nextBtn();
  ok(nb.dis && nb.t.includes('還沒選交易對象'), '只選了技能沒選對象：一樣不能下一步', JSON.stringify(nb));
  await pact(P.merchant.page, seat.vil + '號');
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
  await gotoStep(h.page, '獵人'); await act(h.page, 'next');
  ok(await stepName(h.page) === '幸運兒', '還沒交易時，「幸運兒」排在獵人後面');
  const lt = await text(h.page);
  ok(lt.includes(seat.vil + '號') && lt.includes('輕拍') && lt.includes('查驗'), '第一夜的「幸運兒」步驟提示幾號、給什麼技能');
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
  const names = await h.page.evaluate(() => [...document.querySelectorAll('.steps li')].map(e => e.innerText));
  ok(names.filter(x => x === '幸運兒').length === 1 && names.indexOf('幸運兒') < names.indexOf('獵人'), '交易過之後，「幸運兒」只有一個，排在獵人前面', names.join('>'));
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

/* ───────── 斷線與離開 ───────── */
async function testPause() {
  console.log('\n【斷線與離開】線上玩時暫停，房主可以繼續、重開或關閉');
  const h = await newHost(HEI); await nact(h.page, 'mode', 'online'); await act(h.page, 'close'); await act(h.page, 'deal');
  const S0 = await state(h.page), seatOf = r => S0.players.find(p => p.role === r).id;
  const wolf = await newPlayer(h.code, '狼'), seer = await newPlayer(h.code, '預');
  await sit(wolf, seatOf('wolf')); await sit(seer, seatOf('seer'));
  await act(h.page, 'start'); await until(() => seer.page.$('.cf.av-seer'), '收到牌');
  await gotoStep(h.page, '狼人'); await until(() => hasPanel(wolf.page), '狼人面板');
  const paused = () => h.page.$('.veil.pz'), ptext = () => h.page.evaluate(() => (document.querySelector('.veil.pz') || {}).innerText || '');
  ok(!(await paused()), '大家都在線時沒有暫停');

  await seer.page.close();
  ok(await until(paused, '暫停畫面', 20000), '玩家斷線，裁判台跳出「遊戲暫停」');
  const pt = await ptext();
  ok(pt.includes(seer.seat + '號') && pt.includes('斷線'), '暫停畫面指出是幾號斷線');
  ok(pt.includes('繼續遊戲') && pt.includes('重開房間') && pt.includes('關閉房間') && pt.includes(h.code), '暫停畫面有繼續、重開、關閉三個選項，並顯示房號');
  ok(await until(async () => (await text(wolf.page)).includes('遊戲暫停'), '玩家端暫停'), '其他玩家的手機顯示遊戲暫停');
  ok(!(await hasPanel(wolf.page)), '暫停期間玩家手機上的選項收起來');
  seer.page = await seer.ctx.newPage(); await seer.page.goto(BASE);
  ok(await until(async () => !(await paused()), '自動繼續', 25000), '斷線的人重新連上，自動繼續');
  ok(await until(() => hasPanel(wolf.page), '面板回來'), '繼續後玩家的選項回來');

  await nact(seer.page, 'leave');
  ok(await until(async () => (await ptext()).includes('離開了房間'), '離開暫停', 10000), '玩家按離開，裁判台暫停並標示他離開了');
  await seer.page.goto(BASE + '?room=' + h.code);
  ok(await until(() => seer.page.$('[data-n="pseat"][data-p="' + seer.seat + '"]:not([disabled])'), '座位開放', 25000), '離開的人用房號再加入，原本的座位開放給他');
  ok(await seer.page.evaluate(n => [...document.querySelectorAll('[data-n="pseat"]')].filter(e => !e.disabled).length === 1 && n, seer.seat), '其他座位仍然鎖住');
  await nact(seer.page, 'pseat', seer.seat);
  ok(await until(async () => !(await paused()), '坐回後繼續', 10000), '坐回原位後自動繼續');
  ok(await until(() => seer.page.$('.cf.av-seer'), '牌回來'), '坐回去的人重新看到自己的牌');

  await wolf.page.close(); await until(paused, '再次暫停', 20000);
  await nact(h.page, 'pzGo');
  ok(await until(async () => !(await paused()), '房主繼續'), '房主按「不等了，繼續遊戲」，暫停解除');
  ok(await until(async () => !(await text(seer.page)).includes('遊戲暫停'), '玩家端解除'), '玩家手機上的暫停也解除');
  await act(h.page, 'kill', seatOf('villager'));
  ok((await state(h.page)).nt.kill === seatOf('villager'), '缺席玩家的選擇由裁判代選');
  wolf.page = await wolf.ctx.newPage(); await wolf.page.goto(BASE);
  ok(await until(() => hasPanel(wolf.page), '回來', 25000), '缺席的人之後連回來，照常繼續');

  await seer.page.close(); await until(paused, '第三次暫停', 20000);
  await nact(h.page, 'pzReopen');
  await h.page.waitForFunction(() => /已開啟|^$/.test(''), null, { timeout: 1000 }).catch(() => {});
  // 預言家還沒回來，所以仍在暫停；按繼續後狼人的選項有回來，才能證明狼人已經接上重開後的房間
  await sleep(6000); await nact(h.page, 'pzGo').catch(() => {});
  ok(await until(async () => (await net(h.page)).code === h.code && await hasPanel(wolf.page), '重開', 40000), '房主按「重開房間」：房號不變，在線的人自動接回');
  await wolf.page.close(); await until(paused, '第四次暫停', 20000);
  await h.page.evaluate(() => document.querySelector('.veil.pz [data-n="hostClose"]').click());
  ok((await net(h.page)).mode == null && !(await paused()), '在暫停畫面按「關閉房間」：房間關閉，暫停畫面消失');
  wolf.page = await wolf.ctx.newPage(); await wolf.page.goto(BASE);
  ok(await until(async () => (await text(wolf.page)).includes('找不到房間'), '玩家端', 30000), '房間關閉後，玩家手機顯示找不到房間');
  await closeAll(h, wolf, seer);
}

/* ───────── 投票：警長與放逐 ───────── */
async function testVote() {
  console.log('\n【投票】玩家用手機投警長、投放逐，裁判即時看票再結算');
  const h = await newHost(HEI, { sheriff: true }); await nact(h.page, 'mode', 'phone'); await act(h.page, 'close'); await act(h.page, 'deal');
  const S0 = await state(h.page), ids = r => S0.players.filter(p => p.role === r).map(p => p.id);
  const [v1, v2] = ids('villager'), X = ids('hunter')[0];
  const A = await newPlayer(h.code, '甲'), B = await newPlayer(h.code, '乙'), C = await newPlayer(h.code, '丙'), D = await newPlayer(h.code, '丁');
  await sit(A, ids('wolf')[0]); await sit(B, ids('seer')[0]); await sit(C, ids('witch')[0]); await sit(D, v1);
  await act(h.page, 'start'); await gotoStep(h.page, '狼人'); await act(h.page, 'kill', v1); await gotoStep(h.page, '天亮'); await act(h.page, 'dawn');
  const vote = async () => (await state(h.page)).vote, ht = () => text(h.page);
  ok(await until(async () => (await text(D.page)).includes('第 1 天'), '天亮'), '天亮');
  ok(!(await state(h.page)).players[v1 - 1].alive && !(await text(D.page)).includes('你已出局'), '警長競選還沒結束：昨夜死的人手機先不顯示出局');
  ok((await ht()).includes('準備手機投票') && (await ht()).includes('請大家繼續閉眼'), '裁判台出現警長競選：先閉眼舉手');
  await act(h.page, 'voteSetup');
  await shot(h.page, '0-day-elect-setup-empty');
  ok(await h.page.evaluate(() => document.querySelector('[data-a="voteStart"]').disabled), '還沒選上警的人：不能開始投票');
  await act(h.page, 'voteCand', A.seat); await act(h.page, 'voteCand', X);
  ok((await ht()).includes('請放下手。天亮了，請睜眼。上警的玩家是'), '記完舉手的人，才出現「請睜眼」的台詞並念出上警名單');
  await shot(h.page, '1-setup');
  await nact(C.page, 'noteOpen'); await C.page.fill('[data-nt="text"]', '記一下'); await C.page.focus('[data-nt="text"]');
  await act(h.page, 'voteStart', 'sheriff');
  let V = await vote();
  ok(V.stage === 'open' && V.cand.join() === [A.seat, X].sort((a, b) => a - b).join() && V.voters.length === 10 && V.voters.includes(v1), '開票：兩位候選人，其餘十人（含昨夜死者）可投');
  ok(await until(() => hasPanel(B.page), '投票面板'), '沒上警的玩家手機跳出投票面板');
  ok(await until(() => hasPanel(C.page), '打字中的面板'), '正在打筆記的玩家，輪到投票時面板照樣跳出來');
  await shot(C.page, '12-notes');
  ok(await pacts(B.page) === 3, '選項是兩位候選人加棄票');
  ok(await until(async () => (await text(A.page)).includes('你上警了'), '候選人提示') && await pacts(A.page) === 0, '上警的玩家看到提示、沒有投票選項');
  await pact(B.page, A.seat + '號');
  ok(await until(async () => (await vote()).v[B.seat] === A.seat, '乙的票'), '玩家投票即時出現在裁判台資料');
  ok(await until(async () => (await ht()).includes('已投 1／10'), '票數'), '裁判畫面即時顯示已投人數');
  ok(!(await text(C.page)).includes(B.seat + '號：') && !(await text(C.page)).includes('1 票'), '結算前其他玩家看不到票況');
  await pact(C.page, X + '號'); await until(async () => (await vote()).v[C.seat] === X, '丙的票');
  await pact(C.page, A.seat + '號');
  ok(await until(async () => (await vote()).v[C.seat] === A.seat, '改票'), '結算前可以改票');
  await pact(D.page, '棄票');
  ok(await until(async () => (await vote()).v[D.seat] === 0, '棄票'), '昨夜死者也能投（這裡投棄票）');
  await h.page.selectOption('[data-c="vproxy"][data-p="' + v2 + '"]', String(X));
  ok((await vote()).v[v2] === X && (await ht()).includes('已投 4／10'), '裁判可以替沒連線的人代投');
  await shot(h.page, '2-open-judge'); await shot(B.page, '3-open-player'); await shot(A.page, '4-open-candidate');
  await act(h.page, 'voteEnd');
  ok((await vote()).stage === 'done' && (await ht()).includes('結果：' + A.seat + '號 當選警長'), '結算：兩票對一票，顯示當選者');
  ok(await until(async () => { const t = await text(B.page); return t.includes('警長投票結果') && t.includes(A.seat + '號：2 票') && t.includes('當選警長'); }, '公開結果'), '結算後票況公開到玩家手機');
  ok(!(await hasPanel(B.page)), '結算後投票面板收起');
  await shot(h.page, '5-done-judge'); await shot(B.page, '6-done-player');
  ok((await state(h.page)).sheriff == null, '裁判確認前還沒真的記錄警長');
  await act(h.page, 'voteApply');
  ok((await state(h.page)).sheriff === A.seat && (await state(h.page)).vote == null, '確認後記錄警長');
  await act(h.page, 'voteStart', 'exile'); await act(h.page, 'pickOpen', 'boom'); await act(h.page, 'pickCancel');
  ok((await vote()).stage === 'open', '投票中點自爆再取消：投票還在');
  await act(h.page, 'voteCancel');
  ok((await vote()) == null && (await ht()).includes('開始放逐投票'), '取消投票回到白天畫面');
  ok(await until(async () => (await text(D.page)).includes('你已出局'), '出局'), '競選結束後，昨夜死者手機才顯示出局');

  await shot(h.page, '7-day-after-sheriff');
  console.log('  — 放逐投票與平票重投');
  await act(h.page, 'voteStart', 'exile'); V = await vote();
  ok(V.cand.length === 11 && !V.voters.includes(v1), '放逐投票：活著的十一人可投，死者不能投');
  ok(await until(() => hasPanel(B.page), '放逐面板') && !(await hasPanel(D.page)), '活人手機跳出放逐投票，死者沒有');
  await pact(B.page, C.seat + '號'); await pact(C.page, B.seat + '號'); await pact(A.page, '棄票');
  await until(async () => Object.keys((await vote()).v).length === 3, '三票');
  await act(h.page, 'voteEnd');
  ok((await ht()).includes('平票'), '一比一：結算顯示平票');
  await shot(h.page, '8-tie-judge');
  await act(h.page, 'votePk'); V = await vote();
  ok(V.pk === 1 && V.cand.length === 2 && !V.voters.includes(B.seat) && !V.voters.includes(C.seat) && V.voters.length === 9, '平票重投：只剩平票兩人當候選，他們自己不投');
  ok(await until(async () => (await text(B.page)).includes('平票名單'), '平票提示') && await pacts(B.page) === 0, '平票的人手機顯示不投票');
  ok(await until(async () => await pacts(A.page) === 3, '警長面板') && (await text(A.page)).includes('1.5 票'), '警長的投票面板註明 1.5 票');
  await pact(A.page, B.seat + '號'); await until(async () => (await vote()).v[A.seat] === B.seat, '警長票');
  await h.page.selectOption('[data-c="vproxy"][data-p="' + v2 + '"]', String(C.seat));
  await shot(h.page, '9-pk-open-judge'); await shot(A.page, '10-pk-sheriff-player');
  await act(h.page, 'voteEnd');
  ok((await ht()).includes(B.seat + '號 得票最高') && (await ht()).includes('1.5 票'), '警長 1.5 票勝過一般的一票');
  await act(h.page, 'voteApply');
  const S1 = await state(h.page);
  ok(S1.exiled === B.seat && !S1.players[B.seat - 1].alive && S1.vote == null, '確認後放逐得票最高的人');
  ok(await until(async () => (await text(B.page)).includes('你已出局'), '被放逐者'), '被放逐的玩家手機顯示出局');
  ok((await text(C.page)).includes('結果：' + B.seat + '號 被放逐'), '確認後玩家手機上的結果改成「被放逐」');
  await act(h.page, 'undo');
  ok((await state(h.page)).players[B.seat - 1].alive && (await vote()).stage === 'done', '復原一步：回到結算畫面，票還在');
  await act(h.page, 'voteApply');
  await shot(h.page, '11-day-after-exile');
  await act(h.page, 'toNight');
  ok(await until(async () => !(await text(C.page)).includes('投票結果'), '清結果'), '進入夜晚後，玩家手機上的投票結果收起');
  const ct = await text(C.page);
  ok(ct.includes('票型紀錄') && ct.includes('第 1 天 警長投票') && ct.includes('第 1 天 放逐投票（平票重投）') && ct.includes(B.seat + '號：1.5 票') && ct.includes(C.seat + '號：1 票（' + B.seat + '號）'), '進入夜晚後，玩家手機仍看得到當天每一輪的票型（含平票前那一輪）', ct.slice(-400));
  ok((await text(D.page)).includes('票型紀錄'), '出局的玩家也看得到票型紀錄');
  await act(h.page, 'menu'); await act(h.page, 'end');
  ok(await until(async () => { const t = await text(D.page); return t.includes('身份公布') && t.includes('流程紀錄'); }, '結束畫面'), '裁判結束遊戲後，玩家手機出現身份公布和流程紀錄');
  const et = await text(D.page), chips = await D.page.evaluate(() => [...document.querySelectorAll('.board .chip')].map(e => e.innerText.replace(/\s+/g, ' ')));
  ok(chips.length === 12 && S0.players.every((p, i) => chips[i].includes(String(p.id))) && chips[ids('seer')[0] - 1].includes('預言家') && chips[ids('wolfbro')[0] - 1].includes('狼兄'), '十二個座位的身份全部翻開，和裁判台一致', chips.join(' / '));
  ok(et.includes('第 1 夜') && et.includes('狼人襲擊 ' + v1 + '號') && et.includes('當選警長') && et.includes('放逐投票'), '流程紀錄含夜晚行動、警長與投票', et.slice(0, 300));
  ok(await D.page.evaluate(() => document.querySelectorAll('.board .chip.dead').length) === 2, '出局的兩人在身份公布上劃掉');
  await shot(D.page, '13-end-player');
  await closeAll(h, A, B, C, D);
}

const only = process.argv[2];
try {
  if (!only || only === 'cards') await testCards();
  if (!only || only === 'names') await testNames();
  if (!only || only === 'phone') await testPhone();
  if (!only || only === 'online') await testOnline();
  if (!only || only === 'vote') await testVote();
  if (!only || only === 'pause') await testPause();
} catch (e) { fail++; fails.push('測試中斷：' + e.message); console.log('\n✗ 測試中斷：' + e.message); }
await browser.close(); server.close();
console.log(`\n結果：${pass} 項通過，${fail} 項失敗`); if (fail) { console.log('失敗項目：\n - ' + fails.join('\n - ')); process.exit(1); }
