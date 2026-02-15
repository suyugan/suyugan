"""
Batch download jimeng images via browser base64 extraction.
Run this from the browser evaluate context.
"""
import base64, os, json

output_dir = r"D:\video-analysis\output\原生家庭\images"
os.makedirs(output_dir, exist_ok=True)

# Map of scene -> image data (will be filled by browser)
# For now, write a JS function that fetches all images and returns base64

js_fetch_all = """
(function() {
  var imgs = Array.from(document.querySelectorAll('img[src*="dreamina-sign"][src*="aigc_resize"]'));
  // Get unique IDs (first occurrence of each ID)
  var seen = {};
  var unique = [];
  imgs.forEach(function(img) {
    var m = img.src.match(/\\/([a-f0-9]{32})~/);
    if (m && !seen[m[1]]) {
      seen[m[1]] = true;
      unique.push({id: m[1], src: img.src, w: img.naturalWidth, h: img.naturalHeight});
    }
  });
  return JSON.stringify(unique.slice(0, 70));
})()
"""

print(js_fetch_all)
