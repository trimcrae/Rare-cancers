const sharp=require('C:/Users/mcrae/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
const path=require('path');
(async()=>{for(const n of ['figure-1','figure-2']){
 const file=path.join(__dirname,'figures',n);
 await sharp(file+'.svg',{density:220}).png().toFile(file+'.png');
 await sharp(file+'.svg',{density:100}).png().toFile(file+'-preview.png');
}})();
