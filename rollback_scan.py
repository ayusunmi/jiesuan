# 回退扫码相关新增代码：删除自定义 ZXing 管线块 + 恢复原始配置
with open(r'd:\段娅楠\D\TREA\6a72d5e85bc2a6f5af65e0d8\index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ===== 第1处：删除自定义 ZXing 解码管线整块（从注释起点到第二个重复的注释起点前）=====
marker_a = '// ====== 原生 BarcodeDetector 扫码（更灵敏）======\n// 原理：html5-qrcode 内部的 ZXing'
marker_b = '// ====== 原生 BarcodeDetector 扫码（更灵敏）======\nlet nativeScanStream = null;'

idx_a = html.find(marker_a)
idx_b = html.find(marker_b)

if idx_a >= 0 and idx_b >= 0 and idx_a < idx_b:
    # 要删除的范围：从 marker_a 开始（但保留 marker_a 行之前的那个空行），到 marker_b 开头之前
    # 实际：我们要保留的代码结构是
    #   }\n\n
    #   // ====== 原生 BarcodeDetector 扫码（更灵敏）======
    #   let nativeScanStream = null;
    # 所以删除范围 = idx_a 到 idx_b（包含 marker_b 的 "// ====== 原生..." 行，因为后面还有一份重复的 "let nativeScanStream..."）
    
    # 找到 marker_a 所在行的行首
    line_start = html.rfind('\n', 0, idx_a) + 1  # 如果找不到 rfind，+1 会等于 0
    delete_from = line_start
    delete_to = idx_b  # 删除到第二份注释之前（第二份 "// ====== 原生 BarcodeDetector..." 要保留）
    
    html = html[:delete_from] + html[delete_to:]
    print(f'第1处OK: 删除自定义管线 {delete_from}-{delete_to}')
else:
    print(f'第1处未匹配: idx_a={idx_a} idx_b={idx_b}')

# ===== 第2处：恢复主路径 Html5Qrcode 构造（去掉 formatsToSupport、disableFlip）=====
old_ctor1 = '''  try{
    // 构造参数：限定解码格式为 EAN-13 系列，关闭 Code128/Code39 等无关格式以降低运算负担
    // disableFlip:false 允许解码器尝试水平镜像翻转的条码（默认即 false，此处显式声明）
    // 不启用 experimentalFeatures.useBarCodeDetectorIfSupported：上一轮已验证华为等机型
    // 原生 BarcodeDetector 识别率倒退，html5-qrcode 该参数底层依赖相同，启用会重蹈覆辙
    let ctorOpts = { verbose: false, disableFlip: false };
    try {
      if (typeof Html5QrcodeSupportedFormats !== 'undefined') {
        ctorOpts.formatsToSupport = [
          Html5QrcodeSupportedFormats.EAN_13,
          Html5QrcodeSupportedFormats.EAN_8,
          Html5QrcodeSupportedFormats.UPC_A,
          Html5QrcodeSupportedFormats.UPC_E
        ];
      }
    } catch (_) {}
    html5Qr = new Html5Qrcode('camWrap', ctorOpts);'''
new_ctor1 = '''  try{
    html5Qr = new Html5Qrcode('camWrap', { verbose: false });'''

if old_ctor1 in html:
    html = html.replace(old_ctor1, new_ctor1)
    print('第2处OK: 恢复主路径构造')
else:
    print('第2处未匹配: 主路径构造')

# ===== 第3处：恢复主路径 config（fps 18, qrbox 0.6×0.2）=====
old_cfg1 = '''    const config = {
      fps: 20,
      // ROI 调整为 0.8×0.6（约 4:3）：原 0.6×0.2 过扁，短宽形状的 EAN-13 条码
      // 无法完整落入解码区域导致识别失败。增大高度比例后，窄长和短宽两种形状都能覆盖。
      // ZXing 解码器内部会尝试 0°/180° 及镜像翻转，无需在此配置旋转角度。
      qrbox: function(vw, vh){
        var w = Math.floor(vw * 0.8);
        var h = Math.floor(vh * 0.6);
        if(w < 160) w = 240;
        if(h < 120) h = 160;
        return { width: w, height: h };
      },
      // 移除 aspectRatio: 华为/部分安卓浏览器强制比例会裁剪放大画面
      videoConstraints: videoConstraints
    };'''
new_cfg1 = '''    const config = {
      fps: 18,
      qrbox: function(vw, vh){
        var w = Math.floor(vw * 0.6);
        var h = Math.floor(vh * 0.2);
        if(w < 120) w = 180;
        if(h < 50) h = 70;
        return { width: w, height: h };
      },
      // 移除 aspectRatio: 华为/部分安卓浏览器强制比例会裁剪放大画面
      videoConstraints: videoConstraints
    };'''

if old_cfg1 in html:
    html = html.replace(old_cfg1, new_cfg1)
    print('第3处OK: 恢复主路径 config')
else:
    print('第3处未匹配: 主路径 config')

# ===== 第4处：删除主路径成功后的 startCustomDecode() 调用 =====
old_line1 = '''    $('scanLoading').classList.remove('show');
    toast('摄像头已启动，对准条形码即可','info');
    // 启动自定义 ZXing 解码管线：裁剪右侧 + 对比度增强，解决二维码邻近干扰
    startCustomDecode();'''
new_line1 = '''    $('scanLoading').classList.remove('show');
    toast('摄像头已启动，对准条形码即可','info');'''

if old_line1 in html:
    html = html.replace(old_line1, new_line1)
    print('第4处OK: 删除主路径 startCustomDecode')
else:
    print('第4处未匹配')

# ===== 第5处：恢复降级路径 Html5Qrcode 构造 =====
old_ctor2 = '''        // 降级路径同样限定 EAN-13 系列格式 + disableFlip:false + 0.8×0.6 ROI
        let fbCtorOpts = { verbose: false, disableFlip: false };
        try {
          if (typeof Html5QrcodeSupportedFormats !== 'undefined') {
            fbCtorOpts.formatsToSupport = [
              Html5QrcodeSupportedFormats.EAN_13,
              Html5QrcodeSupportedFormats.EAN_8,
              Html5QrcodeSupportedFormats.UPC_A,
              Html5QrcodeSupportedFormats.UPC_E
            ];
          }
        } catch (_) {}
        html5Qr = new Html5Qrcode('camWrap', fbCtorOpts);'''
new_ctor2 = '''        html5Qr = new Html5Qrcode('camWrap', { verbose: false });'''

if old_ctor2 in html:
    html = html.replace(old_ctor2, new_ctor2)
    print('第5处OK: 恢复降级路径构造')
else:
    print('第5处未匹配: 降级路径构造')

# ===== 第6处：恢复 fallbackConfig =====
old_cfg2 = '''        const fallbackConfig = {
          fps: 20,
          qrbox: function(vw, vh){
            var w = Math.floor(vw * 0.8);
            var h = Math.floor(vh * 0.6);
            if(w < 160) w = 240;
            if(h < 120) h = 160;
            return { width: w, height: h };
          },
          videoConstraints: {
            facingMode: 'environment',
            width: { min: 480 },
            height: { min: 360 }
          }
        };'''
new_cfg2 = '''        const fallbackConfig = {
          fps: 18,
          qrbox: function(vw, vh){
            var w = Math.floor(vw * 0.6);
            var h = Math.floor(vh * 0.2);
            if(w < 120) w = 180;
            if(h < 50) h = 70;
            return { width: w, height: h };
          },
          videoConstraints: {
            facingMode: 'environment',
            width: { min: 480 },
            height: { min: 360 }
          }
        };'''

if old_cfg2 in html:
    html = html.replace(old_cfg2, new_cfg2)
    print('第6处OK: 恢复 fallbackConfig')
else:
    print('第6处未匹配: fallbackConfig')

# ===== 第7处：删除降级路径成功后的 startCustomDecode() 调用 =====
old_line2 = '''        $('scanLoading').classList.remove('show');
        toast('摄像头已启动，对准条形码即可','info');
        // 降级路径也启动自定义 ZXing 解码管线
        startCustomDecode();
        return; // 降级成功，直接返回不报错'''
new_line2 = '''        $('scanLoading').classList.remove('show');
        toast('摄像头已启动，对准条形码即可','info');
        return; // 降级成功，直接返回不报错'''

if old_line2 in html:
    html = html.replace(old_line2, new_line2)
    print('第7处OK: 删除降级路径 startCustomDecode')
else:
    print('第7处未匹配')

# ===== 第8处：删除 stopScan 中的 stopCustomDecode() 调用 =====
old_stop = '''async function stopScan(){
  // 停止原生扫码
  stopNativeScan();
  // 停止自定义 ZXing 解码管线
  stopCustomDecode();
  // 停止 html5-qrcode'''
new_stop = '''async function stopScan(){
  // 停止原生扫码
  stopNativeScan();
  // 停止 html5-qrcode'''

if old_stop in html:
    html = html.replace(old_stop, new_stop)
    print('第8处OK: 删除 stopCustomDecode')
else:
    print('第8处未匹配')

with open(r'd:\段娅楠\D\TREA\6a72d5e85bc2a6f5af65e0d8\index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('完成')
