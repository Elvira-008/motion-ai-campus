const pages = [...document.querySelectorAll('.page')];
const navs = [...document.querySelectorAll('[data-target]')];
const titles = {overview:'Панель управления',student:'AI-помощник студента',tasks:'Генератор практических задач',manager:'Дела студентов'};
function showPage(id){pages.forEach(p=>p.classList.toggle('active-page',p.id===id));document.querySelectorAll('.nav').forEach(n=>n.classList.toggle('active',n.dataset.target===id));document.getElementById('pageTitle').textContent=titles[id]||'Панель управления';}
navs.forEach(n=>n.addEventListener('click',()=>showPage(n.dataset.target)));
const score = document.getElementById('diagScore');
score.addEventListener('input',()=>document.getElementById('scoreLabel').textContent=score.value+'%');
async function api(url, options={}){const r=await fetch(url,{headers:{'Content-Type':'application/json'},...options});if(!r.ok)throw new Error('Ошибка API: '+r.status);return r.json()}
document.getElementById('diagnoseBtn').addEventListener('click',async()=>{
 const btn=document.getElementById('diagnoseBtn');btn.disabled=true;btn.textContent='Анализируем...';
 try{const d=await api('/api/diagnose',{method:'POST',body:JSON.stringify({student_id:Number(document.getElementById('diagStudent').value),topic:document.getElementById('diagTopic').value,score:Number(score.value)})});
 const good=d.score>=75;document.getElementById('diagResult').innerHTML=`<div class="result-card"><span class="status ${good?'good':''}">${d.level}</span><h3>${d.topic}: ${d.score}%</h3><div class="meter"><span style="width:${d.score}%"></span></div><p>${d.message}</p><h4>Рекомендуемые действия</h4><ul>${d.actions.map(x=>`<li>${escapeHtml(x)}</li>`).join('')}</ul></div>`;
 }catch(e){alert(e.message)}finally{btn.disabled=false;btn.textContent='✦ Проверить знания'}
});
document.getElementById('generateBtn').addEventListener('click',async()=>{
 const btn=document.getElementById('generateBtn');btn.disabled=true;btn.textContent='Готовим задание...';
 try{const d=await api('/api/generate-task',{method:'POST',body:JSON.stringify({technology:document.getElementById('taskTech').value,level:document.getElementById('taskLevel').value,topic:document.getElementById('taskTopic').value})});
 document.getElementById('taskResult').innerHTML=`<div class="task-card"><div class="task-meta"><span>${escapeHtml(d.technology)}</span><span>${escapeHtml(d.level)}</span><span>Практика</span></div><h3>${escapeHtml(d.title)}</h3><p>${escapeHtml(d.description)}</p><h4>Требования</h4><ul>${d.requirements.map(x=>`<li>${escapeHtml(x)}</li>`).join('')}</ul><h4>Критерии приёмки</h4><ul>${d.acceptance.map(x=>`<li>${escapeHtml(x)}</li>`).join('')}</ul><p class="note">${escapeHtml(d.note)}</p><button class="secondary" onclick="window.print()">⤓ Сохранить / печать</button></div>`;
 }catch(e){alert(e.message)}finally{btn.disabled=false;btn.textContent='✦ Сгенерировать задание'}
});
function escapeHtml(s){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
async function loadStudents(){try{const data=await api('/api/students');document.getElementById('studentCount').textContent=data.length;document.getElementById('studentsTable').innerHTML=data.map(s=>`<tr><td>${escapeHtml(s.name)}</td><td>${escapeHtml(s.group)}</td><td>${escapeHtml(s.course)}</td></tr>`).join('')}catch(e){document.getElementById('studentsTable').innerHTML='<tr><td colspan="3">Не удалось загрузить данные</td></tr>'}}
document.getElementById('studentForm').addEventListener('submit',async e=>{
 e.preventDefault();const message=document.getElementById('managerMessage');message.textContent='Сохраняем...';
 try{const d=await api('/api/students',{method:'POST',body:JSON.stringify({name:document.getElementById('fullName').value.trim(),group:document.getElementById('groupName').value.trim(),phone:document.getElementById('phone').value.trim(),email:document.getElementById('email').value.trim(),course:document.getElementById('course').value})});message.textContent='✓ '+d.message+' (ID '+d.student.id+')';e.target.reset();await loadStudents()}catch(err){message.textContent='Ошибка: '+err.message}
});
document.getElementById('refreshBtn').addEventListener('click',loadStudents);
document.getElementById('exportBtn').addEventListener('click',async()=>{const out=document.getElementById('exportOutput');try{const data=await api('/api/export');out.hidden=!out.hidden;if(!out.hidden)out.textContent=JSON.stringify(data,null,2)}catch(e){alert(e.message)}});
loadStudents();
