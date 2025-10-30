# main_web.py - Flask app with autostarting simulation and public read-only dashboard
import os, threading, time, json
from flask import Flask, jsonify, request, send_file, send_from_directory, render_template_string
from save_system import SaveManager
from world import World

app = Flask(__name__)
SAVE_FILE = os.environ.get('SAVE_FILE','world_save.json.gz')
ADMIN_KEY = os.environ.get('ADMIN_KEY','CHANGE_ME')  # set this on Railway for admin control
save_manager = SaveManager(filename=SAVE_FILE)
world = World(save_manager=save_manager, autosave_years=1)

# simple in-memory history for charts
history = {'years':[], 'population':[], 'knowledge_count':[], 'births':[], 'deaths':[], 'marriages':[]}
history_lock = threading.Lock()

def snapshot():
    s = world.get_stats()
    if not history['years'] or history['years'][-1] != s['year']:
        history['years'].append(s['year']); history['population'].append(s['population'])
        history['knowledge_count'].append(s['world_knowledge_count']); history['births'].append(s.get('births',0))
        history['deaths'].append(s.get('deaths',0)); history['marriages'].append(s.get('marriages',0))

# cinematic intro + autostart landing page
INDEX_HTML = '''<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Disordered Earth</title><style>body{margin:0;font-family:Arial;background:#081426;color:#eee}#intro{display:flex;align-items:center;justify-content:center;height:100vh;flex-direction:column}
h1{font-size:28px;margin:0} p{color:#9fb} .hidden{display:none}</style></head><body>
<div id="intro"><h1>Disordered Earth</h1><p>an evolving civilization — starting now</p><p class="small">Launching in <span id="count">5</span>...</p></div>
<div id="app" class="hidden">
  <div style="padding:10px"><strong id="year">Year:</strong> <span id="yearv"></span> &nbsp; Population: <span id="popv"></span></div>
  <canvas id="pop" style="max-width:100%;height:200px"></canvas>
  <div style="padding:10px"><small>Public read-only view. Creator can control via admin endpoint.</small></div>
</div>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
  var c=5; var t=setInterval(()=>{c--;document.getElementById('count').innerText=c;if(c<=0){clearInterval(t);document.getElementById('intro').className='hidden';document.getElementById('app').className=''; start();}},1000);
  var chart;
  async function fetchStats(){ try{ let r=await fetch('/history'); if(!r.ok) return; let j=await r.json();
    document.getElementById('yearv').innerText = j.years[j.years.length-1] || 0;
    document.getElementById('popv').innerText = j.population[j.population.length-1] || 0;
    if(!chart){ const ctx=document.getElementById('pop').getContext('2d'); chart=new Chart(ctx,{type:'line',data:{labels:j.years.map(String),datasets:[{label:'Population',data:j.population,fill:true}]},options:{responsive:true}})} else { chart.data.labels=j.years.map(String); chart.data.datasets[0].data=j.population; chart.update(); }
  }catch(e){console.error(e)} }
  function start(){ setInterval(()=>{ fetch('/ping'); fetchStats(); }, 1000); fetchStats(); }
</script></body></html>'''

@app.route('/')
def index():
    return render_template_string(INDEX_HTML)

@app.route('/history')
def history_endpoint():
    with history_lock:
        return jsonify(history)

@app.route('/ping')
def ping():
    # lightweight endpoint to keep backend active and optionally trigger snapshot
    with history_lock:
        snapshot()
    return jsonify({'ok':True})

# admin control endpoint - protected by ADMIN_KEY env var (set on host)
@app.route('/admin', methods=['POST'])
def admin():
    key = request.args.get('key') or request.json.get('key') if request.json else None
    if not key or key != os.environ.get('ADMIN_KEY','CHANGE_ME'):
        return jsonify({'error':'unauthorized'}), 403
    data = request.json or {}
    act = data.get('action')
    if act == 'pause': app.config['paused']=True; return jsonify({'status':'paused'})
    if act == 'resume': app.config['paused']=False; return jsonify({'status':'resumed'})
    if act == 'save': world.force_save('admin_save'); return jsonify({'status':'saved'})
    if act == 'spawn': name = data.get('name','Guest'); from npc import NPC; n=NPC(name,age=16); world.npcs[n.uid]=n; return jsonify({'status':'spawned','uid':n.uid})
    return jsonify({'status':'unknown'})

def sim_loop():
    while True:
        if not app.config.get('paused', False):
            with history_lock:
                world.tick_year(); snapshot()
        time.sleep(float(os.environ.get('TICK_DELAY', '1.0')))

if __name__ == '__main__':
    app.config['paused'] = False
    # pre-snapshot
    with history_lock: snapshot()
    t = threading.Thread(target=sim_loop, daemon=True); t.start()
    # run Flask (for local dev)
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT',5000)))
