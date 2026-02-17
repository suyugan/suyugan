import json

d = json.load(open(r'D:\video-analysis\output\taohaoxing\prompts_arr.json','r',encoding='utf-8'))
js_arr = json.dumps(d, ensure_ascii=True)

js = '(function(){window.__sceneData=' + js_arr + ';window.__sceneLog=[];window.__sceneDone=false;window.__sceneResults={};(async function(){for(var i=0;i<window.__sceneData.length;i++){var num=window.__sceneData[i][0],prompt=window.__sceneData[i][1];var sid=crypto.randomUUID();window.__sceneLog.push("gen_"+num);try{var g=await window.__jimengGen(prompt,sid);window.__sceneLog.push("gen_"+num+"_ret:"+JSON.stringify(g));if(g.ret!=="0"&&g.ret!==0){window.__sceneResults[num]={s:"gen_err",d:g};continue}}catch(e){window.__sceneResults[num]={s:"gen_ex",e:e.message};continue}var url=null,st=Date.now();while(Date.now()-st<120000){await new Promise(function(r){setTimeout(r,5000)});try{var p=await window.__jimengPoll(sid);window.__sceneLog.push("poll_"+num+":"+p.status);if(p.status==="done"){url=p.urls&&p.urls[0];break}if(p.status==="failed")break}catch(e){window.__sceneLog.push("poll_err_"+num)}}window.__sceneResults[num]=url?{s:"done",url:url}:{s:"no_url"};if(i<window.__sceneData.length-1)await new Promise(function(r){setTimeout(r,3000)})}window.__sceneDone=true})();return "started"})()'

with open(r'D:\video-analysis\output\taohaoxing\orchestrator.js','w',encoding='utf-8') as f:
    f.write(js)
print(len(js),'chars')
