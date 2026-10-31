from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

# Race Ready v3.2.1: persistent multi-week calendar.
if 'content="3.2.1"' in s:
    print('Race Ready v3.2.1 already applied')
    raise SystemExit(0)
if 'content="3.2.0"' not in s:
    raise SystemExit('Expected Race Ready v3.2.0')

s=s.replace('content="3.2.0"','content="3.2.1"',1)
s=s.replace('Race Ready · 3.2.0','Race Ready · 3.2.1',1)

old="""async function loadPublishedWeek(url,label){try{let r=await fetch(url+'?v='+Date.now(),{cache:'no-store'});if(!r.ok)throw Error();let d=await r.json();program=d.program||d;localStorage.setItem(S.program,JSON.stringify(program));order=Object.keys(program).filter(k=>k!=='meta');selected=order[0];let first=order.map(k=>program[k].date).find(Boolean);if(first){let x=new Date(first+'T12:00:00');calendarCursor=new Date(x.getFullYear(),x.getMonth(),1)}renderWorkout();renderCalendar();alert(label+' loaded to your calendar. Your records and Podiums were preserved.')}catch(e){alert('Could not load the published week. Try again when connected.') }}"""
new="""function programDateKey(k){return program[k]?.date||(/^\\d{4}-\\d{2}-\\d{2}/.exec(k)?.[0]||'')}
function mergeProgramWeek(incoming){
  const current=(program&&typeof program==='object')?program:{};
  const next={...current};
  Object.keys(incoming||{}).forEach(k=>{if(k!=='meta')next[k]=incoming[k]});
  next.meta={...(current.meta||{}),...(incoming?.meta||{}),title:'Race Ready Training Calendar'};
  program=next;
  localStorage.setItem(S.program,JSON.stringify(program));
  order=Object.keys(program).filter(k=>k!=='meta').sort((a,b)=>(programDateKey(a)||'9999').localeCompare(programDateKey(b)||'9999'));
}
async function loadPublishedWeek(url,label){try{let r=await fetch(url+'?v='+Date.now(),{cache:'no-store'});if(!r.ok)throw Error();let d=await r.json();let incoming=d.program||d;mergeProgramWeek(incoming);let first=Object.keys(incoming).filter(k=>k!=='meta').map(k=>incoming[k]?.date||(/^\\d{4}-\\d{2}-\\d{2}/.exec(k)?.[0]||'')).find(Boolean);if(first){let x=new Date(first+'T12:00:00');calendarCursor=new Date(x.getFullYear(),x.getMonth(),1);selected=order.find(k=>programDateKey(k)===first)||selected}renderWorkout();renderCalendar();renderWeek();alert(label+' added to your calendar. Existing weeks, records and Podiums were preserved.')}catch(e){console.error(e);alert('Could not load the published week. Try again when connected.') }}"""

if old not in s:
    raise SystemExit('v3.2.0 loader not found')
s=s.replace(old,new,1)

# Existing calendar code already defines programDateKey. Remove the older definition so
# the new key-aware version above is the only one.
old_date="function programDateKey(k){return program[k]?.date||''}"
# It may appear before the loader; replacing it with a harmless marker avoids duplicate declarations.
s=s.replace(old_date,"/* programDateKey upgraded in v3.2.1 */",1)

s=s.replace('Load dated Race Ready weeks directly to your calendar. This changes programming only — records and Podiums stay intact.','Add dated Race Ready weeks to your calendar. Existing weeks stay in place; records and Podiums stay intact.',1)

p.write_text(s,encoding='utf-8')
print('Race Ready v3.2.1 multi-week patch applied')
