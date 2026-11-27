import base64

with open('static/images/logo_official_transparent.png', 'rb') as f:
    b64_logo = base64.b64encode(f.read()).decode('utf-8')
data_uri = f'data:image/png;base64,{b64_logo}'

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace header logo
target_start = '<!-- Logo Officiel ONIZUKA SHOP -->'
target_end = '<!-- Contact Rapide Showroom -->'

start_idx = html.find(target_start)
end_idx = html.find(target_end)

if start_idx != -1 and end_idx != -1:
    new_logo_block = f'''<!-- Logo Officiel ONIZUKA SHOP -->
    <div class="flex items-center gap-3">
      <img src="{data_uri}" alt="ONIZUKA SHOP" class="h-10 sm:h-12 w-auto object-contain shrink-0 filter drop-shadow-[0_2px_12px_rgba(245,158,11,0.25)]">
      <div class="hidden sm:block border-l border-slate-800 pl-3 leading-tight">
        <p class="text-[11px] text-amber-400 font-bold uppercase tracking-wider">Boutique Officielle</p>
        <p class="text-[10px] text-slate-400 font-medium">Grand Marché de Bamako • Dibidani</p>
      </div>
    </div>

    '''
    html = html[:start_idx] + new_logo_block + html[end_idx:]
    print("Header logo replaced successfully!")
else:
    print("Could not find logo anchors in index.html")

# Replace Dabanani with Dibidani
html = html.replace('Dabanani', 'Dibidani').replace('dabanani', 'dibidani')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("index.html updated with official logo and Dibidani.")
