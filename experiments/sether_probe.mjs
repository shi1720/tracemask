// Run from repository root: node experiments/sether_probe.mjs /path/to/sether/dist/index.js
// Pin: raeven-co/sether 14ee74e2afca52c57f01ab43ee969db9d2429d0c (0.7.1).
import { pathToFileURL } from 'node:url';
import { writeFileSync } from 'node:fs';
const { createRedactStream, MemoryVault } = await import(pathToFileURL(process.argv[2]));
const results = [];
for (const [kind, secret] of [
  ['identifier64', 'secret-'+ 'x'.repeat(57)],
  ['phrase1024', ('private alpha beta gamma ').repeat(50).slice(0,1024)],
  ['identifier9000', 'secret-'+ 'z'.repeat(8993)],
  ['unicode', 'tenant-é🙂-秘密'],
]) {
 for (const size of [1,4,16,64,256]) {
  for (const setting of ['default256','length_bound']) {
   const prefix = 'Public answer. ', suffix = ' End of answer.';
   const text = prefix+secret+suffix;
   const detector = {type:'LITERAL', detect(text) {
    const found=[]; let start=0;
    while ((start=text.indexOf(secret,start))>=0) {
     found.push({start,end:start+secret.length,value:secret}); start++;
    }
    return found;
   }};
   const stream = createRedactStream({detectors:[detector],vault:new MemoryVault(),
    uuid:()=> 'fixed',safeDistanceBytes:setting==='default256'?256:secret.length});
   let output = '';
   stream.on('data',chunk=>{output+=chunk.toString()});
   const ended = new Promise((resolve,reject)=>{stream.on('end',resolve);stream.on('error',reject)});
   const bytes=Buffer.from(text);
   for(let i=0;i<bytes.length;i+=size) stream.write(bytes.subarray(i,i+size));
   stream.end(); await ended;
   const normalized=output.replaceAll('<LITERAL_fixed>','*'.repeat(Array.from(secret).length));
   const expected=prefix+'*'.repeat(Array.from(secret).length)+suffix;
   const ascii=/^[\x00-\x7F]*$/.test(text);
   const leaked=ascii&&normalized.length===text.length?
    [...normalized.slice(prefix.length,prefix.length+secret.length)].filter(c=>c!=='*').length:null;
   results.push({kind,size,setting,exact:normalized===expected,leaked_positions:leaked,
      replacement_characters:[...output].filter(c=>c==='�').length});
  }
 }
}
writeFileSync('results/sether_probe.json',JSON.stringify({commit:'14ee74e2afca52c57f01ab43ee969db9d2429d0c',version:'0.7.1',
 scope:'Controlled literal Detector; no claim about built-in detector accuracy. UTF-8 byte chunks, not text chunks.',results},null,2)+'\n');
console.log(JSON.stringify(results));
