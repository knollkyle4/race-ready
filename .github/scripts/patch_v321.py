from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

# Race Ready v3.2.1: persistent multi-week calendar + safe migration.
s=s.replace('content="3.2.0"','content="3.2.1"',1)
s=s.replace('Race Ready · 3.2.0','Race Ready · 3.2.1',1)

old="""async function loadPublishedWeek(url,label){try{let r=await fetch(url+'?v='+Date.now(),{cache:'no-store'});if(!r.ok)throw Error();let d=await r.json();program=d.program||d;localStorage.setItem(S.program,JSON.stringify(program));order=Object.keys(program).filter(k=>k!=='meta');selected=order[0];let first=order.map(k=>program[k].date).find(Boolean);if(first){let x=new Date(first+'T12:00:00');calendarCursor=new Date(x.getFullYear(),x.getMonth(),1)}renderWorkout();renderCalendar();alert(label+' loaded to your calendar. Your records and Podiums were preserved.')}catch(e){alert('Could not load the published week. Try again when connected.') }}"""
new="""function mergeProgramWeek(incoming){
  let next={...(program||{})};
  Object.keys(incoming||{}).forEach(k=>{if(k!=='meta')next[k]=incoming[k]});
  let metas=[];
  if(program?.meta)metas.push(program.meta);
  if(incoming?.meta)metas.push(incoming.meta);
  next.meta={title:'Race Ready Training Calendar',subtitle:'Launch Week + loaded Race Ready programming',weeks:metas};
  program=next;
  localStorage.setItem(S.program,JSON.stringify(program));
  order=Object.keys(program).filter(k=>k!=='meta').sort((a,b)=>(programDateKey(a)||'9999').localeCompare(programDateKey(b)||'9999'));
}
function restoreLaunchWeek(){
  const launchKeys=['thu','fri','sat'];
  let changed=false;
  launchKeys.forEach(k=>{if(!program[k]&&defaultProgram[k]){program[k]=defaultProgram[k];changed=true}});
  if(changed){localStorage.setItem(S.program,JSON.stringify(program));order=Object.keys(program).filter(k=>k!=='meta').sort((a,b)=>(programDateKey(a)||'9999').localeCompare(programDateKey(b)||'9999'));}
}
async function loadPublishedWeek(url,label){try{let r=await fetch(url+'?v='+Date.now(),{cache:'no-store'});if(!r.ok)throw Error();let d=await r.json();mergeProgramWeek(d.program||d);restoreLaunchWeek();let incoming=d.program||d;let first=Object.keys(incoming).filter(k=>k!=='meta').map(k=>incoming[k].date).find(Boolean);if(first){let x=new Date(first+'T12:00:00');calendarCursor=new Date(x.getFullYear(),x.getMonth(),1)}selected=order.find(k=>programDateKey(k)===first)||selected;renderWorkout();renderCalendar();renderWeek();alert(label+' added to your calendar. Existing weeks, records and Podiums were preserved.')}catch(e){alert('Could not load the published week. Try again when connected.') }}"""
if old not in s:
    raise SystemExit('v3.2.0 loader not found')
s=s.replace(old,new,1)

# defaultProgram is a stable copy of the built-in launch week before local rrProgram overrides it.
needle="let program=JSON.parse(localStorage.getItem(S.program)||'null')||defaultProgram;"
if needle not in s:
    # accommodate minified declaration form by finding the program assignment
    needle="program=JSON.parse(localStorage.getItem(S.program)||'null')||defaultProgram"
    if needle not in s: raise SystemExit('program assignment not found')

# Auto-migrate installed copies: restore launch dates into any existing Week 1 local program.
anchor="let calendarCursor=new Date(2026,10,1);"
if anchor not in s: raise SystemExit('calendar cursor not found')
s=s.replace(anchor,anchor+"\nsetTimeout(()=>{try{restoreLaunchWeek();renderCalendar();}catch(e){}},0);",1)

# Clarify programming copy.
s=s.replace('Load dated Race Ready weeks directly to your calendar. This changes programming only — records and Podiums stay intact.','Add dated Race Ready weeks to your calendar. Existing weeks stay in place; records and Podiums stay intact.',1)

p.write_text(s,encoding='utf-8')
print('Race Ready v3.2.1 multi-week patch applied')
