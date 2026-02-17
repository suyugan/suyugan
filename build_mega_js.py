"""生成一个大JS，在浏览器中执行完所有10个场景的生成+轮询，最后返回所有结果"""
import json, sys
sys.stdout.reconfigure(encoding='utf-8')

PROMPTS_FILE = r'D:\video-analysis\output\taohaoxing\prompts.json'
GEN_SCRIPT = r'D:\video-analysis\scripts\jimeng_fetch_gen.py'

d = json.load(open(PROMPTS_FILE, 'r', encoding='utf-8'))
scenes = {s['scene_num']: s['prompt'] for s in d['scenes']}

# Build scene data
scene_list = []
for num in range(13, 23):
    import subprocess
    r = subprocess.run(
        ['python', GEN_SCRIPT, '--action', 'generate', '--prompt', scenes[num], '--ratio', '16:9', '--json'],
        capture_output=True, text=True, encoding='utf-8', timeout=15
    )
    data = json.loads(r.stdout.strip())
    # We need the body from the JS... actually let's extract the full generate function params
    scene_list.append({
        "num": num,
        "submit_id": data["submit_id"],
        "gen_js": data["js"],
    })
    # Also get poll js
    r2 = subprocess.run(
        ['python', GEN_SCRIPT, '--action', 'poll', '--submit-id', data["submit_id"]],
        capture_output=True, text=True, encoding='utf-8', timeout=15
    )
    scene_list[-1]["poll_js"] = r2.stdout.strip()

# Build a mega JS that processes all scenes sequentially
# Store all gen/poll JS as window variables, then run them sequentially
mega_js = "window.__scenes = " + json.dumps([{"num": s["num"], "submit_id": s["submit_id"]} for s in scene_list]) + ";\n"
for i, s in enumerate(scene_list):
    mega_js += f"window.__gen_js_{s['num']} = function() {{ return {s['gen_js']}; }};\n"
    mega_js += f"window.__poll_js_{s['num']} = function() {{ return {s['poll_js']}; }};\n"

# Add orchestrator
mega_js += """
window.__runAllScenes = async function() {
  var results = {};
  for (var i = 0; i < window.__scenes.length; i++) {
    var scene = window.__scenes[i];
    var num = scene.num;
    console.log('[scene_' + num + '] generating...');
    try {
      var genResult = await window['__gen_js_' + num]();
      var gr = JSON.parse(genResult);
      console.log('[scene_' + num + '] generate result:', gr);
      if (gr.ret !== '0' && gr.ret !== 0) {
        results[num] = {status: 'gen_error', detail: gr};
        continue;
      }
    } catch(e) {
      results[num] = {status: 'gen_exception', error: e.message};
      continue;
    }
    
    // Poll
    var startTime = Date.now();
    var imageUrl = null;
    while (Date.now() - startTime < 120000) {
      await new Promise(r => setTimeout(r, 5000));
      try {
        var pollResult = await window['__poll_js_' + num]();
        var pr = JSON.parse(pollResult);
        console.log('[scene_' + num + '] poll:', pr.status);
        if (pr.status === 'done') {
          imageUrl = pr.urls && pr.urls[0];
          break;
        } else if (pr.status === 'failed') {
          break;
        }
      } catch(e) {
        console.log('[scene_' + num + '] poll error:', e.message);
      }
    }
    
    if (imageUrl) {
      results[num] = {status: 'done', url: imageUrl};
    } else {
      results[num] = {status: 'no_url'};
    }
    
    // Wait 3s before next
    if (i < window.__scenes.length - 1) {
      await new Promise(r => setTimeout(r, 3000));
    }
  }
  window.__sceneResults = results;
  return JSON.stringify(results);
};
'orchestrator_ready';
"""

with open(r'D:\video-analysis\output\taohaoxing\mega_gen.js', 'w', encoding='utf-8') as f:
    f.write(mega_js)

print(f"Generated mega JS: {len(mega_js)} chars")
print("Scene submit IDs:")
for s in scene_list:
    print(f"  scene_{s['num']:02d}: {s['submit_id']}")
