from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
if 'rr-calendar-v1' in s:
    raise SystemExit('calendar already installed')

s=s.replace('content="3.1.1"','content="3.2.0"',1)
s=s.replace('Race Ready · 3.1.1','Race Ready · 3.2.0',1)

css='''\n/* rr-calendar-v1 */\n.calHead{display:flex;align-items:center;justify-content:space-between;gap:8px;margin:12px 0}.calHead button{width:auto;margin:0;padding:9px 13px}.calTitle{text-align:center;font-weight:900;font-size:18px}.calDow,.calGrid{display:grid;grid-template-columns:repeat(7,1fr);gap:5px}.calDow div{text-align:center;color:var(--muted);font-size:10px;font-weight:800;padding:4px}.calDay{min-height:78px;border:1px solid var(--line);background:#12161b;border-radius:10px;padding:7px;font-size:11px;position:relative}.calDay.out{opacity:.25}.calDay.today{border-color:var(--accent);box-shadow:inset 0 0 0 1px var(--accent)}.calDay.done .calNum{color:var(--good)}.calNum{font-weight:900;font-size:13px}.calWorkout{margin-top:7px;font-size:10px;line-height:1.2;color:var(--accent);font-weight:800}.calEvent{margin-top:5px;font-size:9px;color:#e5c46a}.calDay.clickable{cursor:pointer}.calLegend{display:flex;gap:12px;flex-wrap:wrap;margin:10px 2px;color:var(--muted);font-size:10px}.calDot{display:inline-block;width:7px;height:7px;border-radius:50%;background:var(--accent);margin-right:4px}.calDot.doneDot{background:var(--good)}@media(max-width:480px){.calDay{min-height:67px;padding:5px}.calWorkout{font-size:9px}.calEvent{font-size:8px}}\n'''
s=s.replace('</style></head>',css+'</style></head>',1)

old='<section id="week" class="view"><div class="card hero"><div class="tag">Programming</div><h2 id="weekTitle">Current Week</h2><div class="muted" id="weekSubtitle"></div></div><div id="weeklist"></div></section>'
new='''<section id="week" class="view"><div class="card hero"><div class="tag">Training Calendar</div><h2 id="weekTitle">Current Programming</h2><div class="muted" id="weekSubtitle"></div></div><div class="card"><div class="calHead"><button class="secondary" onclick="changeCalendarMonth(-1)">←</button><div class="calTitle" id="calTitle"></div><button class="secondary" onclick="changeCalendarMonth(1)">→</button></div><div class="calDow"><div>MON</div><div>TUE</div><div>WED</div><div>THU</div><div>FRI</div><div>SAT</div><div>SUN</div></div><div class="calGrid" id="calendarGrid"></div><div class="calLegend"><span><i class="calDot"></i>Programmed</span><span><i class="calDot doneDot"></i>Completed</span></div></div><div id="weeklist"></div></section>'''
if old not in s: raise SystemExit('week section not found')
s=s.replace(old,new,1)

# Add dates to legacy launch days so calendar can place them.
s=s.replace("thu:{dow:'THU',name:'Hybrid CrossFit'","thu:{date:'2026-10-29',dow:'THU',name:'Hybrid CrossFit'",1)
s=s.replace("fri:{dow:'FRI',name:'Full-Body Strength + FBB'","fri:{date:'2026-10-30',dow:'FRI',name:'Full-Body Strength + FBB'",1)
s=s.replace("sat:{dow:'SAT',name:'Race Ready Playground'","sat:{date:'2026-10-31',dow:'SAT',name:'Race Ready Playground'",1)

needle="let order=Object.keys(program).filter(k=>k!=='meta'),selected=order[0]||'thu',progressTab='strength';"
repl=needle+"\nlet calendarCursor=new Date(2026,10,1);"
s=s.replace(needle,repl,1)

# Published dated week can be loaded directly into local programming without deleting records.
calendar_js=r'''
function programDateKey(k){return program[k]?.date||''}
function calendarEvents(date){let out=[];if(date==='2026-11-11')out.push('CHAD1000X');return out}
function renderCalendar(){let grid=document.getElementById('calendarGrid');if(!grid)return;let y=calendarCursor.getFullYear(),m=calendarCursor.getMonth();document.getElementById('calTitle').textContent=new Intl.DateTimeFormat('en-US',{month:'long',year:'numeric'}).format(calendarCursor);let first=new Date(y,m,1),start=(first.getDay()+6)%7,days=new Date(y,m+1,0).getDate(),prevDays=new Date(y,m,0).getDate(),cells=[];let today=new Date(),todayKey=today.getFullYear()+'-'+String(today.getMonth()+1).padStart(2,'0')+'-'+String(today.getDate()).padStart(2,'0');for(let i=0;i<42;i++){let d=i-start+1,cy=y,cm=m,cd=d,out=false;if(d<1){cm=m-1;if(cm<0){cm=11;cy--}cd=prevDays+d;out=true}else if(d>days){cm=m+1;if(cm>11){cm=0;cy++}cd=d-days;out=true}let key=cy+'-'+String(cm+1).padStart(2,'0')+'-'+String(cd).padStart(2,'0'),pk=order.find(k=>programDateKey(k)===key),events=calendarEvents(key),done=pk&&logs[pk+'_done'];cells.push(`<div class="calDay ${out?'out':''} ${key===todayKey?'today':''} ${done?'done':''} ${pk?'clickable':''}" ${pk?`onclick="openCalendarWorkout('${pk}')"`:''}><div class="calNum">${cd}${done?' ✓':''}</div>${pk?`<div class="calWorkout">${esc(program[pk].name)}</div>`:''}${events.map(e=>`<div class="calEvent">${esc(e)}</div>`).join('')}</div>`)}grid.innerHTML=cells.join('')}
function changeCalendarMonth(n){calendarCursor=new Date(calendarCursor.getFullYear(),calendarCursor.getMonth()+n,1);renderCalendar()}
function openCalendarWorkout(k){selected=k;showView('today');renderWorkout()}
async function loadPublishedWeek(url,label){try{let r=await fetch(url+'?v='+Date.now(),{cache:'no-store'});if(!r.ok)throw Error();let d=await r.json();program=d.program||d;localStorage.setItem(S.program,JSON.stringify(program));order=Object.keys(program).filter(k=>k!=='meta');selected=order[0];let first=order.map(k=>program[k].date).find(Boolean);if(first){let x=new Date(first+'T12:00:00');calendarCursor=new Date(x.getFullYear(),x.getMonth(),1)}renderWorkout();renderCalendar();alert(label+' loaded to your calendar. Your records and Podiums were preserved.')}catch(e){alert('Could not load the published week. Try again when connected.') }}
'''
s=s.replace('function renderWeek(){',calendar_js+'\nfunction renderWeek(){',1)

# Calendar refresh whenever week renders.
s=s.replace("function renderWeek(){document.getElementById('weekTitle')", "function renderWeek(){renderCalendar();document.getElementById('weekTitle')",1)

# Add one-tap published programming card in Settings.
settings_old='<div class="card"><div class="tag">Programming</div><h2>Import Future Weeks</h2><div class="muted small">Future Race Ready programming can be imported without rebuilding the app.</div>'
settings_new='<div class="card"><div class="tag">Programming</div><h2>Available Programming</h2><div class="muted small">Load dated Race Ready weeks directly to your calendar. This changes programming only — records and Podiums stay intact.</div><button class="primary" onclick="loadPublishedWeek(\'programming/cycle-1-week-1-2026-11-02.json\',\'Cycle 1 · Week 1 · Nov 2–7\')">Load Nov 2–7 to Calendar</button><div style="height:10px"></div><h2>Import Programming File</h2><div class="muted small">You can still import a programming JSON file manually.</div>'
s=s.replace(settings_old,settings_new,1)

p.write_text(s,encoding='utf-8')
print('Race Ready calendar upgrade applied')
