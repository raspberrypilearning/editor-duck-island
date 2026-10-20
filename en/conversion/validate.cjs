/* Runtime checks in the real Scratch VM, WebGL renderer, and audio engine.
 * Install tools outside the repository (see en/conversion/README.md).
 * node en/conversion/validate.cjs
 */
const fs = require("fs");
const path = require("path");
const http = require("http");
const assert = require("assert/strict");
const toolRoot = process.env.DUCK_TEST_TOOLS || "/private/tmp/duck-island-tools";
const {chromium} = require(path.join(toolRoot, "node_modules/playwright"));
const root = path.resolve(__dirname, "../..");
const checkpointRoot = "/private/tmp/editor-duck-island-checkpoints";
const report = {checks: [], errors: []};
const library = {
  "/vm.js": "node_modules/scratch-vm/dist/web/scratch-vm.js",
  "/render.js": "node_modules/scratch-render/dist/web/scratch-render.js",
  "/storage.js": "node_modules/scratch-storage/dist/web/scratch-storage.js",
  "/audio.js": "audio.js",
  "/svg.js": "node_modules/scratch-svg-renderer/dist/web/scratch-svg-renderer.js",
  "/blocks.js": "node_modules/scratchblocks/build/scratchblocks.min.js",
};
const html = `<!doctype html><meta charset="utf-8">
<style>body{margin:0;background:#e4f3f7;font:16px system-ui}canvas{width:960px;height:720px}
#monitors{position:absolute;left:10px;top:10px;display:flex;gap:8px}
.value{background:#ff8c1a;color:white;padding:5px 12px;border-radius:8px}</style>
<canvas id="stage" width="960" height="720"></canvas><div id="monitors"></div>
<script src="/render.js"></script><script src="/storage.js"></script>
<script src="/audio.js"></script><script src="/svg.js"></script><script src="/vm.js"></script><script src="/blocks.js"></script>
<script>
window.vm = new VirtualMachine();
vm.attachStorage(new (ScratchStorage.ScratchStorage || ScratchStorage.default || ScratchStorage)());
vm.attachRenderer(new (ScratchRender.default || ScratchRender)(document.querySelector('canvas')));
vm.attachAudioEngine(new (ScratchAudio.default || ScratchAudio)());
vm.attachV2BitmapAdapter(new ScratchSVGRenderer.BitmapAdapter());
vm.renderer.resize(960,720);
vm.runtime.currentStepTime = 1000/30;
window.soundPlays=[];
for(const op of ['sound_play','sound_playuntildone']){
 const original=vm.runtime._primitives[op];
 vm.runtime._primitives[op]=(args,util)=>{
  soundPlays.push({opcode:op,target:util.target.getName(),sound:args.SOUND_MENU});
  return original(args,util);
 };
}
window.now = Date.now();
Date.now = () => window.now;
// CPU work budgets must advance even while simulated game time is paused.
vm.runtime.sequencer.timer.nowObj = performance;
window.tick = async (n=1) => {
 for(let i=0;i<n;i++){
  window.now+=1000/30;
  vm.runtime._step();
  if(i%10===0) await new Promise(r=>setTimeout(r,0));
 }
 vm.renderer.draw();
};
window.load = async (url) => {
 vm.stopAll();
 for(const k of ['ArrowRight','ArrowLeft','ArrowUp','ArrowDown',' '])
  vm.postIOData('keyboard',{key:k,isDown:false});
 await vm.loadProject(await (await fetch(url)).arrayBuffer());
 for(const target of vm.runtime.targets)for(const b of Object.values(target.blocks._blocks)){
  if(!b.shadow && !vm.runtime._primitives[b.opcode] && !vm.runtime._hats[b.opcode] &&
     b.opcode!=='procedures_definition')throw new Error('Unsupported opcode '+b.opcode);
 }
 soundPlays.length=0;
 await new Promise(r=>setTimeout(r,50));
 vm.greenFlag(); await tick(4);
};
window.t = name => vm.runtime.targets.find(t=>t.isOriginal && t.getName()===name);
window.clones = name => vm.runtime.targets.filter(t=>!t.isOriginal && t.getName()===name);
window.value = name => {
 const v=Object.values(vm.runtime.getTargetForStage().variables).find(v=>v.name===name)?.value;
 return typeof v==='string' && v.trim()!=='' && Number.isFinite(Number(v)) ? Number(v) : v;
};
window.setValue = (name,value) => Object.values(vm.runtime.getTargetForStage().variables).find(v=>v.name===name).value=value;
window.key = (direction,down=true) => vm.postIOData('keyboard',{key:direction,isDown:down});
window.hold = async (direction,frames=12) => {key(direction);await tick(frames);key(direction,false)};
window.spawn = async (name,x,y) => {
 const random=Math.random;Math.random=()=>0.9;
 const c=t(name).makeClone();vm.runtime.addTarget(c);await tick(2);
 Math.random=random;
 c.setXY(x,y);c.setVisible(true);await tick(1);return c;
};
window.exists = c => vm.runtime.targets.includes(c);
window.assert = (truth,message) => {if(!truth)throw new Error(message)};
window.runningScripts = () => vm.runtime.threads.filter(t=>!t.updateMonitor&&!t.isKilled);
window.finishHookSound = async () => {
 // AudioContext runs in real time, independently of simulated Scratch frames.
 for(let i=0;i<40;i++){
  await new Promise(r=>setTimeout(r,25));await tick(3);
  if(!runningScripts().some(t=>t.target.getName()==='hazard'&&!t.target.isOriginal))return;
 }
};
window.quietSpawners = () => {
 for(const n of ['obstacle','collectable','hazard'])if(t(n))vm.runtime.stopForTarget(t(n));
};
window.removeClones = () => {
 for(const c of [...vm.runtime.targets])if(!c.isOriginal){
  vm.runtime.stopForTarget(c);vm.runtime.disposeTarget(c);
 }
};
window.drawMonitors = () => {
 document.querySelector('#monitors').innerHTML=['score','high score','lives'].filter(n=>value(n)!==undefined)
  .map(n=>'<span class="value">'+n+': '+value(n)+'</span>').join('');
 vm.renderer.draw();
};
</script>`;
const server = http.createServer((req,res) => {
  try {
    const u = decodeURIComponent(req.url.split("?")[0]);
    if(u==="/"){res.setHeader("Content-Type","text/html");res.end(html);return}
    let file;
    if(library[u]) file=path.join(toolRoot,library[u]);
    else if(u.startsWith("/checkpoints/"))file=path.join(checkpointRoot,path.basename(u));
    else if(u.startsWith("/project/"))file=path.resolve(root,u.slice(9));
    if(!file || (!library[u] && !file.startsWith(root+"/") && !file.startsWith(checkpointRoot+"/"))) {
      res.writeHead(404);res.end();return;
    }
    res.setHeader("Content-Type",file.endsWith(".js")?"text/javascript":"application/octet-stream");
    res.end(fs.readFileSync(file));
  } catch(e){res.writeHead(500);res.end(String(e))}
});

const checks = {
  1: `assert(t('player').x===0 && t('player').y===0,'player reset');assert(t('player').currentCostume===1,'faces down');`,
  2: `await hold('ArrowRight');assert(t('player').currentCostume===3,'faces right');`,
  3: `for(const [keyName,index] of [['ArrowRight',3],['ArrowLeft',2],['ArrowDown',1],['ArrowUp',0]]){await hold(keyName);assert(t('player').currentCostume===index,keyName+' costume')}`,
  4: `const ys=[];for(let i=0;i<30;i++){await tick();ys.push(t('player').y)}assert(Math.min(...ys)===0&&Math.max(...ys)===1,'gentle bob range');`,
  5: `key('ArrowRight');const ys=[];for(let i=0;i<40;i++){await tick();ys.push(t('player').y)}key('ArrowRight',false);assert(Math.max(...ys)===3,'fast bob range');await tick(20);key(' ');const idle=[];for(let i=0;i<30;i++){await tick();idle.push(t('player').y)}key(' ',false);assert(Math.max(...idle)===1,'space does not trigger swimming');`,
  6: `assert(t('wave').getCostumes().length===1,'wave artwork exists');`,
  7: `assert(t('wave').x===0&&t('wave').y===-20,'wave position');`,
  8: `const ys=[];for(let i=0;i<30;i++){await tick();ys.push(t('wave').y)}assert(Math.min(...ys)===-21&&Math.max(...ys)===-20,'wave bob range');`,
  9: `assert(t('wave').getCostumes().length===3,'three wave costumes');`,
  10: `key('ArrowLeft');const seen=new Set();for(let i=0;i<40;i++){await tick();seen.add(t('wave').currentCostume)}key('ArrowLeft',false);await tick(20);assert(seen.size===3,'all wave frames animate');assert(t('wave').currentCostume===0,'idle resets smallest wave');`,
  11: `assert(t('obstacle').visible,'drawn rock visible');`,
  12: `assert(clones('obstacle').length===1,'one visible clone');assert(clones('obstacle')[0].visible&&!t('obstacle').visible,'only clone shows');const positions=[];for(let i=0;i<4;i++){vm.greenFlag();await tick(3);positions.push(clones('obstacle')[0].x)}assert(new Set(positions).size>1,'positions vary');`,
  13: `const sizes=[];for(let i=0;i<8;i++){vm.greenFlag();await tick(3);sizes.push(clones('obstacle')[0].size)}assert(sizes.every(n=>n>=50&&n<=100)&&new Set(sizes).size>1,'random size bounds');`,
  14: `assert(clones('obstacle').length===0,'no idle spawning');await hold(' ',100);assert(clones('obstacle').length===0,'no space spawning');await hold('ArrowRight',150);assert(clones('obstacle').length>=2,'paced spawning');const count=clones('obstacle').length;await tick(100);assert(clones('obstacle').length===count,'release stops spawning');`,
  15: `await hold('ArrowRight',4);assert(clones('obstacle')[0].x===220,'right edge');vm.greenFlag();await tick(3);await hold('ArrowLeft',4);assert(clones('obstacle')[0].x===-220,'left edge');`,
  16: `await hold('ArrowUp',4);assert(clones('obstacle')[0].y===160,'top edge');vm.greenFlag();await tick(3);await hold('ArrowDown',4);assert(clones('obstacle')[0].y===-160,'bottom edge');`,
  17: `quietSpawners();const c=await spawn('obstacle',150,100);const x=c.x;await hold('ArrowRight',10);assert(c.x<x,'right moves scenery left');const x2=c.x;await hold('ArrowLeft',10);assert(c.x>x2,'left moves scenery right');`,
  18: `quietSpawners();const c=await spawn('obstacle',150,100);await hold('ArrowUp',10);assert(c.y<100,'up moves scenery down');const y=c.y;await hold('ArrowDown',10);assert(c.y>y,'down moves scenery up');`,
  19: `quietSpawners();let c=await spawn('obstacle',-219,100);await hold('ArrowRight',4);assert(!exists(c),'left cleanup');c=await spawn('obstacle',219,100);await hold('ArrowLeft',4);assert(!exists(c),'right cleanup');`,
  20: `quietSpawners();let c=await spawn('obstacle',100,-159);await hold('ArrowUp',4);assert(!exists(c),'bottom cleanup');c=await spawn('obstacle',100,159);await hold('ArrowDown',4);assert(!exists(c),'top cleanup');c=await spawn('obstacle',100,0);await tick(20);assert(exists(c),'interior rock survives');`,
  21: `quietSpawners();const c=await spawn('obstacle',20,0);await tick(4);assert(value('right blocked')==='yes','right probe detects rock');c.setXY(170,100);await tick(4);assert(value('right blocked')==='no','right probe clears');assert(t('player').x===0,'probe restores position');`,
  22: `quietSpawners();const c=await spawn('obstacle',-20,0);await tick(4);assert(value('left blocked')==='yes','left probe detects rock');c.setXY(-170,100);await tick(4);assert(value('left blocked')==='no','left probe clears');`,
  23: `quietSpawners();const c=await spawn('obstacle',0,20);await tick(4);assert(value('up blocked')==='yes','upper probe');c.setXY(0,-20);await tick(4);assert(value('down blocked')==='yes','lower probe');`,
  24: `quietSpawners();for(const [direction,reverse,x,y] of [['ArrowRight','ArrowLeft',150,0],['ArrowLeft','ArrowRight',-150,0],['ArrowUp','ArrowDown',0,120],['ArrowDown','ArrowUp',0,-120]]){removeClones();const c=await spawn('obstacle',x,y);c.setSize(100);await hold(direction,80);assert(exists(c),'rock survives approach');const before=[c.x,c.y];await hold(direction,12);assert(Math.abs(c.x-before[0])<4&&Math.abs(c.y-before[1])<4,'blocks '+direction);await hold(reverse,12);assert(Math.hypot(c.x-before[0],c.y-before[1])>15,'escapes '+reverse);assert(Math.abs(t('player').x)<0.01,'player stays centred')}`,
  25: `quietSpawners();const c=await spawn('collectable',100,50);assert(c.getCostumes()[0].name==='down'&&c.size===15,'small duck clone');assert(value('score')===undefined,'no premature scoring');`,
  26: `assert(value('score')===0,'score begins at zero');setValue('score',9);vm.greenFlag();await tick(4);assert(value('score')===0,'score resets');`,
  27: `quietSpawners();let c=await spawn('collectable',0,0);await tick(3);assert(!exists(c)&&value('score')===1,'rescue exactly one point');await spawn('obstacle',0,0);await tick(3);assert(value('score')===1,'rocks do not score');`,
  28: `quietSpawners();const c=await spawn('collectable',0,0);await tick(4);assert(!exists(c)&&value('score')===1,'sound does not delay removal');assert(t('collectable').getSounds().some(s=>s.name==='pop'&&s.sampleCount>0),'rescue sound decoded');assert(soundPlays.some(s=>s.target==='collectable'&&s.opcode==='sound_play'),'rescue starts a sound');`,
  29: `quietSpawners();setValue('score',7);const c=await spawn('hazard',0,0);await tick(4);assert(!exists(c)&&value('score')===7,'hook removes without scoring');const blocks=t('hazard').blocks._blocks;assert(!Object.values(blocks).some(b=>b.opcode==='data_setvariableto'&&b.fields.VARIABLE.value==='score'),'hazard owns no score reset');`,
  30: `quietSpawners();setValue('score',7);await spawn('hazard',0,0);await finishHookSound();assert(runningScripts().length===0,'hook stops all');assert(value('score')===7,'hook does not score');`,
  31: `quietSpawners();let c=await spawn('hazard',100,80);c.setDirection(90);const x=c.x;await tick(8);assert(c.x>x,'drifts without keys');c.setXY(219,80);await tick(8);assert(!exists(c),'drift crosses boundary and clears without keys');vm.greenFlag();await tick(4);assert(value('score')===0,'restart resets');`
};

(async()=>{
 await new Promise(r=>server.listen(0,"127.0.0.1",r));
 const port=server.address().port;
 const browser=await chromium.launch({
   executablePath:process.env.DUCK_TEST_BROWSER || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
   headless:true,args:["--enable-webgl","--use-angle=swiftshader","--enable-unsafe-swiftshader","--autoplay-policy=no-user-gesture-required"]
 });
 try {
  const page=await browser.newPage({viewport:{width:960,height:720}});
  page.on("pageerror",e=>report.errors.push(String(e)));
  await page.goto(`http://127.0.0.1:${port}/`);
  await page.waitForFunction(()=>!!window.load);
  await page.click("canvas");
  await page.evaluate(()=>vm.runtime.audioEngine.audioContext.resume());
  for(const [number,check] of Object.entries(checks)){
   await page.evaluate(url=>load(url),`/checkpoints/step_${number.padStart(2,"0")}.sb3`);
   try{
    await page.evaluate(`(async()=>{${check}})()`);
    report.checks.push({step:Number(number),passed:true});
   }catch(e){
    const diagnostic=await page.evaluate(()=>runningScripts().map(t=>({
     target:t.target.getName(),status:t.status,stack:t.stack,
     top:t.target.blocks.getBlock(t.topBlock)?.opcode
    })));
    report.checks.push({step:Number(number),passed:false,error:String(e),diagnostic});
   }
   console.log(JSON.stringify(report.checks.at(-1)));
  }
  // Check extension behaviours together, including manually firing the sign receiver.
  await page.evaluate(()=>load("/project/en/solutions/editor-duck-island-with-challenges.sb3"));
  await page.evaluate(async()=>{
   quietSpawners();
   await spawn('collectable',0,0);await tick(4);
   assert(value('score')===1&&value('high score')===1,'high score increases');
   vm.greenFlag();await tick(4);quietSpawners();
   assert(value('score')===0&&value('high score')===1,'high score survives restart');
   assert(value('lives')===3,'lives reset');
   for(let expected=2;expected>=0;expected--){
    await spawn('hazard',0,0);await finishHookSound();
    assert(value('lives')===expected,'one life per hook');
    if(expected>0)assert(clones('hazard').length===0,'nonfinal hook deleted');
   }
   assert(t('game over').visible,'game over sign appears before stop');
   assert(runningScripts().length===0,'last life stops all');
   vm.greenFlag();await tick(4);assert(!t('game over').visible,'restart hides sign');
  });
  report.checks.push({extension:"score, lives, sign, restart",passed:true});
  // Parse and render every Markdown blocks3 example in the Scratch 3 style.
  let snippets=0;
  for(const name of fs.readdirSync(path.join(root,"en")).filter(n=>/^step_\d+\.md$/.test(n))){
   const text=fs.readFileSync(path.join(root,"en",name),"utf8");
   for(const [,snippet] of text.matchAll(/```blocks3\n([\s\S]*?)```/g)){
    const result=await page.evaluate(src=>{
     const doc=scratchblocks.parse(src,{languages:["en"]});
     const svg=scratchblocks.render(doc,{style:"scratch3"});
     return {width:svg.getAttribute("width"),height:svg.getAttribute("height")};
    },snippet);
    assert(Number(result.width)>0&&Number(result.height)>0,`Invalid blocks in ${name}`);
    snippets++;
   }
  }
  report.checks.push({blockDiagrams:snippets,passed:true});
  await page.evaluate(async()=>{
   await load("/project/en/code/editor-duck-island-complete/editor-duck-island-complete.sb3");
   quietSpawners();
   for(const [n,x,y] of [['obstacle',-120,80],['obstacle',120,-70],['obstacle',70,110],
    ['collectable',90,20],['collectable',-150,-90],['hazard',-80,120],['hazard',170,-110]])
     await spawn(n,x,y);
   drawMonitors();
  });
  await page.screenshot({path:path.join(__dirname,"runtime-preview.png")});
 }catch(e){report.errors.push(String(e));console.error(e)}
 finally{
  await browser.close();server.close();
  fs.writeFileSync(path.join(__dirname,"validation-results.json"),JSON.stringify(report,null,2)+"\n");
 }
 if(report.errors.length||report.checks.some(c=>!c.passed))process.exitCode=1;
})();
