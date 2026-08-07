# -*- coding: utf-8 -*-
"""Move qr-payment-section block from after discountRow to after sub line."""

html_path = r'd:\段娅楠\D\TREA\6a72d5e85bc2a6f5af65e0d8\index.html'

with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Find the qr block start and end markers
qr_start_marker = '    <div class="qr-payment-section">\n'
qr_end_marker = '      <div class="qr-hint">请扫描上方二维码完成支付</div>\n    </div>\n'

qr_start_idx = html.find(qr_start_marker)
if qr_start_idx == -1:
    print('ERROR: qr start marker not found')
    exit(1)

qr_end_idx = html.find(qr_end_marker, qr_start_idx)
if qr_end_idx == -1:
    print('ERROR: qr end marker not found')
    exit(1)

qr_end_idx_full = qr_end_idx + len(qr_end_marker)
qr_block = html[qr_start_idx:qr_end_idx_full]
print(f'Found qr block at char {qr_start_idx}-{qr_end_idx_full}, length: {len(qr_block)}')

# Remove qr block from current position
html_without_qr = html[:qr_start_idx] + html[qr_end_idx_full:]
print('Removed qr block from original position')

# Find the sub line to insert after
sub_marker = '    <div class="sub">请核对订单信息后确认</div>\n'
sub_idx = html_without_qr.find(sub_marker)
if sub_idx == -1:
    print('ERROR: sub marker not found')
    exit(1)

insert_pos = sub_idx + len(sub_marker)
print(f'Insert position: {insert_pos} (after sub line)')

# Insert qr block after sub line
html_final = html_without_qr[:insert_pos] + qr_block + html_without_qr[insert_pos:]
print('Inserted qr block after sub line')

# Write back
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html_final)

print(f'File size: {len(html_final.encode("utf-8"))/1024:.1f} KB')
print('SUCCESS')
