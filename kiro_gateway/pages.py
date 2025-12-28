# -*- coding: utf-8 -*-

"""
KiroGate Frontend Pages.

HTML templates for the web interface.
"""

from kiro_gateway.config import APP_VERSION, AVAILABLE_MODELS
import json

# Static assets proxy base
PROXY_BASE = "https://proxy.jhun.edu.kg"

# SEO and common head
COMMON_HEAD = f'''
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>KiroGate - OpenAI & Anthropic 兼容的 Kiro API 代理网关</title>

  <!-- SEO Meta Tags -->
  <meta name="description" content="KiroGate 是一个开源的 Kiro IDE API 代理网关，支持 OpenAI 和 Anthropic API 格式，让你可以通过任何兼容的工具使用 Claude 模型。支持流式传输、工具调用、多租户等特性。">
  <meta name="keywords" content="KiroGate, Kiro, Claude, OpenAI, Anthropic, API Gateway, Proxy, AI, LLM, Claude Code, Python, FastAPI, 代理网关">
  <meta name="author" content="KiroGate">
  <meta name="robots" content="index, follow">

  <!-- Open Graph / Facebook -->
  <meta property="og:type" content="website">
  <meta property="og:title" content="KiroGate - OpenAI & Anthropic 兼容的 Kiro API 代理网关">
  <meta property="og:description" content="开源的 Kiro IDE API 代理网关，支持 OpenAI 和 Anthropic API 格式，通过任何兼容工具使用 Claude 模型。">
  <meta property="og:site_name" content="KiroGate">

  <!-- Twitter -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="KiroGate - OpenAI & Anthropic 兼容的 Kiro API 代理网关">
  <meta name="twitter:description" content="开源的 Kiro IDE API 代理网关，支持 OpenAI 和 Anthropic API 格式，通过任何兼容工具使用 Claude 模型。">

  <!-- Favicon -->
  <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🚀</text></svg>">

  <script src="{PROXY_BASE}/proxy/cdn.tailwindcss.com"></script>
  <script src="{PROXY_BASE}/proxy/cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
  <script src="{PROXY_BASE}/proxy/cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js"></script>
  <style>
    :root {{
      --primary: #6366f1;
      --primary-dark: #4f46e5;
    }}

    /* Light mode (default) */
    [data-theme="light"] {{
      --bg-main: #ffffff;
      --bg-card: #f8fafc;
      --bg-nav: #ffffff;
      --bg-input: #ffffff;
      --text: #0f172a;
      --text-muted: #64748b;
      --border: #e2e8f0;
      --border-dark: #cbd5e1;
    }}

    /* Dark mode */
    [data-theme="dark"] {{
      --bg-main: #0f172a;
      --bg-card: #1e293b;
      --bg-nav: #1e293b;
      --bg-input: #334155;
      --text: #e2e8f0;
      --text-muted: #94a3b8;
      --border: #334155;
      --border-dark: #475569;
    }}

    body {{
      background: var(--bg-main);
      color: var(--text);
      font-family: system-ui, -apple-system, sans-serif;
      transition: background-color 0.3s, color 0.3s;
    }}
    .card {{
      background: var(--bg-card);
      border-radius: 0.75rem;
      padding: 1.5rem;
      border: 1px solid var(--border);
      transition: background-color 0.3s, border-color 0.3s;
    }}
    .btn-primary {{
      background: var(--primary);
      color: white;
      padding: 0.5rem 1rem;
      border-radius: 0.5rem;
      transition: all 0.2s;
    }}
    .btn-primary:hover {{ background: var(--primary-dark); }}
    .nav-link {{
      color: var(--text-muted);
      transition: color 0.2s;
    }}
    .nav-link:hover, .nav-link.active {{ color: var(--primary); }}
    .theme-toggle {{
      cursor: pointer;
      padding: 0.5rem;
      border-radius: 0.5rem;
      transition: background-color 0.2s;
    }}
    .theme-toggle:hover {{
      background: var(--bg-card);
    }}
    /* 代码块优化 */
    pre {{
      max-width: 100%;
      overflow-x: auto;
      -webkit-overflow-scrolling: touch;
    }}
    pre::-webkit-scrollbar {{
      height: 6px;
    }}
    pre::-webkit-scrollbar-track {{
      background: var(--bg-input);
      border-radius: 3px;
    }}
    pre::-webkit-scrollbar-thumb {{
      background: var(--border-dark);
      border-radius: 3px;
    }}
    /* 加载动画 */
    .loading-spinner {{
      display: inline-block;
      width: 20px;
      height: 20px;
      border: 2px solid var(--border);
      border-radius: 50%;
      border-top-color: var(--primary);
      animation: spin 0.8s linear infinite;
    }}
    @keyframes spin {{
      to {{ transform: rotate(360deg); }}
    }}
    .loading-pulse {{
      animation: pulse 1.5s ease-in-out infinite;
    }}
    @keyframes pulse {{
      0%, 100% {{ opacity: 1; }}
      50% {{ opacity: 0.5; }}
    }}
    /* 表格响应式 */
    .table-responsive {{
      overflow-x: auto;
      -webkit-overflow-scrolling: touch;
    }}
    .table-responsive::-webkit-scrollbar {{
      height: 6px;
    }}
    .table-responsive::-webkit-scrollbar-track {{
      background: var(--bg-input);
    }}
    .table-responsive::-webkit-scrollbar-thumb {{
      background: var(--border-dark);
      border-radius: 3px;
    }}
  </style>
  <script>
    // Theme initialization
    (function() {{
      const theme = localStorage.getItem('theme') || 'light';
      document.documentElement.setAttribute('data-theme', theme);
    }})();
  </script>
'''

COMMON_NAV = f'''
  <nav style="background: var(--bg-nav); border-bottom: 1px solid var(--border);" class="sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between h-16">
        <div class="flex items-center space-x-8">
          <a href="/" class="text-2xl font-bold text-indigo-500">⚡ KiroGate</a>
          <div class="hidden md:flex space-x-6">
            <a href="/" class="nav-link">首页</a>
            <a href="/docs" class="nav-link">文档</a>
            <a href="/swagger" class="nav-link">接口</a>
            <a href="/playground" class="nav-link">测试</a>
            <a href="/deploy" class="nav-link">部署</a>
            <a href="/dashboard" class="nav-link">面板</a>
          </div>
        </div>
        <div class="flex items-center space-x-4">
          <!-- 登录/用户按钮区域 -->
          <div id="auth-btn-area">
            <a href="/login" id="login-btn" class="hidden sm:inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all hover:opacity-90" style="background: var(--primary); color: white;">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1"/></svg>
              登录
            </a>
          </div>
          <button onclick="toggleTheme()" class="theme-toggle" title="切换主题">
            <svg id="theme-icon-sun" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" style="display: none;">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"/>
            </svg>
            <svg id="theme-icon-moon" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" style="display: none;">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"/>
            </svg>
          </button>
          <span class="hidden sm:inline text-sm" style="color: var(--text-muted);">v{APP_VERSION}</span>
          <!-- 移动端汉堡菜单按钮 -->
          <button onclick="toggleMobileMenu()" class="md:hidden theme-toggle" title="菜单">
            <svg id="menu-icon-open" class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
            </svg>
            <svg id="menu-icon-close" class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" style="display: none;">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>
      </div>
    </div>
    <!-- 移动端导航菜单 -->
    <div id="mobile-menu" class="md:hidden hidden" style="background: var(--bg-nav); border-top: 1px solid var(--border);">
      <div class="px-4 py-3 space-y-2">
        <a href="/" class="block nav-link py-2 px-3 rounded hover:bg-indigo-500/10">首页</a>
        <a href="/docs" class="block nav-link py-2 px-3 rounded hover:bg-indigo-500/10">文档</a>
        <a href="/swagger" class="block nav-link py-2 px-3 rounded hover:bg-indigo-500/10">接口</a>
        <a href="/playground" class="block nav-link py-2 px-3 rounded hover:bg-indigo-500/10">测试</a>
        <a href="/deploy" class="block nav-link py-2 px-3 rounded hover:bg-indigo-500/10">部署</a>
        <a href="/dashboard" class="block nav-link py-2 px-3 rounded hover:bg-indigo-500/10">面板</a>
        <div id="mobile-auth-area" class="pt-2 mt-2" style="border-top: 1px solid var(--border);">
          <a href="/login" class="block py-2 px-3 rounded text-center font-medium" style="background: var(--primary); color: white;">登录</a>
        </div>
      </div>
    </div>
  </nav>
  <script>
    function toggleTheme() {{
      const html = document.documentElement;
      const currentTheme = html.getAttribute('data-theme');
      const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
      html.setAttribute('data-theme', newTheme);
      localStorage.setItem('theme', newTheme);
      updateThemeIcon();
    }}

    function updateThemeIcon() {{
      const theme = document.documentElement.getAttribute('data-theme');
      const sunIcon = document.getElementById('theme-icon-sun');
      const moonIcon = document.getElementById('theme-icon-moon');
      if (theme === 'dark') {{
        sunIcon.style.display = 'block';
        moonIcon.style.display = 'none';
      }} else {{
        sunIcon.style.display = 'none';
        moonIcon.style.display = 'block';
      }}
    }}

    function toggleMobileMenu() {{
      const menu = document.getElementById('mobile-menu');
      const openIcon = document.getElementById('menu-icon-open');
      const closeIcon = document.getElementById('menu-icon-close');
      const isHidden = menu.classList.contains('hidden');

      if (isHidden) {{
        menu.classList.remove('hidden');
        openIcon.style.display = 'none';
        closeIcon.style.display = 'block';
      }} else {{
        menu.classList.add('hidden');
        openIcon.style.display = 'block';
        closeIcon.style.display = 'none';
      }}
    }}

    // Initialize icon on page load
    document.addEventListener('DOMContentLoaded', updateThemeIcon);

    // Check auth status and update button
    (async function checkAuth() {{
      try {{
        const r = await fetch('/user/api/profile');
        if (r.ok) {{
          const d = await r.json();
          const area = document.getElementById('auth-btn-area');
          const mobileArea = document.getElementById('mobile-auth-area');
          if (area) {{
            area.innerHTML = `<a href="/user" class="hidden sm:flex items-center gap-2 nav-link font-medium">
              <span class="w-7 h-7 rounded-full flex items-center justify-center text-sm text-white" style="background: var(--primary);">${{(d.username || 'U')[0].toUpperCase()}}</span>
              <span>${{d.username || '用户'}}</span>
            </a>`;
          }}
          if (mobileArea) {{
            mobileArea.innerHTML = `<a href="/user" class="flex items-center justify-center gap-2 py-2 px-3 rounded font-medium" style="background: var(--bg-card); border: 1px solid var(--border);">
              <span class="w-6 h-6 rounded-full flex items-center justify-center text-xs text-white" style="background: var(--primary);">${{(d.username || 'U')[0].toUpperCase()}}</span>
              <span>${{d.username || '用户中心'}}</span>
            </a>`;
          }}
        }}
      }} catch {{}}
    }})();
  </script>
'''

COMMON_FOOTER = '''
  <footer style="background: var(--bg-nav); border-top: 1px solid var(--border);" class="py-6 sm:py-8 mt-12 sm:mt-16">
    <div class="max-w-7xl mx-auto px-4 text-center" style="color: var(--text-muted);">
      <p class="text-sm sm:text-base">KiroGate - OpenAI & Anthropic 兼容的 Kiro API 网关</p>
      <div class="mt-3 sm:mt-4 flex flex-wrap justify-center gap-x-4 gap-y-2 text-xs sm:text-sm">
        <span class="flex items-center gap-1">
          <span style="color: var(--text);">Deno</span>
          <a href="https://kirogate.deno.dev" class="text-indigo-400 hover:underline" target="_blank">Demo</a>
          <span>·</span>
          <a href="https://github.com/dext7r/KiroGate" class="text-indigo-400 hover:underline" target="_blank">GitHub</a>
        </span>
        <span class="hidden sm:inline" style="color: var(--border-dark);">|</span>
        <span class="flex items-center gap-1">
          <span style="color: var(--text);">Python</span>
          <a href="https://kirogate.fly.dev" class="text-indigo-400 hover:underline" target="_blank">Demo</a>
          <span>·</span>
          <a href="https://github.com/aliom-v/KiroGate" class="text-indigo-400 hover:underline" target="_blank">GitHub</a>
        </span>
      </div>
      <p class="mt-3 text-xs sm:text-sm opacity-75">欲买桂花同载酒 终不似少年游</p>
    </div>
  </footer>
'''

# 移除旧的 THEME_SCRIPT，已经集成到 COMMON_NAV 中


def render_home_page() -> str:
    """Render the home page."""
    models_json = json.dumps(AVAILABLE_MODELS)

    return f'''<!DOCTYPE html>
<html lang="zh">
<head>{COMMON_HEAD}</head>
<body>
  {COMMON_NAV}

  <main class="max-w-7xl mx-auto px-4 py-8 sm:py-12">
    <!-- Hero Section -->
    <section class="text-center py-8 sm:py-16">
      <h1 class="text-3xl sm:text-4xl md:text-5xl font-bold mb-4 sm:mb-6 bg-gradient-to-r from-indigo-400 to-purple-500 bg-clip-text text-transparent">
        KiroGate API 网关
      </h1>
      <p class="text-base sm:text-xl mb-6 sm:mb-8 max-w-2xl mx-auto px-4" style="color: var(--text-muted);">
        将 OpenAI 和 Anthropic API 请求无缝代理到 Kiro (AWS CodeWhisperer)，
        支持完整的流式传输、工具调用和多模型切换。
      </p>
      <div class="flex flex-col sm:flex-row justify-center gap-3 sm:gap-4 px-4">
        <a href="/docs" class="btn-primary text-base sm:text-lg px-6 py-3">📖 查看文档</a>
        <a href="/playground" class="btn-primary text-base sm:text-lg px-6 py-3" style="background: var(--bg-card); border: 1px solid var(--border); color: var(--text);">🎮 在线试用</a>
      </div>
    </section>

    <!-- Features Grid -->
    <section class="grid md:grid-cols-3 gap-6 py-12">
      <div class="card">
        <div class="text-3xl mb-4">🔄</div>
        <h3 class="text-xl font-semibold mb-2">双 API 兼容</h3>
        <p style="color: var(--text-muted);">同时支持 OpenAI 和 Anthropic API 格式，无需修改现有代码。</p>
      </div>
      <div class="card">
        <div class="text-3xl mb-4">⚡</div>
        <h3 class="text-xl font-semibold mb-2">流式传输</h3>
        <p style="color: var(--text-muted);">完整的 SSE 流式支持，实时获取模型响应。</p>
      </div>
      <div class="card">
        <div class="text-3xl mb-4">🔧</div>
        <h3 class="text-xl font-semibold mb-2">工具调用</h3>
        <p style="color: var(--text-muted);">支持 Function Calling，构建强大的 AI Agent。</p>
      </div>
      <div class="card">
        <div class="text-3xl mb-4">👥</div>
        <h3 class="text-xl font-semibold mb-2">用户系统</h3>
        <p style="color: var(--text-muted);">支持 LinuxDo/GitHub 登录，捐献 Token 获取 API Key。</p>
      </div>
      <div class="card">
        <div class="text-3xl mb-4">🔑</div>
        <h3 class="text-xl font-semibold mb-2">API Key 生成</h3>
        <p style="color: var(--text-muted);">生成 sk-xxx 格式密钥，与 OpenAI 客户端无缝兼容。</p>
      </div>
      <div class="card">
        <div class="text-3xl mb-4">🎁</div>
        <h3 class="text-xl font-semibold mb-2">Token 共享池</h3>
        <p style="color: var(--text-muted);">公开捐献的 Token 组成共享池，智能负载均衡。</p>
      </div>
      <div class="card">
        <div class="text-3xl mb-4">🔁</div>
        <h3 class="text-xl font-semibold mb-2">自动重试</h3>
        <p style="color: var(--text-muted);">智能处理 403/429/5xx 错误，自动刷新 Token。</p>
      </div>
      <div class="card">
        <div class="text-3xl mb-4">📊</div>
        <h3 class="text-xl font-semibold mb-2">监控面板</h3>
        <p style="color: var(--text-muted);">实时查看请求统计、响应时间和模型使用情况。</p>
      </div>
      <div class="card">
        <div class="text-3xl mb-4">🛡️</div>
        <h3 class="text-xl font-semibold mb-2">Admin 后台</h3>
        <p style="color: var(--text-muted);">用户管理、Token 池管理、IP 黑名单等功能。</p>
      </div>
    </section>

    <!-- Models Chart -->
    <section class="py-12">
      <h2 class="text-2xl font-bold mb-6 text-center">📈 支持的模型</h2>
      <div class="card">
        <div id="modelsChart" style="height: 300px;"></div>
      </div>
    </section>
  </main>

  {COMMON_FOOTER}

  <script>
    // ECharts 模型展示图
    const modelsChart = echarts.init(document.getElementById('modelsChart'));
    modelsChart.setOption({{
      tooltip: {{ trigger: 'axis' }},
      xAxis: {{
        type: 'category',
        data: {models_json},
        axisLabel: {{ rotate: 45, color: '#94a3b8' }},
        axisLine: {{ lineStyle: {{ color: '#334155' }} }}
      }},
      yAxis: {{
        type: 'value',
        name: '性能指数',
        axisLabel: {{ color: '#94a3b8' }},
        axisLine: {{ lineStyle: {{ color: '#334155' }} }},
        splitLine: {{ lineStyle: {{ color: '#1e293b' }} }}
      }},
      series: [{{
        name: '模型能力',
        type: 'bar',
        data: [100, 100, 70, 90, 90, 85, 85, 80],
        itemStyle: {{
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            {{ offset: 0, color: '#6366f1' }},
            {{ offset: 1, color: '#4f46e5' }}
          ])
        }}
      }}]
    }});
    window.addEventListener('resize', () => modelsChart.resize());
  </script>
</body>
</html>'''


def render_docs_page() -> str:
    """Render the API documentation page."""
    return f'''<!DOCTYPE html>
<html lang="zh">
<head>{COMMON_HEAD}</head>
<body>
  {COMMON_NAV}

  <main class="max-w-7xl mx-auto px-4 py-12">
    <h1 class="text-4xl font-bold mb-8">📖 API 文档</h1>

    <div class="space-y-8">
      <section class="card">
        <h2 class="text-2xl font-semibold mb-4">🔑 认证</h2>
        <p style="color: var(--text-muted);" class="mb-4">所有 API 请求需要在 Header 中携带 API Key。支持三种认证模式：</p>

        <h3 class="text-lg font-medium mb-2 text-indigo-400">模式 1: 用户 API Key（sk-xxx 格式）🌟 最简单</h3>
        <pre style="background: var(--bg-input); border: 1px solid var(--border); color: var(--text);" class="p-4 rounded-lg overflow-x-auto text-sm mb-4">
# OpenAI 格式
Authorization: Bearer sk-xxxxxxxxxxxxxxxx

# Anthropic 格式
x-api-key: sk-xxxxxxxxxxxxxxxx</pre>
        <p class="text-sm mb-4" style="color: var(--text-muted);">登录后在用户中心生成，自动使用您捐献的 Token 或公开 Token 池。</p>

        <h3 class="text-lg font-medium mb-2 text-indigo-400">模式 2: 组合模式（用户自带 REFRESH_TOKEN）</h3>
        <pre style="background: var(--bg-input); border: 1px solid var(--border); color: var(--text);" class="p-4 rounded-lg overflow-x-auto text-sm mb-4">
# OpenAI 格式
Authorization: Bearer YOUR_PROXY_API_KEY:YOUR_REFRESH_TOKEN

# Anthropic 格式
x-api-key: YOUR_PROXY_API_KEY:YOUR_REFRESH_TOKEN</pre>

        <h3 class="text-lg font-medium mb-2 text-indigo-400">模式 3: 简单模式（使用服务器配置的 REFRESH_TOKEN）</h3>
        <pre style="background: var(--bg-input); border: 1px solid var(--border); color: var(--text);" class="p-4 rounded-lg overflow-x-auto text-sm">
# OpenAI 格式
Authorization: Bearer YOUR_PROXY_API_KEY

# Anthropic 格式
x-api-key: YOUR_PROXY_API_KEY</pre>

        <div style="background: var(--bg-input); border: 1px solid var(--border);" class="p-4 rounded-lg mt-4">
          <p class="text-sm" style="color: var(--text-muted);">
            <strong>💡 推荐使用方式：</strong>
          </p>
          <ul class="text-sm mt-2 space-y-1" style="color: var(--text-muted);">
            <li>• <strong>普通用户</strong>：登录后生成 <code>sk-xxx</code> 格式的 API Key，最简单易用</li>
            <li>• <strong>自部署用户</strong>：使用组合模式，自带 REFRESH_TOKEN，无需服务器配置</li>
            <li>• <strong>缓存优化</strong>：每个用户的认证信息会被缓存（最多100个用户），提升性能</li>
          </ul>
        </div>
      </section>

      <section class="card">
        <h2 class="text-2xl font-semibold mb-4">📡 端点列表</h2>
        <div class="space-y-4">
          <div style="background: var(--bg-input); border: 1px solid var(--border);" class="p-4 rounded-lg">
            <div class="flex items-center gap-2 mb-2">
              <span class="px-2 py-1 text-xs font-bold rounded bg-green-500 text-white">GET</span>
              <code>/</code>
            </div>
            <p class="text-sm" style="color: var(--text-muted);">健康检查端点</p>
          </div>
          <div style="background: var(--bg-input); border: 1px solid var(--border);" class="p-4 rounded-lg">
            <div class="flex items-center gap-2 mb-2">
              <span class="px-2 py-1 text-xs font-bold rounded bg-green-500 text-white">GET</span>
              <code>/health</code>
            </div>
            <p class="text-sm" style="color: var(--text-muted);">详细健康检查，返回 token 状态和缓存信息</p>
          </div>
          <div style="background: var(--bg-input); border: 1px solid var(--border);" class="p-4 rounded-lg">
            <div class="flex items-center gap-2 mb-2">
              <span class="px-2 py-1 text-xs font-bold rounded bg-green-500 text-white">GET</span>
              <code>/v1/models</code>
            </div>
            <p class="text-sm" style="color: var(--text-muted);">获取可用模型列表 (需要认证)</p>
          </div>
          <div style="background: var(--bg-input); border: 1px solid var(--border);" class="p-4 rounded-lg">
            <div class="flex items-center gap-2 mb-2">
              <span class="px-2 py-1 text-xs font-bold rounded bg-blue-500 text-white">POST</span>
              <code>/v1/chat/completions</code>
            </div>
            <p class="text-sm" style="color: var(--text-muted);">OpenAI 兼容的聊天补全 API (需要认证)</p>
          </div>
          <div style="background: var(--bg-input); border: 1px solid var(--border);" class="p-4 rounded-lg">
            <div class="flex items-center gap-2 mb-2">
              <span class="px-2 py-1 text-xs font-bold rounded bg-blue-500 text-white">POST</span>
              <code>/v1/messages</code>
            </div>
            <p class="text-sm" style="color: var(--text-muted);">Anthropic 兼容的消息 API (需要认证)</p>
          </div>
        </div>
      </section>

      <section class="card">
        <h2 class="text-2xl font-semibold mb-4">💡 使用示例</h2>
        <h3 class="text-lg font-medium mb-2 text-indigo-400">OpenAI SDK (Python)</h3>
        <pre style="background: var(--bg-input); border: 1px solid var(--border); color: var(--text);" class="p-4 rounded-lg overflow-x-auto text-sm mb-4">
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="YOUR_PROXY_API_KEY"
)

response = client.chat.completions.create(
    model="claude-sonnet-4-5",
    messages=[{{"role": "user", "content": "Hello!"}}],
    stream=True
)

for chunk in response:
    print(chunk.choices[0].delta.content, end="")</pre>

        <h3 class="text-lg font-medium mb-2 text-indigo-400">Anthropic SDK (Python)</h3>
        <pre style="background: var(--bg-input); border: 1px solid var(--border); color: var(--text);" class="p-4 rounded-lg overflow-x-auto text-sm mb-4">
import anthropic

client = anthropic.Anthropic(
    base_url="http://localhost:8000",
    api_key="YOUR_PROXY_API_KEY"
)

message = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=1024,
    messages=[{{"role": "user", "content": "Hello!"}}]
)

print(message.content[0].text)</pre>

        <h3 class="text-lg font-medium mb-2 text-indigo-400">cURL</h3>
        <pre style="background: var(--bg-input); border: 1px solid var(--border); color: var(--text);" class="p-4 rounded-lg overflow-x-auto text-sm">
curl http://localhost:8000/v1/chat/completions \\
  -H "Authorization: Bearer YOUR_PROXY_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "model": "claude-sonnet-4-5",
    "messages": [{{"role": "user", "content": "Hello!"}}]
  }}'</pre>
      </section>

      <section class="card">
        <h2 class="text-2xl font-semibold mb-4">🤖 可用模型</h2>
        <ul class="grid md:grid-cols-2 gap-2">
          {"".join([f'<li style="background: var(--bg-input); border: 1px solid var(--border);" class="px-4 py-2 rounded text-sm"><code>{m}</code></li>' for m in AVAILABLE_MODELS])}
        </ul>
      </section>
    </div>
  </main>

  {COMMON_FOOTER}
</body>
</html>'''


def render_playground_page() -> str:
    """Render the API playground page."""
    models_options = "".join([f'<option value="{m}">{m}</option>' for m in AVAILABLE_MODELS])

    return f'''<!DOCTYPE html>
<html lang="zh">
<head>{COMMON_HEAD}</head>
<body>
  {COMMON_NAV}

  <main class="max-w-7xl mx-auto px-4 py-12">
    <h1 class="text-4xl font-bold mb-8">🎮 API Playground</h1>

    <div class="grid md:grid-cols-2 gap-6">
      <!-- Request Panel -->
      <div class="card">
        <h2 class="text-xl font-semibold mb-4">请求配置</h2>

        <div class="space-y-4">
          <div>
            <label class="block text-sm mb-1" style="color: var(--text-muted);">API Key</label>
            <input type="password" id="apiKey" style="background: var(--bg-input); border: 1px solid var(--border); color: var(--text);" class="w-full rounded px-3 py-2" placeholder="sk-xxx 或 PROXY_KEY 或 PROXY_KEY:REFRESH_TOKEN" oninput="updateAuthMode()">
            <div id="authModeDisplay" class="mt-2 text-sm flex items-center gap-2">
              <span id="authModeIcon">🔒</span>
              <span id="authModeText" style="color: var(--text-muted);">支持 sk-xxx / PROXY_KEY / PROXY_KEY:TOKEN 三种格式</span>
            </div>
          </div>

          <div>
            <label class="block text-sm mb-1" style="color: var(--text-muted);">模型</label>
            <select id="model" style="background: var(--bg-input); border: 1px solid var(--border); color: var(--text);" class="w-full rounded px-3 py-2">
              {models_options}
            </select>
          </div>

          <div>
            <label class="block text-sm mb-1" style="color: var(--text-muted);">消息内容</label>
            <textarea id="message" rows="4" style="background: var(--bg-input); border: 1px solid var(--border); color: var(--text);" class="w-full rounded px-3 py-2" placeholder="输入你的消息...">Hello! Please introduce yourself briefly.</textarea>
          </div>

          <div class="flex items-center gap-4">
            <label class="flex items-center gap-2">
              <input type="checkbox" id="stream" checked class="rounded">
              <span class="text-sm">流式响应</span>
            </label>
            <label class="flex items-center gap-2">
              <input type="radio" name="apiFormat" value="openai" checked>
              <span class="text-sm">OpenAI 格式</span>
            </label>
            <label class="flex items-center gap-2">
              <input type="radio" name="apiFormat" value="anthropic">
              <span class="text-sm">Anthropic 格式</span>
            </label>
          </div>

          <button id="sendBtn" onclick="sendRequest()" class="btn-primary w-full py-3 text-base sm:text-lg">
            <span id="sendBtnText">🚀 发送请求</span>
            <span id="sendBtnLoading" class="hidden"><span class="loading-spinner mr-2"></span>请求中...</span>
          </button>
        </div>
      </div>

      <!-- Response Panel -->
      <div class="card">
        <h2 class="text-lg sm:text-xl font-semibold mb-4">响应结果</h2>
        <div id="response" style="background: var(--bg-input); border: 1px solid var(--border); color: var(--text);" class="rounded p-3 sm:p-4 min-h-[250px] sm:min-h-[300px] whitespace-pre-wrap text-xs sm:text-sm font-mono overflow-auto">
          <span style="color: var(--text-muted);">响应将显示在这里...</span>
        </div>
        <div id="stats" class="mt-3 sm:mt-4 text-xs sm:text-sm" style="color: var(--text-muted);"></div>
      </div>
    </div>
  </main>

  {COMMON_FOOTER}

  <script>
    function updateAuthMode() {{
      const apiKey = document.getElementById('apiKey').value;
      const iconEl = document.getElementById('authModeIcon');
      const textEl = document.getElementById('authModeText');

      if (!apiKey) {{
        iconEl.textContent = '🔒';
        textEl.innerHTML = '支持 sk-xxx / PROXY_KEY / PROXY_KEY:TOKEN 三种格式';
        textEl.style.color = 'var(--text-muted)';
        return;
      }}

      if (apiKey.startsWith('sk-')) {{
        iconEl.textContent = '🔑';
        textEl.innerHTML = '<span style="color: #22c55e; font-weight: 600;">用户 API Key</span> <span style="color: var(--text-muted);">- 使用您的 Token 或公开池</span>';
      }} else if (apiKey.includes(':')) {{
        iconEl.textContent = '👥';
        textEl.innerHTML = '<span style="color: #3b82f6; font-weight: 600;">组合模式</span> <span style="color: var(--text-muted);">- PROXY_KEY:REFRESH_TOKEN</span>';
      }} else {{
        iconEl.textContent = '🔐';
        textEl.innerHTML = '<span style="color: #f59e0b; font-weight: 600;">简单模式</span> <span style="color: var(--text-muted);">- 使用服务器 Token</span>';
      }}
    }}

    async function sendRequest() {{
      const apiKey = document.getElementById('apiKey').value;
      const model = document.getElementById('model').value;
      const message = document.getElementById('message').value;
      const stream = document.getElementById('stream').checked;
      const format = document.querySelector('input[name="apiFormat"]:checked').value;

      const responseEl = document.getElementById('response');
      const statsEl = document.getElementById('stats');
      const sendBtn = document.getElementById('sendBtn');
      const sendBtnText = document.getElementById('sendBtnText');
      const sendBtnLoading = document.getElementById('sendBtnLoading');

      // 显示加载状态
      sendBtn.disabled = true;
      sendBtnText.classList.add('hidden');
      sendBtnLoading.classList.remove('hidden');
      responseEl.innerHTML = '<span class="loading-pulse" style="color: var(--text-muted);">请求中...</span>';
      statsEl.textContent = '';

      const startTime = Date.now();

      try {{
        const endpoint = format === 'openai' ? '/v1/chat/completions' : '/v1/messages';
        const headers = {{
          'Content-Type': 'application/json',
        }};

        if (format === 'openai') {{
          headers['Authorization'] = 'Bearer ' + apiKey;
        }} else {{
          headers['x-api-key'] = apiKey;
        }}

        const body = format === 'openai' ? {{
          model,
          messages: [{{ role: 'user', content: message }}],
          stream
        }} : {{
          model,
          max_tokens: 1024,
          messages: [{{ role: 'user', content: message }}],
          stream
        }};

        const response = await fetch(endpoint, {{
          method: 'POST',
          headers,
          body: JSON.stringify(body)
        }});

        if (!response.ok) {{
          const error = await response.text();
          throw new Error(error);
        }}

        if (stream) {{
          responseEl.textContent = '';
          const reader = response.body.getReader();
          const decoder = new TextDecoder();
          let fullContent = '';
          let buffer = '';

          while (true) {{
            const {{ done, value }} = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, {{ stream: true }});
            const lines = buffer.split('\\n');
            buffer = lines.pop() || '';

            for (let i = 0; i < lines.length; i++) {{
              const line = lines[i].trim();

              if (format === 'openai') {{
                if (line.startsWith('data: ') && !line.includes('[DONE]')) {{
                  try {{
                    const data = JSON.parse(line.slice(6));
                    const content = data.choices?.[0]?.delta?.content || '';
                    fullContent += content;
                  }} catch {{}}
                }}
              }} else if (format === 'anthropic') {{
                if (line.startsWith('event: content_block_delta')) {{
                  const nextLine = lines[i + 1];
                  if (nextLine && nextLine.trim().startsWith('data: ')) {{
                    try {{
                      const data = JSON.parse(nextLine.trim().slice(6));
                      if (data.delta?.text) {{
                        fullContent += data.delta.text;
                      }}
                    }} catch {{}}
                  }}
                }}
              }}
            }}
            responseEl.textContent = fullContent;
          }}
        }} else {{
          const data = await response.json();
          if (format === 'openai') {{
            responseEl.textContent = data.choices?.[0]?.message?.content || JSON.stringify(data, null, 2);
          }} else {{
            const text = data.content?.find(c => c.type === 'text')?.text || JSON.stringify(data, null, 2);
            responseEl.textContent = text;
          }}
        }}

        const duration = ((Date.now() - startTime) / 1000).toFixed(2);
        statsEl.textContent = '耗时: ' + duration + 's';

      }} catch (e) {{
        responseEl.textContent = '错误: ' + e.message;
      }} finally {{
        // 恢复按钮状态
        sendBtn.disabled = false;
        sendBtnText.classList.remove('hidden');
        sendBtnLoading.classList.add('hidden');
      }}
    }}
  </script>
</body>
</html>'''


def render_deploy_page() -> str:
    """Render the deployment guide page."""
    return f'''<!DOCTYPE html>
<html lang="zh">
<head>{COMMON_HEAD}</head>
<body>
  {COMMON_NAV}

  <main class="max-w-7xl mx-auto px-4 py-12">
    <h1 class="text-4xl font-bold mb-8">🚀 部署指南</h1>

    <div class="space-y-8">
      <section class="card">
        <h2 class="text-2xl font-semibold mb-4">📋 环境要求</h2>
        <ul class="list-disc list-inside space-y-2" style="color: var(--text-muted);">
          <li>Python 3.10+</li>
          <li>pip 或 poetry</li>
          <li>网络连接（需访问 AWS CodeWhisperer API）</li>
        </ul>
      </section>

      <section class="card">
        <h2 class="text-2xl font-semibold mb-4">⚙️ 环境变量配置</h2>
        <pre style="background: var(--bg-input); border: 1px solid var(--border); color: var(--text);" class="p-4 rounded-lg overflow-x-auto text-sm">
# 必填项
PROXY_API_KEY="your-secret-api-key"      # 代理服务器密码

# 可选项（仅简单模式需要）
# 如果使用组合模式（PROXY_API_KEY:REFRESH_TOKEN），可以不配置此项
REFRESH_TOKEN="your-kiro-refresh-token"  # Kiro Refresh Token

# 其他可选配置
KIRO_REGION="us-east-1"                  # AWS 区域
PROFILE_ARN="arn:aws:..."                # Profile ARN
LOG_LEVEL="INFO"                          # 日志级别

# 或使用凭证文件
KIRO_CREDS_FILE="~/.kiro/credentials.json"</pre>

        <div style="background: var(--bg-input); border: 1px solid var(--border);" class="p-4 rounded-lg mt-4">
          <p class="text-sm font-semibold mb-2" style="color: var(--text);">配置说明：</p>
          <ul class="text-sm space-y-1" style="color: var(--text-muted);">
            <li>• <strong>简单模式</strong>：必须配置 <code>REFRESH_TOKEN</code> 环境变量</li>
            <li>• <strong>组合模式（推荐）</strong>：无需配置 <code>REFRESH_TOKEN</code>，用户在请求中直接传递</li>
            <li>• <strong>多租户部署</strong>：使用组合模式可以让多个用户共享同一网关实例</li>
          </ul>
        </div>
      </section>

      <section class="card">
        <h2 class="text-2xl font-semibold mb-4">🐍 本地运行</h2>
        <pre style="background: var(--bg-input); border: 1px solid var(--border); color: var(--text);" class="p-4 rounded-lg overflow-x-auto text-sm">
# 克隆仓库
git clone https://github.com/dext7r/KiroGate.git
cd KiroGate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 填写配置

# 启动服务
python main.py</pre>
      </section>

      <section class="card">
        <h2 class="text-2xl font-semibold mb-4 flex items-center gap-2">
          <span>🐳</span>
          <span>Docker 部署</span>
        </h2>
        <h3 class="text-lg font-medium mb-2 text-indigo-400">Docker Compose（推荐）</h3>
        <pre style="background: var(--bg-input); border: 1px solid var(--border); color: var(--text);" class="p-4 rounded-lg overflow-x-auto text-sm mb-4">
# 复制配置文件
cp .env.example .env
# 编辑 .env 填写你的凭证

# 启动服务（自动创建持久卷）
docker-compose up -d

# 查看日志
docker logs -f kirogate</pre>

        <h3 class="text-lg font-medium mb-2 mt-4 text-indigo-400">手动 Docker 运行</h3>
        <pre style="background: var(--bg-input); border: 1px solid var(--border); color: var(--text);" class="p-4 rounded-lg overflow-x-auto text-sm">
docker build -t kirogate .
docker run -d -p 8000:8000 \\
  -v kirogate_data:/app/data \\
  -e PROXY_API_KEY="your-key" \\
  -e ADMIN_PASSWORD="your-admin-pwd" \\
  --name kirogate kirogate</pre>
      </section>

      <section class="card">
        <h2 class="text-2xl font-semibold mb-4">🚀 Fly.io 部署</h2>
        <pre style="background: var(--bg-input); border: 1px solid var(--border); color: var(--text);" class="p-4 rounded-lg overflow-x-auto text-sm">
# 1. 安装 Fly CLI 并登录
curl -L https://fly.io/install.sh | sh
fly auth login

# 2. 创建应用
fly apps create kirogate

# 3. 创建持久卷（重要！保证数据不丢失）
fly volumes create kirogate_data --region nrt --size 1

# 4. 设置环境变量
fly secrets set PROXY_API_KEY="your-password"
fly secrets set ADMIN_PASSWORD="your-admin-password"
fly secrets set ADMIN_SECRET_KEY="your-random-secret"

# 5. 部署
fly deploy</pre>
      </section>

      <section class="card">
        <h2 class="text-2xl font-semibold mb-4">💾 数据持久化</h2>
        <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3);" class="p-4 rounded-lg mb-4">
          <p class="text-sm font-semibold text-red-400">⚠️ 重要提醒</p>
          <p class="text-sm mt-1" style="color: var(--text-muted);">用户数据（数据库）需要持久化存储，否则每次部署会丢失所有用户、Token 和 API Key！</p>
        </div>
        <div class="space-y-3">
          <div style="background: var(--bg-input);" class="p-3 rounded-lg">
            <p class="font-medium text-green-400">Docker Compose</p>
            <p class="text-sm" style="color: var(--text-muted);">已配置命名卷 <code>kirogate_data:/app/data</code>，使用 <code>docker-compose down</code> 保留数据</p>
          </div>
          <div style="background: var(--bg-input);" class="p-3 rounded-lg">
            <p class="font-medium text-blue-400">Fly.io</p>
            <p class="text-sm" style="color: var(--text-muted);">需手动创建卷：<code>fly volumes create kirogate_data --region nrt --size 1</code></p>
          </div>
        </div>
      </section>

      <section class="card">
        <h2 class="text-2xl font-semibold mb-4">🔐 获取 Refresh Token</h2>
        <div style="background: linear-gradient(135deg, rgba(34, 197, 94, 0.1), rgba(16, 185, 129, 0.1)); border: 1px solid #22c55e;" class="p-4 rounded-lg mb-4">
          <p class="text-sm font-semibold mb-2 text-green-400">🌐 方式一：浏览器获取（推荐）</p>
          <ol class="text-sm space-y-1" style="color: var(--text-muted);">
            <li>1. 打开 <a href="https://app.kiro.dev/account/usage" target="_blank" class="text-indigo-400 hover:underline">https://app.kiro.dev/account/usage</a> 并登录</li>
            <li>2. 按 <kbd class="px-1 py-0.5 rounded text-xs" style="background: var(--bg-input); border: 1px solid var(--border);">F12</kbd> 打开开发者工具</li>
            <li>3. 点击 <strong>应用/Application</strong> → <strong>存储/Storage</strong> → <strong>Cookie</strong></li>
            <li>4. 选择 <code style="background: var(--bg-input);" class="px-1 rounded">https://app.kiro.dev</code></li>
            <li>5. 复制 <code class="text-green-400">RefreshToken</code> 的值</li>
          </ol>
        </div>

        <div style="background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(168, 85, 247, 0.1)); border: 1px solid var(--primary);" class="p-4 rounded-lg">
          <p class="text-sm font-semibold mb-2" style="color: var(--text);">🛠️ 方式二：Kiro Account Manager</p>
          <p class="text-sm" style="color: var(--text-muted);">
            使用 <a href="https://github.com/chaogei/Kiro-account-manager" class="text-indigo-400 hover:underline font-medium" target="_blank">Kiro Account Manager</a>
            可以轻松管理多个账号的 Refresh Token。
          </p>
        </div>
      </section>
    </div>
  </main>

  {COMMON_FOOTER}
</body>
</html>'''


def render_status_page(status_data: dict) -> str:
    """Render the status page."""
    status_color = "#22c55e" if status_data.get("status") == "healthy" else "#ef4444"
    token_color = "#22c55e" if status_data.get("token_valid") else "#ef4444"

    return f'''<!DOCTYPE html>
<html lang="zh">
<head>{COMMON_HEAD}
  <meta http-equiv="refresh" content="30">
</head>
<body>
  {COMMON_NAV}

  <main class="max-w-4xl mx-auto px-4 py-12">
    <h1 class="text-4xl font-bold mb-8">📊 系统状态</h1>

    <div class="grid md:grid-cols-2 gap-6 mb-8">
      <div class="card">
        <h2 class="text-lg font-semibold mb-4">服务状态</h2>
        <div class="flex items-center gap-3">
          <div class="w-4 h-4 rounded-full" style="background: {status_color};"></div>
          <span class="text-2xl font-bold">{status_data.get("status", "unknown").upper()}</span>
        </div>
      </div>
      <div class="card">
        <h2 class="text-lg font-semibold mb-4">Token 状态</h2>
        <div class="flex items-center gap-3">
          <div class="w-4 h-4 rounded-full" style="background: {token_color};"></div>
          <span class="text-2xl font-bold">{"有效" if status_data.get("token_valid") else "无效/未配置"}</span>
        </div>
      </div>
    </div>

    <div class="card mb-8">
      <h2 class="text-xl font-semibold mb-4">详细信息</h2>
      <div class="grid grid-cols-2 gap-4">
        <div>
          <p class="text-sm" style="color: var(--text-muted);">版本</p>
          <p class="font-mono">{status_data.get("version", "unknown")}</p>
        </div>
        <div>
          <p class="text-sm" style="color: var(--text-muted);">缓存大小</p>
          <p class="font-mono">{status_data.get("cache_size", 0)}</p>
        </div>
        <div>
          <p class="text-sm" style="color: var(--text-muted);">最后更新</p>
          <p class="font-mono text-sm">{status_data.get("cache_last_update", "N/A")}</p>
        </div>
        <div>
          <p class="text-sm" style="color: var(--text-muted);">时间戳</p>
          <p class="font-mono text-sm">{status_data.get("timestamp", "N/A")}</p>
        </div>
      </div>
    </div>

    <p class="text-sm text-center" style="color: var(--text-muted);">页面每 30 秒自动刷新</p>
  </main>

  {COMMON_FOOTER}
</body>
</html>'''


def render_dashboard_page() -> str:
    """Render the dashboard page with metrics."""
    return f'''<!DOCTYPE html>
<html lang="zh">
<head>{COMMON_HEAD}
<style>
.mc{{background:var(--bg-card);border:1px solid var(--border);border-radius:.75rem;padding:1.25rem;text-align:center;transition:all .3s ease}}
.mc:hover{{border-color:var(--primary);transform:translateY(-2px);box-shadow:0 8px 25px rgba(99,102,241,0.15)}}
.mi{{font-size:1.75rem;margin-bottom:.75rem}}
.stat-value{{font-size:1.75rem;font-weight:700;line-height:1.2}}
.stat-label{{font-size:.75rem;margin-top:.5rem;opacity:.7}}
.chart-card{{background:var(--bg-card);border:1px solid var(--border);border-radius:.75rem;padding:1.5rem}}
.chart-title{{font-size:1rem;font-weight:600;margin-bottom:1rem;display:flex;align-items:center;gap:.5rem}}
</style>
</head>
<body>
  {COMMON_NAV}
  <main class="max-w-7xl mx-auto px-4 py-8">
    <div class="flex justify-between items-center mb-8">
      <h1 class="text-3xl font-bold flex items-center gap-3">
        <span class="text-4xl">📊</span>
        <span>Dashboard</span>
      </h1>
      <button onclick="refreshData()" class="btn-primary flex items-center gap-2">
        <span>🔄</span> 刷新
      </button>
    </div>

    <!-- Primary Stats -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
      <div class="mc">
        <div class="mi">📈</div>
        <div class="stat-value text-indigo-400" id="totalRequests">-</div>
        <div class="stat-label" style="color:var(--text-muted)">总请求</div>
      </div>
      <div class="mc">
        <div class="mi">✅</div>
        <div class="stat-value text-green-400" id="successRate">-</div>
        <div class="stat-label" style="color:var(--text-muted)">成功率</div>
      </div>
      <div class="mc">
        <div class="mi">⏱️</div>
        <div class="stat-value text-yellow-400" id="avgResponseTime">-</div>
        <div class="stat-label" style="color:var(--text-muted)">平均耗时</div>
      </div>
      <div class="mc">
        <div class="mi">🕐</div>
        <div class="stat-value text-purple-400" id="uptime">-</div>
        <div class="stat-label" style="color:var(--text-muted)">运行时长</div>
      </div>
    </div>

    <!-- Secondary Stats -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
      <div class="mc">
        <div class="mi">⚡</div>
        <div class="stat-value text-blue-400" style="font-size:1.5rem" id="streamRequests">-</div>
        <div class="stat-label" style="color:var(--text-muted)">流式请求</div>
      </div>
      <div class="mc">
        <div class="mi">💾</div>
        <div class="stat-value text-cyan-400" style="font-size:1.5rem" id="nonStreamRequests">-</div>
        <div class="stat-label" style="color:var(--text-muted)">非流式请求</div>
      </div>
      <div class="mc">
        <div class="mi">❌</div>
        <div class="stat-value text-red-400" style="font-size:1.5rem" id="failedRequests">-</div>
        <div class="stat-label" style="color:var(--text-muted)">失败请求</div>
      </div>
      <div class="mc">
        <div class="mi">🤖</div>
        <div class="stat-value text-emerald-400" style="font-size:1.25rem" id="topModel">-</div>
        <div class="stat-label" style="color:var(--text-muted)">热门模型</div>
      </div>
    </div>

    <!-- API Type Stats -->
    <div class="grid grid-cols-2 gap-4 mb-8">
      <div class="mc">
        <div class="mi">🟢</div>
        <div class="stat-value text-green-400" style="font-size:1.5rem" id="openaiRequests">-</div>
        <div class="stat-label" style="color:var(--text-muted)">OpenAI API</div>
      </div>
      <div class="mc">
        <div class="mi">🟣</div>
        <div class="stat-value text-purple-400" style="font-size:1.5rem" id="anthropicRequests">-</div>
        <div class="stat-label" style="color:var(--text-muted)">Anthropic API</div>
      </div>
    </div>

    <!-- Charts -->
    <div class="grid lg:grid-cols-2 gap-6 mb-8">
      <div class="chart-card">
        <h2 class="chart-title">📈 24小时请求趋势</h2>
        <div id="latencyChart" style="height:280px"></div>
      </div>
      <div class="chart-card">
        <h2 class="chart-title">📊 状态分布</h2>
        <div style="height:280px;position:relative">
          <canvas id="statusChart"></canvas>
        </div>
      </div>
    </div>

    <!-- Recent Requests -->
    <div class="chart-card">
      <h2 class="chart-title">📋 最近请求</h2>
      <div class="table-responsive">
        <table class="w-full text-sm">
          <thead>
            <tr class="text-left" style="color:var(--text-muted);border-bottom:1px solid var(--border)">
              <th class="py-3 px-3">时间</th>
              <th class="py-3 px-3">API</th>
              <th class="py-3 px-3">路径</th>
              <th class="py-3 px-3">状态</th>
              <th class="py-3 px-3">耗时</th>
              <th class="py-3 px-3">模型</th>
            </tr>
          </thead>
          <tbody id="recentRequestsTable">
            <tr><td colspan="6" class="py-6 text-center" style="color:var(--text-muted)">加载中...</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  </main>
  {COMMON_FOOTER}
  <script>
let lc,sc;
const START_TIME = new Date('2025-12-25T00:00:00').getTime();
async function refreshData(){{
  try{{
    const r=await fetch('/api/metrics'),d=await r.json();
    document.getElementById('totalRequests').textContent=d.totalRequests||0;
    document.getElementById('successRate').textContent=d.totalRequests>0?((d.successRequests/d.totalRequests)*100).toFixed(1)+'%':'0%';
    document.getElementById('avgResponseTime').textContent=(d.avgResponseTime||0).toFixed(0)+'ms';

    // Calculate uptime from fixed start time
    const now=Date.now();
    const u=Math.floor((now-START_TIME)/1000);
    const days=Math.floor(u/86400);
    const hours=Math.floor((u%86400)/3600);
    const mins=Math.floor((u%3600)/60);
    document.getElementById('uptime').textContent=days>0?days+'d '+hours+'h':hours+'h '+mins+'m';

    document.getElementById('streamRequests').textContent=d.streamRequests||0;
    document.getElementById('nonStreamRequests').textContent=d.nonStreamRequests||0;
    document.getElementById('failedRequests').textContent=d.failedRequests||0;

    const m=Object.entries(d.modelUsage||{{}}).filter(e=>e[0]!=='unknown').sort((a,b)=>b[1]-a[1])[0];
    const formatModel=(name)=>{{
      if(!name)return'-';
      let n=name.replace(/-\\d{{8}}$/,'');
      const parts=n.split('-');
      if(parts.length<=2)return n;
      if(n.includes('claude')){{
        const ver=parts.filter(p=>/^\\d+$/.test(p)).join('.');
        const type=parts.find(p=>['opus','sonnet','haiku'].includes(p))||parts[parts.length-1];
        return ver?type+'-'+ver:type;
      }}
      return parts.slice(-2).join('-');
    }};
    document.getElementById('topModel').textContent=m?formatModel(m[0]):'-';
    document.getElementById('openaiRequests').textContent=(d.apiTypeUsage||{{}}).openai||0;
    document.getElementById('anthropicRequests').textContent=(d.apiTypeUsage||{{}}).anthropic||0;

    // Update 24-hour chart
    const hr=d.hourlyRequests||[];
    lc.setOption({{
      xAxis:{{data:hr.map(h=>new Date(h.hour).getHours()+':00')}},
      series:[{{data:hr.map(h=>h.count)}}]
    }});

    sc.data.datasets[0].data=[d.successRequests||0,d.failedRequests||0];
    sc.update();

    const rq=(d.recentRequests||[]).slice(-10).reverse();
    const tb=document.getElementById('recentRequestsTable');
    tb.innerHTML=rq.length?rq.map(q=>`
      <tr style="border-bottom:1px solid var(--border)">
        <td class="py-3 px-3">${{new Date(q.timestamp).toLocaleTimeString()}}</td>
        <td class="py-3 px-3"><span class="text-xs px-2 py-1 rounded ${{q.apiType==='anthropic'?'bg-purple-600':'bg-green-600'}} text-white">${{q.apiType}}</span></td>
        <td class="py-3 px-3 font-mono text-xs">${{q.path}}</td>
        <td class="py-3 px-3 ${{q.status<400?'text-green-400':'text-red-400'}}">${{q.status}}</td>
        <td class="py-3 px-3">${{q.duration.toFixed(0)}}ms</td>
        <td class="py-3 px-3">${{q.model||'-'}}</td>
      </tr>`).join(''):'<tr><td colspan="6" class="py-6 text-center" style="color:var(--text-muted)">暂无请求</td></tr>';
  }}catch(e){{console.error(e)}}
}}

lc=echarts.init(document.getElementById('latencyChart'));
lc.setOption({{
  tooltip:{{trigger:'axis',backgroundColor:'rgba(30,41,59,0.95)',borderColor:'#334155',textStyle:{{color:'#e2e8f0'}}}},
  grid:{{left:'3%',right:'4%',bottom:'3%',containLabel:true}},
  xAxis:{{type:'category',data:[],axisLabel:{{color:'#94a3b8',fontSize:11}},axisLine:{{lineStyle:{{color:'#334155'}}}}}},
  yAxis:{{type:'value',name:'请求数',nameTextStyle:{{color:'#94a3b8'}},axisLabel:{{color:'#94a3b8'}},axisLine:{{lineStyle:{{color:'#334155'}}}},splitLine:{{lineStyle:{{color:'#1e293b'}}}}}},
  series:[{{
    type:'bar',
    data:[],
    itemStyle:{{
      color:new echarts.graphic.LinearGradient(0,0,0,1,[
        {{offset:0,color:'#818cf8'}},
        {{offset:1,color:'#6366f1'}}
      ]),
      borderRadius:[4,4,0,0]
    }},
    emphasis:{{itemStyle:{{color:'#a5b4fc'}}}}
  }}]
}});

sc=new Chart(document.getElementById('statusChart'),{{
  type:'doughnut',
  data:{{
    labels:['成功','失败'],
    datasets:[{{data:[0,0],backgroundColor:['#22c55e','#ef4444'],borderWidth:0,hoverOffset:8}}]
  }},
  options:{{
    responsive:true,
    maintainAspectRatio:false,
    cutout:'65%',
    plugins:{{
      legend:{{position:'bottom',labels:{{color:'#94a3b8',padding:20,font:{{size:13}}}}}}
    }}
  }}
}});

refreshData();
setInterval(refreshData,5000);
window.addEventListener('resize',()=>lc.resize());
  </script>
</body>
</html>'''


def render_swagger_page() -> str:
    """Render the Swagger UI page."""
    return f'''<!DOCTYPE html>
<html lang="zh">
<head>
  {COMMON_HEAD}
  <link rel="stylesheet" href="{PROXY_BASE}/proxy/cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css">
  <style>
    .swagger-ui .topbar {{ display: none; }}
    .swagger-ui .info .title {{ font-size: 2rem; }}
    .swagger-ui .opblock-tag {{ font-size: 1.2rem; }}
    .swagger-ui .opblock.opblock-post {{ border-color: #49cc90; background: rgba(73, 204, 144, 0.1); }}
    .swagger-ui .opblock.opblock-get {{ border-color: #61affe; background: rgba(97, 175, 254, 0.1); }}
    .swagger-ui {{ background: var(--bg); }}
    .swagger-ui .info .title, .swagger-ui .info .base-url {{ color: var(--text); }}
    .swagger-ui .opblock-tag {{ color: var(--text); }}
    .swagger-ui .opblock-summary-description {{ color: var(--text-muted); }}
  </style>
</head>
<body>
  {COMMON_NAV}
  <main class="max-w-7xl mx-auto px-4 py-6">
    <div id="swagger-ui"></div>
  </main>
  {COMMON_FOOTER}
  <script src="{PROXY_BASE}/proxy/cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
  <script>
    window.onload = function() {{
      SwaggerUIBundle({{
        url: "/openapi.json",
        dom_id: '#swagger-ui',
        deepLinking: true,
        presets: [
          SwaggerUIBundle.presets.apis,
          SwaggerUIBundle.SwaggerUIStandalonePreset
        ],
        layout: "BaseLayout",
        defaultModelsExpandDepth: 1,
        defaultModelExpandDepth: 1,
        docExpansion: "list",
        filter: true,
        showExtensions: true,
        showCommonExtensions: true,
        syntaxHighlight: {{
          activate: true,
          theme: "monokai"
        }}
      }});
    }}
  </script>
</body>
</html>'''


def render_admin_login_page(error: str = "") -> str:
    """Render the admin login page."""
    error_html = f'<div class="bg-red-500/20 border border-red-500 text-red-400 px-4 py-3 rounded-lg mb-4">{error}</div>' if error else ''

    return f'''<!DOCTYPE html>
<html lang="zh">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Admin Login - KiroGate</title>
  <meta name="robots" content="noindex, nofollow">
  <script src="{PROXY_BASE}/proxy/cdn.tailwindcss.com"></script>
  <style>
    :root {{ --bg-main: #ffffff; --bg-card: #f8fafc; --text: #1e293b; --text-muted: #64748b; --border: #e2e8f0; --primary: #6366f1; --bg-input: #f1f5f9; }}
    .dark {{ --bg-main: #0f172a; --bg-card: #1e293b; --text: #e2e8f0; --text-muted: #94a3b8; --border: #334155; --bg-input: #334155; }}
    body {{ background: var(--bg-main); color: var(--text); font-family: system-ui, sans-serif; min-height: 100vh; display: flex; align-items: center; justify-content: center; transition: background .3s, color .3s; }}
    .card {{ background: var(--bg-card); border: 1px solid var(--border); }}
    input {{ background: var(--bg-input); border-color: var(--border); color: var(--text); }}
  </style>
</head>
<body>
  <button onclick="toggleTheme()" class="fixed top-4 right-4 p-2 rounded-lg" style="background: var(--bg-card); border: 1px solid var(--border);">
    <span id="themeIcon">🌙</span>
  </button>
  <div class="w-full max-w-md px-6">
    <div class="card rounded-xl p-8 shadow-2xl">
      <div class="text-center mb-8">
        <span class="text-4xl">🔐</span>
        <h1 class="text-2xl font-bold mt-4">Admin Login</h1>
        <p class="text-sm mt-2" style="color: var(--text-muted);">KiroGate 管理后台</p>
      </div>

      {error_html}

      <form action="/admin/login" method="POST" class="space-y-6">
        <div>
          <label class="block text-sm mb-2" style="color: var(--text-muted);">管理员密码</label>
          <input type="password" name="password" required autofocus
            class="w-full px-4 py-3 rounded-lg border focus:outline-none focus:ring-2 focus:ring-indigo-500"
            placeholder="请输入管理员密码">
        </div>
        <button type="submit" class="w-full py-3 rounded-lg font-semibold text-white transition-all hover:opacity-90"
          style="background: var(--primary);">
          登 录
        </button>
      </form>

      <div class="mt-6 text-center">
        <a href="/" class="text-sm hover:underline" style="color: #6366f1;">← 返回首页</a>
      </div>
    </div>
  </div>
  <script>
    function initTheme() {{
      const saved = localStorage.getItem('theme');
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      const isDark = saved === 'dark' || (!saved && prefersDark);
      document.documentElement.classList.toggle('dark', isDark);
      document.getElementById('themeIcon').textContent = isDark ? '☀️' : '🌙';
    }}
    function toggleTheme() {{
      const isDark = document.documentElement.classList.toggle('dark');
      localStorage.setItem('theme', isDark ? 'dark' : 'light');
      document.getElementById('themeIcon').textContent = isDark ? '☀️' : '🌙';
    }}
    initTheme();
  </script>
</body>
</html>'''


def render_admin_page() -> str:
    """Render the admin dashboard page."""
    return f'''<!DOCTYPE html>
<html lang="zh">
<head>{COMMON_HEAD}
  <meta name="robots" content="noindex, nofollow">
  <style>
    .card {{ background: var(--bg-card); border: 1px solid var(--border); border-radius: .75rem; padding: 1.5rem; }}
    .btn {{ padding: .5rem 1rem; border-radius: .5rem; font-weight: 500; transition: all .2s; cursor: pointer; }}
    .btn-primary {{ background: var(--primary); color: white; }}
    .btn-primary:hover {{ opacity: .9; }}
    .btn-danger {{ background: #ef4444; color: white; }}
    .btn-danger:hover {{ opacity: .9; }}
    .btn-success {{ background: #22c55e; color: white; }}
    .btn-success:hover {{ opacity: .9; }}
    .tab {{ padding: .75rem 1.25rem; cursor: pointer; border-bottom: 2px solid transparent; transition: all .2s; }}
    .tab:hover {{ color: var(--primary); }}
    .tab.active {{ color: var(--primary); border-bottom-color: var(--primary); }}
    .table-row {{ border-bottom: 1px solid var(--border); }}
    .table-row:hover {{ background: rgba(99,102,241,0.05); }}
    .switch {{ position: relative; width: 50px; height: 26px; }}
    .switch input {{ opacity: 0; width: 0; height: 0; }}
    .slider {{ position: absolute; cursor: pointer; inset: 0; background: #475569; border-radius: 26px; transition: .3s; }}
    .slider:before {{ content: ""; position: absolute; height: 20px; width: 20px; left: 3px; bottom: 3px; background: white; border-radius: 50%; transition: .3s; }}
    input:checked + .slider {{ background: #22c55e; }}
    input:checked + .slider:before {{ transform: translateX(24px); }}
    .status-dot {{ width: 10px; height: 10px; border-radius: 50%; display: inline-block; }}
    .status-ok {{ background: #22c55e; }}
    .status-error {{ background: #ef4444; }}
  </style>
</head>
<body>
  <!-- Admin Header -->
  <header style="background: var(--bg-card); border-bottom: 1px solid var(--border);" class="sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
      <div class="flex items-center gap-4">
        <a href="/" class="flex items-center gap-2 text-xl font-bold" style="color: var(--text); text-decoration: none;">
          <span>⚡</span>
          <span class="hidden sm:inline">KiroGate</span>
        </a>
        <span class="inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-medium" style="background: rgba(239, 68, 68, 0.15); color: #ef4444;">🛡️ Admin</span>
      </div>
      <nav class="hidden md:flex items-center gap-6">
        <a href="/" style="color: var(--text-muted); text-decoration: none;">首页</a>
        <a href="/docs" style="color: var(--text-muted); text-decoration: none;">文档</a>
        <a href="/playground" style="color: var(--text-muted); text-decoration: none;">测试</a>
        <a href="/dashboard" style="color: var(--text-muted); text-decoration: none;">面板</a>
        <a href="/user" style="color: var(--text-muted); text-decoration: none;">用户</a>
      </nav>
      <div class="flex items-center gap-2">
        <button onclick="toggleTheme()" class="p-2 rounded-lg" style="background: var(--bg-input); border: 1px solid var(--border);" title="切换主题">
          <span id="themeIcon">🌙</span>
        </button>
        <a href="/admin/logout" class="hidden sm:inline-block btn btn-danger text-sm">退出</a>
        <button onclick="document.getElementById('adminMobileMenu').classList.toggle('hidden')" class="md:hidden p-2 rounded-lg" style="background: var(--bg-input); border: 1px solid var(--border);">☰</button>
      </div>
    </div>
    <!-- Mobile Menu -->
    <div id="adminMobileMenu" class="hidden md:hidden px-4 py-3" style="border-top: 1px solid var(--border);">
      <div class="flex flex-col gap-2">
        <a href="/" class="py-2 px-3 rounded" style="color: var(--text);">首页</a>
        <a href="/docs" class="py-2 px-3 rounded" style="color: var(--text);">文档</a>
        <a href="/playground" class="py-2 px-3 rounded" style="color: var(--text);">测试</a>
        <a href="/dashboard" class="py-2 px-3 rounded" style="color: var(--text);">面板</a>
        <a href="/user" class="py-2 px-3 rounded" style="color: var(--text);">用户中心</a>
        <a href="/admin/logout" class="py-2 px-3 rounded text-red-400">退出登录</a>
      </div>
    </div>
  </header>

  <main class="max-w-7xl mx-auto px-4 py-6">
    <!-- Status Cards -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
      <div class="card text-center">
        <div class="text-2xl mb-2" id="siteIcon">🟢</div>
        <div class="flex items-center justify-center gap-2">
          <label class="switch" style="transform: scale(0.8);">
            <input type="checkbox" id="siteToggleQuick" checked onchange="toggleSite(this.checked)">
            <span class="slider"></span>
          </label>
        </div>
        <div class="text-sm mt-2" style="color: var(--text-muted);">站点开关</div>
      </div>
      <div class="card text-center cursor-pointer hover:ring-2 hover:ring-indigo-500/50 transition-all" onclick="showTab('donated-tokens')">
        <div class="text-2xl mb-2">🔑</div>
        <div class="text-2xl font-bold" id="tokenStatus">-</div>
        <div class="text-sm" style="color: var(--text-muted);">Token 状态</div>
      </div>
      <div class="card text-center cursor-pointer hover:ring-2 hover:ring-indigo-500/50 transition-all" onclick="showTab('overview')">
        <div class="text-2xl mb-2">📊</div>
        <div class="text-2xl font-bold" id="totalRequests">-</div>
        <div class="text-sm" style="color: var(--text-muted);">总请求数</div>
      </div>
      <div class="card text-center cursor-pointer hover:ring-2 hover:ring-indigo-500/50 transition-all" onclick="showTab('tokens')">
        <div class="text-2xl mb-2">👥</div>
        <div class="text-2xl font-bold" id="cachedTokens">-</div>
        <div class="text-sm" style="color: var(--text-muted);">缓存用户</div>
      </div>
    </div>

    <!-- Tabs -->
    <div class="flex flex-wrap border-b mb-6" style="border-color: var(--border);">
      <div class="tab active" onclick="showTab('overview')">📈 概览</div>
      <div class="tab" onclick="showTab('users')">👥 用户</div>
      <div class="tab" onclick="showTab('donated-tokens')">🎁 Token 池</div>
      <div class="tab" onclick="showTab('ip-stats')">🌐 IP 统计</div>
      <div class="tab" onclick="showTab('blacklist')">🚫 黑名单</div>
      <div class="tab" onclick="showTab('tokens')">🔑 缓存</div>
      <div class="tab" onclick="showTab('system')">⚙️ 系统</div>
    </div>

    <!-- Tab Content: Overview -->
    <div id="tab-overview" class="tab-content">
      <div class="card">
        <h2 class="text-lg font-semibold mb-4">📊 实时统计</h2>
        <div class="grid md:grid-cols-3 gap-4">
          <div style="background: var(--bg-input);" class="p-4 rounded-lg">
            <div class="text-sm" style="color: var(--text-muted);">成功率</div>
            <div class="text-2xl font-bold text-green-400" id="successRate">-</div>
          </div>
          <div style="background: var(--bg-input);" class="p-4 rounded-lg">
            <div class="text-sm" style="color: var(--text-muted);">平均响应时间</div>
            <div class="text-2xl font-bold text-yellow-400" id="avgLatency">-</div>
          </div>
          <div style="background: var(--bg-input);" class="p-4 rounded-lg">
            <div class="text-sm" style="color: var(--text-muted);">活跃连接</div>
            <div class="text-2xl font-bold text-blue-400" id="activeConns">-</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Tab Content: Users -->
    <div id="tab-users" class="tab-content hidden">
      <div class="card">
        <div class="flex flex-wrap justify-between items-center gap-4 mb-4">
          <h2 class="text-lg font-semibold">👥 注册用户管理</h2>
          <div class="flex items-center gap-2">
            <input type="text" id="usersSearch" placeholder="搜索用户名..." oninput="filterUsers()"
              class="px-3 py-2 rounded-lg text-sm w-40" style="background: var(--bg-input); border: 1px solid var(--border); color: var(--text);">
            <select id="usersPageSize" onchange="filterUsers()" class="px-3 py-2 rounded-lg text-sm" style="background: var(--bg-input); border: 1px solid var(--border); color: var(--text);">
              <option value="10">10/页</option>
              <option value="20" selected>20/页</option>
              <option value="50">50/页</option>
            </select>
            <button onclick="refreshUsers()" class="btn btn-primary text-sm">刷新</button>
          </div>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead>
              <tr style="color: var(--text-muted); border-bottom: 1px solid var(--border);">
                <th class="text-left py-3 px-3 cursor-pointer hover:text-indigo-400" onclick="sortUsers('id')">ID ↕</th>
                <th class="text-left py-3 px-3 cursor-pointer hover:text-indigo-400" onclick="sortUsers('username')">用户名 ↕</th>
                <th class="text-left py-3 px-3">信任等级</th>
                <th class="text-left py-3 px-3 cursor-pointer hover:text-indigo-400" onclick="sortUsers('token_count')">Token 数 ↕</th>
                <th class="text-left py-3 px-3">API Key</th>
                <th class="text-left py-3 px-3">状态</th>
                <th class="text-left py-3 px-3 cursor-pointer hover:text-indigo-400" onclick="sortUsers('created_at')">注册时间 ↕</th>
                <th class="text-left py-3 px-3">操作</th>
              </tr>
            </thead>
            <tbody id="usersTable">
              <tr><td colspan="8" class="py-6 text-center" style="color: var(--text-muted);">加载中...</td></tr>
            </tbody>
          </table>
        </div>
        <div id="usersPagination" class="flex items-center justify-between mt-4 pt-4" style="border-top: 1px solid var(--border); display: none;">
          <span id="usersInfo" class="text-sm" style="color: var(--text-muted);"></span>
          <div id="usersPages" class="flex gap-1"></div>
        </div>
      </div>
    </div>

    <!-- Tab Content: Donated Tokens -->
    <div id="tab-donated-tokens" class="tab-content hidden">
      <div class="card">
        <div class="flex flex-wrap justify-between items-center gap-4 mb-4">
          <h2 class="text-lg font-semibold">🎁 捐献 Token 池</h2>
          <div class="flex items-center gap-2">
            <input type="text" id="poolSearch" placeholder="搜索用户名..." oninput="filterPoolTokens()"
              class="px-3 py-2 rounded-lg text-sm w-40" style="background: var(--bg-input); border: 1px solid var(--border); color: var(--text);">
            <select id="poolVisibilityFilter" onchange="filterPoolTokens()" class="px-3 py-2 rounded-lg text-sm" style="background: var(--bg-input); border: 1px solid var(--border); color: var(--text);">
              <option value="">全部可见性</option>
              <option value="public">公开</option>
              <option value="private">私有</option>
            </select>
            <select id="poolPageSize" onchange="filterPoolTokens()" class="px-3 py-2 rounded-lg text-sm" style="background: var(--bg-input); border: 1px solid var(--border); color: var(--text);">
              <option value="10">10/页</option>
              <option value="20" selected>20/页</option>
              <option value="50">50/页</option>
            </select>
            <button onclick="batchDeletePoolTokens()" class="btn btn-danger text-sm">批量删除</button>
            <button onclick="refreshDonatedTokens()" class="btn btn-primary text-sm">刷新</button>
          </div>
        </div>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div style="background: var(--bg-input);" class="p-3 rounded-lg text-center">
            <div class="text-xl font-bold text-green-400" id="poolTotalTokens">-</div>
            <div class="text-xs" style="color: var(--text-muted);">总 Token</div>
          </div>
          <div style="background: var(--bg-input);" class="p-3 rounded-lg text-center">
            <div class="text-xl font-bold text-blue-400" id="poolActiveTokens">-</div>
            <div class="text-xs" style="color: var(--text-muted);">有效</div>
          </div>
          <div style="background: var(--bg-input);" class="p-3 rounded-lg text-center">
            <div class="text-xl font-bold text-purple-400" id="poolPublicTokens">-</div>
            <div class="text-xs" style="color: var(--text-muted);">公开</div>
          </div>
          <div style="background: var(--bg-input);" class="p-3 rounded-lg text-center">
            <div class="text-xl font-bold text-yellow-400" id="poolAvgSuccessRate">-</div>
            <div class="text-xs" style="color: var(--text-muted);">平均成功率</div>
          </div>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead>
              <tr style="color: var(--text-muted); border-bottom: 1px solid var(--border);">
                <th class="text-left py-3 px-3">
                  <input type="checkbox" id="selectAllPool" onchange="toggleSelectAllPool(this.checked)">
                </th>
                <th class="text-left py-3 px-3 cursor-pointer hover:text-indigo-400" onclick="sortPoolTokens('id')">ID ↕</th>
                <th class="text-left py-3 px-3 cursor-pointer hover:text-indigo-400" onclick="sortPoolTokens('username')">所有者 ↕</th>
                <th class="text-left py-3 px-3">可见性</th>
                <th class="text-left py-3 px-3">状态</th>
                <th class="text-left py-3 px-3 cursor-pointer hover:text-indigo-400" onclick="sortPoolTokens('success_rate')">成功率 ↕</th>
                <th class="text-left py-3 px-3 cursor-pointer hover:text-indigo-400" onclick="sortPoolTokens('use_count')">使用次数 ↕</th>
                <th class="text-left py-3 px-3 cursor-pointer hover:text-indigo-400" onclick="sortPoolTokens('last_used')">最后使用 ↕</th>
                <th class="text-left py-3 px-3">操作</th>
              </tr>
            </thead>
            <tbody id="donatedTokensTable">
              <tr><td colspan="9" class="py-6 text-center" style="color: var(--text-muted);">加载中...</td></tr>
            </tbody>
          </table>
        </div>
        <div id="poolPagination" class="flex items-center justify-between mt-4 pt-4" style="border-top: 1px solid var(--border); display: none;">
          <span id="poolInfo" class="text-sm" style="color: var(--text-muted);"></span>
          <div id="poolPages" class="flex gap-1"></div>
        </div>
      </div>
    </div>

    <!-- Tab Content: IP Stats -->
    <div id="tab-ip-stats" class="tab-content hidden">
      <div class="card">
        <div class="flex flex-wrap justify-between items-center gap-4 mb-4">
          <h2 class="text-lg font-semibold">🌐 IP 请求统计</h2>
          <div class="flex items-center gap-2">
            <input type="text" id="ipStatsSearch" placeholder="搜索IP..." oninput="filterIpStats()"
              class="px-3 py-2 rounded-lg text-sm w-40" style="background: var(--bg-input); border: 1px solid var(--border); color: var(--text);">
            <select id="ipStatsPageSize" onchange="filterIpStats()" class="px-3 py-2 rounded-lg text-sm" style="background: var(--bg-input); border: 1px solid var(--border); color: var(--text);">
              <option value="10">10/页</option>
              <option value="20" selected>20/页</option>
              <option value="50">50/页</option>
            </select>
            <button onclick="batchBanIps()" class="btn btn-danger text-sm">批量封禁</button>
            <button onclick="refreshIpStats()" class="btn btn-primary text-sm">刷新</button>
          </div>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead>
              <tr style="color: var(--text-muted); border-bottom: 1px solid var(--border);">
                <th class="text-left py-3 px-3">
                  <input type="checkbox" id="selectAllIps" onchange="toggleSelectAllIps(this.checked)">
                </th>
                <th class="text-left py-3 px-3 cursor-pointer hover:text-indigo-400" onclick="sortIpStats('ip')">IP 地址 ↕</th>
                <th class="text-left py-3 px-3 cursor-pointer hover:text-indigo-400" onclick="sortIpStats('count')">请求次数 ↕</th>
                <th class="text-left py-3 px-3 cursor-pointer hover:text-indigo-400" onclick="sortIpStats('last_seen')">最后访问 ↕</th>
                <th class="text-left py-3 px-3">操作</th>
              </tr>
            </thead>
            <tbody id="ipStatsTable">
              <tr><td colspan="5" class="py-6 text-center" style="color: var(--text-muted);">加载中...</td></tr>
            </tbody>
          </table>
        </div>
        <div id="ipStatsPagination" class="flex items-center justify-between mt-4 pt-4" style="border-top: 1px solid var(--border); display: none;">
          <span id="ipStatsInfo" class="text-sm" style="color: var(--text-muted);"></span>
          <div id="ipStatsPages" class="flex gap-1"></div>
        </div>
      </div>
    </div>

    <!-- Tab Content: Blacklist -->
    <div id="tab-blacklist" class="tab-content hidden">
      <div class="card">
        <div class="flex flex-wrap justify-between items-center gap-4 mb-4">
          <h2 class="text-lg font-semibold">🚫 IP 黑名单</h2>
          <div class="flex items-center gap-2">
            <input type="text" id="blacklistSearch" placeholder="搜索 IP 或原因..." oninput="filterBlacklist()"
              class="px-3 py-2 rounded-lg text-sm w-40" style="background: var(--bg-input); border: 1px solid var(--border); color: var(--text);">
            <select id="blacklistPageSize" onchange="filterBlacklist()" class="px-3 py-2 rounded-lg text-sm" style="background: var(--bg-input); border: 1px solid var(--border); color: var(--text);">
              <option value="10">10/页</option>
              <option value="20" selected>20/页</option>
              <option value="50">50/页</option>
            </select>
            <button onclick="refreshBlacklist()" class="btn btn-primary text-sm">刷新</button>
            <input type="text" id="banIpInput" placeholder="输入 IP 地址"
              class="px-3 py-2 rounded-lg text-sm" style="background: var(--bg-input); border: 1px solid var(--border); color: var(--text);">
            <button onclick="banIp()" class="btn btn-danger text-sm">封禁</button>
          </div>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead>
              <tr style="color: var(--text-muted); border-bottom: 1px solid var(--border);">
                <th class="text-left py-3 px-3">
                  <input type="checkbox" id="blacklistSelectAll" onchange="toggleSelectAllBlacklist(this.checked)">
                </th>
                <th class="text-left py-3 px-3">IP 地址</th>
                <th class="text-left py-3 px-3 cursor-pointer hover:text-indigo-400" onclick="sortBlacklist('banned_at')">封禁时间 ↕</th>
                <th class="text-left py-3 px-3">原因</th>
                <th class="text-left py-3 px-3">操作</th>
              </tr>
            </thead>
            <tbody id="blacklistTable">
              <tr><td colspan="5" class="py-6 text-center" style="color: var(--text-muted);">加载中...</td></tr>
            </tbody>
          </table>
        </div>
        <div class="flex items-center justify-between mt-4 pt-4" style="border-top: 1px solid var(--border);">
          <div class="flex items-center gap-2">
            <button onclick="batchUnbanBlacklist()" class="btn btn-success text-sm" id="batchUnbanBtn" style="display: none;">批量解封 (<span id="selectedBlacklistCount">0</span>)</button>
          </div>
          <div id="blacklistPagination" class="flex items-center gap-4" style="display: none;">
            <span id="blacklistInfo" class="text-sm" style="color: var(--text-muted);"></span>
            <div id="blacklistPages" class="flex gap-1"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Tab Content: Token Management -->
    <div id="tab-tokens" class="tab-content hidden">
      <div class="card mb-6">
        <div class="flex flex-wrap justify-between items-center gap-4 mb-4">
          <h2 class="text-lg font-semibold">🔑 缓存的用户 Token</h2>
          <div class="flex items-center gap-2">
            <input type="text" id="tokensSearch" placeholder="搜索 Token..." oninput="filterCachedTokens()"
              class="px-3 py-2 rounded-lg text-sm w-40" style="background: var(--bg-input); border: 1px solid var(--border); color: var(--text);">
            <select id="tokensPageSize" onchange="filterCachedTokens()" class="px-3 py-2 rounded-lg text-sm" style="background: var(--bg-input); border: 1px solid var(--border); color: var(--text);">
              <option value="10">10/页</option>
              <option value="20" selected>20/页</option>
              <option value="50">50/页</option>
            </select>
            <button onclick="refreshTokenList()" class="btn btn-primary text-sm">刷新</button>
            <button onclick="batchRemoveTokens()" class="btn btn-danger text-sm">批量移除</button>
          </div>
        </div>
        <p class="text-sm mb-4" style="color: var(--text-muted);">
          多租户模式下，每个用户的 REFRESH_TOKEN 会被缓存以提升性能。最多缓存 100 个用户。
        </p>
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead>
              <tr style="color: var(--text-muted); border-bottom: 1px solid var(--border);">
                <th class="text-left py-3 px-3">
                  <input type="checkbox" id="selectAllTokens" onchange="toggleAllTokens(this.checked)" class="rounded">
                </th>
                <th class="text-left py-3 px-3 cursor-pointer hover:text-indigo-400" onclick="sortCachedTokens('index')"># ↕</th>
                <th class="text-left py-3 px-3 cursor-pointer hover:text-indigo-400" onclick="sortCachedTokens('masked_token')">Token (已脱敏) ↕</th>
                <th class="text-left py-3 px-3 cursor-pointer hover:text-indigo-400" onclick="sortCachedTokens('has_access_token')">状态 ↕</th>
                <th class="text-left py-3 px-3">操作</th>
              </tr>
            </thead>
            <tbody id="tokenListTable">
              <tr><td colspan="5" class="py-6 text-center" style="color: var(--text-muted);">加载中...</td></tr>
            </tbody>
          </table>
        </div>
        <div id="tokensPagination" class="flex items-center justify-between mt-4 pt-4" style="border-top: 1px solid var(--border); display: none;">
          <span id="tokensInfo" class="text-sm" style="color: var(--text-muted);"></span>
          <div id="tokensPages" class="flex gap-1"></div>
        </div>
      </div>

      <div class="card">
        <h2 class="text-lg font-semibold mb-4">📊 Token 使用统计</h2>
        <div class="grid md:grid-cols-2 gap-4">
          <div style="background: var(--bg-input);" class="p-4 rounded-lg">
            <div class="text-sm" style="color: var(--text-muted);">全局 Token 状态</div>
            <div class="text-xl font-bold mt-1" id="globalTokenStatus">-</div>
          </div>
          <div style="background: var(--bg-input);" class="p-4 rounded-lg">
            <div class="text-sm" style="color: var(--text-muted);">缓存用户数</div>
            <div class="text-xl font-bold mt-1" id="cachedUsersCount">-</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Tab Content: System -->
    <div id="tab-system" class="tab-content hidden">
      <div class="grid md:grid-cols-2 gap-6">
        <div class="card">
          <h2 class="text-lg font-semibold mb-4">⚙️ 站点控制</h2>
          <div class="flex items-center justify-between p-4 rounded-lg" style="background: var(--bg-input);">
            <div>
              <div class="font-medium">站点开关</div>
              <div class="text-sm" style="color: var(--text-muted);">关闭后所有 API 请求返回 503</div>
            </div>
            <label class="switch">
              <input type="checkbox" id="siteToggle" onchange="toggleSite(this.checked)">
              <span class="slider"></span>
            </label>
          </div>
        </div>

        <div class="card">
          <h2 class="text-lg font-semibold mb-4">🔧 系统操作</h2>
          <div class="space-y-3">
            <button onclick="refreshToken()" class="w-full btn btn-primary flex items-center justify-center gap-2">
              <span>🔄</span> 刷新 Kiro Token
            </button>
            <button onclick="clearCache()" class="w-full btn flex items-center justify-center gap-2"
              style="background: var(--bg-input); border: 1px solid var(--border);">
              <span>🗑️</span> 清除模型缓存
            </button>
          </div>
        </div>
      </div>

      <div class="card mt-6">
        <h2 class="text-lg font-semibold mb-4">📋 系统信息</h2>
        <div class="grid md:grid-cols-2 gap-4 text-sm">
          <div class="flex justify-between p-3 rounded" style="background: var(--bg-input);">
            <span style="color: var(--text-muted);">版本</span>
            <span class="font-mono">{APP_VERSION}</span>
          </div>
          <div class="flex justify-between p-3 rounded" style="background: var(--bg-input);">
            <span style="color: var(--text-muted);">缓存大小</span>
            <span class="font-mono" id="cacheSize">-</span>
          </div>
        </div>
      </div>
    </div>
  </main>

  <script>
    let currentTab = 'overview';
    const allTabs = ['overview','users','donated-tokens','ip-stats','blacklist','tokens','system'];

    function renderTokenStatus(status) {{
      if (status === 'active') return '<span class="text-green-400">有效</span>';
      if (status === 'invalid') return '<span class="text-red-400">无效</span>';
      if (status === 'expired') return '<span class="text-red-400">已过期</span>';
      return `<span class="text-red-400">${{status || '-'}}</span>`;
    }}

    function showTab(tab) {{
      document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(c => c.classList.add('hidden'));
      document.querySelector(`.tab:nth-child(${{allTabs.indexOf(tab)+1}})`).classList.add('active');
      document.getElementById('tab-' + tab).classList.remove('hidden');
      currentTab = tab;
      if (tab === 'users') refreshUsers();
      if (tab === 'donated-tokens') refreshDonatedTokens();
      if (tab === 'ip-stats') refreshIpStats();
      if (tab === 'blacklist') refreshBlacklist();
      if (tab === 'tokens') refreshTokenList();
    }}

    async function refreshStats() {{
      try {{
        const r = await fetch('/admin/api/stats');
        const d = await r.json();
        // Site toggle and icon
        const siteEnabled = d.site_enabled;
        document.getElementById('siteIcon').textContent = siteEnabled ? '🟢' : '🔴';
        document.getElementById('siteToggleQuick').checked = siteEnabled;
        document.getElementById('siteToggle').checked = siteEnabled;
        // Token status
        document.getElementById('tokenStatus').innerHTML = d.token_valid ? '<span class="text-green-400">有效</span>' : '<span class="text-yellow-400">未知</span>';
        document.getElementById('totalRequests').textContent = d.total_requests || 0;
        document.getElementById('cachedTokens').textContent = d.cached_tokens || 0;
        document.getElementById('successRate').textContent = d.total_requests > 0 ? ((d.success_requests / d.total_requests) * 100).toFixed(1) + '%' : '0%';
        document.getElementById('avgLatency').textContent = (d.avg_latency || 0).toFixed(0) + 'ms';
        document.getElementById('activeConns').textContent = d.active_connections || 0;
        document.getElementById('cacheSize').textContent = d.cache_size || 0;
        // Token tab stats
        document.getElementById('globalTokenStatus').innerHTML = d.token_valid ? '<span class="text-green-400">有效</span>' : '<span class="text-yellow-400">未配置/未知</span>';
        document.getElementById('cachedUsersCount').textContent = (d.cached_tokens || 0) + ' / 100';
      }} catch (e) {{ console.error(e); }}
    }}

    // IP Stats 数据和状态
    let allIpStats = [];
    let ipStatsCurrentPage = 1;
    let ipStatsSortField = 'count';
    let ipStatsSortAsc = false;
    let selectedIps = new Set();

    async function refreshIpStats() {{
      try {{
        const r = await fetch('/admin/api/ip-stats');
        const d = await r.json();
        allIpStats = d || [];
        ipStatsCurrentPage = 1;
        selectedIps.clear();
        document.getElementById('selectAllIps').checked = false;
        filterIpStats();
      }} catch (e) {{ console.error(e); }}
    }}

    function filterIpStats() {{
      const search = document.getElementById('ipStatsSearch').value.toLowerCase();
      const pageSize = parseInt(document.getElementById('ipStatsPageSize').value);

      let filtered = allIpStats.filter(ip => ip.ip.toLowerCase().includes(search));

      filtered.sort((a, b) => {{
        let va = a[ipStatsSortField], vb = b[ipStatsSortField];
        if (ipStatsSortField === 'last_seen') {{
          va = va || 0;
          vb = vb || 0;
        }}
        if (va < vb) return ipStatsSortAsc ? -1 : 1;
        if (va > vb) return ipStatsSortAsc ? 1 : -1;
        return 0;
      }});

      const totalPages = Math.ceil(filtered.length / pageSize) || 1;
      if (ipStatsCurrentPage > totalPages) ipStatsCurrentPage = totalPages;
      const start = (ipStatsCurrentPage - 1) * pageSize;
      const paged = filtered.slice(start, start + pageSize);

      renderIpStatsTable(paged);
      renderIpStatsPagination(filtered.length, pageSize, totalPages);
    }}

    function sortIpStats(field) {{
      if (ipStatsSortField === field) {{
        ipStatsSortAsc = !ipStatsSortAsc;
      }} else {{
        ipStatsSortField = field;
        ipStatsSortAsc = false;
      }}
      filterIpStats();
    }}

    function goIpStatsPage(page) {{
      ipStatsCurrentPage = page;
      filterIpStats();
    }}

    function toggleSelectAllIps(checked) {{
      const checkboxes = document.querySelectorAll('#ipStatsTable input[type="checkbox"]');
      checkboxes.forEach(cb => {{
        cb.checked = checked;
        if (checked) selectedIps.add(cb.value);
        else selectedIps.delete(cb.value);
      }});
    }}

    function toggleIpSelection(ip, checked) {{
      if (checked) selectedIps.add(ip);
      else selectedIps.delete(ip);
    }}

    async function batchBanIps() {{
      if (selectedIps.size === 0) {{ alert('请先选择要封禁的 IP'); return; }}
      if (!confirm(`确定要封禁选中的 ${{selectedIps.size}} 个 IP 吗？`)) return;
      for (const ip of selectedIps) {{
        const fd = new FormData();
        fd.append('ip', ip);
        await fetch('/admin/api/ban-ip', {{ method: 'POST', body: fd }});
      }}
      selectedIps.clear();
      refreshIpStats();
      refreshBlacklist();
    }}

    function renderIpStatsTable(ips) {{
      const tb = document.getElementById('ipStatsTable');
      if (!ips.length) {{
        tb.innerHTML = '<tr><td colspan="5" class="py-6 text-center" style="color: var(--text-muted);">暂无数据</td></tr>';
        return;
      }}
      tb.innerHTML = ips.map(ip => `
        <tr class="table-row">
          <td class="py-3 px-3">
            <input type="checkbox" value="${{ip.ip}}" ${{selectedIps.has(ip.ip) ? 'checked' : ''}} onchange="toggleIpSelection('${{ip.ip}}', this.checked)">
          </td>
          <td class="py-3 px-3 font-mono">${{ip.ip}}</td>
          <td class="py-3 px-3">${{ip.count}}</td>
          <td class="py-3 px-3">${{ip.last_seen ? new Date(ip.last_seen * 1000).toLocaleString() : '-'}}</td>
          <td class="py-3 px-3">
            <button onclick="banIpDirect('${{ip.ip}}')" class="text-xs px-2 py-1 rounded bg-red-500/20 text-red-400 hover:bg-red-500/30">封禁</button>
          </td>
        </tr>
      `).join('');
    }}

    function renderIpStatsPagination(total, pageSize, totalPages) {{
      const pagination = document.getElementById('ipStatsPagination');
      const info = document.getElementById('ipStatsInfo');
      const pages = document.getElementById('ipStatsPages');

      if (total === 0) {{
        pagination.style.display = 'none';
        return;
      }}

      pagination.style.display = 'flex';
      const start = (ipStatsCurrentPage - 1) * pageSize + 1;
      const end = Math.min(ipStatsCurrentPage * pageSize, total);
      info.textContent = `显示 ${{start}}-${{end}} 条，共 ${{total}} 条`;

      let html = '';
      if (ipStatsCurrentPage > 1) html += `<button onclick="goIpStatsPage(${{ipStatsCurrentPage - 1}})" class="px-3 py-1 rounded text-sm" style="background: var(--bg-input);">上一页</button>`;

      for (let i = 1; i <= totalPages; i++) {{
        if (i === 1 || i === totalPages || (i >= ipStatsCurrentPage - 1 && i <= ipStatsCurrentPage + 1)) {{
          html += `<button onclick="goIpStatsPage(${{i}})" class="px-3 py-1 rounded text-sm ${{i === ipStatsCurrentPage ? 'text-white' : ''}}" style="background: ${{i === ipStatsCurrentPage ? 'var(--primary)' : 'var(--bg-input)'}};">${{i}}</button>`;
        }} else if (i === 2 || i === totalPages - 1) {{
          html += `<span class="px-2">...</span>`;
        }}
      }}

      if (ipStatsCurrentPage < totalPages) html += `<button onclick="goIpStatsPage(${{ipStatsCurrentPage + 1}})" class="px-3 py-1 rounded text-sm" style="background: var(--bg-input);">下一页</button>`;
      pages.innerHTML = html;
    }}

    // 黑名单数据和状态
    let allBlacklist = [];
    let blacklistCurrentPage = 1;
    let blacklistSortField = 'banned_at';
    let blacklistSortAsc = false;
    let selectedBlacklistIps = new Set();

    async function refreshBlacklist() {{
      try {{
        const r = await fetch('/admin/api/blacklist');
        const d = await r.json();
        allBlacklist = d || [];
        blacklistCurrentPage = 1;
        selectedBlacklistIps.clear();
        filterBlacklist();
      }} catch (e) {{ console.error(e); }}
    }}

    function filterBlacklist() {{
      const search = document.getElementById('blacklistSearch').value.toLowerCase();
      const pageSize = parseInt(document.getElementById('blacklistPageSize').value);

      // 筛选
      let filtered = allBlacklist.filter(b =>
        b.ip.toLowerCase().includes(search) ||
        (b.reason || '').toLowerCase().includes(search)
      );

      // 排序
      filtered.sort((a, b) => {{
        let va = a[blacklistSortField], vb = b[blacklistSortField];
        if (blacklistSortField === 'banned_at') {{
          va = va || 0;
          vb = vb || 0;
        }}
        if (va < vb) return blacklistSortAsc ? -1 : 1;
        if (va > vb) return blacklistSortAsc ? 1 : -1;
        return 0;
      }});

      // 分页
      const totalPages = Math.ceil(filtered.length / pageSize) || 1;
      if (blacklistCurrentPage > totalPages) blacklistCurrentPage = totalPages;
      const start = (blacklistCurrentPage - 1) * pageSize;
      const paged = filtered.slice(start, start + pageSize);

      renderBlacklistTable(paged);
      renderBlacklistPagination(filtered.length, pageSize, totalPages);
      updateBatchUnbanButton();
    }}

    function sortBlacklist(field) {{
      if (blacklistSortField === field) {{
        blacklistSortAsc = !blacklistSortAsc;
      }} else {{
        blacklistSortField = field;
        blacklistSortAsc = true;
      }}
      filterBlacklist();
    }}

    function goBlacklistPage(page) {{
      blacklistCurrentPage = page;
      filterBlacklist();
    }}

    function renderBlacklistTable(blacklist) {{
      const tb = document.getElementById('blacklistTable');
      if (!blacklist.length) {{
        tb.innerHTML = '<tr><td colspan="5" class="py-6 text-center" style="color: var(--text-muted);">黑名单为空</td></tr>';
        document.getElementById('blacklistSelectAll').checked = false;
        return;
      }}
      tb.innerHTML = blacklist.map(ip => `
        <tr class="table-row">
          <td class="py-3 px-3">
            <input type="checkbox" class="blacklist-checkbox" value="${{ip.ip}}" onchange="toggleBlacklistSelection('${{ip.ip}}', this.checked)">
          </td>
          <td class="py-3 px-3 font-mono">${{ip.ip}}</td>
          <td class="py-3 px-3">${{ip.banned_at ? new Date(ip.banned_at * 1000).toLocaleString() : '-'}}</td>
          <td class="py-3 px-3">${{ip.reason || '-'}}</td>
          <td class="py-3 px-3">
            <button onclick="unbanIp('${{ip.ip}}')" class="text-xs px-2 py-1 rounded bg-green-500/20 text-green-400 hover:bg-green-500/30">解封</button>
          </td>
        </tr>
      `).join('');

      // Update checkbox states
      document.querySelectorAll('.blacklist-checkbox').forEach(cb => {{
        cb.checked = selectedBlacklistIps.has(cb.value);
      }});
      const allChecked = blacklist.length > 0 && blacklist.every(ip => selectedBlacklistIps.has(ip.ip));
      document.getElementById('blacklistSelectAll').checked = allChecked;
    }}

    function renderBlacklistPagination(total, pageSize, totalPages) {{
      const pagination = document.getElementById('blacklistPagination');
      const info = document.getElementById('blacklistInfo');
      const pages = document.getElementById('blacklistPages');

      if (total === 0) {{
        pagination.style.display = 'none';
        return;
      }}

      pagination.style.display = 'flex';
      const start = (blacklistCurrentPage - 1) * pageSize + 1;
      const end = Math.min(blacklistCurrentPage * pageSize, total);
      info.textContent = `显示 ${{start}}-${{end}} 条，共 ${{total}} 条`;

      let html = '';
      if (blacklistCurrentPage > 1) html += `<button onclick="goBlacklistPage(${{blacklistCurrentPage - 1}})" class="px-3 py-1 rounded text-sm" style="background: var(--bg-input);">上一页</button>`;

      for (let i = 1; i <= totalPages; i++) {{
        if (i === 1 || i === totalPages || (i >= blacklistCurrentPage - 1 && i <= blacklistCurrentPage + 1)) {{
          html += `<button onclick="goBlacklistPage(${{i}})" class="px-3 py-1 rounded text-sm ${{i === blacklistCurrentPage ? 'text-white' : ''}}" style="background: ${{i === blacklistCurrentPage ? 'var(--primary)' : 'var(--bg-input)'}};">${{i}}</button>`;
        }} else if (i === blacklistCurrentPage - 2 || i === blacklistCurrentPage + 2) {{
          html += '<span class="px-2">...</span>';
        }}
      }}

      if (blacklistCurrentPage < totalPages) html += `<button onclick="goBlacklistPage(${{blacklistCurrentPage + 1}})" class="px-3 py-1 rounded text-sm" style="background: var(--bg-input);">下一页</button>`;
      pages.innerHTML = html;
    }}

    function toggleBlacklistSelection(ip, checked) {{
      if (checked) {{
        selectedBlacklistIps.add(ip);
      }} else {{
        selectedBlacklistIps.delete(ip);
      }}
      updateBatchUnbanButton();

      // Update select all checkbox
      const allCheckboxes = document.querySelectorAll('.blacklist-checkbox');
      const allChecked = allCheckboxes.length > 0 && Array.from(allCheckboxes).every(cb => cb.checked);
      document.getElementById('blacklistSelectAll').checked = allChecked;
    }}

    function toggleSelectAllBlacklist(checked) {{
      document.querySelectorAll('.blacklist-checkbox').forEach(cb => {{
        cb.checked = checked;
        if (checked) {{
          selectedBlacklistIps.add(cb.value);
        }} else {{
          selectedBlacklistIps.delete(cb.value);
        }}
      }});
      updateBatchUnbanButton();
    }}

    function updateBatchUnbanButton() {{
      const btn = document.getElementById('batchUnbanBtn');
      const count = document.getElementById('selectedBlacklistCount');
      if (selectedBlacklistIps.size > 0) {{
        btn.style.display = 'inline-block';
        count.textContent = selectedBlacklistIps.size;
      }} else {{
        btn.style.display = 'none';
      }}
    }}

    async function batchUnbanBlacklist() {{
      if (selectedBlacklistIps.size === 0) return;
      if (!confirm(`确定要解封选中的 ${{selectedBlacklistIps.size}} 个 IP 吗？`)) return;

      const ips = Array.from(selectedBlacklistIps);
      for (const ip of ips) {{
        const fd = new FormData();
        fd.append('ip', ip);
        await fetch('/admin/api/unban-ip', {{ method: 'POST', body: fd }});
      }}

      selectedBlacklistIps.clear();
      refreshBlacklist();
      refreshStats();
    }}


    async function banIpDirect(ip) {{
      if (!confirm('确定要封禁 ' + ip + ' 吗？')) return;
      const fd = new FormData();
      fd.append('ip', ip);
      fd.append('reason', '管理员手动封禁');
      await fetch('/admin/api/ban-ip', {{ method: 'POST', body: fd }});
      refreshIpStats();
      refreshBlacklist();
      refreshStats();
    }}

    async function banIp() {{
      const ip = document.getElementById('banIpInput').value.trim();
      if (!ip) return alert('请输入 IP 地址');
      const fd = new FormData();
      fd.append('ip', ip);
      fd.append('reason', '管理员手动封禁');
      await fetch('/admin/api/ban-ip', {{ method: 'POST', body: fd }});
      document.getElementById('banIpInput').value = '';
      refreshBlacklist();
      refreshStats();
    }}

    async function unbanIp(ip) {{
      if (!confirm('确定要解封 ' + ip + ' 吗？')) return;
      const fd = new FormData();
      fd.append('ip', ip);
      await fetch('/admin/api/unban-ip', {{ method: 'POST', body: fd }});
      refreshBlacklist();
      refreshStats();
    }}

    async function toggleSite(enabled) {{
      const fd = new FormData();
      fd.append('enabled', enabled);
      await fetch('/admin/api/toggle-site', {{ method: 'POST', body: fd }});
      refreshStats();
    }}

    async function refreshToken() {{
      const r = await fetch('/admin/api/refresh-token', {{ method: 'POST' }});
      const d = await r.json();
      alert(d.message || (d.success ? '刷新成功' : '刷新失败'));
      refreshStats();
    }}

    async function clearCache() {{
      const r = await fetch('/admin/api/clear-cache', {{ method: 'POST' }});
      const d = await r.json();
      alert(d.message || (d.success ? '清除成功' : '清除失败'));
    }}

    // 缓存 Token 列表数据和状态
    let allCachedTokens = [];
    let tokensCurrentPage = 1;
    let tokensSortField = 'index';
    let tokensSortAsc = false;
    let selectedTokens = new Set();

    async function refreshTokenList() {{
      try {{
        const r = await fetch('/admin/api/tokens');
        const d = await r.json();
        allCachedTokens = (d.tokens || []).map((t, i) => ({{ ...t, index: i + 1 }}));
        tokensCurrentPage = 1;
        selectedTokens.clear();
        filterCachedTokens();
      }} catch (e) {{ console.error(e); }}
    }}

    function filterCachedTokens() {{
      const search = document.getElementById('tokensSearch').value.toLowerCase();
      const pageSize = parseInt(document.getElementById('tokensPageSize').value);

      // 筛选
      let filtered = allCachedTokens.filter(t =>
        t.masked_token.toLowerCase().includes(search) ||
        t.token_id.toLowerCase().includes(search)
      );

      // 排序
      filtered.sort((a, b) => {{
        let va = a[tokensSortField], vb = b[tokensSortField];
        if (tokensSortField === 'has_access_token') {{
          va = va ? 1 : 0;
          vb = vb ? 1 : 0;
        }}
        if (va < vb) return tokensSortAsc ? -1 : 1;
        if (va > vb) return tokensSortAsc ? 1 : -1;
        return 0;
      }});

      // 分页
      const totalPages = Math.ceil(filtered.length / pageSize) || 1;
      if (tokensCurrentPage > totalPages) tokensCurrentPage = totalPages;
      const start = (tokensCurrentPage - 1) * pageSize;
      const paged = filtered.slice(start, start + pageSize);

      renderTokensTable(paged);
      renderTokensPagination(filtered.length, pageSize, totalPages);
    }}

    function sortCachedTokens(field) {{
      if (tokensSortField === field) {{
        tokensSortAsc = !tokensSortAsc;
      }} else {{
        tokensSortField = field;
        tokensSortAsc = true;
      }}
      filterCachedTokens();
    }}

    function goTokensPage(page) {{
      tokensCurrentPage = page;
      filterCachedTokens();
    }}

    function toggleAllTokens(checked) {{
      if (checked) {{
        allCachedTokens.forEach(t => selectedTokens.add(t.token_id));
      }} else {{
        selectedTokens.clear();
      }}
      filterCachedTokens();
    }}

    function toggleTokenSelection(tokenId, checked) {{
      if (checked) {{
        selectedTokens.add(tokenId);
      }} else {{
        selectedTokens.delete(tokenId);
      }}
      updateSelectAllCheckbox();
    }}

    function updateSelectAllCheckbox() {{
      const selectAll = document.getElementById('selectAllTokens');
      if (selectAll) {{
        selectAll.checked = allCachedTokens.length > 0 && selectedTokens.size === allCachedTokens.length;
        selectAll.indeterminate = selectedTokens.size > 0 && selectedTokens.size < allCachedTokens.length;
      }}
    }}

    function renderTokensTable(tokens) {{
      const tb = document.getElementById('tokenListTable');
      if (!tokens.length) {{
        tb.innerHTML = '<tr><td colspan="5" class="py-6 text-center" style="color: var(--text-muted);">暂无数据</td></tr>';
        return;
      }}
      tb.innerHTML = tokens.map(t => `
        <tr class="table-row">
          <td class="py-3 px-3">
            <input type="checkbox" class="rounded"
              ${{selectedTokens.has(t.token_id) ? 'checked' : ''}}
              onchange="toggleTokenSelection('${{t.token_id}}', this.checked)">
          </td>
          <td class="py-3 px-3">${{t.index}}</td>
          <td class="py-3 px-3 font-mono">${{t.masked_token}}</td>
          <td class="py-3 px-3">${{t.has_access_token ? '<span class="text-green-400">已认证</span>' : '<span class="text-yellow-400">待认证</span>'}}</td>
          <td class="py-3 px-3">
            <button onclick="removeToken('${{t.token_id}}')" class="text-xs px-2 py-1 rounded bg-red-500/20 text-red-400 hover:bg-red-500/30">移除</button>
          </td>
        </tr>
      `).join('');
      updateSelectAllCheckbox();
    }}

    function renderTokensPagination(total, pageSize, totalPages) {{
      const pagination = document.getElementById('tokensPagination');
      const info = document.getElementById('tokensInfo');
      const pages = document.getElementById('tokensPages');

      if (total === 0) {{
        pagination.style.display = 'none';
        return;
      }}

      pagination.style.display = 'flex';
      const start = (tokensCurrentPage - 1) * pageSize + 1;
      const end = Math.min(tokensCurrentPage * pageSize, total);
      info.textContent = `显示 ${{start}}-${{end}} 条，共 ${{total}} 条`;

      let html = '';
      if (tokensCurrentPage > 1) html += `<button onclick="goTokensPage(${{tokensCurrentPage - 1}})" class="px-3 py-1 rounded text-sm" style="background: var(--bg-input);">上一页</button>`;

      for (let i = 1; i <= totalPages; i++) {{
        if (i === 1 || i === totalPages || (i >= tokensCurrentPage - 1 && i <= tokensCurrentPage + 1)) {{
          html += `<button onclick="goTokensPage(${{i}})" class="px-3 py-1 rounded text-sm ${{i === tokensCurrentPage ? 'text-white' : ''}}" style="background: ${{i === tokensCurrentPage ? 'var(--primary)' : 'var(--bg-input)'}};">${{i}}</button>`;
        }} else if (i === tokensCurrentPage - 2 || i === tokensCurrentPage + 2) {{
          html += '<span class="px-2">...</span>';
        }}
      }}

      if (tokensCurrentPage < totalPages) html += `<button onclick="goTokensPage(${{tokensCurrentPage + 1}})" class="px-3 py-1 rounded text-sm" style="background: var(--bg-input);">下一页</button>`;
      pages.innerHTML = html;
    }}

    async function removeToken(tokenId) {{
      if (!confirm('确定要移除此 Token 吗？用户需要重新认证。')) return;
      const fd = new FormData();
      fd.append('token_id', tokenId);
      await fetch('/admin/api/remove-token', {{ method: 'POST', body: fd }});
      refreshTokenList();
      refreshStats();
    }}

    async function batchRemoveTokens() {{
      if (selectedTokens.size === 0) {{
        alert('请先选择要移除的 Token');
        return;
      }}
      if (!confirm(`确定要移除选中的 ${{selectedTokens.size}} 个 Token 吗？相关用户需要重新认证。`)) return;

      const promises = Array.from(selectedTokens).map(async tokenId => {{
        const fd = new FormData();
        fd.append('token_id', tokenId);
        return fetch('/admin/api/remove-token', {{ method: 'POST', body: fd }});
      }});

      await Promise.all(promises);
      selectedTokens.clear();
      refreshTokenList();
      refreshStats();
      alert('批量移除完成');
    }}

    // 用户列表数据和状态
    let allUsers = [];
    let usersCurrentPage = 1;
    let usersSortField = 'id';
    let usersSortAsc = false;

    async function refreshUsers() {{
      try {{
        const r = await fetch('/admin/api/users');
        const d = await r.json();
        allUsers = d.users || [];
        usersCurrentPage = 1;
        filterUsers();
      }} catch (e) {{ console.error(e); }}
    }}

    function filterUsers() {{
      const search = document.getElementById('usersSearch').value.toLowerCase();
      const pageSize = parseInt(document.getElementById('usersPageSize').value);

      // 筛选
      let filtered = allUsers.filter(u =>
        u.username.toLowerCase().includes(search) ||
        u.id.toString().includes(search)
      );

      // 排序
      filtered.sort((a, b) => {{
        let va = a[usersSortField], vb = b[usersSortField];
        if (usersSortField === 'created_at') {{
          va = new Date(va || 0).getTime();
          vb = new Date(vb || 0).getTime();
        }}
        if (va < vb) return usersSortAsc ? -1 : 1;
        if (va > vb) return usersSortAsc ? 1 : -1;
        return 0;
      }});

      // 分页
      const totalPages = Math.ceil(filtered.length / pageSize) || 1;
      if (usersCurrentPage > totalPages) usersCurrentPage = totalPages;
      const start = (usersCurrentPage - 1) * pageSize;
      const paged = filtered.slice(start, start + pageSize);

      renderUsersTable(paged);
      renderUsersPagination(filtered.length, pageSize, totalPages);
    }}

    function sortUsers(field) {{
      if (usersSortField === field) {{
        usersSortAsc = !usersSortAsc;
      }} else {{
        usersSortField = field;
        usersSortAsc = true;
      }}
      filterUsers();
    }}

    function goUsersPage(page) {{
      usersCurrentPage = page;
      filterUsers();
    }}

    function renderUsersTable(users) {{
      const tb = document.getElementById('usersTable');
      if (!users.length) {{
        tb.innerHTML = '<tr><td colspan="8" class="py-6 text-center" style="color: var(--text-muted);">暂无数据</td></tr>';
        return;
      }}
      tb.innerHTML = users.map(u => `
        <tr class="table-row">
          <td class="py-3 px-3">${{u.id}}</td>
          <td class="py-3 px-3 font-medium">${{u.username}}</td>
          <td class="py-3 px-3">Lv.${{u.trust_level}}</td>
          <td class="py-3 px-3">${{u.token_count}}</td>
          <td class="py-3 px-3">${{u.api_key_count}}</td>
          <td class="py-3 px-3">${{u.is_banned ? '<span class="text-red-400">已封禁</span>' : '<span class="text-green-400">正常</span>'}}</td>
          <td class="py-3 px-3">${{u.created_at ? new Date(u.created_at).toLocaleString() : '-'}}</td>
          <td class="py-3 px-3">
            ${{u.is_banned
              ? `<button onclick="unbanUser(${{u.id}})" class="text-xs px-2 py-1 rounded bg-green-500/20 text-green-400 hover:bg-green-500/30">解封</button>`
              : `<button onclick="banUser(${{u.id}})" class="text-xs px-2 py-1 rounded bg-red-500/20 text-red-400 hover:bg-red-500/30">封禁</button>`
            }}
          </td>
        </tr>
      `).join('');
    }}

    function renderUsersPagination(total, pageSize, totalPages) {{
      const pagination = document.getElementById('usersPagination');
      const info = document.getElementById('usersInfo');
      const pages = document.getElementById('usersPages');

      if (total === 0) {{
        pagination.style.display = 'none';
        return;
      }}

      pagination.style.display = 'flex';
      const start = (usersCurrentPage - 1) * pageSize + 1;
      const end = Math.min(usersCurrentPage * pageSize, total);
      info.textContent = `显示 ${{start}}-${{end}} 条，共 ${{total}} 条`;

      let html = '';
      if (usersCurrentPage > 1) html += `<button onclick="goUsersPage(${{usersCurrentPage - 1}})" class="px-3 py-1 rounded text-sm" style="background: var(--bg-input);">上一页</button>`;

      for (let i = 1; i <= totalPages; i++) {{
        if (i === 1 || i === totalPages || (i >= usersCurrentPage - 1 && i <= usersCurrentPage + 1)) {{
          html += `<button onclick="goUsersPage(${{i}})" class="px-3 py-1 rounded text-sm ${{i === usersCurrentPage ? 'text-white' : ''}}" style="background: ${{i === usersCurrentPage ? 'var(--primary)' : 'var(--bg-input)'}};">${{i}}</button>`;
        }} else if (i === usersCurrentPage - 2 || i === usersCurrentPage + 2) {{
          html += '<span class="px-2">...</span>';
        }}
      }}

      if (usersCurrentPage < totalPages) html += `<button onclick="goUsersPage(${{usersCurrentPage + 1}})" class="px-3 py-1 rounded text-sm" style="background: var(--bg-input);">下一页</button>`;
      pages.innerHTML = html;
    }}

    async function banUser(userId) {{
      if (!confirm('确定要封禁此用户吗？')) return;
      const fd = new FormData();
      fd.append('user_id', userId);
      await fetch('/admin/api/users/ban', {{ method: 'POST', body: fd }});
      refreshUsers();
    }}

    async function unbanUser(userId) {{
      if (!confirm('确定要解封此用户吗？')) return;
      const fd = new FormData();
      fd.append('user_id', userId);
      await fetch('/admin/api/users/unban', {{ method: 'POST', body: fd }});
      refreshUsers();
    }}

    // 捐献 Token 池数据和状态
    let allPoolTokens = [];
    let poolCurrentPage = 1;
    let poolSortField = 'id';
    let poolSortAsc = false;
    let selectedPoolTokens = new Set();
    let poolStatsData = {{}};

    async function refreshDonatedTokens() {{
      try {{
        const r = await fetch('/admin/api/donated-tokens');
        const d = await r.json();
        poolStatsData = d;
        document.getElementById('poolTotalTokens').textContent = d.total || 0;
        document.getElementById('poolActiveTokens').textContent = d.active || 0;
        document.getElementById('poolPublicTokens').textContent = d.public || 0;
        document.getElementById('poolAvgSuccessRate').textContent = d.avg_success_rate ? d.avg_success_rate.toFixed(1) + '%' : '-';
        allPoolTokens = (d.tokens || []).map(t => ({{
          ...t,
          success_rate: t.success_rate || 0,
          use_count: (t.success_count || 0) + (t.fail_count || 0)
        }}));
        poolCurrentPage = 1;
        selectedPoolTokens.clear();
        document.getElementById('selectAllPool').checked = false;
        filterPoolTokens();
      }} catch (e) {{ console.error(e); }}
    }}

    function filterPoolTokens() {{
      const search = document.getElementById('poolSearch').value.toLowerCase();
      const visibility = document.getElementById('poolVisibilityFilter').value;
      const pageSize = parseInt(document.getElementById('poolPageSize').value);

      let filtered = allPoolTokens.filter(t => {{
        const matchSearch = (t.username || '').toLowerCase().includes(search) || t.id.toString().includes(search);
        const matchVisibility = !visibility || t.visibility === visibility;
        return matchSearch && matchVisibility;
      }});

      filtered.sort((a, b) => {{
        let va = a[poolSortField], vb = b[poolSortField];
        if (poolSortField === 'last_used') {{
          va = va ? new Date(va).getTime() : 0;
          vb = vb ? new Date(vb).getTime() : 0;
        }}
        if (va < vb) return poolSortAsc ? -1 : 1;
        if (va > vb) return poolSortAsc ? 1 : -1;
        return 0;
      }});

      const totalPages = Math.ceil(filtered.length / pageSize) || 1;
      if (poolCurrentPage > totalPages) poolCurrentPage = totalPages;
      const start = (poolCurrentPage - 1) * pageSize;
      const paged = filtered.slice(start, start + pageSize);

      renderPoolTable(paged);
      renderPoolPagination(filtered.length, pageSize, totalPages);
    }}

    function sortPoolTokens(field) {{
      if (poolSortField === field) {{
        poolSortAsc = !poolSortAsc;
      }} else {{
        poolSortField = field;
        poolSortAsc = false;
      }}
      filterPoolTokens();
    }}

    function goPoolPage(page) {{
      poolCurrentPage = page;
      filterPoolTokens();
    }}

    function toggleSelectAllPool(checked) {{
      const checkboxes = document.querySelectorAll('#donatedTokensTable input[type="checkbox"]');
      checkboxes.forEach(cb => {{
        cb.checked = checked;
        if (checked) selectedPoolTokens.add(parseInt(cb.value));
        else selectedPoolTokens.delete(parseInt(cb.value));
      }});
    }}

    function togglePoolSelection(id, checked) {{
      if (checked) selectedPoolTokens.add(id);
      else selectedPoolTokens.delete(id);
    }}

    async function batchDeletePoolTokens() {{
      if (selectedPoolTokens.size === 0) {{ alert('请先选择要删除的 Token'); return; }}
      if (!confirm(`确定要删除选中的 ${{selectedPoolTokens.size}} 个 Token 吗？`)) return;
      for (const id of selectedPoolTokens) {{
        const fd = new FormData();
        fd.append('token_id', id);
        await fetch('/admin/api/donated-tokens/delete', {{ method: 'POST', body: fd }});
      }}
      selectedPoolTokens.clear();
      refreshDonatedTokens();
    }}

    function renderPoolTable(tokens) {{
      const tb = document.getElementById('donatedTokensTable');
      if (!tokens.length) {{
        tb.innerHTML = '<tr><td colspan="9" class="py-6 text-center" style="color: var(--text-muted);">暂无捐献 Token</td></tr>';
        return;
      }}
      tb.innerHTML = tokens.map(t => `
        <tr class="table-row">
          <td class="py-3 px-3">
            <input type="checkbox" value="${{t.id}}" ${{selectedPoolTokens.has(t.id) ? 'checked' : ''}} onchange="togglePoolSelection(${{t.id}}, this.checked)">
          </td>
          <td class="py-3 px-3">#${{t.id}}</td>
          <td class="py-3 px-3">${{t.username || '未知'}}</td>
          <td class="py-3 px-3">${{t.visibility === 'public' ? '<span class="text-green-400">公开</span>' : '<span class="text-blue-400">私有</span>'}}</td>
          <td class="py-3 px-3">${{renderTokenStatus(t.status)}}</td>
          <td class="py-3 px-3">${{(t.success_rate * 100).toFixed(1)}}%</td>
          <td class="py-3 px-3">${{t.use_count}}</td>
          <td class="py-3 px-3">${{t.last_used ? new Date(t.last_used).toLocaleString() : '-'}}</td>
          <td class="py-3 px-3">
            <button onclick="toggleTokenVisibility(${{t.id}}, '${{t.visibility === 'public' ? 'private' : 'public'}}')" class="text-xs px-2 py-1 rounded bg-indigo-500/20 text-indigo-400 hover:bg-indigo-500/30 mr-1">切换</button>
            <button onclick="deleteDonatedToken(${{t.id}})" class="text-xs px-2 py-1 rounded bg-red-500/20 text-red-400 hover:bg-red-500/30">删除</button>
          </td>
        </tr>
      `).join('');
    }}

    function renderPoolPagination(total, pageSize, totalPages) {{
      const pagination = document.getElementById('poolPagination');
      const info = document.getElementById('poolInfo');
      const pages = document.getElementById('poolPages');

      if (total === 0) {{
        pagination.style.display = 'none';
        return;
      }}

      pagination.style.display = 'flex';
      const start = (poolCurrentPage - 1) * pageSize + 1;
      const end = Math.min(poolCurrentPage * pageSize, total);
      info.textContent = `显示 ${{start}}-${{end}} 条，共 ${{total}} 条`;

      let html = '';
      if (poolCurrentPage > 1) html += `<button onclick="goPoolPage(${{poolCurrentPage - 1}})" class="px-3 py-1 rounded text-sm" style="background: var(--bg-input);">上一页</button>`;

      for (let i = 1; i <= totalPages; i++) {{
        if (i === 1 || i === totalPages || (i >= poolCurrentPage - 1 && i <= poolCurrentPage + 1)) {{
          html += `<button onclick="goPoolPage(${{i}})" class="px-3 py-1 rounded text-sm ${{i === poolCurrentPage ? 'text-white' : ''}}" style="background: ${{i === poolCurrentPage ? 'var(--primary)' : 'var(--bg-input)'}};">${{i}}</button>`;
        }} else if (i === 2 || i === totalPages - 1) {{
          html += `<span class="px-2">...</span>`;
        }}
      }}

      if (poolCurrentPage < totalPages) html += `<button onclick="goPoolPage(${{poolCurrentPage + 1}})" class="px-3 py-1 rounded text-sm" style="background: var(--bg-input);">下一页</button>`;
      pages.innerHTML = html;
    }}

    async function toggleTokenVisibility(tokenId, newVisibility) {{
      const fd = new FormData();
      fd.append('token_id', tokenId);
      fd.append('visibility', newVisibility);
      await fetch('/admin/api/donated-tokens/visibility', {{ method: 'POST', body: fd }});
      refreshDonatedTokens();
    }}

    async function deleteDonatedToken(tokenId) {{
      if (!confirm('确定要删除此 Token 吗？')) return;
      const fd = new FormData();
      fd.append('token_id', tokenId);
      await fetch('/admin/api/donated-tokens/delete', {{ method: 'POST', body: fd }});
      refreshDonatedTokens();
    }}

    refreshStats();
    setInterval(refreshStats, 10000);

    // Theme management
    function initTheme() {{
      const saved = localStorage.getItem('theme');
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      const isDark = saved === 'dark' || (!saved && prefersDark);
      document.documentElement.classList.toggle('dark', isDark);
      document.getElementById('themeIcon').textContent = isDark ? '☀️' : '🌙';
    }}
    function toggleTheme() {{
      const isDark = document.documentElement.classList.toggle('dark');
      localStorage.setItem('theme', isDark ? 'dark' : 'light');
      document.getElementById('themeIcon').textContent = isDark ? '☀️' : '🌙';
    }}
    initTheme();
  </script>
  {COMMON_FOOTER}
</body>
</html>'''


def render_user_page(user) -> str:
    """Render the user dashboard page."""
    # Determine avatar display
    if user.avatar_url:
        avatar_html = f'<img src="{user.avatar_url}" class="w-16 h-16 rounded-full object-cover" alt="{user.username}">'
    else:
        avatar_html = f'<div class="w-16 h-16 rounded-full bg-indigo-500/20 flex items-center justify-center text-2xl">{user.username[0].upper() if user.username else "👤"}</div>'

    # Determine user info display based on login provider
    if user.github_id:
        user_info = '<span class="text-sm px-2 py-1 rounded bg-gray-700 text-white">GitHub 用户</span>'
    elif user.linuxdo_id:
        user_info = f'<span style="color: var(--text-muted);">信任等级: Lv.{user.trust_level}</span>'
    else:
        user_info = ''

    return f'''<!DOCTYPE html>
<html lang="zh">
<head>{COMMON_HEAD}</head>
<body>
  {COMMON_NAV}
  <main class="max-w-6xl mx-auto px-4 py-8">
    <div class="card mb-6">
      <div class="flex items-center gap-4">
        {avatar_html}
        <div>
          <h1 class="text-2xl font-bold">{user.username}</h1>
          <p>{user_info}</p>
        </div>
        <div class="ml-auto">
          <a href="/oauth2/logout" class="btn-primary">退出登录</a>
        </div>
      </div>
    </div>
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
      <div class="card text-center">
        <div class="text-3xl font-bold text-indigo-400" id="tokenCount">-</div>
        <div class="text-sm" style="color: var(--text-muted);">我的 Token</div>
      </div>
      <div class="card text-center">
        <div class="text-3xl font-bold text-green-400" id="publicTokenCount">-</div>
        <div class="text-sm" style="color: var(--text-muted);">公开 Token</div>
      </div>
      <div class="card text-center">
        <div class="text-3xl font-bold text-amber-400" id="apiKeyCount">-</div>
        <div class="text-sm" style="color: var(--text-muted);">API Keys</div>
      </div>
      <div class="card text-center">
        <div class="text-3xl font-bold text-purple-400" id="requestCount">-</div>
        <div class="text-sm" style="color: var(--text-muted);">总请求</div>
      </div>
    </div>
    <div class="flex gap-2 mb-4 border-b" style="border-color: var(--border);">
      <button class="tab px-4 py-2 font-medium" onclick="showTab('tokens')" id="tab-tokens">🔑 Token 管理</button>
      <button class="tab px-4 py-2 font-medium" onclick="showTab('keys')" id="tab-keys">🗝️ API Keys</button>
    </div>
    <div id="panel-tokens" class="tab-panel">
      <div class="card">
        <!-- 可折叠的获取 Token 说明 -->
        <details class="mb-6 rounded-lg" style="background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(168, 85, 247, 0.1)); border: 1px solid var(--primary);">
          <summary class="p-4 cursor-pointer font-bold flex items-center gap-2 select-none">
            <span>💡</span> 如何获取 Refresh Token
            <svg class="w-4 h-4 ml-auto transition-transform details-arrow" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
          </summary>
          <div class="px-4 pb-4">
            <ol class="text-sm space-y-2" style="color: var(--text-muted);">
              <li><span class="font-medium" style="color: var(--text);">1.</span> 打开 <a href="https://app.kiro.dev/account/usage" target="_blank" class="text-indigo-400 hover:underline">https://app.kiro.dev/account/usage</a> 并登录</li>
              <li><span class="font-medium" style="color: var(--text);">2.</span> 按 <kbd class="px-1.5 py-0.5 rounded text-xs" style="background: var(--bg-input); border: 1px solid var(--border);">F12</kbd> 打开开发者工具</li>
              <li><span class="font-medium" style="color: var(--text);">3.</span> 点击 <strong>应用/Application</strong> 标签页</li>
              <li><span class="font-medium" style="color: var(--text);">4.</span> 左侧展开 <strong>存储/Storage</strong> → <strong>Cookie</strong></li>
              <li><span class="font-medium" style="color: var(--text);">5.</span> 选择 <code class="px-1 rounded" style="background: var(--bg-input);">https://app.kiro.dev</code></li>
              <li><span class="font-medium" style="color: var(--text);">6.</span> 找到名称为 <code class="px-1 rounded text-green-400" style="background: var(--bg-input);">RefreshToken</code> 的条目，复制其 <strong>值/Value</strong></li>
            </ol>
          </div>
        </details>

        <!-- 子标签切换：我的 Token / 公开 Token -->
        <div class="flex gap-1 mb-4 p-1 rounded-lg" style="background: var(--bg-input);">
          <button onclick="showTokenSubTab('mine')" id="subtab-mine" class="subtab flex-1 px-4 py-2 rounded-md text-sm font-medium transition-all">🔐 我的 Token</button>
          <button onclick="showTokenSubTab('public')" id="subtab-public" class="subtab flex-1 px-4 py-2 rounded-md text-sm font-medium transition-all">🌐 公开 Token 池</button>
        </div>

        <!-- 我的 Token 面板 -->
        <div id="subtab-panel-mine">
          <div class="flex flex-wrap items-center gap-3 mb-4">
            <h2 class="text-lg font-bold">我的 Token</h2>
            <div class="flex-1 flex items-center gap-2 flex-wrap">
              <input type="text" id="tokensSearch" placeholder="搜索 ID 或状态..." oninput="filterTokens()" class="px-3 py-1.5 rounded-lg text-sm" style="background: var(--bg-input); border: 1px solid var(--border); min-width: 160px;">
              <select id="tokensPageSize" onchange="filterTokens()" class="px-3 py-1.5 rounded-lg text-sm" style="background: var(--bg-input); border: 1px solid var(--border);">
                <option value="10">10 条/页</option>
                <option value="20">20 条/页</option>
                <option value="50">50 条/页</option>
              </select>
              <button onclick="refreshTokens()" class="btn btn-primary text-sm px-3 py-1.5 rounded-lg" style="background: var(--primary); color: white;">刷新</button>
              <button onclick="batchDeleteTokens()" id="batchDeleteBtn" class="btn btn-danger text-sm px-3 py-1.5 rounded-lg" style="background: #ef4444; color: white; display: none;">批量删除</button>
            </div>
            <button onclick="showDonateModal()" class="btn-primary">+ 捐献 Token</button>
          </div>
          <div class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead>
                <tr style="color: var(--text-muted); border-bottom: 1px solid var(--border);">
                  <th class="text-left py-3 px-3" style="width: 40px;">
                    <input type="checkbox" id="selectAllTokens" onchange="toggleAllTokens(this.checked)" class="cursor-pointer">
                  </th>
                  <th class="text-left py-3 px-3 cursor-pointer hover:text-indigo-400" onclick="sortTokens('id')">ID ↕</th>
                  <th class="text-left py-3 px-3 cursor-pointer hover:text-indigo-400" onclick="sortTokens('visibility')">可见性 ↕</th>
                  <th class="text-left py-3 px-3 cursor-pointer hover:text-indigo-400" onclick="sortTokens('status')">状态 ↕</th>
                  <th class="text-left py-3 px-3 cursor-pointer hover:text-indigo-400" onclick="sortTokens('success_rate')">成功率 ↕</th>
                  <th class="text-left py-3 px-3 cursor-pointer hover:text-indigo-400" onclick="sortTokens('last_used')">最后使用 ↕</th>
                  <th class="text-left py-3 px-3">操作</th>
                </tr>
              </thead>
              <tbody id="tokenTable">
                <tr><td colspan="7" class="py-6 text-center" style="color: var(--text-muted);">加载中...</td></tr>
              </tbody>
            </table>
          </div>
          <div id="tokensPagination" class="flex items-center justify-between mt-4 pt-4" style="border-top: 1px solid var(--border); display: none;">
            <span id="tokensInfo" class="text-sm" style="color: var(--text-muted);"></span>
            <div id="tokensPages" class="flex gap-1"></div>
          </div>
        </div>

        <!-- 公开 Token 池面板 -->
        <div id="subtab-panel-public" style="display: none;">
          <div class="flex flex-wrap items-center gap-3 mb-4">
            <h2 class="text-lg font-bold">公开 Token 池</h2>
            <div class="flex-1 flex items-center gap-2 flex-wrap">
              <input type="text" id="publicTokenSearch" placeholder="搜索贡献者..." oninput="filterPublicTokens()" class="px-3 py-1.5 rounded-lg text-sm" style="background: var(--bg-input); border: 1px solid var(--border); min-width: 140px;">
              <select id="publicTokenPageSize" onchange="filterPublicTokens()" class="px-3 py-1.5 rounded-lg text-sm" style="background: var(--bg-input); border: 1px solid var(--border);">
                <option value="10">10 条/页</option>
                <option value="20" selected>20 条/页</option>
                <option value="50">50 条/页</option>
              </select>
              <button onclick="loadPublicTokens()" class="btn btn-primary text-sm px-3 py-1.5 rounded-lg" style="background: var(--primary); color: white;">刷新</button>
            </div>
            <div class="flex items-center gap-4 text-sm">
              <span style="color: var(--text-muted);">共 <strong id="publicPoolCount" class="text-green-400">-</strong> 个</span>
              <span style="color: var(--text-muted);">平均成功率 <strong id="publicPoolAvgRate" class="text-indigo-400">-</strong></span>
            </div>
          </div>
          <div class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead>
                <tr style="color: var(--text-muted); border-bottom: 1px solid var(--border);">
                  <th class="text-left py-3 px-3">#</th>
                  <th class="text-left py-3 px-3 cursor-pointer hover:text-indigo-400" onclick="sortPublicTokens('username')">贡献者 ↕</th>
                  <th class="text-left py-3 px-3">状态</th>
                  <th class="text-left py-3 px-3 cursor-pointer hover:text-indigo-400" onclick="sortPublicTokens('success_rate')">成功率 ↕</th>
                  <th class="text-left py-3 px-3 cursor-pointer hover:text-indigo-400" onclick="sortPublicTokens('use_count')">使用次数 ↕</th>
                  <th class="text-left py-3 px-3 cursor-pointer hover:text-indigo-400" onclick="sortPublicTokens('last_used')">最后使用 ↕</th>
                </tr>
              </thead>
              <tbody id="publicTokenTable">
                <tr><td colspan="6" class="py-6 text-center" style="color: var(--text-muted);">加载中...</td></tr>
              </tbody>
            </table>
          </div>
          <div id="publicTokenPagination" class="flex items-center justify-between mt-4 pt-4" style="border-top: 1px solid var(--border); display: none;">
            <span id="publicTokenInfo" class="text-sm" style="color: var(--text-muted);"></span>
            <div id="publicTokenPages" class="flex gap-1"></div>
          </div>
          <p class="mt-4 text-sm" style="color: var(--text-muted);">
            💡 公开 Token 池由社区成员自愿贡献，供所有用户共享使用。您也可以切换到"我的 Token"捐献您的 Token。
          </p>
        </div>
      </div>
    </div>
    <div id="panel-keys" class="tab-panel" style="display: none;">
      <div class="card">
        <div class="flex flex-wrap justify-between items-center gap-4 mb-4">
          <h2 class="text-lg font-bold">我的 API Keys</h2>
          <div class="flex items-center gap-2">
            <input type="text" id="keysSearch" placeholder="搜索 Key 或名称..." oninput="filterKeys()"
              class="px-3 py-2 rounded-lg text-sm w-40" style="background: var(--bg-input); border: 1px solid var(--border); color: var(--text);">
            <select id="keysPageSize" onchange="filterKeys()" class="px-3 py-2 rounded-lg text-sm" style="background: var(--bg-input); border: 1px solid var(--border); color: var(--text);">
              <option value="10" selected>10/页</option>
              <option value="20">20/页</option>
              <option value="50">50/页</option>
            </select>
            <button onclick="refreshKeys()" class="btn btn-primary text-sm">刷新</button>
            <button onclick="generateKey()" class="btn-primary text-sm">+ 生成新 Key</button>
          </div>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead>
              <tr style="color: var(--text-muted); border-bottom: 1px solid var(--border);">
                <th class="text-left py-3 px-3">
                  <input type="checkbox" id="selectAllKeys" onchange="toggleSelectAllKeys()" style="cursor: pointer;">
                </th>
                <th class="text-left py-3 px-3 cursor-pointer hover:text-indigo-400" onclick="sortKeys('key_prefix')">Key ↕</th>
                <th class="text-left py-3 px-3 cursor-pointer hover:text-indigo-400" onclick="sortKeys('name')">名称 ↕</th>
                <th class="text-left py-3 px-3 cursor-pointer hover:text-indigo-400" onclick="sortKeys('request_count')">请求数 ↕</th>
                <th class="text-left py-3 px-3 cursor-pointer hover:text-indigo-400" onclick="sortKeys('last_used')">最后使用 ↕</th>
                <th class="text-left py-3 px-3 cursor-pointer hover:text-indigo-400" onclick="sortKeys('created_at')">创建时间 ↕</th>
                <th class="text-left py-3 px-3">操作</th>
              </tr>
            </thead>
            <tbody id="keyTable"></tbody>
          </table>
        </div>
        <div class="flex items-center justify-between mt-4 pt-4" style="border-top: 1px solid var(--border);">
          <div class="flex items-center gap-2">
            <button onclick="batchDeleteKeys()" class="text-xs px-3 py-1.5 rounded bg-red-500/20 text-red-400 hover:bg-red-500/30" id="batchDeleteBtn" style="display: none;">批量删除</button>
            <span id="selectedKeysCount" class="text-sm" style="color: var(--text-muted); display: none;"></span>
          </div>
          <div id="keysPagination" style="display: none;">
            <span id="keysInfo" class="text-sm mr-4" style="color: var(--text-muted);"></span>
            <div id="keysPages" class="inline-flex gap-1"></div>
          </div>
        </div>
        <p class="mt-4 text-sm" style="color: var(--text-muted);">
          💡 API Key 仅在创建时显示一次，请妥善保存。使用方式: <code class="bg-black/20 px-1 rounded">Authorization: Bearer sk-xxx</code><br>
          ⚠️ 每个账户最多可创建 <strong>10</strong> 个 API Key
        </p>
      </div>
    </div>
  </main>
  <div id="donateModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" style="display: none;">
    <div class="card w-full max-w-md mx-4">
      <h3 class="text-lg font-bold mb-4">🎁 添加 Refresh Token</h3>

      <!-- 模式选择 -->
      <div class="flex gap-1 mb-4 p-1 rounded-lg" style="background: var(--bg-input);">
        <button onclick="setDonateMode('private')" id="donateMode-private" class="donate-mode-btn flex-1 px-4 py-2 rounded-md text-sm font-medium transition-all active">🔐 个人使用</button>
        <button onclick="setDonateMode('public')" id="donateMode-public" class="donate-mode-btn flex-1 px-4 py-2 rounded-md text-sm font-medium transition-all">🌐 公开捐献</button>
      </div>

      <!-- 模式说明 -->
      <div id="donateDesc-private" class="mb-4 p-3 rounded-lg text-sm" style="background: rgba(99, 102, 241, 0.1); border: 1px solid rgba(99, 102, 241, 0.3);">
        <p class="font-medium text-indigo-400 mb-1">💡 个人使用模式</p>
        <ul class="space-y-1" style="color: var(--text-muted);">
          <li>• Token 仅供您自己使用</li>
          <li>• 不会加入公共 Token 池</li>
          <li>• 适合保护个人配额不被他人消耗</li>
        </ul>
      </div>
      <div id="donateDesc-public" class="mb-4 p-3 rounded-lg text-sm" style="background: rgba(34, 197, 94, 0.1); border: 1px solid rgba(34, 197, 94, 0.3); display: none;">
        <p class="font-medium text-green-400 mb-1">🌍 公开捐献模式</p>
        <ul class="space-y-1" style="color: var(--text-muted);">
          <li>• Token 加入公共池供所有用户共享</li>
          <li>• 帮助社区其他成员使用服务</li>
          <li>• 您仍可随时切换为私有或删除</li>
        </ul>
      </div>

      <textarea id="donateToken" class="w-full h-28 p-3 rounded-lg" style="background: var(--bg-input); border: 1px solid var(--border);" placeholder="粘贴你的 Refresh Token..."></textarea>

      <!-- 匿名选项（仅公开模式显示） -->
      <div id="anonymousOption" class="mt-3 p-3 rounded-lg" style="background: var(--bg-input); display: none;">
        <label class="flex items-center gap-3 cursor-pointer">
          <input type="checkbox" id="donateAnonymous" class="w-4 h-4 rounded">
          <div>
            <span class="font-medium">匿名捐献</span>
            <p class="text-xs mt-0.5" style="color: var(--text-muted);">勾选后其他用户将看不到您的用户名</p>
          </div>
        </label>
      </div>

      <input type="hidden" id="donateVisibility" value="private">

      <div class="flex justify-end gap-2 mt-4">
        <button onclick="hideDonateModal()" class="px-4 py-2 rounded-lg" style="background: var(--bg-input);">取消</button>
        <button onclick="donateToken()" class="btn-primary">提交</button>
      </div>
    </div>
  </div>
  <!-- API Key 显示弹窗 -->
  <div id="keyModal" style="display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 100; align-items: center; justify-content: center;">
    <div class="card" style="max-width: 500px; width: 90%; margin: 20px;">
      <h3 class="text-lg font-bold mb-4">🔑 API Key 已生成</h3>
      <p class="text-sm mb-4" style="color: var(--text-muted);">请立即复制保存，此 Key <strong class="text-red-400">仅显示一次</strong>：</p>
      <div id="tokenSourceInfo" class="mb-4 p-3 rounded-lg text-sm" style="display: none;"></div>
      <div class="flex items-center gap-2 p-3 rounded-lg" style="background: var(--bg-input);">
        <code id="generatedKey" class="flex-1 font-mono text-sm break-all" style="word-break: break-all;"></code>
        <button onclick="copyKey()" class="btn-primary text-sm px-3 py-1 flex-shrink-0">复制</button>
      </div>
      <p id="copyStatus" class="text-sm mt-2 text-green-400" style="display: none;">✓ 已复制到剪贴板</p>
      <div class="flex justify-end mt-4">
        <button onclick="hideKeyModal()" class="btn-primary">确定</button>
      </div>
    </div>
  </div>
  <!-- Key 名称输入弹窗 -->
  <div id="keyNameModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" style="display: none;">
    <div class="card w-full max-w-sm mx-4">
      <h3 class="text-lg font-bold mb-2">Key 名称</h3>
      <p class="text-sm mb-4" style="color: var(--text-muted);">可选，便于识别</p>
      <input id="keyNameInput" type="text" placeholder="例如：我的桌面客户端" class="w-full rounded px-3 py-2" style="background: var(--bg-input); border: 1px solid var(--border); color: var(--text);">
      <div class="flex justify-end gap-2 mt-4">
        <button onclick="handleKeyName(false)" class="px-4 py-2 rounded-lg" style="background: var(--bg-input); border: 1px solid var(--border);">取消</button>
        <button onclick="handleKeyName(true)" class="btn-primary px-4 py-2">确定</button>
      </div>
    </div>
  </div>
  <!-- 自定义确认对话框 -->
  <div id="confirmModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" style="display: none;">
    <div class="card w-full max-w-sm mx-4 text-center">
      <div id="confirmIcon" class="text-4xl mb-4">⚠️</div>
      <h3 id="confirmTitle" class="text-lg font-bold mb-2">确认操作</h3>
      <p id="confirmMessage" class="text-sm mb-6" style="color: var(--text-muted);"></p>
      <div class="flex justify-center gap-3">
        <button onclick="handleConfirm(false)" class="px-4 py-2 rounded-lg" style="background: var(--bg-input); border: 1px solid var(--border);">取消</button>
        <button onclick="handleConfirm(true)" id="confirmBtn" class="px-4 py-2 rounded-lg text-white" style="background: #ef4444;">确认</button>
      </div>
    </div>
  </div>
  {COMMON_FOOTER}
  <style>
    .tab {{ color: var(--text-muted); border-bottom: 2px solid transparent; }}
    .tab.active {{ color: var(--primary); border-bottom-color: var(--primary); }}
    .table-row:hover {{ background: var(--bg-input); }}
    .subtab {{ color: var(--text-muted); }}
    .subtab.active {{ background: var(--primary); color: white; }}
    .donate-mode-btn {{ color: var(--text-muted); }}
    .donate-mode-btn.active {{ background: var(--primary); color: white; }}
    details[open] .details-arrow {{ transform: rotate(180deg); }}
  </style>
  <script>
    let currentTab = 'tokens';
    let confirmCallback = null;
    let keyNameCallback = null;
    let userHasTokens = false;

    // Token 表格状态
    let allTokens = [];
    let tokensCurrentPage = 1;
    let tokensSortField = 'id';
    let tokensSortAsc = false;
    let selectedTokenIds = new Set();

    function renderTokenStatus(status) {{
      if (status === 'active') return '<span class="text-green-400">有效</span>';
      if (status === 'invalid') return '<span class="text-red-400">无效</span>';
      if (status === 'expired') return '<span class="text-red-400">已过期</span>';
      return `<span class="text-red-400">${{status || '-'}}</span>`;
    }}

    function showTab(tab) {{
      currentTab = tab;
      document.querySelectorAll('.tab-panel').forEach(p => p.style.display = 'none');
      document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
      document.getElementById('panel-' + tab).style.display = 'block';
      document.getElementById('tab-' + tab).classList.add('active');
    }}

    // 自定义确认对话框
    function showConfirmModal(options) {{
      return new Promise((resolve) => {{
        document.getElementById('confirmIcon').textContent = options.icon || '⚠️';
        document.getElementById('confirmTitle').textContent = options.title || '确认操作';
        document.getElementById('confirmMessage').textContent = options.message || '';
        const btn = document.getElementById('confirmBtn');
        btn.textContent = options.confirmText || '确认';
        btn.style.background = options.danger ? '#ef4444' : '#6366f1';
        confirmCallback = resolve;
        document.getElementById('confirmModal').style.display = 'flex';
      }});
    }}

    function handleConfirm(result) {{
      document.getElementById('confirmModal').style.display = 'none';
      if (confirmCallback) {{
        confirmCallback(result);
        confirmCallback = null;
      }}
    }}

    function showKeyNameModal(defaultValue) {{
      return new Promise((resolve) => {{
        keyNameCallback = resolve;
        const input = document.getElementById('keyNameInput');
        input.value = defaultValue || '';
        document.getElementById('keyNameModal').style.display = 'flex';
        input.focus();
        input.select();
      }});
    }}

    function handleKeyName(confirmed) {{
      document.getElementById('keyNameModal').style.display = 'none';
      if (keyNameCallback) {{
        if (!confirmed) {{
          keyNameCallback(null);
        }} else {{
          keyNameCallback(document.getElementById('keyNameInput').value.trim());
        }}
        keyNameCallback = null;
      }}
    }}

    async function loadProfile() {{
      try {{
        const r = await fetch('/user/api/profile');
        const d = await r.json();
        document.getElementById('tokenCount').textContent = d.token_count || 0;
        document.getElementById('publicTokenCount').textContent = d.public_token_count || 0;
        document.getElementById('apiKeyCount').textContent = d.api_key_count || 0;
        document.getElementById('requestCount').textContent = '-';
        userHasTokens = (d.token_count || 0) > 0;
      }} catch (e) {{ console.error(e); }}
    }}

    async function loadTokens() {{
      try {{
        const r = await fetch('/user/api/tokens');
        const d = await r.json();
        allTokens = d.tokens || [];
        tokensCurrentPage = 1;
        selectedTokenIds.clear();
        filterTokens();
      }} catch (e) {{ console.error(e); }}
    }}

    async function refreshTokens() {{
      await loadTokens();
    }}

    function filterTokens() {{
      const search = document.getElementById('tokensSearch').value.toLowerCase();
      const pageSize = parseInt(document.getElementById('tokensPageSize').value);

      // 筛选
      let filtered = allTokens.filter(t =>
        ('#' + t.id).toLowerCase().includes(search) ||
        t.visibility.toLowerCase().includes(search) ||
        t.status.toLowerCase().includes(search)
      );

      // 排序
      filtered.sort((a, b) => {{
        let va = a[tokensSortField], vb = b[tokensSortField];
        if (tokensSortField === 'last_used') {{
          va = va ? new Date(va).getTime() : 0;
          vb = vb ? new Date(vb).getTime() : 0;
        }} else if (tokensSortField === 'success_rate') {{
          va = va || 0;
          vb = vb || 0;
        }}
        if (va < vb) return tokensSortAsc ? -1 : 1;
        if (va > vb) return tokensSortAsc ? 1 : -1;
        return 0;
      }});

      // 分页
      const totalPages = Math.ceil(filtered.length / pageSize) || 1;
      if (tokensCurrentPage > totalPages) tokensCurrentPage = totalPages;
      const start = (tokensCurrentPage - 1) * pageSize;
      const paged = filtered.slice(start, start + pageSize);

      renderTokenTable(paged);
      renderTokensPagination(filtered.length, pageSize, totalPages);
      updateBatchDeleteTokenBtn();
    }}

    function sortTokens(field) {{
      if (tokensSortField === field) {{
        tokensSortAsc = !tokensSortAsc;
      }} else {{
        tokensSortField = field;
        tokensSortAsc = true;
      }}
      filterTokens();
    }}

    function goTokensPage(page) {{
      tokensCurrentPage = page;
      filterTokens();
    }}

    function renderTokenTable(tokens) {{
      const tb = document.getElementById('tokenTable');
      if (!tokens || !tokens.length) {{
        tb.innerHTML = '<tr><td colspan="7" class="py-6 text-center" style="color: var(--text-muted);">暂无 Token，点击上方按钮捐献</td></tr>';
        document.getElementById('tokensPagination').style.display = 'none';
        document.getElementById('selectAllTokens').checked = false;
        return;
      }}
      tb.innerHTML = tokens.map(t => `
        <tr class="table-row">
          <td class="py-3 px-3">
            <input type="checkbox" class="token-checkbox" data-token-id="${{t.id}}" onchange="toggleTokenSelection(${{t.id}}, this.checked)" ${{selectedTokenIds.has(t.id) ? 'checked' : ''}} style="cursor: pointer;">
          </td>
          <td class="py-3 px-3">#${{t.id}}</td>
          <td class="py-3 px-3"><span class="${{t.visibility === 'public' ? 'text-green-400' : 'text-blue-400'}}">${{t.visibility === 'public' ? '公开' : '私有'}}</span></td>
          <td class="py-3 px-3">${{renderTokenStatus(t.status)}}</td>
          <td class="py-3 px-3">${{t.success_rate}}%</td>
          <td class="py-3 px-3">${{t.last_used ? new Date(t.last_used).toLocaleString() : '-'}}</td>
          <td class="py-3 px-3">
            <button onclick="toggleVisibility(${{t.id}}, '${{t.visibility === 'public' ? 'private' : 'public'}}')" class="text-xs px-2 py-1 rounded bg-indigo-500/20 text-indigo-400 mr-1">切换</button>
            <button onclick="deleteToken(${{t.id}})" class="text-xs px-2 py-1 rounded bg-red-500/20 text-red-400">删除</button>
          </td>
        </tr>
      `).join('');

      const allChecked = tokens.length > 0 && tokens.every(t => selectedTokenIds.has(t.id));
      document.getElementById('selectAllTokens').checked = allChecked;
    }}

    function renderTokensPagination(total, pageSize, totalPages) {{
      const pagination = document.getElementById('tokensPagination');
      const info = document.getElementById('tokensInfo');
      const pages = document.getElementById('tokensPages');

      if (total === 0) {{
        pagination.style.display = 'none';
        return;
      }}

      pagination.style.display = 'flex';
      const start = (tokensCurrentPage - 1) * pageSize + 1;
      const end = Math.min(tokensCurrentPage * pageSize, total);
      info.textContent = `显示 ${{start}}-${{end}} 条，共 ${{total}} 条`;

      let html = '';
      if (tokensCurrentPage > 1) html += `<button onclick="goTokensPage(${{tokensCurrentPage - 1}})" class="px-3 py-1 rounded text-sm" style="background: var(--bg-input);">上一页</button>`;

      for (let i = 1; i <= totalPages; i++) {{
        if (i === 1 || i === totalPages || (i >= tokensCurrentPage - 1 && i <= tokensCurrentPage + 1)) {{
          html += `<button onclick="goTokensPage(${{i}})" class="px-3 py-1 rounded text-sm ${{i === tokensCurrentPage ? 'text-white' : ''}}" style="background: ${{i === tokensCurrentPage ? 'var(--primary)' : 'var(--bg-input)'}};">${{i}}</button>`;
        }} else if (i === tokensCurrentPage - 2 || i === tokensCurrentPage + 2) {{
          html += '<span class="px-2">...</span>';
        }}
      }}

      if (tokensCurrentPage < totalPages) html += `<button onclick="goTokensPage(${{tokensCurrentPage + 1}})" class="px-3 py-1 rounded text-sm" style="background: var(--bg-input);">下一页</button>`;
      pages.innerHTML = html;
    }}

    function toggleTokenSelection(tokenId, checked) {{
      if (checked) {{
        selectedTokenIds.add(tokenId);
      }} else {{
        selectedTokenIds.delete(tokenId);
      }}
      updateBatchDeleteTokenBtn();

      const allCheckboxes = document.querySelectorAll('.token-checkbox');
      const allChecked = allCheckboxes.length > 0 && Array.from(allCheckboxes).every(cb => cb.checked);
      document.getElementById('selectAllTokens').checked = allChecked;
    }}

    function toggleAllTokens(checked) {{
      document.querySelectorAll('.token-checkbox').forEach(cb => {{
        cb.checked = checked;
        const tokenId = parseInt(cb.dataset.tokenId);
        if (checked) {{
          selectedTokenIds.add(tokenId);
        }} else {{
          selectedTokenIds.delete(tokenId);
        }}
      }});
      updateBatchDeleteTokenBtn();
    }}

    function updateBatchDeleteTokenBtn() {{
      const btn = document.getElementById('batchDeleteBtn');
      if (selectedTokenIds.size > 0) {{
        btn.style.display = 'inline-block';
        btn.textContent = `批量删除 (${{selectedTokenIds.size}})`;
      }} else {{
        btn.style.display = 'none';
      }}
    }}

    async function batchDeleteTokens() {{
      if (selectedTokenIds.size === 0) return;
      const confirmed = await showConfirmModal({{
        icon: '🗑️',
        title: '批量删除',
        message: `确定要删除选中的 ${{selectedTokenIds.size}} 个 Token 吗？此操作不可恢复。`,
        confirmText: '删除',
        danger: true
      }});
      if (!confirmed) return;

      for (const tokenId of selectedTokenIds) {{
        await fetch('/user/api/tokens/' + tokenId, {{ method: 'DELETE' }});
      }}
      selectedTokenIds.clear();
      loadTokens();
      loadProfile();
    }}

    // API Keys 列表数据和状态
    let allKeys = [];
    let keysCurrentPage = 1;
    let keysSortField = 'created_at';
    let keysSortAsc = false;
    let selectedKeys = new Set();

    async function loadKeys() {{
      try {{
        const r = await fetch('/user/api/keys');
        const d = await r.json();
        allKeys = d.keys || [];
        keysCurrentPage = 1;
        selectedKeys.clear();
        filterKeys();
      }} catch (e) {{ console.error(e); }}
    }}

    async function refreshKeys() {{
      await loadKeys();
    }}

    function filterKeys() {{
      const search = document.getElementById('keysSearch').value.toLowerCase();
      const pageSize = parseInt(document.getElementById('keysPageSize').value);

      // 筛选
      let filtered = allKeys.filter(k =>
        k.key_prefix.toLowerCase().includes(search) ||
        (k.name && k.name.toLowerCase().includes(search))
      );

      // 排序
      filtered.sort((a, b) => {{
        let va = a[keysSortField], vb = b[keysSortField];
        if (keysSortField === 'created_at' || keysSortField === 'last_used') {{
          va = va ? new Date(va).getTime() : 0;
          vb = vb ? new Date(vb).getTime() : 0;
        }} else if (keysSortField === 'name') {{
          va = va || '';
          vb = vb || '';
        }}
        if (va < vb) return keysSortAsc ? -1 : 1;
        if (va > vb) return keysSortAsc ? 1 : -1;
        return 0;
      }});

      // 分页
      const totalPages = Math.ceil(filtered.length / pageSize) || 1;
      if (keysCurrentPage > totalPages) keysCurrentPage = totalPages;
      const start = (keysCurrentPage - 1) * pageSize;
      const paged = filtered.slice(start, start + pageSize);

      renderKeysTable(paged);
      renderKeysPagination(filtered.length, pageSize, totalPages);
      updateBatchDeleteUI();
    }}

    function sortKeys(field) {{
      if (keysSortField === field) {{
        keysSortAsc = !keysSortAsc;
      }} else {{
        keysSortField = field;
        keysSortAsc = true;
      }}
      filterKeys();
    }}

    function goKeysPage(page) {{
      keysCurrentPage = page;
      filterKeys();
    }}

    function renderKeysTable(keys) {{
      const tb = document.getElementById('keyTable');
      if (!keys || !keys.length) {{
        tb.innerHTML = '<tr><td colspan="7" class="py-6 text-center" style="color: var(--text-muted);">暂无 API Key，点击上方按钮生成</td></tr>';
        document.getElementById('keysPagination').style.display = 'none';
        return;
      }}
      tb.innerHTML = keys.map(k => `
        <tr class="table-row">
          <td class="py-3 px-3">
            <input type="checkbox" class="key-checkbox" data-key-id="${{k.id}}" onchange="toggleKeySelection(${{k.id}}, this.checked)" ${{selectedKeys.has(k.id) ? 'checked' : ''}} style="cursor: pointer;">
          </td>
          <td class="py-3 px-3 font-mono">${{k.key_prefix}}</td>
          <td class="py-3 px-3">
            <span title="${{k.name || ''}}" style="display: inline-block; max-width: 120px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; vertical-align: middle;">${{k.name || '-'}}</span>
          </td>
          <td class="py-3 px-3">${{k.request_count}}</td>
          <td class="py-3 px-3">${{k.last_used ? new Date(k.last_used).toLocaleString() : '-'}}</td>
          <td class="py-3 px-3">${{k.created_at ? new Date(k.created_at).toLocaleString() : '-'}}</td>
          <td class="py-3 px-3"><button onclick="deleteKey(${{k.id}})" class="text-xs px-2 py-1 rounded bg-red-500/20 text-red-400 hover:bg-red-500/30">删除</button></td>
        </tr>
      `).join('');
    }}

    function renderKeysPagination(total, pageSize, totalPages) {{
      const pagination = document.getElementById('keysPagination');
      const info = document.getElementById('keysInfo');
      const pages = document.getElementById('keysPages');

      if (total === 0) {{
        pagination.style.display = 'none';
        return;
      }}

      pagination.style.display = 'flex';
      const start = (keysCurrentPage - 1) * pageSize + 1;
      const end = Math.min(keysCurrentPage * pageSize, total);
      info.textContent = `显示 ${{start}}-${{end}} 条，共 ${{total}} 条`;

      let html = '';
      if (keysCurrentPage > 1) html += `<button onclick="goKeysPage(${{keysCurrentPage - 1}})" class="px-3 py-1 rounded text-sm" style="background: var(--bg-input);">上一页</button>`;

      for (let i = 1; i <= totalPages; i++) {{
        if (i === 1 || i === totalPages || (i >= keysCurrentPage - 1 && i <= keysCurrentPage + 1)) {{
          html += `<button onclick="goKeysPage(${{i}})" class="px-3 py-1 rounded text-sm ${{i === keysCurrentPage ? 'text-white' : ''}}" style="background: ${{i === keysCurrentPage ? 'var(--primary)' : 'var(--bg-input)'}};">${{i}}</button>`;
        }} else if (i === keysCurrentPage - 2 || i === keysCurrentPage + 2) {{
          html += '<span class="px-2">...</span>';
        }}
      }}

      if (keysCurrentPage < totalPages) html += `<button onclick="goKeysPage(${{keysCurrentPage + 1}})" class="px-3 py-1 rounded text-sm" style="background: var(--bg-input);">下一页</button>`;
      pages.innerHTML = html;
    }}

    function toggleKeySelection(keyId, checked) {{
      if (checked) {{
        selectedKeys.add(keyId);
      }} else {{
        selectedKeys.delete(keyId);
      }}
      updateBatchDeleteUI();
      updateSelectAllCheckbox();
    }}

    function toggleSelectAllKeys() {{
      const selectAll = document.getElementById('selectAllKeys');
      const checkboxes = document.querySelectorAll('.key-checkbox');
      checkboxes.forEach(cb => {{
        const keyId = parseInt(cb.dataset.keyId);
        if (selectAll.checked) {{
          selectedKeys.add(keyId);
          cb.checked = true;
        }} else {{
          selectedKeys.delete(keyId);
          cb.checked = false;
        }}
      }});
      updateBatchDeleteUI();
    }}

    function updateSelectAllCheckbox() {{
      const selectAll = document.getElementById('selectAllKeys');
      const checkboxes = document.querySelectorAll('.key-checkbox');
      if (checkboxes.length === 0) {{
        selectAll.checked = false;
        selectAll.indeterminate = false;
        return;
      }}
      const allChecked = Array.from(checkboxes).every(cb => cb.checked);
      const someChecked = Array.from(checkboxes).some(cb => cb.checked);
      selectAll.checked = allChecked;
      selectAll.indeterminate = someChecked && !allChecked;
    }}

    function updateBatchDeleteUI() {{
      const count = selectedKeys.size;
      const btn = document.getElementById('batchDeleteBtn');
      const countSpan = document.getElementById('selectedKeysCount');
      if (count > 0) {{
        btn.style.display = 'inline-block';
        countSpan.style.display = 'inline';
        countSpan.textContent = `已选择 ${{count}} 个`;
      }} else {{
        btn.style.display = 'none';
        countSpan.style.display = 'none';
      }}
    }}

    async function batchDeleteKeys() {{
      if (selectedKeys.size === 0) return;
      const confirmed = await showConfirmModal({{
        title: '批量删除 API Keys',
        message: `确定要删除选中的 ${{selectedKeys.size}} 个 API Key 吗？删除后使用这些 Key 的所有应用将无法继续访问。`,
        icon: '🗑️',
        confirmText: '确认删除',
        danger: true
      }});
      if (!confirmed) return;

      const promises = Array.from(selectedKeys).map(keyId =>
        fetch('/user/api/keys/' + keyId, {{ method: 'DELETE' }})
      );
      await Promise.all(promises);
      selectedKeys.clear();
      loadKeys();
      loadProfile();
    }}

    function showDonateModal() {{ document.getElementById('donateModal').style.display = 'flex'; }}
    function hideDonateModal() {{
      document.getElementById('donateModal').style.display = 'none';
      setDonateMode('private');
      document.getElementById('donateToken').value = '';
      document.getElementById('donateAnonymous').checked = false;
    }}

    function setDonateMode(mode) {{
      const privateBtn = document.getElementById('donateMode-private');
      const publicBtn = document.getElementById('donateMode-public');
      const privateDesc = document.getElementById('donateDesc-private');
      const publicDesc = document.getElementById('donateDesc-public');
      const anonOption = document.getElementById('anonymousOption');

      if (mode === 'private') {{
        privateBtn.classList.add('active');
        publicBtn.classList.remove('active');
        privateDesc.style.display = 'block';
        publicDesc.style.display = 'none';
        anonOption.style.display = 'none';
      }} else {{
        privateBtn.classList.remove('active');
        publicBtn.classList.add('active');
        privateDesc.style.display = 'none';
        publicDesc.style.display = 'block';
        anonOption.style.display = 'block';
      }}
      document.getElementById('donateVisibility').value = mode;
    }}

    function showKeyModal(key, usePublicPool) {{
      document.getElementById('generatedKey').textContent = key;
      document.getElementById('copyStatus').style.display = 'none';
      const infoEl = document.getElementById('tokenSourceInfo');
      if (usePublicPool) {{
        infoEl.innerHTML = '💡 <strong>提示：</strong>您尚未捐献 Token，此 Key 将使用公开 Token 池。捐献自己的 Token 可获得更稳定的服务。';
        infoEl.style.display = 'block';
        infoEl.style.background = 'rgba(245, 158, 11, 0.15)';
        infoEl.style.color = '#f59e0b';
      }} else {{
        infoEl.innerHTML = '✅ <strong>提示：</strong>此 Key 将优先使用您捐献的私有 Token。';
        infoEl.style.display = 'block';
        infoEl.style.background = 'rgba(34, 197, 94, 0.15)';
        infoEl.style.color = '#22c55e';
      }}
      document.getElementById('keyModal').style.display = 'flex';
    }}

    function hideKeyModal() {{ document.getElementById('keyModal').style.display = 'none'; }}

    async function copyKey() {{
      const key = document.getElementById('generatedKey').textContent;
      try {{
        await navigator.clipboard.writeText(key);
        document.getElementById('copyStatus').style.display = 'block';
      }} catch (e) {{
        const range = document.createRange();
        range.selectNode(document.getElementById('generatedKey'));
        window.getSelection().removeAllRanges();
        window.getSelection().addRange(range);
        document.execCommand('copy');
        document.getElementById('copyStatus').style.display = 'block';
      }}
    }}

    async function donateToken() {{
      const token = document.getElementById('donateToken').value.trim();
      if (!token) return showConfirmModal({{ title: '提示', message: '请输入 Token', icon: '💡', confirmText: '好的', danger: false }});
      const visibility = document.getElementById('donateVisibility').value;
      const anonymous = document.getElementById('donateAnonymous').checked;
      const fd = new FormData();
      fd.append('refresh_token', token);
      fd.append('visibility', visibility);
      if (visibility === 'public' && anonymous) fd.append('anonymous', 'true');
      try {{
        const r = await fetch('/user/api/tokens', {{ method: 'POST', body: fd }});
        const d = await r.json();
        if (d.success) {{
          await showConfirmModal({{ title: '成功', message: visibility === 'public' ? 'Token 已添加到公开池，感谢您的贡献！' : 'Token 添加成功！', icon: '🎉', confirmText: '好的', danger: false }});
          hideDonateModal();
          document.getElementById('donateToken').value = '';
          loadTokens();
          loadProfile();
        }} else {{
          showConfirmModal({{ title: '失败', message: d.message || '添加失败', icon: '❌', confirmText: '好的', danger: false }});
        }}
      }} catch (e) {{
        showConfirmModal({{ title: '错误', message: '请求失败，请稍后重试', icon: '❌', confirmText: '好的', danger: false }});
      }}
    }}

    async function toggleVisibility(tokenId, newVisibility) {{
      const confirmed = await showConfirmModal({{
        title: '切换可见性',
        message: `确定将此 Token 切换为${{newVisibility === 'public' ? '公开' : '私有'}}吗？${{newVisibility === 'public' ? '\\n公开后将加入公共池供所有用户使用。' : ''}}`,
        icon: '🔄',
        confirmText: '确认切换',
        danger: false
      }});
      if (!confirmed) return;
      const fd = new FormData();
      fd.append('visibility', newVisibility);
      await fetch('/user/api/tokens/' + tokenId, {{ method: 'PUT', body: fd }});
      loadTokens();
      loadProfile();
    }}

    async function deleteToken(tokenId) {{
      const confirmed = await showConfirmModal({{
        title: '删除 Token',
        message: '确定要删除此 Token 吗？此操作不可恢复。',
        icon: '🗑️',
        confirmText: '确认删除',
        danger: true
      }});
      if (!confirmed) return;
      await fetch('/user/api/tokens/' + tokenId, {{ method: 'DELETE' }});
      loadTokens();
      loadProfile();
    }}

    async function generateKey() {{
      // 检查是否达到上限
      if (allKeys.length >= 10) {{
        showConfirmModal({{
          title: '已达上限',
          message: '每个账户最多可创建 10 个 API Key。\\n请删除不需要的 Key 后再试。',
          icon: '⚠️',
          confirmText: '好的',
          danger: false
        }});
        return;
      }}

      // 如果用户没有 Token，先提示
      if (!userHasTokens) {{
        const proceed = await showConfirmModal({{
          title: '提示',
          message: '您尚未捐献任何 Token。生成的 API Key 将使用公开 Token 池，可能会有配额限制。\\n\\n建议先捐献您的 Token 以获得更好的体验。\\n\\n是否继续生成？',
          icon: '💡',
          confirmText: '继续生成',
          danger: false
        }});
        if (!proceed) return;
      }}

      // 弹出输入名称的对话框
      const name = await showKeyNameModal('');
      if (name === null) return; // 用户取消

      const fd = new FormData();
      fd.append('name', name);
      try {{
        const r = await fetch('/user/api/keys', {{ method: 'POST', body: fd }});
        const d = await r.json();
        if (d.success) {{
          showKeyModal(d.key, d.uses_public_pool);
          loadKeys();
          loadProfile();
        }} else {{
          showConfirmModal({{ title: '失败', message: d.message || '生成失败', icon: '❌', confirmText: '好的', danger: false }});
        }}
      }} catch (e) {{
        showConfirmModal({{ title: '错误', message: '请求失败，请稍后重试', icon: '❌', confirmText: '好的', danger: false }});
      }}
    }}

    async function deleteKey(keyId) {{
      const confirmed = await showConfirmModal({{
        title: '删除 API Key',
        message: '确定要删除此 API Key 吗？删除后使用该 Key 的所有应用将无法继续访问。',
        icon: '🗑️',
        confirmText: '确认删除',
        danger: true
      }});
      if (!confirmed) return;
      await fetch('/user/api/keys/' + keyId, {{ method: 'DELETE' }});
      loadKeys();
      loadProfile();
    }}

    // 公开 Token 池状态
    let allPublicTokens = [];
    let publicTokenCurrentPage = 1;
    let publicTokenSortField = 'success_rate';
    let publicTokenSortAsc = false;

    function showTokenSubTab(tab) {{
      const mineBtn = document.getElementById('subtab-mine');
      const publicBtn = document.getElementById('subtab-public');
      const minePanel = document.getElementById('subtab-panel-mine');
      const publicPanel = document.getElementById('subtab-panel-public');

      if (tab === 'mine') {{
        mineBtn.classList.add('active');
        publicBtn.classList.remove('active');
        minePanel.style.display = 'block';
        publicPanel.style.display = 'none';
      }} else {{
        mineBtn.classList.remove('active');
        publicBtn.classList.add('active');
        minePanel.style.display = 'none';
        publicPanel.style.display = 'block';
        if (allPublicTokens.length === 0) loadPublicTokens();
      }}
    }}

    async function loadPublicTokens() {{
      try {{
        const r = await fetch('/api/public-tokens');
        const d = await r.json();
        allPublicTokens = (d.tokens || []).map(t => ({{
          ...t,
          use_count: (t.success_count || 0) + (t.fail_count || 0)
        }}));
        document.getElementById('publicPoolCount').textContent = d.count || 0;
        if (allPublicTokens.length > 0) {{
          const avgRate = allPublicTokens.reduce((sum, t) => sum + (t.success_rate || 0), 0) / allPublicTokens.length;
          document.getElementById('publicPoolAvgRate').textContent = avgRate.toFixed(1) + '%';
        }} else {{
          document.getElementById('publicPoolAvgRate').textContent = '-';
        }}
        publicTokenCurrentPage = 1;
        filterPublicTokens();
      }} catch (e) {{ console.error(e); }}
    }}

    function filterPublicTokens() {{
      const search = document.getElementById('publicTokenSearch').value.toLowerCase();
      const pageSize = parseInt(document.getElementById('publicTokenPageSize').value);

      let filtered = allPublicTokens.filter(t =>
        (t.username || '').toLowerCase().includes(search)
      );

      filtered.sort((a, b) => {{
        let va = a[publicTokenSortField], vb = b[publicTokenSortField];
        if (publicTokenSortField === 'last_used') {{
          va = va ? new Date(va).getTime() : 0;
          vb = vb ? new Date(vb).getTime() : 0;
        }}
        if (va < vb) return publicTokenSortAsc ? -1 : 1;
        if (va > vb) return publicTokenSortAsc ? 1 : -1;
        return 0;
      }});

      const totalPages = Math.ceil(filtered.length / pageSize) || 1;
      if (publicTokenCurrentPage > totalPages) publicTokenCurrentPage = totalPages;
      const start = (publicTokenCurrentPage - 1) * pageSize;
      const paged = filtered.slice(start, start + pageSize);

      renderPublicTokenTable(paged);
      renderPublicTokenPagination(filtered.length, pageSize, totalPages);
    }}

    function sortPublicTokens(field) {{
      if (publicTokenSortField === field) {{
        publicTokenSortAsc = !publicTokenSortAsc;
      }} else {{
        publicTokenSortField = field;
        publicTokenSortAsc = false;
      }}
      filterPublicTokens();
    }}

    function goPublicTokensPage(page) {{
      publicTokenCurrentPage = page;
      filterPublicTokens();
    }}

    function renderPublicTokenTable(tokens) {{
      const tb = document.getElementById('publicTokenTable');
      if (!tokens.length) {{
        tb.innerHTML = '<tr><td colspan="6" class="py-6 text-center" style="color: var(--text-muted);">暂无公开 Token</td></tr>';
        return;
      }}
      tb.innerHTML = tokens.map((t, i) => `
        <tr class="table-row">
          <td class="py-3 px-3">${{(publicTokenCurrentPage - 1) * parseInt(document.getElementById('publicTokenPageSize').value) + i + 1}}</td>
          <td class="py-3 px-3">${{t.username || '匿名'}}</td>
          <td class="py-3 px-3">${{renderTokenStatus(t.status)}}</td>
          <td class="py-3 px-3"><span class="${{(t.success_rate || 0) >= 80 ? 'text-green-400' : (t.success_rate || 0) >= 50 ? 'text-yellow-400' : 'text-red-400'}}">${{(t.success_rate || 0).toFixed(1)}}%</span></td>
          <td class="py-3 px-3">${{t.use_count || 0}}</td>
          <td class="py-3 px-3">${{t.last_used ? new Date(t.last_used).toLocaleString() : '-'}}</td>
        </tr>
      `).join('');
    }}

    function renderPublicTokenPagination(total, pageSize, totalPages) {{
      const pagination = document.getElementById('publicTokenPagination');
      const info = document.getElementById('publicTokenInfo');
      const pages = document.getElementById('publicTokenPages');

      if (total === 0) {{
        pagination.style.display = 'none';
        return;
      }}

      pagination.style.display = 'flex';
      const start = (publicTokenCurrentPage - 1) * pageSize + 1;
      const end = Math.min(publicTokenCurrentPage * pageSize, total);
      info.textContent = `显示 ${{start}}-${{end}} 条，共 ${{total}} 条`;

      let html = '';
      if (publicTokenCurrentPage > 1) html += `<button onclick="goPublicTokensPage(${{publicTokenCurrentPage - 1}})" class="px-3 py-1 rounded text-sm" style="background: var(--bg-input);">上一页</button>`;

      for (let i = 1; i <= totalPages; i++) {{
        if (i === 1 || i === totalPages || (i >= publicTokenCurrentPage - 1 && i <= publicTokenCurrentPage + 1)) {{
          html += `<button onclick="goPublicTokensPage(${{i}})" class="px-3 py-1 rounded text-sm ${{i === publicTokenCurrentPage ? 'text-white' : ''}}" style="background: ${{i === publicTokenCurrentPage ? 'var(--primary)' : 'var(--bg-input)'}};">${{i}}</button>`;
        }} else if (i === publicTokenCurrentPage - 2 || i === publicTokenCurrentPage + 2) {{
          html += '<span class="px-2">...</span>';
        }}
      }}

      if (publicTokenCurrentPage < totalPages) html += `<button onclick="goPublicTokensPage(${{publicTokenCurrentPage + 1}})" class="px-3 py-1 rounded text-sm" style="background: var(--bg-input);">下一页</button>`;
      pages.innerHTML = html;
    }}

    showTab('tokens');
    showTokenSubTab('mine');
    const keyNameInput = document.getElementById('keyNameInput');
    keyNameInput.addEventListener('keydown', (e) => {{
      if (e.key === 'Enter') handleKeyName(true);
      if (e.key === 'Escape') handleKeyName(false);
    }});
    loadProfile();
    loadTokens();
    loadKeys();
  </script>
</body>
</html>'''


def render_tokens_page(user=None) -> str:
    """Render the public token pool page."""
    login_section = '<a href="/user" class="btn-primary">用户中心</a>' if user else '<a href="/login" class="btn-primary">登录捐献</a>'
    return f'''<!DOCTYPE html>
<html lang="zh">
<head>{COMMON_HEAD}</head>
<body>
  {COMMON_NAV}
  <main class="max-w-4xl mx-auto px-4 py-8">
    <div class="text-center mb-8">
      <h1 class="text-3xl font-bold mb-2">🌐 公开 Token 池</h1>
      <p style="color: var(--text-muted);">社区捐献的 Refresh Token，供所有用户共享使用</p>
    </div>
    <div class="grid grid-cols-2 gap-4 mb-8">
      <div class="card text-center">
        <div class="text-4xl font-bold text-green-400" id="poolCount">-</div>
        <div style="color: var(--text-muted);">可用 Token</div>
      </div>
      <div class="card text-center">
        <div class="text-4xl font-bold text-indigo-400" id="avgRate">-</div>
        <div style="color: var(--text-muted);">平均成功率</div>
      </div>
    </div>
    <div class="card mb-6">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-bold">Token 列表</h2>
        {login_section}
      </div>
      <div class="table-responsive">
        <table class="w-full">
          <thead>
            <tr style="border-bottom: 1px solid var(--border);">
              <th class="text-left py-3 px-3">#</th>
              <th class="text-left py-3 px-3">成功率</th>
              <th class="text-left py-3 px-3">最后使用</th>
            </tr>
          </thead>
          <tbody id="poolTable"></tbody>
        </table>
      </div>
    </div>
    <div class="card">
      <h3 class="font-bold mb-3">💡 如何使用</h3>
      <ol class="list-decimal list-inside space-y-2" style="color: var(--text-muted);">
        <li>通过 LinuxDo 或 GitHub 登录本站</li>
        <li>在用户中心捐献你的 Refresh Token</li>
        <li>选择"公开"以加入公共池</li>
        <li>生成 API Key (sk-xxx 格式)</li>
        <li>使用 API Key 调用本站接口</li>
      </ol>
    </div>
  </main>
  {COMMON_FOOTER}
  <script>
    async function loadPool() {{
      try {{
        const r = await fetch('/api/public-tokens');
        const d = await r.json();
        document.getElementById('poolCount').textContent = d.count || 0;
        const tokens = d.tokens || [];
        if (tokens.length > 0) {{
          const avgRate = tokens.reduce((sum, t) => sum + t.success_rate, 0) / tokens.length;
          document.getElementById('avgRate').textContent = avgRate.toFixed(1) + '%';
        }} else {{ document.getElementById('avgRate').textContent = '-'; }}
        const tb = document.getElementById('poolTable');
        if (!tokens.length) {{
          tb.innerHTML = '<tr><td colspan="3" class="py-6 text-center" style="color: var(--text-muted);">暂无公开 Token</td></tr>';
          return;
        }}
        tb.innerHTML = tokens.map((t, i) => `
          <tr style="border-bottom: 1px solid var(--border);">
            <td class="py-3 px-3">${{i + 1}}</td>
            <td class="py-3 px-3"><span class="${{t.success_rate >= 80 ? 'text-green-400' : t.success_rate >= 50 ? 'text-yellow-400' : 'text-red-400'}}">${{t.success_rate}}%</span></td>
            <td class="py-3 px-3" style="color: var(--text-muted);">${{t.last_used ? new Date(t.last_used).toLocaleString() : '-'}}</td>
          </tr>
        `).join('');
      }} catch (e) {{ console.error(e); }}
    }}
    loadPool();
    setInterval(loadPool, 30000);
  </script>
</body>
</html>'''


def render_login_page() -> str:
    """Render the login selection page with multiple OAuth2 providers."""
    return f'''<!DOCTYPE html>
<html lang="zh">
<head>{COMMON_HEAD}
  <style>
    .login-card {{
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 1.5rem;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.15);
    }}
    .btn-login {{
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 12px;
      width: 100%;
      padding: 14px 24px;
      border-radius: 12px;
      font-weight: 600;
      font-size: 1rem;
      transition: all 0.3s ease;
      text-decoration: none;
    }}
    .btn-login:hover {{ transform: translateY(-2px); box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.2); }}
    .btn-linuxdo {{ background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); color: white; }}
    .btn-linuxdo:hover {{ background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%); }}
    .btn-github {{ background: #24292f; color: white; }}
    .btn-github:hover {{ background: #1b1f23; }}
    .logo-bounce {{ animation: bounce 2s infinite; }}
    @keyframes bounce {{
      0%, 100% {{ transform: translateY(0); }}
      50% {{ transform: translateY(-10px); }}
    }}
  </style>
</head>
<body>
  {COMMON_NAV}

  <main class="flex-1 flex items-center justify-center py-12 px-4" style="min-height: calc(100vh - 200px);">
    <div class="w-full max-w-sm">
      <div class="login-card p-8">
        <div class="text-center mb-8">
          <div class="logo-bounce inline-block text-6xl mb-4">⚡</div>
          <h1 class="text-2xl font-bold mb-2">欢迎使用 KiroGate</h1>
          <p style="color: var(--text-muted);">选择登录方式开始使用</p>
        </div>

        <div class="space-y-4">
          <a href="/oauth2/login" class="btn-login btn-linuxdo">
            <img src="https://linux.do/uploads/default/optimized/4X/c/c/d/ccd8c210609d498cbeb3d5201d4c259348447562_2_32x32.png" width="24" height="24" alt="LinuxDo" style="border-radius: 6px; background: white; padding: 2px;">
            <span>LinuxDo 登录</span>
          </a>

          <a href="/oauth2/github/login" class="btn-login btn-github">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/></svg>
            <span>GitHub 登录</span>
          </a>
        </div>

        <div class="my-8 flex items-center">
          <div class="flex-1 h-px" style="background: var(--border);"></div>
          <span class="px-4 text-sm" style="color: var(--text-muted);">登录后可以</span>
          <div class="flex-1 h-px" style="background: var(--border);"></div>
        </div>

        <div class="grid grid-cols-2 gap-4 text-center text-sm">
          <div class="p-3 rounded-xl" style="background: var(--bg-main);">
            <div class="text-2xl mb-1">🎁</div>
            <div style="color: var(--text-muted);">捐献 Token</div>
          </div>
          <div class="p-3 rounded-xl" style="background: var(--bg-main);">
            <div class="text-2xl mb-1">🔑</div>
            <div style="color: var(--text-muted);">生成 API Key</div>
          </div>
        </div>
      </div>
    </div>
  </main>

  {COMMON_FOOTER}
</body>
</html>'''


def render_404_page() -> str:
    """Render the 404 Not Found page."""
    return f'''<!DOCTYPE html>
<html lang="zh">
<head>{COMMON_HEAD}</head>
<body>
  {COMMON_NAV}
  <main class="max-w-2xl mx-auto px-4 py-16 text-center">
    <div class="mb-8">
      <div class="text-9xl font-bold" style="background: linear-gradient(135deg, var(--primary) 0%, #ec4899 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">404</div>
    </div>
    <h1 class="text-3xl font-bold mb-4">页面未找到</h1>
    <p class="text-lg mb-8" style="color: var(--text-muted);">
      抱歉，您访问的页面不存在或已被移动。
    </p>
    <div class="flex flex-col sm:flex-row gap-4 justify-center">
      <a href="/" class="btn-primary inline-flex items-center gap-2">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/>
        </svg>
        返回首页
      </a>
      <a href="/docs" class="inline-flex items-center gap-2 px-6 py-3 rounded-lg font-medium transition-all" style="background: var(--bg-card); border: 1px solid var(--border);">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>
        </svg>
        查看文档
      </a>
    </div>
    <div class="mt-12 p-6 rounded-lg" style="background: var(--bg-card); border: 1px solid var(--border);">
      <h3 class="font-bold mb-3">💡 可能有帮助的链接</h3>
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm">
        <a href="/playground" class="p-3 rounded-lg hover:bg-opacity-80 transition-all" style="background: var(--bg);">🎮 Playground</a>
        <a href="/status" class="p-3 rounded-lg hover:bg-opacity-80 transition-all" style="background: var(--bg);">📊 系统状态</a>
        <a href="/swagger" class="p-3 rounded-lg hover:bg-opacity-80 transition-all" style="background: var(--bg);">📚 API 文档</a>
        <a href="/tokens" class="p-3 rounded-lg hover:bg-opacity-80 transition-all" style="background: var(--bg);">🌐 Token 池</a>
      </div>
    </div>
  </main>
  {COMMON_FOOTER}
</body>
</html>'''
