// Render the existing OXI mascot; no new character drawing or raster editing.
const fs = require('fs');
const { oxiG } = require('./brand/mascot.cjs');
const rows = JSON.parse(fs.readFileSync(0, 'utf8'));
const arms = ['sheet','point','lens','wave','up','down'];
const legs = ['walkA','walkB','stand','walk','walkA','stand'];
const eyes = ['open','wink','open','happy','half','squint'];
const mouths = ['smirk','grin','o','grin','smirk','flat'];
const result = {};
for (const row of rows) {
  const i = row.index ?? Number(row.id.slice(-3));
  result[row.id] = oxiG({theme:row.theme,bg:row.bg,armR:arms[i%6],armL:i%2?'up':'down',legs:legs[(i+1)%6],eyes:eyes[(i+3)%6],mouth:mouths[i%6],look:[(i%3)*3+3,-2],tilt:(i%5-2)*4})
    .replace(/(ox[a-z]?)(\d+)/g,(_,prefix)=>prefix+row.id+'_');
}
process.stdout.write(JSON.stringify(result));
