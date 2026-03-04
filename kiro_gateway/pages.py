# -*- coding: utf-8 -*-

"""
KiroGate Frontend Pages.

HTML templates for the web interface.
"""

from kiro_gateway.config import APP_VERSION, AVAILABLE_MODELS, STATIC_ASSETS_PROXY_ENABLED, STATIC_ASSETS_PROXY_BASE
import html
import json


def get_asset_url(cdn_url: str) -> str:
    """
    根据配置返回静态资源 URL。

    Args:
        cdn_url: 原始 CDN URL (例如: "cdn.tailwindcss.com" 或 "cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js")

    Returns:
        完整的资源 URL
    """
    if STATIC_ASSETS_PROXY_ENABLED:
        # 使用代理
        return f"{STATIC_ASSETS_PROXY_BASE}/proxy/{cdn_url}"
    else:
        # 直接访问 CDN
        return f"https://{cdn_url}"


# 兼容性：保留旧的 PROXY_BASE 变量名（已废弃，请使用 get_asset_url）
PROXY_BASE = STATIC_ASSETS_PROXY_BASE if STATIC_ASSETS_PROXY_ENABLED else ""

# SEO and common head
COMMON_HEAD = r'''
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
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;600;700&family=Sora:wght@400;500;600;700&display=swap" rel="stylesheet">

  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js"></script>
  <style>
    :root {{
      --primary: #38bdf8;
      --primary-dark: #0284c7;
      --primary-light: #7dd3fc;
      --accent: #22d3ee;
      --accent-2: #a3e635;
      --success: #22c55e;
      --warning: #f59e0b;
      --danger: #f43f5e;
    }}

    /* Light mode (default) */
    [data-theme="light"] {{
      --bg-main: #f4f7fb;
      --bg-card: rgba(255, 255, 255, 0.78);
      --bg-nav: rgba(248, 250, 252, 0.82);
      --bg-input: rgba(255, 255, 255, 0.92);
      --bg-hover: rgba(226, 232, 240, 0.7);
      --text: #0f172a;
      --text-muted: #64748b;
      --border: rgba(148, 163, 184, 0.35);
      --border-dark: rgba(100, 116, 139, 0.5);
      --shadow-sm: 0 1px 2px rgba(15, 23, 42, 0.08);
      --shadow: 0 12px 28px rgba(15, 23, 42, 0.08);
      --shadow-lg: 0 24px 48px rgba(15, 23, 42, 0.12);
      --glow: 0 0 32px rgba(56, 189, 248, 0.18);
      --grid-line: rgba(148, 163, 184, 0.2);
    }}

    /* Dark mode */
    [data-theme="dark"] {{
      --bg-main: #05070f;
      --bg-card: rgba(15, 23, 42, 0.72);
      --bg-nav: rgba(7, 10, 18, 0.82);
      --bg-input: rgba(15, 23, 42, 0.85);
      --bg-hover: rgba(30, 41, 59, 0.6);
      --text: #e2e8f0;
      --text-muted: #94a3b8;
      --border: rgba(148, 163, 184, 0.16);
      --border-dark: rgba(148, 163, 184, 0.28);
      --shadow-sm: 0 1px 2px rgba(2, 6, 23, 0.45);
      --shadow: 0 14px 32px rgba(2, 6, 23, 0.55);
      --shadow-lg: 0 30px 60px rgba(2, 6, 23, 0.65);
      --glow: 0 0 40px rgba(56, 189, 248, 0.3);
      --grid-line: rgba(148, 163, 184, 0.1);
    }}

    * {{
      scrollbar-width: thin;
      scrollbar-color: var(--border-dark) transparent;
    }}

    body {{
      background: var(--bg-main);
      color: var(--text);
      font-family: 'Sora', 'Noto Sans SC', system-ui, -apple-system, sans-serif;
      transition: background-color 0.3s ease, color 0.3s ease;
      line-height: 1.6;
      min-height: 100vh;
      position: relative;
      isolation: isolate;
    }}
    body::before {{
      content: '';
      position: fixed;
      inset: -20% -10% -20% -10%;
      background:
        radial-gradient(circle at 15% 15%, rgba(56, 189, 248, 0.25), transparent 45%),
        radial-gradient(circle at 85% 10%, rgba(34, 211, 238, 0.2), transparent 45%),
        radial-gradient(circle at 50% 90%, rgba(163, 230, 53, 0.18), transparent 50%);
      z-index: -2;
      pointer-events: none;
    }}
    body::after {{
      content: '';
      position: fixed;
      inset: 0;
      background-image:
        linear-gradient(var(--grid-line) 1px, transparent 1px),
        linear-gradient(90deg, var(--grid-line) 1px, transparent 1px);
      background-size: 28px 28px;
      opacity: 0.5;
      z-index: -1;
      pointer-events: none;
    }}
    nav, main, footer {{
      position: relative;
      z-index: 1;
    }}

    /* Enhanced card with subtle gradient border */
    .card {{
      background: var(--bg-card);
      border-radius: 1rem;
      padding: 1.5rem;
      border: 1px solid var(--border);
      box-shadow: var(--shadow);
      transition: all 0.3s ease;
      position: relative;
      backdrop-filter: blur(14px);
      -webkit-backdrop-filter: blur(14px);
    }}
    .card:hover {{
      box-shadow: var(--shadow-lg), var(--glow);
      border-color: var(--border-dark);
      transform: translateY(-1px);
    }}

    /* Primary button with gradient and glow */
    .btn-primary {{
      background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 70%, var(--accent-2) 120%);
      color: #ffffff;
      padding: 0.625rem 1.25rem;
      border-radius: 0.75rem;
      font-weight: 600;
      letter-spacing: 0.01em;
      transition: all 0.3s ease;
      box-shadow: 0 12px 24px rgba(56, 189, 248, 0.25);
      border: 1px solid rgba(255, 255, 255, 0.08);
      cursor: pointer;
    }}
    .btn-primary:hover {{
      transform: translateY(-2px);
      box-shadow: 0 18px 36px rgba(56, 189, 248, 0.35);
      filter: brightness(1.05);
    }}
    .btn-primary:active {{
      transform: translateY(0);
    }}

    /* Navigation link with underline animation */
    .nav-link {{
      color: var(--text-muted);
      transition: color 0.2s ease;
      position: relative;
      padding-bottom: 2px;
    }}
    .nav-link::after {{
      content: '';
      position: absolute;
      bottom: 0;
      left: 0;
      width: 0;
      height: 2px;
      background: linear-gradient(90deg, var(--primary), var(--accent), var(--accent-2));
      transition: width 0.3s ease;
      border-radius: 1px;
    }}
    .nav-link:hover {{ color: var(--primary); }}
    .nav-link:hover::after {{ width: 100%; }}
    .nav-link.active {{ color: var(--primary); }}
    .nav-link.active::after {{ width: 100%; }}

    /* Theme toggle with smooth animation */
    .theme-toggle {{
      cursor: pointer;
      padding: 0.5rem;
      border-radius: 0.625rem;
      transition: all 0.2s ease;
      background: transparent;
      border: 1px solid transparent;
    }}
    .theme-toggle:hover {{
      background: var(--bg-hover);
      border-color: var(--border);
    }}
    /* 代码块优化 */
    pre {{
      max-width: 100%;
      overflow-x: auto;
      -webkit-overflow-scrolling: touch;
      background: var(--bg-input);
      border: 1px solid var(--border);
      border-radius: 0.75rem;
      font-size: 0.875rem;
    }}
    pre::-webkit-scrollbar {{
      height: 6px;
    }}
    pre::-webkit-scrollbar-track {{
      background: transparent;
      border-radius: 3px;
    }}
    pre::-webkit-scrollbar-thumb {{
      background: var(--border-dark);
      border-radius: 3px;
    }}
    pre::-webkit-scrollbar-thumb:hover {{
      background: var(--text-muted);
    }}

    /* Enhanced loading animations */
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
    @keyframes fadeIn {{
      from {{ opacity: 0; transform: translateY(10px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}
    .fade-in {{
      animation: fadeIn 0.4s ease-out;
    }}

    /* 表格响应式 */
    .table-responsive {{
      overflow-x: auto;
      -webkit-overflow-scrolling: touch;
      border-radius: 0.75rem;
    }}
    .table-responsive::-webkit-scrollbar {{
      height: 6px;
    }}
    .table-responsive::-webkit-scrollbar-track {{
      background: transparent;
    }}
    .table-responsive::-webkit-scrollbar-thumb {{
      background: var(--border-dark);
      border-radius: 3px;
    }}

    /* Enhanced table rows */
    .table-row {{
      border-bottom: 1px solid var(--border);
      transition: background-color 0.2s ease;
    }}
    .table-row:hover {{
      background: var(--bg-hover);
    }}
    .table-row:last-child {{
      border-bottom: none;
    }}
    .data-table {{
      border-collapse: separate;
      border-spacing: 0;
      width: 100%;
    }}
    .data-table thead th {{
      position: sticky;
      top: 0;
      z-index: 1;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      font-size: 0.7rem;
      color: var(--text-muted);
      background: linear-gradient(90deg, rgba(56, 189, 248, 0.08), rgba(34, 211, 238, 0.05));
      border-bottom: 1px solid var(--border);
      backdrop-filter: blur(10px);
    }}
    .data-table tbody tr {{
      transition: transform 0.2s ease, background-color 0.2s ease;
    }}
    .data-table tbody tr:hover {{
      transform: translateY(-1px);
    }}
    .toolbar {{
      background: rgba(15, 23, 42, 0.04);
      border: 1px solid var(--border);
      border-radius: 1rem;
      padding: 0.75rem;
      box-shadow: var(--shadow-sm);
    }}
    [data-theme="dark"] .toolbar {{
      background: rgba(15, 23, 42, 0.35);
    }}
    .announcement-banner {{
      background: linear-gradient(135deg, rgba(56, 189, 248, 0.08) 0%, rgba(34, 211, 238, 0.08) 60%, rgba(163, 230, 53, 0.06) 100%);
      border-bottom: 1px solid var(--border);
      backdrop-filter: blur(10px);
    }}
    .announcement-banner .title {{
      color: var(--text);
      font-weight: 600;
    }}
    .announcement-banner .content {{
      color: var(--text-muted);
    }}
    .btn-announcement {{
      background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
      color: #fff;
      padding: 0.4rem 0.85rem;
      border-radius: 0.5rem;
      font-size: 0.875rem;
      font-weight: 500;
      transition: all 0.2s ease;
      border: none;
      cursor: pointer;
    }}
    .btn-announcement:hover {{
      transform: translateY(-1px);
      box-shadow: 0 8px 18px rgba(56, 189, 248, 0.35);
    }}
    .btn-announcement-outline {{
      background: var(--bg-card);
      color: var(--text);
      padding: 0.4rem 0.85rem;
      border-radius: 0.5rem;
      font-size: 0.875rem;
      border: 1px solid var(--border);
      transition: all 0.2s ease;
      cursor: pointer;
    }}
    .btn-announcement-outline:hover {{
      background: var(--bg-hover);
      border-color: var(--border-dark);
    }}

    /* Mode banner with gradient */
    .mode-banner {{
      background: linear-gradient(90deg, rgba(56, 189, 248, 0.08) 0%, rgba(34, 211, 238, 0.12) 50%, rgba(163, 230, 53, 0.08) 100%);
      border-bottom: 1px dashed var(--border);
    }}
    .mode-pill {{
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
      padding: 0.25rem 0.75rem;
      border-radius: 9999px;
      font-size: 0.75rem;
      font-weight: 600;
      border: 1px solid transparent;
      transition: all 0.2s ease;
    }}
    .mode-pill.normal {{
      background: rgba(16, 185, 129, 0.12);
      color: #10b981;
      border-color: rgba(16, 185, 129, 0.3);
    }}
    .mode-pill.self-use {{
      background: rgba(245, 158, 11, 0.12);
      color: #f59e0b;
      border-color: rgba(245, 158, 11, 0.3);
    }}
    .mode-pill.maintenance {{
      background: rgba(239, 68, 68, 0.12);
      color: #ef4444;
      border-color: rgba(239, 68, 68, 0.3);
    }}

    /* Self-use mode visibility */
    .self-use-only {{
      display: none;
    }}
    body[data-self-use="true"] .public-only {{
      display: none !important;
    }}
    body[data-self-use="true"] .self-use-only {{
      display: block;
    }}

    /* Feature cards with hover effect */
    .feature-card {{
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 1rem;
      padding: 1.5rem;
      transition: all 0.3s ease;
      position: relative;
      overflow: hidden;
    }}
    .feature-card::before {{
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 3px;
      background: linear-gradient(90deg, var(--primary), var(--accent));
      opacity: 0;
      transition: opacity 0.3s ease;
    }}
    .feature-card:hover {{
      transform: translateY(-4px);
      box-shadow: var(--shadow-lg), var(--glow);
      border-color: var(--primary-light);
    }}
    .feature-card:hover::before {{
      opacity: 1;
    }}

    /* Stat cards */
    .stat-card {{
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 1rem;
      padding: 1.25rem;
      text-align: center;
      transition: all 0.3s ease;
    }}
    .stat-card:hover {{
      transform: translateY(-2px);
      box-shadow: var(--shadow-lg);
    }}
    .stat-value {{
      font-size: 2rem;
      font-weight: 700;
      line-height: 1.2;
      background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }}
    .stat-label {{
      font-size: 0.875rem;
      color: var(--text-muted);
      margin-top: 0.5rem;
    }}

    /* Input fields */
    input[type="text"], input[type="password"], input[type="email"], input[type="number"], textarea, select {{
      background: var(--bg-input);
      border: 1px solid var(--border);
      color: var(--text);
      border-radius: 0.625rem;
      padding: 0.625rem 0.875rem;
      transition: all 0.2s ease;
      outline: none;
    }}
    input:focus, textarea:focus, select:focus {{
      border-color: var(--primary);
      box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.16);
    }}

    /* Gradient text */
    .gradient-text {{
      background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }}

    /* Hero section background */
    .hero-bg {{
      position: relative;
      overflow: hidden;
    }}
    .hero-bg::before {{
      content: '';
      position: absolute;
      top: -50%;
      left: -50%;
      width: 200%;
      height: 200%;
      background: radial-gradient(circle at 30% 20%, rgba(56, 189, 248, 0.12) 0%, transparent 50%),
                  radial-gradient(circle at 70% 80%, rgba(34, 211, 238, 0.1) 0%, transparent 50%);
      animation: heroFloat 20s ease-in-out infinite;
      pointer-events: none;
    }}
    @keyframes heroFloat {{
      0%, 100% {{ transform: translate(0, 0) rotate(0deg); }}
      50% {{ transform: translate(-2%, 2%) rotate(1deg); }}
    }}
    .text-indigo-400,
    .text-indigo-500 {{
      color: var(--primary) !important;
    }}
    .text-indigo-300 {{
      color: var(--primary-light) !important;
    }}
    .text-purple-400 {{
      color: var(--accent) !important;
    }}
    .bg-indigo-500\/10,
    .hover\:bg-indigo-500\/10:hover {{
      background-color: rgba(56, 189, 248, 0.12) !important;
    }}
    .bg-indigo-500\/20,
    .hover\:bg-indigo-500\/20:hover {{
      background-color: rgba(56, 189, 248, 0.2) !important;
    }}
    .bg-indigo-500\/30,
    .hover\:bg-indigo-500\/30:hover {{
      background-color: rgba(56, 189, 248, 0.3) !important;
    }}
    .bg-purple-500\/20 {{
      background-color: rgba(34, 211, 238, 0.2) !important;
    }}
    .hover\:ring-indigo-500\/50:hover {{
      --tw-ring-color: rgba(56, 189, 248, 0.5) !important;
    }}
    .hover\:text-indigo-300:hover,
    .hover\:text-indigo-400:hover {{
      color: var(--primary) !important;
    }}
    .accent-indigo-500 {{
      accent-color: var(--primary);
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

# 还原 COMMON_HEAD 中为兼容 f-string 而写入的双大括号，避免输出到页面后出现语法错误。
COMMON_HEAD = COMMON_HEAD.replace("{{", "{").replace("}}", "}")

COMMON_NAV = r'''
  <nav style="background: var(--bg-nav); border-bottom: 1px solid var(--border); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);" class="sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between h-16">
        <div class="flex items-center space-x-8">
          <a href="/" class="flex items-center gap-2 text-2xl font-bold group">
            <span class="text-2xl group-hover:scale-110 transition-transform">⚡</span>
            <span class="gradient-text">KiroGate</span>
          </a>
          <div class="hidden md:flex space-x-6">
            <a href="/" class="nav-link">首页</a>
            <a href="/docs" class="nav-link">文档</a>
            <a href="/swagger" class="nav-link">接口</a>
            <a href="/playground" class="nav-link">测试</a>
            <a href="/deploy" class="nav-link">部署</a>
            <a href="/dashboard" class="nav-link">面板</a>
          </div>
        </div>
        <div class="flex items-center space-x-3">
          <!-- 登录/用户按钮区域 -->
          <div id="auth-btn-area">
            <a href="/login" id="login-btn" class="hidden sm:inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all btn-primary">
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
          <span class="hidden sm:inline text-xs px-2 py-1 rounded-full" style="background: var(--bg-input); color: var(--text-muted);">v{APP_VERSION}</span>
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
      <div class="px-4 py-3 space-y-1">
        <a href="/" class="block nav-link py-2.5 px-4 rounded-lg hover:bg-indigo-500/10 transition-colors">首页</a>
        <a href="/docs" class="block nav-link py-2.5 px-4 rounded-lg hover:bg-indigo-500/10 transition-colors">文档</a>
        <a href="/swagger" class="block nav-link py-2.5 px-4 rounded-lg hover:bg-indigo-500/10 transition-colors">接口</a>
        <a href="/playground" class="block nav-link py-2.5 px-4 rounded-lg hover:bg-indigo-500/10 transition-colors">测试</a>
        <a href="/deploy" class="block nav-link py-2.5 px-4 rounded-lg hover:bg-indigo-500/10 transition-colors">部署</a>
        <a href="/dashboard" class="block nav-link py-2.5 px-4 rounded-lg hover:bg-indigo-500/10 transition-colors">面板</a>
        <div id="mobile-auth-area" class="pt-3 mt-3" style="border-top: 1px solid var(--border);">
          <a href="/login" class="block py-2.5 px-4 rounded-lg text-center font-medium btn-primary">登录</a>
        </div>
      </div>
    </div>
  </nav>
  <div id="siteModeBanner" class="mode-banner" style="display: none;">
    <div class="max-w-7xl mx-auto px-4 py-2 flex items-center gap-2">
      <span class="text-xs sm:text-sm" style="color: var(--text-muted);">当前模式：</span>
      <span id="siteModeText" class="mode-pill normal">正常运行</span>
    </div>
  </div>
  <div id="siteAnnouncement" class="announcement-banner" style="display: none;">
    <div class="max-w-7xl mx-auto px-4 py-3 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
      <div class="flex items-start gap-2">
        <span class="text-lg">📣</span>
        <div>
          <div class="text-sm font-semibold title">站点公告</div>
          <div id="siteAnnouncementContent" class="text-sm content"></div>
        </div>
      </div>
      <div id="announcementActions" class="flex items-center gap-2">
        <button onclick="markAnnouncementRead()" class="btn-announcement">已读</button>
        <button onclick="dismissAnnouncement()" class="btn-announcement-outline">不再提醒</button>
      </div>
    </div>
  </div>
  <script>
    let currentAnnouncementId = null;

    function escapeHtml(value) {{
      return String(value || '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
    }}

    (function() {{
      const modeEl = document.getElementById('siteModeText');
      const banner = document.getElementById('siteModeBanner');
      if (!modeEl || !banner) return;
      fetch('/api/site-mode')
        .then(r => r.ok ? r.json() : null)
        .then(d => {{
          if (!d) return;
          modeEl.textContent = d.label || '正常运行';
          modeEl.classList.remove('normal', 'self-use', 'maintenance');
          const cls = d.mode === 'self_use' ? 'self-use' : d.mode === 'maintenance' ? 'maintenance' : 'normal';
          modeEl.classList.add(cls);

          // 只在非正常模式时显示横幅
          if (d.mode === 'normal') {{
            banner.style.display = 'none';
          }} else {{
            banner.style.display = 'block';
          }}
        }})
        .catch(() => {{}});
    }})();

    function hideAnnouncement() {{
      const banner = document.getElementById('siteAnnouncement');
      if (banner) banner.style.display = 'none';
    }}

    async function loadAnnouncement() {{
      try {{
        const r = await fetch('/user/api/announcement');
        if (!r.ok) return;
        const d = await r.json();
        if (!d.active || !d.announcement || !d.announcement.content) return;
        currentAnnouncementId = d.announcement.id;
        const banner = document.getElementById('siteAnnouncement');
        const content = document.getElementById('siteAnnouncementContent');
        const actions = document.getElementById('announcementActions');
        const canMark = d.can_mark !== false;
        if (banner && content) {{
          content.innerHTML = d.announcement.content;
          banner.style.display = 'block';
        }}
        if (actions) {{
          actions.style.display = canMark ? 'flex' : 'none';
        }}
      }} catch {{}}
    }}

    async function markAnnouncementRead() {{
      if (!currentAnnouncementId) return;
      const fd = new FormData();
      fd.append('announcement_id', currentAnnouncementId);
      try {{
        await fetch('/user/api/announcement/read', {{ method: 'POST', body: fd }});
      }} catch {{}}
      hideAnnouncement();
    }}

    async function dismissAnnouncement() {{
      if (!currentAnnouncementId) return;
      const fd = new FormData();
      fd.append('announcement_id', currentAnnouncementId);
      try {{
        await fetch('/user/api/announcement/dismiss', {{ method: 'POST', body: fd }});
      }} catch {{}}
      hideAnnouncement();
    }}

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
          const rawName = d.username || '用户';
          const safeName = escapeHtml(rawName);
          const safeInitial = escapeHtml(rawName.slice(0, 1).toUpperCase() || 'U');
          const area = document.getElementById('auth-btn-area');
          const mobileArea = document.getElementById('mobile-auth-area');
          if (area) {{
            area.innerHTML = `<a href="/user" class="hidden sm:flex items-center gap-2 nav-link font-medium">
              <span class="w-7 h-7 rounded-full flex items-center justify-center text-sm text-white" style="background: var(--primary);">${{safeInitial}}</span>
              <span>${{safeName}}</span>
            </a>`;
          }}
          if (mobileArea) {{
            mobileArea.innerHTML = `<a href="/user" class="flex items-center justify-center gap-2 py-2 px-3 rounded font-medium" style="background: var(--bg-card); border: 1px solid var(--border);">
              <span class="w-6 h-6 rounded-full flex items-center justify-center text-xs text-white" style="background: var(--primary);">${{safeInitial}}</span>
              <span>${{safeName || '用户中心'}}</span>
            </a>`;
          }}
        }}
      }} catch {{}} finally {{
        loadAnnouncement();
      }}
    }})();
  </script>
'''

COMMON_FOOTER = '''
  <footer style="background: var(--bg-card); border-top: 1px solid var(--border);" class="py-8 sm:py-10 mt-16 sm:mt-20">
    <div class="max-w-7xl mx-auto px-4">
      <div class="flex flex-col items-center">
        <div class="flex items-center gap-2 mb-4">
          <span class="text-2xl">⚡</span>
          <span class="text-xl font-bold gradient-text">KiroGate</span>
        </div>
        <p class="text-sm text-center mb-4" style="color: var(--text-muted);">OpenAI & Anthropic 兼容的 Kiro API 网关</p>
        <div class="flex flex-wrap justify-center gap-x-6 gap-y-2 text-sm mb-6">
          <span class="flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-blue-400"></span>
            <span style="color: var(--text);">Python</span>
            <a href="https://kirogate.fly.dev" class="text-indigo-400 hover:text-indigo-300 transition-colors" target="_blank">Online</a>
            <span style="color: var(--border-dark);">·</span>
            <a href="https://github.com/dext7r/KiroGate" class="text-indigo-400 hover:text-indigo-300 transition-colors" target="_blank">GitHub</a>
          </span>
        </div>
        <p class="text-xs opacity-60" style="color: var(--text-muted);">欲买桂花同载酒 终不似少年游</p>
      </div>
    </div>
  </footer>
'''

# 还原 COMMON_NAV 中为兼容 f-string 而写入的双大括号，避免前端脚本语法错误。
COMMON_NAV = COMMON_NAV.replace("{{", "{").replace("}}", "}")
# 填充版本号占位符。
COMMON_NAV = COMMON_NAV.replace("{APP_VERSION}", APP_VERSION)

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
    <section class="text-center py-12 sm:py-20 hero-bg">
      <div class="relative z-10">
        <div class="inline-flex items-center gap-2 px-4 py-2 rounded-full mb-6" style="background: var(--bg-card); border: 1px solid var(--border);">
          <span class="w-2 h-2 rounded-full bg-green-400 animate-pulse"></span>
          <span class="text-sm" style="color: var(--text-muted);">服务运行中</span>
        </div>
        <h1 class="text-4xl sm:text-5xl md:text-6xl font-bold mb-6">
          <span class="gradient-text">KiroGate</span>
          <span style="color: var(--text);"> API 网关</span>
        </h1>
        <p class="text-lg sm:text-xl mb-8 max-w-2xl mx-auto px-4" style="color: var(--text-muted);">
          将 OpenAI 和 Anthropic API 请求无缝代理到 Kiro (AWS CodeWhisperer)，
          支持完整的流式传输、工具调用和多模型切换。
        </p>
        <div class="flex flex-col sm:flex-row justify-center gap-4 px-4">
          <a href="/docs" class="btn-primary text-lg px-8 py-3.5 inline-flex items-center justify-center gap-2">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/></svg>
            查看文档
          </a>
          <a href="/playground" class="text-lg px-8 py-3.5 rounded-xl font-medium inline-flex items-center justify-center gap-2 transition-all hover:scale-105" style="background: var(--bg-card); border: 1px solid var(--border); color: var(--text);">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
            在线试用
          </a>
        </div>
      </div>
    </section>

    <!-- Features Grid -->
    <section class="grid md:grid-cols-3 gap-6 py-16">
      <div class="feature-card">
        <div class="text-4xl mb-4">🔄</div>
        <h3 class="text-xl font-semibold mb-3">双 API 兼容</h3>
        <p style="color: var(--text-muted);">同时支持 OpenAI 和 Anthropic API 格式，无需修改现有代码。</p>
      </div>
      <div class="feature-card">
        <div class="text-4xl mb-4">⚡</div>
        <h3 class="text-xl font-semibold mb-3">流式传输</h3>
        <p style="color: var(--text-muted);">完整的 SSE 流式支持，实时获取模型响应。</p>
      </div>
      <div class="feature-card">
        <div class="text-4xl mb-4">🔧</div>
        <h3 class="text-xl font-semibold mb-3">工具调用</h3>
        <p style="color: var(--text-muted);">支持 Function Calling，构建强大的 AI Agent。</p>
      </div>
      <div class="feature-card">
        <div class="text-4xl mb-4">👥</div>
        <h3 class="text-xl font-semibold mb-3">用户系统</h3>
        <p style="color: var(--text-muted);">支持 LinuxDo/GitHub 登录，添加 Token 获取 API Key。</p>
      </div>
      <div class="feature-card">
        <div class="text-4xl mb-4">🔑</div>
        <h3 class="text-xl font-semibold mb-3">API Key 生成</h3>
        <p style="color: var(--text-muted);">生成 sk-xxx 格式密钥，与 OpenAI 客户端无缝兼容。</p>
      </div>
      <div class="feature-card">
        <div class="text-4xl mb-4">🎁</div>
        <h3 class="text-xl font-semibold mb-3">Token 共享池</h3>
        <p style="color: var(--text-muted);">公开添加的 Token 组成共享池，智能负载均衡。</p>
      </div>
      <div class="feature-card">
        <div class="text-4xl mb-4">🔁</div>
        <h3 class="text-xl font-semibold mb-3">自动重试</h3>
        <p style="color: var(--text-muted);">智能处理 403/429/5xx 错误，自动刷新 Token。</p>
      </div>
      <div class="feature-card">
        <div class="text-4xl mb-4">📊</div>
        <h3 class="text-xl font-semibold mb-3">监控面板</h3>
        <p style="color: var(--text-muted);">实时查看请求统计、响应时间和模型使用情况。</p>
      </div>
      <div class="feature-card">
        <div class="text-4xl mb-4">🛡️</div>
        <h3 class="text-xl font-semibold mb-3">Admin 后台</h3>
        <p style="color: var(--text-muted);">用户管理、Token 池管理、IP 黑名单等功能。</p>
      </div>
    </section>

    <!-- Models Chart -->
    <section class="py-12">
      <div class="text-center mb-8">
        <h2 class="text-3xl font-bold mb-3">支持的模型</h2>
        <p style="color: var(--text-muted);">多种 Claude 模型可供选择</p>
      </div>
      <div class="card">
        <div id="modelsChart" style="height: 320px;"></div>
      </div>
    </section>
  </main>

  {COMMON_FOOTER}

  <script>
    // 等待 echarts 加载完成
    function initModelsChart() {{
      if (typeof echarts === 'undefined') {{
        setTimeout(initModelsChart, 100);
        return;
      }}
      const modelsChart = echarts.init(document.getElementById('modelsChart'));
      const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
      modelsChart.setOption({{
      tooltip: {{
        trigger: 'axis',
        backgroundColor: isDark ? 'rgba(17, 24, 39, 0.95)' : 'rgba(255, 255, 255, 0.95)',
        borderColor: isDark ? '#334155' : '#e2e8f0',
        textStyle: {{ color: isDark ? '#e2e8f0' : '#0f172a' }}
      }},
      grid: {{ left: '3%', right: '4%', bottom: '15%', top: '10%', containLabel: true }},
      xAxis: {{
        type: 'category',
        data: {models_json},
        axisLabel: {{ rotate: 30, color: isDark ? '#94a3b8' : '#64748b', fontSize: 11 }},
        axisLine: {{ lineStyle: {{ color: isDark ? '#334155' : '#e2e8f0' }} }}
      }},
      yAxis: {{
        type: 'value',
        name: '性能指数',
        nameTextStyle: {{ color: isDark ? '#94a3b8' : '#64748b' }},
        axisLabel: {{ color: isDark ? '#94a3b8' : '#64748b' }},
        axisLine: {{ lineStyle: {{ color: isDark ? '#334155' : '#e2e8f0' }} }},
        splitLine: {{ lineStyle: {{ color: isDark ? '#1e293b' : '#f1f5f9' }} }}
      }},
      series: [{{
        name: '模型能力',
        type: 'bar',
        data: [100, 100, 70, 90, 90, 85, 85, 80],
        itemStyle: {{
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            {{ offset: 0, color: '#818cf8' }},
            {{ offset: 1, color: '#6366f1' }}
          ]),
          borderRadius: [6, 6, 0, 0]
        }},
        emphasis: {{
          itemStyle: {{
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              {{ offset: 0, color: '#a5b4fc' }},
              {{ offset: 1, color: '#818cf8' }}
            ])
          }}
        }}
      }}]
    }});
    window.addEventListener('resize', () => modelsChart.resize());
    }}

    // 页面加载完成后初始化图表
    if (document.readyState === 'loading') {{
      document.addEventListener('DOMContentLoaded', initModelsChart);
    }} else {{
      initModelsChart();
    }}
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
    <div class="text-center mb-12">
      <h1 class="text-4xl font-bold mb-4">
        <span class="gradient-text">API 文档</span>
      </h1>
      <p style="color: var(--text-muted);">快速上手 KiroGate API</p>
    </div>

    <div class="space-y-8">
      <section class="card">
        <div class="flex items-center gap-3 mb-6">
          <div class="w-10 h-10 rounded-lg flex items-center justify-center text-xl" style="background: linear-gradient(135deg, var(--primary), var(--accent));">🔑</div>
          <h2 class="text-2xl font-semibold">认证方式</h2>
        </div>
        <p style="color: var(--text-muted);" class="mb-6">所有 API 请求需要在 Header 中携带 API Key。支持三种认证模式：</p>

        <div class="space-y-6">
          <div class="p-4 rounded-xl" style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(16, 185, 129, 0.05)); border: 1px solid rgba(16, 185, 129, 0.2);">
            <h3 class="text-lg font-medium mb-3 text-emerald-400">模式 1: 用户 API Key（sk-xxx 格式）⭐ 推荐</h3>
            <pre class="p-4 rounded-lg overflow-x-auto text-sm mb-3">
# OpenAI 格式
Authorization: Bearer sk-xxxxxxxxxxxxxxxx

# Anthropic 格式
x-api-key: sk-xxxxxxxxxxxxxxxx</pre>
            <p class="text-sm" style="color: var(--text-muted);">登录后在用户中心生成，自动使用您添加的 Token 或公开 Token 池。</p>
          </div>

          <div class="p-4 rounded-xl" style="background: var(--bg-input); border: 1px solid var(--border);">
            <h3 class="text-lg font-medium mb-3 text-blue-400">模式 2: 组合模式（用户自带 REFRESH_TOKEN）</h3>
            <pre class="p-4 rounded-lg overflow-x-auto text-sm mb-3">
# OpenAI 格式
Authorization: Bearer YOUR_PROXY_API_KEY:YOUR_REFRESH_TOKEN

# Anthropic 格式
x-api-key: YOUR_PROXY_API_KEY:YOUR_REFRESH_TOKEN</pre>
          </div>

          <div class="p-4 rounded-xl" style="background: var(--bg-input); border: 1px solid var(--border);">
            <h3 class="text-lg font-medium mb-3 text-amber-400">模式 3: 简单模式（使用服务器配置的 REFRESH_TOKEN）</h3>
            <pre class="p-4 rounded-lg overflow-x-auto text-sm">
# OpenAI 格式
Authorization: Bearer YOUR_PROXY_API_KEY

# Anthropic 格式
x-api-key: YOUR_PROXY_API_KEY</pre>
          </div>
        </div>

        <div class="p-4 rounded-xl mt-6" style="background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(139, 92, 246, 0.1)); border: 1px solid rgba(99, 102, 241, 0.2);">
          <p class="text-sm font-semibold mb-2" style="color: var(--text);">💡 推荐使用方式</p>
          <ul class="text-sm space-y-1.5" style="color: var(--text-muted);">
            <li>• <strong>普通用户</strong>：登录后生成 <code class="px-1.5 py-0.5 rounded" style="background: var(--bg-input);">sk-xxx</code> 格式的 API Key，最简单易用</li>
            <li>• <strong>自部署用户</strong>：使用组合模式，自带 REFRESH_TOKEN，无需服务器配置</li>
            <li>• <strong>缓存优化</strong>：每个用户的认证信息会被缓存（最多100个用户），提升性能</li>
          </ul>
        </div>
      </section>

      <section class="card">
        <div class="flex items-center gap-3 mb-6">
          <div class="w-10 h-10 rounded-lg flex items-center justify-center text-xl" style="background: linear-gradient(135deg, var(--primary), var(--accent));">📡</div>
          <h2 class="text-2xl font-semibold">端点列表</h2>
        </div>
        <div class="space-y-3">
          <div class="p-4 rounded-xl flex items-start gap-4" style="background: var(--bg-input); border: 1px solid var(--border);">
            <span class="px-2.5 py-1 text-xs font-bold rounded-md bg-emerald-500 text-white shrink-0">GET</span>
            <div>
              <code class="font-mono">/</code>
              <p class="text-sm mt-1" style="color: var(--text-muted);">健康检查端点</p>
            </div>
          </div>
          <div class="p-4 rounded-xl flex items-start gap-4" style="background: var(--bg-input); border: 1px solid var(--border);">
            <span class="px-2.5 py-1 text-xs font-bold rounded-md bg-emerald-500 text-white shrink-0">GET</span>
            <div>
              <code class="font-mono">/health</code>
              <p class="text-sm mt-1" style="color: var(--text-muted);">详细健康检查，返回 token 状态和缓存信息</p>
            </div>
          </div>
          <div class="p-4 rounded-xl flex items-start gap-4" style="background: var(--bg-input); border: 1px solid var(--border);">
            <span class="px-2.5 py-1 text-xs font-bold rounded-md bg-emerald-500 text-white shrink-0">GET</span>
            <div>
              <code class="font-mono">/v1/models</code>
              <p class="text-sm mt-1" style="color: var(--text-muted);">获取可用模型列表 (需要认证)</p>
            </div>
          </div>
          <div class="p-4 rounded-xl flex items-start gap-4" style="background: var(--bg-input); border: 1px solid var(--border);">
            <span class="px-2.5 py-1 text-xs font-bold rounded-md bg-blue-500 text-white shrink-0">POST</span>
            <div>
              <code class="font-mono">/v1/chat/completions</code>
              <p class="text-sm mt-1" style="color: var(--text-muted);">OpenAI 兼容的聊天补全 API (需要认证)</p>
            </div>
          </div>
          <div class="p-4 rounded-xl flex items-start gap-4" style="background: var(--bg-input); border: 1px solid var(--border);">
            <span class="px-2.5 py-1 text-xs font-bold rounded-md bg-blue-500 text-white shrink-0">POST</span>
            <div>
              <code class="font-mono">/v1/messages</code>
              <p class="text-sm mt-1" style="color: var(--text-muted);">Anthropic 兼容的消息 API (需要认证)</p>
            </div>
          </div>
        </div>
      </section>

      <section class="card">
        <div class="flex items-center gap-3 mb-6">
          <div class="w-10 h-10 rounded-lg flex items-center justify-center text-xl" style="background: linear-gradient(135deg, var(--primary), var(--accent));">💡</div>
          <h2 class="text-2xl font-semibold">使用示例</h2>
        </div>

        <div class="space-y-6">
          <div>
            <h3 class="text-lg font-medium mb-3 flex items-center gap-2">
              <span class="w-6 h-6 rounded bg-yellow-500/20 text-yellow-400 flex items-center justify-center text-xs">🐍</span>
              OpenAI SDK (Python)
            </h3>
            <pre class="p-4 rounded-lg overflow-x-auto text-sm">
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
          </div>

          <div>
            <h3 class="text-lg font-medium mb-3 flex items-center gap-2">
              <span class="w-6 h-6 rounded bg-purple-500/20 text-purple-400 flex items-center justify-center text-xs">🤖</span>
              Anthropic SDK (Python)
            </h3>
            <pre class="p-4 rounded-lg overflow-x-auto text-sm">
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
          </div>

          <div>
            <h3 class="text-lg font-medium mb-3 flex items-center gap-2">
              <span class="w-6 h-6 rounded bg-green-500/20 text-green-400 flex items-center justify-center text-xs">$</span>
              cURL
            </h3>
            <pre class="p-4 rounded-lg overflow-x-auto text-sm">
curl http://localhost:8000/v1/chat/completions \\
  -H "Authorization: Bearer YOUR_PROXY_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "model": "claude-sonnet-4-5",
    "messages": [{{"role": "user", "content": "Hello!"}}]
  }}'</pre>
          </div>
        </div>
      </section>

      <section class="card">
        <div class="flex items-center gap-3 mb-6">
          <div class="w-10 h-10 rounded-lg flex items-center justify-center text-xl" style="background: linear-gradient(135deg, var(--primary), var(--accent));">🤖</div>
          <h2 class="text-2xl font-semibold">可用模型</h2>
        </div>
        <div class="grid md:grid-cols-2 gap-3">
          {"".join([f'<div class="px-4 py-3 rounded-lg flex items-center gap-3" style="background: var(--bg-input); border: 1px solid var(--border);"><span class="w-2 h-2 rounded-full bg-green-400"></span><code class="text-sm">{m}</code></div>' for m in AVAILABLE_MODELS])}
        </div>
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
    <div class="text-center mb-10">
      <h1 class="text-4xl font-bold mb-4">
        <span class="gradient-text">API Playground</span>
      </h1>
      <p style="color: var(--text-muted);">在线测试 KiroGate API</p>
    </div>

    <div class="grid lg:grid-cols-2 gap-6">
      <!-- Request Panel -->
      <div class="card">
        <div class="flex items-center gap-3 mb-6">
          <div class="w-10 h-10 rounded-lg flex items-center justify-center text-xl" style="background: linear-gradient(135deg, var(--primary), var(--accent));">⚙️</div>
          <h2 class="text-xl font-semibold">请求配置</h2>
        </div>

        <div class="space-y-5">
          <div>
            <label class="block text-sm font-medium mb-2" style="color: var(--text-muted);">API Key</label>
            <div class="relative flex gap-2">
              <div class="relative flex-1">
                <input type="password" id="apiKey" class="w-full rounded-lg px-4 py-2.5 pr-10" placeholder="sk-xxx 或 PROXY_KEY 或 PROXY_KEY:REFRESH_TOKEN" oninput="updateAuthMode()">
                <button type="button" onclick="toggleKeyVisibility()" class="absolute right-3 top-1/2 -translate-y-1/2 p-1 hover:opacity-70 transition-opacity" style="color: var(--text-muted);" title="显示/隐藏">
                  <span id="toggleKeyIcon">👁️</span>
                </button>
              </div>
              <button type="button" onclick="copyApiKey(this)" class="px-3 py-2.5 rounded-lg hover:opacity-80 transition-opacity" style="background: var(--bg-input); border: 1px solid var(--border); color: var(--text-muted);" title="复制">📋</button>
              <button type="button" onclick="clearApiKey()" class="px-3 py-2.5 rounded-lg hover:opacity-80 transition-opacity" style="background: var(--bg-input); border: 1px solid var(--border); color: var(--text-muted);" title="清除">🗑️</button>
            </div>
            <div id="authModeDisplay" class="mt-2 text-sm flex items-center gap-2">
              <span id="authModeIcon">🔒</span>
              <span id="authModeText" style="color: var(--text-muted);">支持 sk-xxx / PROXY_KEY / PROXY_KEY:TOKEN 三种格式</span>
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium mb-2" style="color: var(--text-muted);">模型</label>
            <select id="model" class="w-full rounded-lg px-4 py-2.5">
              {models_options}
            </select>
          </div>

          <div>
            <div class="flex justify-between items-center mb-2">
              <label class="text-sm font-medium" style="color: var(--text-muted);">消息内容</label>
              <button type="button" onclick="clearMessage()" class="text-xs px-2.5 py-1 rounded-lg hover:opacity-80 transition-opacity" style="background: var(--bg-input); border: 1px solid var(--border); color: var(--text-muted);">🗑️ 清除</button>
            </div>
            <textarea id="message" rows="4" class="w-full rounded-lg px-4 py-3" placeholder="输入你的消息...">Hello! Please introduce yourself briefly.</textarea>
          </div>

          <div class="flex flex-wrap items-center gap-4 p-4 rounded-lg" style="background: var(--bg-input);">
            <label class="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" id="stream" checked class="w-4 h-4 rounded accent-indigo-500">
              <span class="text-sm">流式响应</span>
            </label>
            <div class="flex items-center gap-3">
              <label class="flex items-center gap-2 cursor-pointer">
                <input type="radio" name="apiFormat" value="openai" checked class="w-4 h-4 accent-indigo-500">
                <span class="text-sm">OpenAI 格式</span>
              </label>
              <label class="flex items-center gap-2 cursor-pointer">
                <input type="radio" name="apiFormat" value="anthropic" class="w-4 h-4 accent-indigo-500">
                <span class="text-sm">Anthropic 格式</span>
              </label>
            </div>
          </div>

          <button id="sendBtn" onclick="sendRequest()" class="btn-primary w-full py-3.5 text-lg font-medium">
            <span id="sendBtnText" class="flex items-center justify-center gap-2">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
              发送请求
            </span>
            <span id="sendBtnLoading" class="hidden flex items-center justify-center gap-2"><span class="loading-spinner mr-2"></span>请求中...</span>
          </button>
        </div>
      </div>

      <!-- Response Panel -->
      <div class="card">
        <div class="flex items-center gap-3 mb-6">
          <div class="w-10 h-10 rounded-lg flex items-center justify-center text-xl" style="background: linear-gradient(135deg, var(--primary), var(--accent));">📤</div>
          <h2 class="text-xl font-semibold">响应结果</h2>
        </div>
        <div id="response" class="rounded-xl p-4 min-h-[300px] whitespace-pre-wrap text-sm font-mono overflow-auto" style="background: var(--bg-input); border: 1px solid var(--border);">
          <span style="color: var(--text-muted);">响应将显示在这里...</span>
        </div>
        <div id="stats" class="mt-4 text-sm flex items-center gap-2" style="color: var(--text-muted);"></div>
      </div>
    </div>
  </main>

  {COMMON_FOOTER}

  <script>
    function toggleKeyVisibility() {{
      const input = document.getElementById('apiKey');
      const icon = document.getElementById('toggleKeyIcon');
      if (input.type === 'password') {{
        input.type = 'text';
        icon.textContent = '🙈';
      }} else {{
        input.type = 'password';
        icon.textContent = '👁️';
      }}
    }}

    function copyApiKey(btn) {{
      const input = document.getElementById('apiKey');
      if (!input.value) return;
      navigator.clipboard.writeText(input.value);
      if (btn) {{
        const original = btn.textContent;
        btn.textContent = '✅';
        setTimeout(() => btn.textContent = original, 1000);
      }}
    }}

    function clearApiKey() {{
      document.getElementById('apiKey').value = '';
      localStorage.removeItem('playground_api_key');
      updateAuthMode();
    }}

    function clearMessage() {{
      document.getElementById('message').value = '';
    }}

    function updateAuthMode() {{
      const apiKey = document.getElementById('apiKey').value;
      const iconEl = document.getElementById('authModeIcon');
      const textEl = document.getElementById('authModeText');

      // 持久化到 localStorage
      if (apiKey) {{
        localStorage.setItem('playground_api_key', apiKey);
      }} else {{
        localStorage.removeItem('playground_api_key');
      }}

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

    // 页面加载时恢复 API Key
    (function() {{
      const savedKey = localStorage.getItem('playground_api_key');
      if (savedKey) {{
        document.getElementById('apiKey').value = savedKey;
        updateAuthMode();
      }}
    }})();
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
    <div class="text-center mb-12">
      <h1 class="text-4xl font-bold mb-4">
        <span class="gradient-text">部署指南</span>
      </h1>
      <p style="color: var(--text-muted);">快速部署你自己的 KiroGate 实例</p>
    </div>

    <div class="space-y-8">
      <section class="card">
        <div class="flex items-center gap-3 mb-6">
          <div class="w-10 h-10 rounded-lg flex items-center justify-center text-xl" style="background: linear-gradient(135deg, var(--primary), var(--accent));">📋</div>
          <h2 class="text-2xl font-semibold">环境要求</h2>
        </div>
        <div class="grid sm:grid-cols-3 gap-4">
          <div class="p-4 rounded-xl text-center" style="background: var(--bg-input); border: 1px solid var(--border);">
            <div class="text-3xl mb-2">🐍</div>
            <div class="font-medium">Python 3.10+</div>
          </div>
          <div class="p-4 rounded-xl text-center" style="background: var(--bg-input); border: 1px solid var(--border);">
            <div class="text-3xl mb-2">📦</div>
            <div class="font-medium">pip 或 poetry</div>
          </div>
          <div class="p-4 rounded-xl text-center" style="background: var(--bg-input); border: 1px solid var(--border);">
            <div class="text-3xl mb-2">🌐</div>
            <div class="font-medium">网络连接</div>
          </div>
        </div>
      </section>

      <section class="card">
        <div class="flex items-center gap-3 mb-6">
          <div class="w-10 h-10 rounded-lg flex items-center justify-center text-xl" style="background: linear-gradient(135deg, var(--primary), var(--accent));">⚙️</div>
          <h2 class="text-2xl font-semibold">环境变量配置</h2>
        </div>
        <pre class="p-4 rounded-lg overflow-x-auto text-sm">
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

        <div class="p-4 rounded-xl mt-4" style="background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(139, 92, 246, 0.1)); border: 1px solid rgba(99, 102, 241, 0.2);">
          <p class="text-sm font-semibold mb-2" style="color: var(--text);">💡 配置说明</p>
          <ul class="text-sm space-y-1.5" style="color: var(--text-muted);">
            <li>• <strong>简单模式</strong>：必须配置 <code class="px-1.5 py-0.5 rounded" style="background: var(--bg-input);">REFRESH_TOKEN</code> 环境变量</li>
            <li>• <strong>组合模式（推荐）</strong>：无需配置 <code class="px-1.5 py-0.5 rounded" style="background: var(--bg-input);">REFRESH_TOKEN</code>，用户在请求中直接传递</li>
            <li>• <strong>多租户部署</strong>：使用组合模式可以让多个用户共享同一网关实例</li>
          </ul>
        </div>
      </section>

      <section class="card">
        <div class="flex items-center gap-3 mb-6">
          <div class="w-10 h-10 rounded-lg flex items-center justify-center text-xl" style="background: linear-gradient(135deg, var(--primary), var(--accent));">🐍</div>
          <h2 class="text-2xl font-semibold">本地运行</h2>
        </div>
        <pre class="p-4 rounded-lg overflow-x-auto text-sm">
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
        <div class="flex items-center gap-3 mb-6">
          <div class="w-10 h-10 rounded-lg flex items-center justify-center text-xl" style="background: linear-gradient(135deg, var(--primary), var(--accent));">🐳</div>
          <h2 class="text-2xl font-semibold">Docker 部署</h2>
        </div>

        <div class="space-y-6">
          <div>
            <h3 class="text-lg font-medium mb-3 text-emerald-400">Docker Compose（推荐）</h3>
            <pre class="p-4 rounded-lg overflow-x-auto text-sm">
# 复制配置文件
cp .env.example .env
# 编辑 .env 填写你的凭证

# 启动服务（自动创建持久卷）
docker-compose up -d

# 查看日志
docker logs -f kirogate</pre>
          </div>

          <div>
            <h3 class="text-lg font-medium mb-3 text-blue-400">手动 Docker 运行</h3>
            <pre class="p-4 rounded-lg overflow-x-auto text-sm">
docker build -t kirogate .
docker run -d -p 8000:8000 \\
  -v kirogate_data:/app/data \\
  -e PROXY_API_KEY="your-key" \\
  -e ADMIN_PASSWORD="your-admin-pwd" \\
  --name kirogate kirogate</pre>
          </div>
        </div>
      </section>

      <section class="card">
        <div class="flex items-center gap-3 mb-6">
          <div class="w-10 h-10 rounded-lg flex items-center justify-center text-xl" style="background: linear-gradient(135deg, var(--primary), var(--accent));">🚀</div>
          <h2 class="text-2xl font-semibold">Fly.io 部署</h2>
        </div>
        <pre class="p-4 rounded-lg overflow-x-auto text-sm">
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
        <div class="flex items-center gap-3 mb-6">
          <div class="w-10 h-10 rounded-lg flex items-center justify-center text-xl" style="background: linear-gradient(135deg, var(--danger), #f97316);">💾</div>
          <h2 class="text-2xl font-semibold">数据持久化</h2>
        </div>
        <div class="p-4 rounded-xl mb-4" style="background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3);">
          <p class="text-sm font-semibold text-red-400">⚠️ 重要提醒</p>
          <p class="text-sm mt-1" style="color: var(--text-muted);">用户数据（数据库）需要持久化存储，否则每次部署会丢失所有用户、Token 和 API Key！</p>
        </div>
        <div class="grid sm:grid-cols-2 gap-4">
          <div class="p-4 rounded-xl" style="background: var(--bg-input); border: 1px solid var(--border);">
            <p class="font-medium text-emerald-400 mb-2">🐳 Docker Compose</p>
            <p class="text-sm" style="color: var(--text-muted);">已配置命名卷 <code class="px-1.5 py-0.5 rounded" style="background: var(--bg-card);">kirogate_data:/app/data</code>，使用 <code class="px-1.5 py-0.5 rounded" style="background: var(--bg-card);">docker-compose down</code> 保留数据</p>
          </div>
          <div class="p-4 rounded-xl" style="background: var(--bg-input); border: 1px solid var(--border);">
            <p class="font-medium text-blue-400 mb-2">🚀 Fly.io</p>
            <p class="text-sm" style="color: var(--text-muted);">需手动创建卷：<code class="px-1.5 py-0.5 rounded" style="background: var(--bg-card);">fly volumes create kirogate_data --region nrt --size 1</code></p>
          </div>
        </div>
      </section>

      <section class="card">
        <div class="flex items-center gap-3 mb-6">
          <div class="w-10 h-10 rounded-lg flex items-center justify-center text-xl" style="background: linear-gradient(135deg, var(--primary), var(--accent));">🔐</div>
          <h2 class="text-2xl font-semibold">获取 Refresh Token</h2>
        </div>

        <div class="space-y-4">
          <div class="p-4 rounded-xl" style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(16, 185, 129, 0.05)); border: 1px solid rgba(16, 185, 129, 0.2);">
            <p class="text-sm font-semibold mb-3 text-emerald-400">🌐 方式一：浏览器获取（推荐）</p>
            <ol class="text-sm space-y-2" style="color: var(--text-muted);">
              <li><span class="inline-flex items-center justify-center w-5 h-5 rounded-full text-xs font-bold mr-2" style="background: var(--primary); color: white;">1</span>打开 <a href="https://app.kiro.dev/account/usage" target="_blank" class="text-indigo-400 hover:underline">https://app.kiro.dev/account/usage</a> 并登录</li>
              <li><span class="inline-flex items-center justify-center w-5 h-5 rounded-full text-xs font-bold mr-2" style="background: var(--primary); color: white;">2</span>按 <kbd class="px-1.5 py-0.5 rounded text-xs" style="background: var(--bg-input); border: 1px solid var(--border);">F12</kbd> 打开开发者工具</li>
              <li><span class="inline-flex items-center justify-center w-5 h-5 rounded-full text-xs font-bold mr-2" style="background: var(--primary); color: white;">3</span>点击 <strong>应用/Application</strong> → <strong>存储/Storage</strong> → <strong>Cookie</strong></li>
              <li><span class="inline-flex items-center justify-center w-5 h-5 rounded-full text-xs font-bold mr-2" style="background: var(--primary); color: white;">4</span>选择 <code class="px-1.5 py-0.5 rounded" style="background: var(--bg-input);">https://app.kiro.dev</code></li>
              <li><span class="inline-flex items-center justify-center w-5 h-5 rounded-full text-xs font-bold mr-2" style="background: var(--primary); color: white;">5</span>复制 <code class="text-emerald-400">RefreshToken</code> 的值</li>
            </ol>
          </div>

          <div class="p-4 rounded-xl" style="background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(139, 92, 246, 0.1)); border: 1px solid rgba(99, 102, 241, 0.2);">
            <p class="text-sm font-semibold mb-2" style="color: var(--text);">🛠️ 方式二：Kiro Account Manager</p>
            <p class="text-sm" style="color: var(--text-muted);">
              使用 <a href="https://github.com/chaogei/Kiro-account-manager" class="text-indigo-400 hover:underline font-medium" target="_blank">Kiro Account Manager</a>
              可以轻松管理多个账号的 Refresh Token。
            </p>
          </div>
        </div>
      </section>
    </div>
  </main>

  {COMMON_FOOTER}
</body>
</html>'''


def render_status_page(status_data: dict) -> str:
    """Render the status page."""
    status_color = "#10b981" if status_data.get("status") == "healthy" else "#ef4444"
    token_color = "#10b981" if status_data.get("token_valid") else "#ef4444"

    return f'''<!DOCTYPE html>
<html lang="zh">
<head>{COMMON_HEAD}
  <meta http-equiv="refresh" content="30">
</head>
<body>
  {COMMON_NAV}

  <main class="max-w-4xl mx-auto px-4 py-12">
    <div class="text-center mb-10">
      <h1 class="text-4xl font-bold mb-4">
        <span class="gradient-text">系统状态</span>
      </h1>
      <p style="color: var(--text-muted);">实时监控服务运行状态</p>
    </div>

    <div class="grid md:grid-cols-2 gap-6 mb-8">
      <div class="card text-center stat-card">
        <h2 class="text-lg font-semibold mb-4" style="color: var(--text-muted);">服务状态</h2>
        <div class="flex items-center justify-center gap-3">
          <div class="w-4 h-4 rounded-full animate-pulse" style="background: {status_color};"></div>
          <span class="text-3xl font-bold">{status_data.get("status", "unknown").upper()}</span>
        </div>
      </div>
      <div class="card text-center">
        <h2 class="text-lg font-semibold mb-4" style="color: var(--text-muted);">Token 状态</h2>
        <div class="flex items-center justify-center gap-3">
          <div class="w-4 h-4 rounded-full" style="background: {token_color};"></div>
          <span class="text-3xl font-bold">{"有效" if status_data.get("token_valid") else "无效/未配置"}</span>
        </div>
      </div>
    </div>

    <div class="card mb-8">
      <div class="flex items-center gap-3 mb-6">
        <div class="w-10 h-10 rounded-lg flex items-center justify-center text-xl" style="background: linear-gradient(135deg, var(--primary), var(--accent));">📊</div>
        <h2 class="text-xl font-semibold">详细信息</h2>
      </div>
      <div class="grid grid-cols-2 gap-4">
        <div class="p-4 rounded-xl" style="background: var(--bg-input); border: 1px solid var(--border);">
          <p class="text-sm mb-1" style="color: var(--text-muted);">版本</p>
          <p class="font-mono text-lg font-medium">{status_data.get("version", "unknown")}</p>
        </div>
        <div class="p-4 rounded-xl" style="background: var(--bg-input); border: 1px solid var(--border);">
          <p class="text-sm mb-1" style="color: var(--text-muted);">缓存大小</p>
          <p class="font-mono text-lg font-medium">{status_data.get("cache_size", 0)}</p>
        </div>
        <div class="p-4 rounded-xl" style="background: var(--bg-input); border: 1px solid var(--border);">
          <p class="text-sm mb-1" style="color: var(--text-muted);">最后更新</p>
          <p class="font-mono text-sm">{status_data.get("cache_last_update", "N/A")}</p>
        </div>
        <div class="p-4 rounded-xl" style="background: var(--bg-input); border: 1px solid var(--border);">
          <p class="text-sm mb-1" style="color: var(--text-muted);">时间戳</p>
          <p class="font-mono text-sm">{status_data.get("timestamp", "N/A")}</p>
        </div>
      </div>
    </div>

    <p class="text-sm text-center" style="color: var(--text-muted);">
      <span class="inline-flex items-center gap-2">
        <span class="loading-spinner"></span>
        页面每 30 秒自动刷新
      </span>
    </p>
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
.mc{{background:var(--bg-card);border:1px solid var(--border);border-radius:1rem;padding:1.25rem;text-align:center;transition:all .3s ease}}
.mc:hover{{border-color:var(--primary);transform:translateY(-2px);box-shadow:var(--shadow-lg),var(--glow)}}
.mi{{font-size:2rem;margin-bottom:.75rem}}
.stat-value{{font-size:1.75rem;font-weight:700;line-height:1.2}}
.stat-label{{font-size:.75rem;margin-top:.5rem;color:var(--text-muted)}}
.chart-card{{background:var(--bg-card);border:1px solid var(--border);border-radius:1rem;padding:1.5rem;box-shadow:var(--shadow)}}
.chart-title{{font-size:1rem;font-weight:600;margin-bottom:1rem;display:flex;align-items:center;gap:.5rem}}
</style>
</head>
<body>
  {COMMON_NAV}
  <main class="max-w-7xl mx-auto px-4 py-8">
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
      <div>
        <h1 class="text-3xl font-bold">
          <span class="gradient-text">Dashboard</span>
        </h1>
        <p class="text-sm mt-1" style="color: var(--text-muted);">实时监控请求统计</p>
      </div>
      <button onclick="refreshData()" class="btn-primary flex items-center gap-2">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
        刷新
      </button>
    </div>

    <!-- Primary Stats -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6 kpi-grid">
      <div class="mc">
        <div class="mi">📈</div>
        <div class="stat-value text-indigo-400" id="totalRequests">-</div>
        <div class="stat-label">总请求</div>
      </div>
      <div class="mc">
        <div class="mi">✅</div>
        <div class="stat-value text-emerald-400" id="successRate">-</div>
        <div class="stat-label">成功率</div>
      </div>
      <div class="mc">
        <div class="mi">⏱️</div>
        <div class="stat-value text-amber-400" id="avgResponseTime">-</div>
        <div class="stat-label">平均耗时</div>
      </div>
      <div class="mc">
        <div class="mi">🕐</div>
        <div class="stat-value text-purple-400" id="uptime">-</div>
        <div class="stat-label">运行时长</div>
      </div>
    </div>

    <!-- Secondary Stats -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
      <div class="mc">
        <div class="mi">⚡</div>
        <div class="stat-value text-blue-400" style="font-size:1.5rem" id="streamRequests">-</div>
        <div class="stat-label">流式请求</div>
      </div>
      <div class="mc">
        <div class="mi">💾</div>
        <div class="stat-value text-cyan-400" style="font-size:1.5rem" id="nonStreamRequests">-</div>
        <div class="stat-label">非流式请求</div>
      </div>
      <div class="mc">
        <div class="mi">❌</div>
        <div class="stat-value text-red-400" style="font-size:1.5rem" id="failedRequests">-</div>
        <div class="stat-label">失败请求</div>
      </div>
      <div class="mc">
        <div class="mi">🤖</div>
        <div class="stat-value text-emerald-400" style="font-size:1.25rem" id="topModel">-</div>
        <div class="stat-label">热门模型</div>
      </div>
    </div>

    <!-- API Type Stats -->
    <div class="grid grid-cols-2 gap-4 mb-8">
      <div class="mc">
        <div class="mi">🟢</div>
        <div class="stat-value text-emerald-400" style="font-size:1.5rem" id="openaiRequests">-</div>
        <div class="stat-label">OpenAI API</div>
      </div>
      <div class="mc">
        <div class="mi">🟣</div>
        <div class="stat-value text-purple-400" style="font-size:1.5rem" id="anthropicRequests">-</div>
        <div class="stat-label">Anthropic API</div>
      </div>
    </div>

    <!-- Charts -->
    <div class="grid lg:grid-cols-2 gap-6 mb-8">
      <div class="chart-card">
        <h2 class="chart-title">
          <span class="w-8 h-8 rounded-lg flex items-center justify-center text-sm" style="background: linear-gradient(135deg, var(--primary), var(--accent));">📈</span>
          24小时请求趋势
        </h2>
        <div id="latencyChart" style="height:280px"></div>
      </div>
      <div class="chart-card">
        <h2 class="chart-title">
          <span class="w-8 h-8 rounded-lg flex items-center justify-center text-sm" style="background: linear-gradient(135deg, var(--primary), var(--accent));">📊</span>
          状态分布
        </h2>
        <div style="height:280px;position:relative">
          <canvas id="statusChart"></canvas>
        </div>
      </div>
    </div>

    <!-- Recent Requests -->
    <div class="chart-card">
      <h2 class="chart-title">
        <span class="w-8 h-8 rounded-lg flex items-center justify-center text-sm" style="background: linear-gradient(135deg, var(--primary), var(--accent));">📋</span>
        最近请求
      </h2>
      <div class="table-responsive">
        <table class="w-full text-sm data-table">
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
const START_TIME = null;
const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
async function refreshData(){{
  try{{
    const r=await fetch('/api/metrics'),d=await r.json();
    document.getElementById('totalRequests').textContent=d.totalRequests||0;
    document.getElementById('successRate').textContent=d.totalRequests>0?((d.successRequests/d.totalRequests)*100).toFixed(1)+'%':'0%';
    document.getElementById('avgResponseTime').textContent=(d.avgResponseTime||0).toFixed(0)+'ms';

    const startTime = d.startTime || START_TIME || Date.now();
    const now=Date.now();
    const u=Math.max(0, Math.floor((now-startTime)/1000));
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
      <tr class="table-row">
        <td class="py-3 px-3">${{new Date(q.timestamp).toLocaleTimeString()}}</td>
        <td class="py-3 px-3"><span class="text-xs px-2 py-1 rounded-md ${{q.apiType==='anthropic'?'bg-purple-500/20 text-purple-400':'bg-emerald-500/20 text-emerald-400'}}">${{q.apiType}}</span></td>
        <td class="py-3 px-3 font-mono text-xs">${{q.path}}</td>
        <td class="py-3 px-3 ${{q.status<400?'text-emerald-400':'text-red-400'}}">${{q.status}}</td>
        <td class="py-3 px-3">${{q.duration.toFixed(0)}}ms</td>
        <td class="py-3 px-3">${{q.model||'-'}}</td>
      </tr>`).join(''):'<tr><td colspan="6" class="py-6 text-center" style="color:var(--text-muted)">暂无请求</td></tr>';
  }}catch(e){{console.error(e)}}
}}

// 等待 echarts 和 Chart 加载完成
function initDashboardCharts() {{
  if (typeof echarts === 'undefined' || typeof Chart === 'undefined') {{
    setTimeout(initDashboardCharts, 100);
    return;
  }}
  lc=echarts.init(document.getElementById('latencyChart'));
lc.setOption({{
  tooltip:{{trigger:'axis',backgroundColor:isDark?'rgba(17,24,39,0.95)':'rgba(255,255,255,0.95)',borderColor:isDark?'#334155':'#e2e8f0',textStyle:{{color:isDark?'#e2e8f0':'#0f172a'}}}},
  grid:{{left:'3%',right:'4%',bottom:'3%',containLabel:true}},
  xAxis:{{type:'category',data:[],axisLabel:{{color:isDark?'#94a3b8':'#64748b',fontSize:11}},axisLine:{{lineStyle:{{color:isDark?'#334155':'#e2e8f0'}}}}}},
  yAxis:{{type:'value',name:'请求数',nameTextStyle:{{color:isDark?'#94a3b8':'#64748b'}},axisLabel:{{color:isDark?'#94a3b8':'#64748b'}},axisLine:{{lineStyle:{{color:isDark?'#334155':'#e2e8f0'}}}},splitLine:{{lineStyle:{{color:isDark?'#1e293b':'#f1f5f9'}}}}}},
  series:[{{
    type:'bar',
    data:[],
    itemStyle:{{
      color:new echarts.graphic.LinearGradient(0,0,0,1,[
        {{offset:0,color:'#818cf8'}},
        {{offset:1,color:'#6366f1'}}
      ]),
      borderRadius:[6,6,0,0]
    }},
    emphasis:{{itemStyle:{{color:'#a5b4fc'}}}}
  }}]
}});

sc=new Chart(document.getElementById('statusChart'),{{
  type:'doughnut',
  data:{{
    labels:['成功','失败'],
    datasets:[{{data:[0,0],backgroundColor:['#10b981','#ef4444'],borderWidth:0,hoverOffset:8}}]
  }},
  options:{{
    responsive:true,
    maintainAspectRatio:false,
    cutout:'65%',
    plugins:{{
      legend:{{position:'bottom',labels:{{color:isDark?'#94a3b8':'#64748b',padding:20,font:{{size:13}}}}}}
    }}
  }}
}});

  refreshData();
  setInterval(refreshData,5000);
  window.addEventListener('resize',()=>lc.resize());
}}

// 页面加载完成后初始化图表
if (document.readyState === 'loading') {{
  document.addEventListener('DOMContentLoaded', initDashboardCharts);
}} else {{
  initDashboardCharts();
}}
  </script>
</body>
</html>'''


def render_swagger_page() -> str:
    """Render the Swagger UI page."""
    return f'''<!DOCTYPE html>
<html lang="zh">
<head>
  {COMMON_HEAD}
  <link rel="stylesheet" href="{get_asset_url("cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css")}">
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
  <script src="{get_asset_url("cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js")}"></script>
  <script>
    window.onload = function() {{
      SwaggerUIBundle({{
        url: "/openapi.json",
        dom_id: '#swagger-ui',
        deepLinking: true,
        persistAuthorization: true,
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
    safe_error = html.escape(error) if error else ''
    error_html = f'<div class="bg-red-500/20 border border-red-500 text-red-400 px-4 py-3 rounded-lg mb-4">{safe_error}</div>' if safe_error else ''

    return f'''<!DOCTYPE html>
<html lang="zh">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Admin Login - KiroGate</title>
  <meta name="robots" content="noindex, nofollow">
  <script src="{get_asset_url("cdn.tailwindcss.com")}"></script>
  <style>
    :root {{ --bg-main: #f4f7fb; --bg-card: rgba(255, 255, 255, 0.82); --text: #0f172a; --text-muted: #64748b; --border: rgba(148, 163, 184, 0.35); --primary: #38bdf8; --bg-input: rgba(255, 255, 255, 0.9); }}
    .dark {{ --bg-main: #05070f; --bg-card: rgba(15, 23, 42, 0.8); --text: #e2e8f0; --text-muted: #94a3b8; --border: rgba(148, 163, 184, 0.2); --bg-input: rgba(15, 23, 42, 0.85); }}
    body {{ background: var(--bg-main); color: var(--text); font-family: 'Sora', 'Noto Sans SC', system-ui, sans-serif; min-height: 100vh; display: flex; align-items: center; justify-content: center; transition: background .3s, color .3s; }}
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
    .admin-header {{
      background: var(--bg-nav);
      border-bottom: 1px solid var(--border);
      backdrop-filter: blur(14px);
    }}
    .admin-shell {{
      position: relative;
    }}
    .card {{
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 1rem;
      padding: 1.5rem;
      box-shadow: var(--shadow);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
    }}
    .admin-tag {{
      background: rgba(56, 189, 248, 0.15);
      color: var(--primary);
      border: 1px solid rgba(56, 189, 248, 0.4);
    }}
    .btn {{
      padding: .5rem 1rem;
      border-radius: .75rem;
      font-weight: 600;
      transition: all .2s ease;
      cursor: pointer;
      background: var(--bg-input);
      border: 1px solid var(--border);
      color: var(--text);
    }}
    .btn:hover {{
      border-color: var(--border-dark);
      transform: translateY(-1px);
    }}
    .btn-primary {{
      background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 70%, var(--accent-2) 120%);
      color: #fff;
      border: 1px solid rgba(255, 255, 255, 0.08);
      box-shadow: 0 12px 24px rgba(56, 189, 248, 0.28);
    }}
    .btn-primary:hover {{ box-shadow: 0 16px 36px rgba(56, 189, 248, 0.35); }}
    .btn-danger {{
      background: rgba(244, 63, 94, 0.18);
      color: #fecdd3;
      border: 1px solid rgba(244, 63, 94, 0.4);
    }}
    .btn-success {{
      background: rgba(34, 197, 94, 0.18);
      color: #bbf7d0;
      border: 1px solid rgba(34, 197, 94, 0.4);
    }}
    .btn:disabled {{ opacity: 0.5; cursor: not-allowed; transform: none; }}
    .tab {{
      padding: .75rem 1.25rem;
      cursor: pointer;
      border-bottom: 2px solid transparent;
      transition: all .2s ease;
      letter-spacing: 0.02em;
    }}
    .tab:hover {{ color: var(--primary); }}
    .tab.active {{
      color: var(--primary);
      border-bottom-color: var(--primary);
      text-shadow: 0 0 18px rgba(56, 189, 248, 0.35);
    }}
    .table-row {{ border-bottom: 1px solid var(--border); }}
    .table-row:hover {{ background: var(--bg-hover); }}
    .switch {{ position: relative; width: 50px; height: 26px; }}
    .switch input {{ opacity: 0; width: 0; height: 0; }}
    .slider {{ position: absolute; cursor: pointer; inset: 0; background: #475569; border-radius: 26px; transition: .3s; }}
    .slider:before {{ content: ""; position: absolute; height: 20px; width: 20px; left: 3px; bottom: 3px; background: white; border-radius: 50%; transition: .3s; }}
    input:checked + .slider {{ background: var(--success); }}
    input:checked + .slider:before {{ transform: translateX(24px); }}
    .status-dot {{ width: 10px; height: 10px; border-radius: 50%; display: inline-block; }}
    .status-ok {{ background: var(--success); }}
    .status-error {{ background: var(--danger); }}
  </style>
</head>
<body>
  <!-- Admin Header -->
  <header class="sticky top-0 z-50 admin-header">
    <div class="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
      <div class="flex items-center gap-4">
        <a href="/" class="flex items-center gap-2 text-xl font-bold" style="color: var(--text); text-decoration: none;">
          <span>⚡</span>
          <span class="hidden sm:inline">KiroGate</span>
        </a>
        <span class="inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-medium admin-tag">🛡️ Admin</span>
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

  <main class="max-w-7xl mx-auto px-4 py-6 admin-shell">
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
      <div class="card text-center stat-card cursor-pointer hover:ring-2 hover:ring-indigo-500/50 transition-all" onclick="showTab('donated-tokens')">
        <div class="text-2xl mb-2">🔑</div>
        <div class="text-2xl font-bold" id="tokenStatus">-</div>
        <div class="text-sm" style="color: var(--text-muted);">Token 状态</div>
      </div>
      <div class="card text-center stat-card cursor-pointer hover:ring-2 hover:ring-indigo-500/50 transition-all" onclick="showTab('overview')">
        <div class="text-2xl mb-2">📊</div>
        <div class="text-2xl font-bold" id="totalRequests">-</div>
        <div class="text-sm" style="color: var(--text-muted);">总请求数</div>
      </div>
      <div class="card text-center stat-card cursor-pointer hover:ring-2 hover:ring-indigo-500/50 transition-all" onclick="showTab('tokens')">
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
      <div class="tab" onclick="showTab('announcement')">📣 公告</div>
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
        <div class="flex flex-wrap justify-between items-center gap-4 mb-4 toolbar">
          <h2 class="text-lg font-semibold">👥 注册用户管理</h2>
          <div class="flex items-center gap-2">
            <input type="text" id="usersSearch" placeholder="搜索用户名/邮箱..." oninput="filterUsers()"
              class="px-3 py-2 rounded-lg text-sm w-40" style="background: var(--bg-input); border: 1px solid var(--border); color: var(--text);">
            <select id="usersStatusFilter" onchange="filterUsers()" class="px-3 py-2 rounded-lg text-sm" style="background: var(--bg-input); border: 1px solid var(--border); color: var(--text);">
              <option value="">全部状态</option>
              <option value="false">正常</option>
              <option value="true">已封禁</option>
            </select>
            <select id="usersApprovalFilter" onchange="filterUsers()" class="px-3 py-2 rounded-lg text-sm" style="background: var(--bg-input); border: 1px solid var(--border); color: var(--text);">
              <option value="">全部审核</option>
              <option value="pending">待审核</option>
              <option value="approved">已通过</option>
              <option value="rejected">已拒绝</option>
            </select>
            <input type="number" id="usersTrustLevel" min="0" placeholder="信任等级" oninput="filterUsers()"
              class="px-3 py-2 rounded-lg text-sm w-28" style="background: var(--bg-input); border: 1px solid var(--border); color: var(--text);">
            <select id="usersPageSize" onchange="filterUsers()" class="px-3 py-2 rounded-lg text-sm" style="background: var(--bg-input); border: 1px solid var(--border); color: var(--text);">
              <option value="10">10/页</option>
              <option value="20" selected>20/页</option>
              <option value="50">50/页</option>
            </select>
            <button onclick="batchBanUsers()" id="batchBanUsersBtn" class="btn btn-danger text-sm">批量封禁</button>
            <button onclick="batchUnbanUsers()" id="batchUnbanUsersBtn" class="btn btn-success text-sm">批量解禁</button>
            <button onclick="batchApproveUsers()" id="batchApproveUsersBtn" class="btn btn-success text-sm">批量通过</button>
            <button onclick="batchRejectUsers()" id="batchRejectUsersBtn" class="btn btn-danger text-sm">批量拒绝</button>
            <button onclick="refreshUsers()" class="btn btn-primary text-sm">刷新</button>
          </div>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full text-sm data-table">
            <thead>
              <tr style="color: var(--text-muted); border-bottom: 1px solid var(--border);">
                <th class="text-left py-3 px-3">
                  <input type="checkbox" id="selectAllUsers" onchange="toggleSelectAllUsers(this.checked)">
                </th>
                <th class="text-left py-3 px-3 cursor-pointer hover:text-indigo-400" onclick="sortUsers('id')">ID ↕</th>
                <th class="text-left py-3 px-3 cursor-pointer hover:text-indigo-400" onclick="sortUsers('username')">用户名 ↕</th>
                <th class="text-left py-3 px-3">邮箱</th>
                <th class="text-left py-3 px-3 cursor-pointer hover:text-indigo-400" onclick="sortUsers('trust_level')">信任等级 ↕</th>
                <th class="text-left py-3 px-3 cursor-pointer hover:text-indigo-400" onclick="sortUsers('token_count')">Token 数 ↕</th>
                <th class="text-left py-3 px-3 cursor-pointer hover:text-indigo-400" onclick="sortUsers('api_key_count')">API Key ↕</th>
                <th class="text-left py-3 px-3 cursor-pointer hover:text-indigo-400" onclick="sortUsers('approval_status')">审核 ↕</th>
                <th class="text-left py-3 px-3 cursor-pointer hover:text-indigo-400" onclick="sortUsers('is_banned')">状态 ↕</th>
                <th class="text-left py-3 px-3 cursor-pointer hover:text-indigo-400" onclick="sortUsers('created_at')">注册时间 ↕</th>
                <th class="text-left py-3 px-3">操作</th>
              </tr>
            </thead>
            <tbody id="usersTable">
              <tr><td colspan="11" class="py-6 text-center" style="color: var(--text-muted);">加载中...</td></tr>
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
        <div class="flex flex-wrap justify-between items-center gap-4 mb-4 toolbar">
          <h2 class="text-lg font-semibold">🎁 添加 Token 池</h2>
          <div class="flex items-center gap-2">
            <input type="text" id="poolSearch" placeholder="搜索用户名..." oninput="filterPoolTokens()"
              class="px-3 py-2 rounded-lg text-sm w-40" style="background: var(--bg-input); border: 1px solid var(--border); color: var(--text);">
            <select id="poolVisibilityFilter" onchange="filterPoolTokens()" class="px-3 py-2 rounded-lg text-sm" style="background: var(--bg-input); border: 1px solid var(--border); color: var(--text);">
              <option value="">全部可见性</option>
              <option value="public">公开</option>
              <option value="private">私有</option>
            </select>
            <select id="poolStatusFilter" onchange="filterPoolTokens()" class="px-3 py-2 rounded-lg text-sm" style="background: var(--bg-input); border: 1px solid var(--border); color: var(--text);">
              <option value="">全部状态</option>
              <option value="active">有效</option>
              <option value="invalid">无效</option>
              <option value="expired">已过期</option>
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
          <div style="background: var(--bg-input);" class="p-3 rounded-lg text-center cursor-pointer hover:ring-2 hover:ring-indigo-500/50 transition-all" onclick="applyPoolQuickFilter('all')">
            <div class="text-xl font-bold text-green-400" id="poolTotalTokens">-</div>
            <div class="text-xs" style="color: var(--text-muted);">总 Token</div>
          </div>
          <div style="background: var(--bg-input);" class="p-3 rounded-lg text-center cursor-pointer hover:ring-2 hover:ring-indigo-500/50 transition-all" onclick="applyPoolQuickFilter('active')">
            <div class="text-xl font-bold text-blue-400" id="poolActiveTokens">-</div>
            <div class="text-xs" style="color: var(--text-muted);">有效</div>
          </div>
          <div style="background: var(--bg-input);" class="p-3 rounded-lg text-center cursor-pointer hover:ring-2 hover:ring-indigo-500/50 transition-all" onclick="applyPoolQuickFilter('public')">
            <div class="text-xl font-bold text-purple-400" id="poolPublicTokens">-</div>
            <div class="text-xs" style="color: var(--text-muted);">公开</div>
          </div>
          <div style="background: var(--bg-input);" class="p-3 rounded-lg text-center">
            <div class="text-xl font-bold text-yellow-400" id="poolAvgSuccessRate">-</div>
            <div class="text-xs" style="color: var(--text-muted);">平均成功率</div>
          </div>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full text-sm data-table">
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
        <div class="flex flex-wrap justify-between items-center gap-4 mb-4 toolbar">
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
          <table class="w-full text-sm data-table">
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
        <div class="flex flex-wrap justify-between items-center gap-4 mb-4 toolbar">
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
          <table class="w-full text-sm data-table">
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
        <div class="flex flex-wrap justify-between items-center gap-4 mb-4 toolbar">
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
          <table class="w-full text-sm data-table">
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

    <!-- Tab Content: Announcement -->
    <div id="tab-announcement" class="tab-content hidden">
      <div class="card">
        <div class="flex flex-wrap items-center justify-between gap-4 mb-4 toolbar">
          <h2 class="text-lg font-semibold">📣 站点公告</h2>
          <label class="switch">
            <input type="checkbox" id="announcementToggle">
            <span class="slider"></span>
          </label>
        </div>
        <textarea id="announcementContent" class="w-full h-36 p-3 rounded-lg" style="background: var(--bg-input); border: 1px solid var(--border);" placeholder="请输入公告内容..."></textarea>
        <div class="flex flex-wrap items-center justify-between gap-3 mt-3">
          <div class="flex flex-wrap items-center gap-4 text-xs" style="color: var(--text-muted);">
            <span>最近更新：<span id="announcementUpdatedAt">-</span></span>
            <label class="flex items-center gap-2">
              <input type="checkbox" id="announcementGuestToggle">
              <span>未登录可见</span>
            </label>
          </div>
          <div class="flex items-center gap-2">
            <button onclick="refreshAnnouncement()" class="btn" style="background: var(--bg-input); border: 1px solid var(--border);">刷新</button>
            <button onclick="saveAnnouncement()" class="btn btn-primary">保存</button>
          </div>
        </div>
        <p class="text-xs mt-3" style="color: var(--text-muted);">公告开启后，用户可标记已读或不再提醒；更新内容会重新提醒所有用户。</p>
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
          <div class="flex items-center justify-between p-4 rounded-lg mt-4" style="background: var(--bg-input);">
            <div>
              <div class="font-medium">自用模式</div>
              <div class="text-sm" style="color: var(--text-muted);">禁用公开 Token 池并关闭新用户注册</div>
            </div>
            <label class="switch">
              <input type="checkbox" id="selfUseToggle" onchange="toggleSelfUse(this.checked)">
              <span class="slider"></span>
            </label>
          </div>
          <div class="flex items-center justify-between p-4 rounded-lg mt-4" style="background: var(--bg-input);">
            <div>
              <div class="font-medium">注册审核</div>
              <div class="text-sm" style="color: var(--text-muted);">开启后新注册用户需审核通过</div>
            </div>
            <label class="switch">
              <input type="checkbox" id="approvalToggle" onchange="toggleApproval(this.checked)">
              <span class="slider"></span>
            </label>
          </div>
        </div>

        <div class="card">
          <h2 class="text-lg font-semibold mb-4">🔐 Proxy API Key</h2>
          <div class="space-y-3">
            <input id="proxyApiKeyInput" type="password" class="w-full rounded px-3 py-2"
              style="background: var(--bg-input); border: 1px solid var(--border); color: var(--text);"
              placeholder="未加载">
            <div class="flex flex-wrap items-center gap-2">
              <button onclick="refreshProxyApiKey()" class="btn" style="background: var(--bg-input); border: 1px solid var(--border);">刷新</button>
              <button onclick="toggleProxyApiKey()" id="proxyApiKeyToggle" class="btn" style="background: var(--bg-input); border: 1px solid var(--border);">显示</button>
              <button onclick="copyProxyApiKey()" class="btn" style="background: var(--bg-input); border: 1px solid var(--border);">复制</button>
              <button onclick="saveProxyApiKey()" class="btn btn-primary">保存</button>
            </div>
            <p class="text-xs" style="color: var(--text-muted);">保存后立即生效，旧 Key 会失效。</p>
          </div>
        </div>

        <div class="card">
          <h2 class="text-lg font-semibold mb-4">💾 数据导入导出</h2>
          <div class="space-y-4">
            <div class="space-y-2">
              <div class="text-sm font-medium">导出选择（支持单选/多选）</div>
              <select id="dbExportSelect" multiple size="2" class="w-full rounded px-3 py-2 text-sm"
                style="background: var(--bg-input); border: 1px solid var(--border); color: var(--text);">
                <option value="users">用户数据库（加载中）</option>
                <option value="metrics">统计数据库（加载中）</option>
              </select>
              <div class="flex flex-wrap items-center gap-2">
                <button onclick="selectAllDbOptions('dbExportSelect', true)" class="btn"
                  style="background: var(--bg-input); border: 1px solid var(--border);">全选</button>
                <button onclick="selectAllDbOptions('dbExportSelect', false)" class="btn"
                  style="background: var(--bg-input); border: 1px solid var(--border);">清空</button>
                <button onclick="exportDatabase()" class="btn btn-primary">导出所选（zip）</button>
              </div>
            </div>
            <div class="space-y-2">
              <div class="text-sm font-medium">导入（先解析再确认）</div>
              <input id="dbImportFile" type="file" accept=".zip,.db" class="w-full rounded px-3 py-2 text-sm"
                style="background: var(--bg-input); border: 1px solid var(--border); color: var(--text);">
              <div class="flex flex-wrap items-center gap-2">
                <button onclick="previewDatabaseImport()" class="btn"
                  style="background: var(--bg-input); border: 1px solid var(--border);">解析文件</button>
                <button id="dbImportConfirmBtn" onclick="confirmDatabaseImport()" class="btn btn-primary" disabled>确认导入</button>
              </div>
              <select id="dbImportSelect" multiple size="2" class="w-full rounded px-3 py-2 text-sm"
                style="background: var(--bg-input); border: 1px solid var(--border); color: var(--text);">
                <option disabled>请先解析导出文件</option>
              </select>
              <p id="dbImportStatus" class="text-xs" style="color: var(--text-muted);">导入前会校验数据库结构。</p>
            </div>
            <p class="text-xs" style="color: var(--text-muted);">导入会覆盖现有数据，建议先导出备份；完成后请重启服务以加载最新数据。</p>
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
    const allTabs = ['overview','users','donated-tokens','ip-stats','blacklist','tokens','announcement','system'];

    function escapeHtml(value) {{
      return String(value || '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
    }}

    function buildQuery(params) {{
      const qs = new URLSearchParams();
      Object.entries(params).forEach(([key, value]) => {{
        if (value === undefined || value === null || value === '') return;
        qs.append(key, String(value));
      }});
      const str = qs.toString();
      return str ? `?${{str}}` : '';
    }}

    async function fetchJson(url, options = {{}}) {{
      const r = await fetch(url, options);
      const text = await r.text();
      let data = {{}};
      try {{ data = text ? JSON.parse(text) : {{}}; }} catch (e) {{ data = {{}}; }}
      if (!r.ok) throw data;
      return data;
    }}

    let currentAnnouncementId = null;

    async function refreshAnnouncement() {{
      try {{
        const d = await fetchJson('/admin/api/announcement');
        const ann = d.announcement || null;
        currentAnnouncementId = ann ? ann.id : null;
        document.getElementById('announcementContent').value = ann?.content || '';
        const guestToggle = document.getElementById('announcementGuestToggle');
        if (guestToggle) guestToggle.checked = !!ann?.allow_guest;
        document.getElementById('announcementToggle').checked = !!d.is_active;
        const updated = ann?.updated_at ? new Date(ann.updated_at).toLocaleString() : '-';
        document.getElementById('announcementUpdatedAt').textContent = updated;
      }} catch (e) {{ console.error(e); }}
    }}

    async function saveAnnouncement() {{
      const content = document.getElementById('announcementContent').value.trim();
      const isActive = document.getElementById('announcementToggle').checked;
      const allowGuest = document.getElementById('announcementGuestToggle')?.checked;
      if (isActive && !content) {{
        alert('请填写公告内容');
        return;
      }}
      const fd = new FormData();
      fd.append('content', content);
      fd.append('is_active', isActive ? 'true' : 'false');
      fd.append('allow_guest', allowGuest ? 'true' : 'false');
      try {{
        await fetchJson('/admin/api/announcement', {{ method: 'POST', body: fd }});
        alert('保存成功');
        refreshAnnouncement();
      }} catch (e) {{
        alert(e.error || '保存失败');
      }}
    }}

    async function refreshProxyApiKey() {{
      try {{
        const d = await fetchJson('/admin/api/proxy-key');
        const input = document.getElementById('proxyApiKeyInput');
        if (input) input.value = d.proxy_api_key || '';
      }} catch (e) {{ console.error(e); }}
    }}

    function toggleProxyApiKey() {{
      const input = document.getElementById('proxyApiKeyInput');
      const btn = document.getElementById('proxyApiKeyToggle');
      if (!input || !btn) return;
      const isHidden = input.type === 'password';
      input.type = isHidden ? 'text' : 'password';
      btn.textContent = isHidden ? '隐藏' : '显示';
    }}

    async function copyProxyApiKey() {{
      const input = document.getElementById('proxyApiKeyInput');
      if (!input || !input.value) return;
      try {{
        await navigator.clipboard.writeText(input.value);
        alert('已复制');
      }} catch (e) {{
        input.select();
        document.execCommand('copy');
        alert('已复制');
      }}
    }}

    async function saveProxyApiKey() {{
      const input = document.getElementById('proxyApiKeyInput');
      const value = input ? input.value.trim() : '';
      if (!value) {{
        alert('请填写 API Key');
        return;
      }}
      const fd = new FormData();
      fd.append('proxy_api_key', value);
      try {{
        await fetchJson('/admin/api/proxy-key', {{ method: 'POST', body: fd }});
        alert('保存成功');
        refreshProxyApiKey();
      }} catch (e) {{
        alert(e.error || '保存失败');
      }}
    }}

    let dbImportToken = null;

    function formatBytes(bytes) {{
      const value = Number(bytes);
      if (!Number.isFinite(value)) return '-';
      const units = ['B', 'KB', 'MB', 'GB', 'TB'];
      let size = value;
      let idx = 0;
      while (size >= 1024 && idx < units.length - 1) {{
        size /= 1024;
        idx += 1;
      }}
      const digits = idx === 0 ? 0 : (size >= 10 ? 0 : 1);
      return `${{size.toFixed(digits)}} ${{units[idx]}}`;
    }}

    function setDbSelectOptions(selectId, items, autoSelectAll = false) {{
      const select = document.getElementById(selectId);
      if (!select) return;
      select.innerHTML = '';
      items.forEach(item => {{
        const option = document.createElement('option');
        option.value = item.key;
        const sizeText = item.exists === false ? '不存在' : formatBytes(item.size_bytes);
        option.textContent = `${{item.label}}（${{sizeText}}）`;
        option.disabled = item.exists === false;
        option.selected = autoSelectAll && !option.disabled;
        select.appendChild(option);
      }});
      if (!items.length) {{
        const option = document.createElement('option');
        option.textContent = '暂无可选项';
        option.disabled = true;
        select.appendChild(option);
      }}
    }}

    function selectAllDbOptions(selectId, enabled) {{
      const select = document.getElementById(selectId);
      if (!select) return;
      Array.from(select.options).forEach(option => {{
        if (!option.disabled) option.selected = !!enabled;
      }});
    }}

    function getSelectedDbOptions(selectId) {{
      const select = document.getElementById(selectId);
      if (!select) return [];
      return Array.from(select.selectedOptions).map(option => option.value).filter(Boolean);
    }}

    function getSelectedDbLabels(selectId) {{
      const select = document.getElementById(selectId);
      if (!select) return [];
      return Array.from(select.selectedOptions).map(option => {{
        const text = option.textContent || '';
        return text.split('（')[0] || text;
      }});
    }}

    function resetDbImportState(message) {{
      dbImportToken = null;
      setDbSelectOptions('dbImportSelect', [], false);
      const status = document.getElementById('dbImportStatus');
      if (status) status.textContent = message || '请先解析导出文件。';
      const btn = document.getElementById('dbImportConfirmBtn');
      if (btn) btn.disabled = true;
    }}

    async function loadDbInfo() {{
      try {{
        const d = await fetchJson('/admin/api/db/info');
        const items = Array.isArray(d.items) ? d.items : [];
        setDbSelectOptions('dbExportSelect', items, false);
      }} catch (e) {{
        setDbSelectOptions('dbExportSelect', [
          {{ key: 'users', label: '用户数据库', size_bytes: null, exists: true }},
          {{ key: 'metrics', label: '统计数据库', size_bytes: null, exists: true }},
        ], false);
      }}
    }}

    function exportDatabase() {{
      const selected = getSelectedDbOptions('dbExportSelect');
      if (!selected.length) {{
        alert('请选择要导出的数据库');
        return;
      }}
      const qs = new URLSearchParams();
      qs.set('db_types', selected.join(','));
      window.location.href = `/admin/api/db/export?${{qs.toString()}}`;
    }}

    async function previewDatabaseImport() {{
      const input = document.getElementById('dbImportFile');
      if (!input || !input.files || !input.files.length) {{
        alert('请选择要导入的文件');
        return;
      }}
      const fd = new FormData();
      fd.append('file', input.files[0]);
      try {{
        const d = await fetchJson('/admin/api/db/import/preview', {{ method: 'POST', body: fd }});
        dbImportToken = d.token || null;
        const items = Array.isArray(d.items) ? d.items : [];
        setDbSelectOptions('dbImportSelect', items, true);
        const status = document.getElementById('dbImportStatus');
        if (status) status.textContent = d.message || '解析完成，请选择需要导入的数据库。';
        const btn = document.getElementById('dbImportConfirmBtn');
        if (btn) btn.disabled = !dbImportToken || items.length === 0;
      }} catch (e) {{
        resetDbImportState(e.error || '解析失败');
        alert(e.error || '解析失败');
      }}
    }}

    async function confirmDatabaseImport() {{
      const selected = getSelectedDbOptions('dbImportSelect');
      if (!dbImportToken) {{
        alert('请先解析导入文件');
        return;
      }}
      if (!selected.length) {{
        alert('请选择要导入的数据库');
        return;
      }}
      const labels = getSelectedDbLabels('dbImportSelect').join('、');
      if (!confirm(`确定导入：${{labels}} 吗？此操作会覆盖现有数据。`)) return;
      const fd = new FormData();
      fd.append('token', dbImportToken);
      fd.append('db_types', selected.join(','));
      try {{
        const d = await fetchJson('/admin/api/db/import/confirm', {{ method: 'POST', body: fd }});
        alert(d.message || '导入完成');
        const input = document.getElementById('dbImportFile');
        if (input) input.value = '';
        resetDbImportState('导入完成，请在需要时重新解析文件。');
        loadDbInfo();
      }} catch (e) {{
        alert(e.error || '导入失败');
      }}
    }}

    function renderTokenStatus(status) {{
      if (status === 'active') return '<span class="text-green-400">有效</span>';
      if (status === 'invalid') return '<span class="text-red-400">无效</span>';
      if (status === 'expired') return '<span class="text-red-400">已过期</span>';
      return `<span class="text-red-400">${{status || '-'}}</span>`;
    }}

    function normalizeSuccessRate(rate) {{
      const value = Number(rate);
      if (!Number.isFinite(value)) return null;
      return value <= 1 ? value * 100 : value;
    }}

    function formatSuccessRate(rate, digits = 1) {{
      const percent = normalizeSuccessRate(rate);
      if (percent === null) return '-';
      return percent.toFixed(digits) + '%';
    }}

    function setTokenVisibility(value) {{
      const select = document.getElementById('tokenVisibilityFilter');
      if (!select) return;
      select.value = value;
      updateTokenChips();
      filterTokens();
    }}

    function setTokenStatus(value) {{
      const select = document.getElementById('tokenStatusFilter');
      if (!select) return;
      select.value = value;
      updateTokenChips();
      filterTokens();
    }}

    function updateTokenChips() {{
      const visibility = document.getElementById('tokenVisibilityFilter')?.value ?? '';
      const status = document.getElementById('tokenStatusFilter')?.value ?? '';
      document.querySelectorAll('.filter-chip[data-group="visibility"]').forEach(chip => {{
        chip.classList.toggle('active', chip.dataset.value === visibility);
      }});
      document.querySelectorAll('.filter-chip[data-group="status"]').forEach(chip => {{
        chip.classList.toggle('active', chip.dataset.value === status);
      }});
    }}

    function setKeysActive(value) {{
      document.getElementById('keysActiveFilter').value = value;
      updateKeysChips();
      filterKeys();
    }}

    function updateKeysChips() {{
      const activeValue = document.getElementById('keysActiveFilter').value;
      document.querySelectorAll('.filter-chip[data-group="keys-active"]').forEach(chip => {{
        chip.classList.toggle('active', chip.dataset.value === activeValue);
      }});
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
      if (tab === 'announcement') refreshAnnouncement();
      if (tab === 'system') refreshProxyApiKey();
    }}

    async function refreshStats() {{
      try {{
        const d = await fetchJson('/admin/api/stats');
        // Site toggle and icon
        const siteEnabled = d.site_enabled;
        document.getElementById('siteIcon').textContent = siteEnabled ? '🟢' : '🔴';
        document.getElementById('siteToggleQuick').checked = siteEnabled;
        document.getElementById('siteToggle').checked = siteEnabled;
        const selfUseToggle = document.getElementById('selfUseToggle');
        if (selfUseToggle) selfUseToggle.checked = !!d.self_use_enabled;
        const approvalToggle = document.getElementById('approvalToggle');
        if (approvalToggle) approvalToggle.checked = !!d.require_approval;
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
        const pageSize = parseInt(document.getElementById('ipStatsPageSize').value);
        const search = document.getElementById('ipStatsSearch').value.trim();
        const d = await fetchJson('/admin/api/ip-stats' + buildQuery({{
          page: ipStatsCurrentPage,
          page_size: pageSize,
          search,
          sort_field: ipStatsSortField,
          sort_order: ipStatsSortAsc ? 'asc' : 'desc'
        }}));
        allIpStats = d.items || [];
        const total = d.pagination?.total ?? allIpStats.length;
        const totalPages = Math.ceil(total / pageSize) || 1;
        if (totalPages > 0 && ipStatsCurrentPage > totalPages) {{
          ipStatsCurrentPage = totalPages;
          return refreshIpStats();
        }}
        selectedIps.clear();
        document.getElementById('selectAllIps').checked = false;
        renderIpStatsTable(allIpStats);
        renderIpStatsPagination(total, pageSize, totalPages);
      }} catch (e) {{ console.error(e); }}
    }}

    function filterIpStats() {{
      ipStatsCurrentPage = 1;
      refreshIpStats();
    }}

    function sortIpStats(field) {{
      if (ipStatsSortField === field) {{
        ipStatsSortAsc = !ipStatsSortAsc;
      }} else {{
        ipStatsSortField = field;
        ipStatsSortAsc = false;
      }}
      ipStatsCurrentPage = 1;
      refreshIpStats();
    }}

    function goIpStatsPage(page) {{
      ipStatsCurrentPage = page;
      refreshIpStats();
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
      tb.innerHTML = ips.map(ip => {{
        const lastSeen = ip.last_seen ?? ip.lastSeen;
        return `
        <tr class="table-row">
          <td class="py-3 px-3">
            <input type="checkbox" value="${{ip.ip}}" ${{selectedIps.has(ip.ip) ? 'checked' : ''}} onchange="toggleIpSelection('${{ip.ip}}', this.checked)">
          </td>
          <td class="py-3 px-3 font-mono">${{ip.ip}}</td>
          <td class="py-3 px-3">${{ip.count}}</td>
          <td class="py-3 px-3">${{lastSeen ? new Date(lastSeen).toLocaleString() : '-'}}</td>
          <td class="py-3 px-3">
            <button onclick="banIpDirect('${{ip.ip}}')" class="text-xs px-2 py-1 rounded bg-red-500/20 text-red-400 hover:bg-red-500/30">封禁</button>
          </td>
        </tr>
      `;
      }}).join('');
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
        const pageSize = parseInt(document.getElementById('blacklistPageSize').value);
        const search = document.getElementById('blacklistSearch').value.trim();
        const d = await fetchJson('/admin/api/blacklist' + buildQuery({{
          page: blacklistCurrentPage,
          page_size: pageSize,
          search,
          sort_field: blacklistSortField,
          sort_order: blacklistSortAsc ? 'asc' : 'desc'
        }}));
        allBlacklist = d.items || [];
        const total = d.pagination?.total ?? allBlacklist.length;
        const totalPages = Math.ceil(total / pageSize) || 1;
        if (totalPages > 0 && blacklistCurrentPage > totalPages) {{
          blacklistCurrentPage = totalPages;
          return refreshBlacklist();
        }}
        selectedBlacklistIps.clear();
        renderBlacklistTable(allBlacklist);
        renderBlacklistPagination(total, pageSize, totalPages);
        updateBatchUnbanButton();
      }} catch (e) {{ console.error(e); }}
    }}

    function filterBlacklist() {{
      blacklistCurrentPage = 1;
      refreshBlacklist();
    }}

    function sortBlacklist(field) {{
      if (blacklistSortField === field) {{
        blacklistSortAsc = !blacklistSortAsc;
      }} else {{
        blacklistSortField = field;
        blacklistSortAsc = true;
      }}
      blacklistCurrentPage = 1;
      refreshBlacklist();
    }}

    function goBlacklistPage(page) {{
      blacklistCurrentPage = page;
      refreshBlacklist();
    }}

    function renderBlacklistTable(blacklist) {{
      const tb = document.getElementById('blacklistTable');
      if (!blacklist.length) {{
        tb.innerHTML = '<tr><td colspan="5" class="py-6 text-center" style="color: var(--text-muted);">黑名单为空</td></tr>';
        document.getElementById('blacklistSelectAll').checked = false;
        return;
      }}
      tb.innerHTML = blacklist.map(ip => {{
        const bannedAt = ip.banned_at ?? ip.bannedAt;
        const reason = escapeHtml(ip.reason || '-');
        return `
        <tr class="table-row">
          <td class="py-3 px-3">
            <input type="checkbox" class="blacklist-checkbox" value="${{ip.ip}}" onchange="toggleBlacklistSelection('${{ip.ip}}', this.checked)">
          </td>
          <td class="py-3 px-3 font-mono">${{ip.ip}}</td>
          <td class="py-3 px-3">${{bannedAt ? new Date(bannedAt).toLocaleString() : '-'}}</td>
          <td class="py-3 px-3">${{reason}}</td>
          <td class="py-3 px-3">
            <button onclick="unbanIp('${{ip.ip}}')" class="text-xs px-2 py-1 rounded bg-green-500/20 text-green-400 hover:bg-green-500/30">解封</button>
          </td>
        </tr>
      `;
      }}).join('');

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

    async function toggleSelfUse(enabled) {{
      const fd = new FormData();
      fd.append('enabled', enabled);
      await fetch('/admin/api/toggle-self-use', {{ method: 'POST', body: fd }});
      refreshStats();
    }}

    async function toggleApproval(enabled) {{
      const fd = new FormData();
      fd.append('enabled', enabled);
      await fetch('/admin/api/toggle-approval', {{ method: 'POST', body: fd }});
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
        const pageSize = parseInt(document.getElementById('tokensPageSize').value);
        const search = document.getElementById('tokensSearch').value.trim();
        const d = await fetchJson('/admin/api/tokens' + buildQuery({{
          page: tokensCurrentPage,
          page_size: pageSize,
          search
        }}));
        allCachedTokens = (d.tokens || []).map((t, i) => ({{ ...t, index: (tokensCurrentPage - 1) * pageSize + i + 1 }}));
        const total = d.pagination?.total ?? d.count ?? allCachedTokens.length;
        const totalPages = Math.ceil(total / pageSize) || 1;
        if (totalPages > 0 && tokensCurrentPage > totalPages) {{
          tokensCurrentPage = totalPages;
          return refreshTokenList();
        }}
        selectedTokens.clear();
        renderCachedTokens();
        renderTokensPagination(total, pageSize, totalPages);
      }} catch (e) {{ console.error(e); }}
    }}

    function filterCachedTokens() {{
      tokensCurrentPage = 1;
      refreshTokenList();
    }}

    function renderCachedTokens() {{
      const tokens = [...allCachedTokens];
      tokens.sort((a, b) => {{
        let va = a[tokensSortField], vb = b[tokensSortField];
        if (tokensSortField === 'has_access_token') {{
          va = va ? 1 : 0;
          vb = vb ? 1 : 0;
        }}
        if (va < vb) return tokensSortAsc ? -1 : 1;
        if (va > vb) return tokensSortAsc ? 1 : -1;
        return 0;
      }});
      renderTokensTable(tokens);
    }}

    function sortCachedTokens(field) {{
      if (tokensSortField === field) {{
        tokensSortAsc = !tokensSortAsc;
      }} else {{
        tokensSortField = field;
        tokensSortAsc = true;
      }}
      renderCachedTokens();
    }}

    function goTokensPage(page) {{
      tokensCurrentPage = page;
      refreshTokenList();
    }}

    function toggleAllTokens(checked) {{
      if (checked) {{
        allCachedTokens.forEach(t => selectedTokens.add(t.token_id));
      }} else {{
        selectedTokens.clear();
      }}
      renderCachedTokens();
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
    let selectedUsers = new Set();

    async function refreshUsers() {{
      try {{
        const pageSize = parseInt(document.getElementById('usersPageSize').value);
        const search = document.getElementById('usersSearch').value.trim();
        const statusValue = document.getElementById('usersStatusFilter')?.value ?? '';
        const approvalValue = document.getElementById('usersApprovalFilter')?.value ?? '';
        const trustLevelRaw = document.getElementById('usersTrustLevel')?.value ?? '';
        const trustLevel = trustLevelRaw === '' ? undefined : parseInt(trustLevelRaw, 10);
        const d = await fetchJson('/admin/api/users' + buildQuery({{
          page: usersCurrentPage,
          page_size: pageSize,
          search,
          is_banned: statusValue === '' ? undefined : statusValue,
          approval_status: approvalValue === '' ? undefined : approvalValue,
          trust_level: Number.isFinite(trustLevel) ? trustLevel : undefined,
          sort_field: usersSortField,
          sort_order: usersSortAsc ? 'asc' : 'desc'
        }}));
        allUsers = d.users || [];
        const total = d.pagination?.total ?? allUsers.length;
        const totalPages = Math.ceil(total / pageSize) || 1;
        if (totalPages > 0 && usersCurrentPage > totalPages) {{
          usersCurrentPage = totalPages;
          return refreshUsers();
        }}
        selectedUsers.clear();
        document.getElementById('selectAllUsers').checked = false;
        renderUsersTable(allUsers);
        renderUsersPagination(total, pageSize, totalPages);
        updateBatchUserButtons();
      }} catch (e) {{ console.error(e); }}
    }}

    function filterUsers() {{
      usersCurrentPage = 1;
      refreshUsers();
    }}

    function sortUsers(field) {{
      if (usersSortField === field) {{
        usersSortAsc = !usersSortAsc;
      }} else {{
        usersSortField = field;
        usersSortAsc = true;
      }}
      usersCurrentPage = 1;
      refreshUsers();
    }}

    function goUsersPage(page) {{
      usersCurrentPage = page;
      refreshUsers();
    }}

    function renderUsersTable(users) {{
      const tb = document.getElementById('usersTable');
      if (!users.length) {{
        tb.innerHTML = '<tr><td colspan="9" class="py-6 text-center" style="color: var(--text-muted);">暂无数据</td></tr>';
        document.getElementById('selectAllUsers').checked = false;
        return;
      }}
      tb.innerHTML = users.map(u => {{
        const username = escapeHtml(u.username || '-');
        const email = escapeHtml(u.email || '-');
        const approval = u.approval_status || 'approved';
        const approvalBadge = approval === 'approved'
          ? '<span class="text-green-400">已通过</span>'
          : approval === 'pending'
            ? '<span class="text-yellow-400">待审核</span>'
            : '<span class="text-red-400">已拒绝</span>';
        const approvalActions = [
          approval !== 'approved'
            ? `<button onclick="approveUser(${{u.id}})" class="text-xs px-2 py-1 rounded bg-green-500/20 text-green-400 hover:bg-green-500/30">通过</button>`
            : '',
          approval !== 'rejected'
            ? `<button onclick="rejectUser(${{u.id}})" class="text-xs px-2 py-1 rounded bg-red-500/20 text-red-400 hover:bg-red-500/30">拒绝</button>`
            : ''
        ].filter(Boolean).join('');
        return `
        <tr class="table-row">
          <td class="py-3 px-3">
            <input type="checkbox" value="${{u.id}}" ${{selectedUsers.has(u.id) ? 'checked' : ''}} onchange="toggleUserSelection(${{u.id}}, this.checked)">
          </td>
          <td class="py-3 px-3">${{u.id}}</td>
          <td class="py-3 px-3 font-medium">${{username}}</td>
          <td class="py-3 px-3">${{email}}</td>
          <td class="py-3 px-3">Lv.${{u.trust_level}}</td>
          <td class="py-3 px-3">${{u.token_count}}</td>
          <td class="py-3 px-3">${{u.api_key_count}}</td>
          <td class="py-3 px-3">${{approvalBadge}}</td>
          <td class="py-3 px-3">${{u.is_banned ? '<span class="text-red-400">已封禁</span>' : '<span class="text-green-400">正常</span>'}}</td>
          <td class="py-3 px-3">${{u.created_at ? new Date(u.created_at).toLocaleString() : '-'}}</td>
          <td class="py-3 px-3">
            ${{u.is_banned
              ? `<button onclick="unbanUser(${{u.id}})" class="text-xs px-2 py-1 rounded bg-green-500/20 text-green-400 hover:bg-green-500/30">解封</button>`
              : `<button onclick="banUser(${{u.id}})" class="text-xs px-2 py-1 rounded bg-red-500/20 text-red-400 hover:bg-red-500/30">封禁</button>`
            }}
            ${{approvalActions}}
          </td>
        </tr>
      `;
      }}).join('');
      const allChecked = users.length > 0 && users.every(u => selectedUsers.has(u.id));
      document.getElementById('selectAllUsers').checked = allChecked;
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

    async function approveUser(userId) {{
      if (!confirm('确定要通过此用户吗？')) return;
      const fd = new FormData();
      fd.append('user_id', userId);
      await fetch('/admin/api/users/approve', {{ method: 'POST', body: fd }});
      refreshUsers();
    }}

    async function rejectUser(userId) {{
      if (!confirm('确定要拒绝此用户吗？')) return;
      const fd = new FormData();
      fd.append('user_id', userId);
      await fetch('/admin/api/users/reject', {{ method: 'POST', body: fd }});
      refreshUsers();
    }}

    function toggleSelectAllUsers(checked) {{
      const checkboxes = document.querySelectorAll('#usersTable input[type="checkbox"]');
      checkboxes.forEach(cb => {{
        cb.checked = checked;
        if (checked) selectedUsers.add(parseInt(cb.value, 10));
        else selectedUsers.delete(parseInt(cb.value, 10));
      }});
      updateBatchUserButtons();
    }}

    function toggleUserSelection(userId, checked) {{
      if (checked) selectedUsers.add(userId);
      else selectedUsers.delete(userId);
      updateBatchUserButtons();
      const allCheckboxes = document.querySelectorAll('#usersTable input[type="checkbox"]');
      const allChecked = allCheckboxes.length > 0 && Array.from(allCheckboxes).every(cb => cb.checked);
      document.getElementById('selectAllUsers').checked = allChecked;
    }}

    function updateBatchUserButtons() {{
      const banBtn = document.getElementById('batchBanUsersBtn');
      const unbanBtn = document.getElementById('batchUnbanUsersBtn');
      const approveBtn = document.getElementById('batchApproveUsersBtn');
      const rejectBtn = document.getElementById('batchRejectUsersBtn');
      const hasSelection = selectedUsers.size > 0;
      if (banBtn) banBtn.disabled = !hasSelection;
      if (unbanBtn) unbanBtn.disabled = !hasSelection;
      if (approveBtn) approveBtn.disabled = !hasSelection;
      if (rejectBtn) rejectBtn.disabled = !hasSelection;
    }}

    async function batchBanUsers() {{
      if (selectedUsers.size === 0) {{
        alert('请先选择要封禁的用户');
        return;
      }}
      if (!confirm(`确定要封禁选中的 ${{selectedUsers.size}} 个用户吗？`)) return;
      const promises = Array.from(selectedUsers).map(userId => {{
        const fd = new FormData();
        fd.append('user_id', userId);
        return fetch('/admin/api/users/ban', {{ method: 'POST', body: fd }});
      }});
      await Promise.all(promises);
      selectedUsers.clear();
      refreshUsers();
    }}

    async function batchUnbanUsers() {{
      if (selectedUsers.size === 0) {{
        alert('请先选择要解封的用户');
        return;
      }}
      if (!confirm(`确定要解封选中的 ${{selectedUsers.size}} 个用户吗？`)) return;
      const promises = Array.from(selectedUsers).map(userId => {{
        const fd = new FormData();
        fd.append('user_id', userId);
        return fetch('/admin/api/users/unban', {{ method: 'POST', body: fd }});
      }});
      await Promise.all(promises);
      selectedUsers.clear();
      refreshUsers();
    }}

    async function batchApproveUsers() {{
      if (selectedUsers.size === 0) {{
        alert('请先选择要通过的用户');
        return;
      }}
      if (!confirm(`确定要通过选中的 ${{selectedUsers.size}} 个用户吗？`)) return;
      const promises = Array.from(selectedUsers).map(userId => {{
        const fd = new FormData();
        fd.append('user_id', userId);
        return fetch('/admin/api/users/approve', {{ method: 'POST', body: fd }});
      }});
      await Promise.all(promises);
      selectedUsers.clear();
      refreshUsers();
    }}

    async function batchRejectUsers() {{
      if (selectedUsers.size === 0) {{
        alert('请先选择要拒绝的用户');
        return;
      }}
      if (!confirm(`确定要拒绝选中的 ${{selectedUsers.size}} 个用户吗？`)) return;
      const promises = Array.from(selectedUsers).map(userId => {{
        const fd = new FormData();
        fd.append('user_id', userId);
        return fetch('/admin/api/users/reject', {{ method: 'POST', body: fd }});
      }});
      await Promise.all(promises);
      selectedUsers.clear();
      refreshUsers();
    }}

    // 添加 Token 池数据和状态
    let allPoolTokens = [];
    let poolCurrentPage = 1;
    let poolSortField = 'id';
    let poolSortAsc = false;
    let selectedPoolTokens = new Set();
    let poolStatsData = {{}};

    async function refreshDonatedTokens() {{
      try {{
        const pageSize = parseInt(document.getElementById('poolPageSize').value);
        const search = document.getElementById('poolSearch').value.trim();
        const visibility = document.getElementById('poolVisibilityFilter').value;
        const status = document.getElementById('poolStatusFilter').value;
        const d = await fetchJson('/admin/api/donated-tokens' + buildQuery({{
          page: poolCurrentPage,
          page_size: pageSize,
          search,
          visibility,
          status,
          sort_field: poolSortField,
          sort_order: poolSortAsc ? 'asc' : 'desc'
        }}));
        poolStatsData = d;
        document.getElementById('poolTotalTokens').textContent = d.total || 0;
        document.getElementById('poolActiveTokens').textContent = d.active || 0;
        document.getElementById('poolPublicTokens').textContent = d.public || 0;
        document.getElementById('poolAvgSuccessRate').textContent =
          d.avg_success_rate === undefined || d.avg_success_rate === null ? '-' : formatSuccessRate(d.avg_success_rate, 1);
        allPoolTokens = (d.tokens || []).map(t => ({{
          ...t,
          success_rate: t.success_rate || 0,
          use_count: (t.success_count || 0) + (t.fail_count || 0)
        }}));
        const total = d.pagination?.total ?? allPoolTokens.length;
        const totalPages = Math.ceil(total / pageSize) || 1;
        if (totalPages > 0 && poolCurrentPage > totalPages) {{
          poolCurrentPage = totalPages;
          return refreshDonatedTokens();
        }}
        selectedPoolTokens.clear();
        document.getElementById('selectAllPool').checked = false;
        renderPoolTable(allPoolTokens);
        renderPoolPagination(total, pageSize, totalPages);
      }} catch (e) {{ console.error(e); }}
    }}

    function filterPoolTokens() {{
      poolCurrentPage = 1;
      refreshDonatedTokens();
    }}

    function applyPoolQuickFilter(type) {{
      const visibilityEl = document.getElementById('poolVisibilityFilter');
      const statusEl = document.getElementById('poolStatusFilter');
      if (!visibilityEl || !statusEl) return;
      if (type === 'active') {{
        visibilityEl.value = '';
        statusEl.value = 'active';
      }} else if (type === 'public') {{
        visibilityEl.value = 'public';
        statusEl.value = '';
      }} else {{
        visibilityEl.value = '';
        statusEl.value = '';
      }}
      poolCurrentPage = 1;
      refreshDonatedTokens();
    }}

    function sortPoolTokens(field) {{
      if (poolSortField === field) {{
        poolSortAsc = !poolSortAsc;
      }} else {{
        poolSortField = field;
        poolSortAsc = false;
      }}
      poolCurrentPage = 1;
      refreshDonatedTokens();
    }}

    function goPoolPage(page) {{
      poolCurrentPage = page;
      refreshDonatedTokens();
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
        tb.innerHTML = '<tr><td colspan="9" class="py-6 text-center" style="color: var(--text-muted);">暂无添加 Token</td></tr>';
        return;
      }}
      tb.innerHTML = tokens.map(t => {{
        const username = escapeHtml(t.username || '未知');
        return `
        <tr class="table-row">
          <td class="py-3 px-3">
            <input type="checkbox" value="${{t.id}}" ${{selectedPoolTokens.has(t.id) ? 'checked' : ''}} onchange="togglePoolSelection(${{t.id}}, this.checked)">
          </td>
          <td class="py-3 px-3">#${{t.id}}</td>
          <td class="py-3 px-3">${{username}}</td>
          <td class="py-3 px-3">${{t.visibility === 'public' ? '<span class="text-green-400">公开</span>' : '<span class="text-blue-400">私有</span>'}}</td>
          <td class="py-3 px-3">${{renderTokenStatus(t.status)}}</td>
          <td class="py-3 px-3">${{formatSuccessRate(t.success_rate, 1)}}</td>
          <td class="py-3 px-3">${{t.use_count}}</td>
          <td class="py-3 px-3">${{t.last_used ? new Date(t.last_used).toLocaleString() : '-'}}</td>
          <td class="py-3 px-3">
            <button onclick="toggleTokenVisibility(${{t.id}}, '${{t.visibility === 'public' ? 'private' : 'public'}}')" class="text-xs px-2 py-1 rounded bg-indigo-500/20 text-indigo-400 hover:bg-indigo-500/30 mr-1">切换</button>
            <button onclick="deleteDonatedToken(${{t.id}})" class="text-xs px-2 py-1 rounded bg-red-500/20 text-red-400 hover:bg-red-500/30">删除</button>
          </td>
        </tr>
      `;
      }}).join('');
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
    refreshAnnouncement();
    refreshProxyApiKey();
    loadDbInfo();
    resetDbImportState('请先上传并解析导出文件。');
    const dbImportFile = document.getElementById('dbImportFile');
    if (dbImportFile) {{
      dbImportFile.addEventListener('change', () => {{
        resetDbImportState('已选择新文件，请先解析。');
      }});
    }}
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
    from kiro_gateway.metrics import metrics

    self_use_enabled = metrics.is_self_use_enabled()
    body_self_use_attr = "true" if self_use_enabled else "false"

    display_name_raw = user.username or "用户"
    display_name = html.escape(display_name_raw)
    avatar_initial = html.escape(display_name_raw[0].upper() if display_name_raw else "👤")
    avatar_url = (user.avatar_url or "").strip()
    avatar_url_safe = ""
    if avatar_url.startswith(("http://", "https://")):
        avatar_url_safe = html.escape(avatar_url, quote=True)
    # Determine avatar display
    if avatar_url_safe:
        avatar_html = f'<img src="{avatar_url_safe}" class="w-16 h-16 rounded-full object-cover" alt="{display_name}">'
    else:
        avatar_html = f'<div class="w-16 h-16 rounded-full bg-indigo-500/20 flex items-center justify-center text-2xl">{avatar_initial}</div>'

    # Determine user info display based on login provider
    if user.github_id:
        user_info = '<span class="text-sm px-2 py-1 rounded bg-gray-700 text-white">GitHub 用户</span>'
    elif user.linuxdo_id:
        user_info = f'<span style="color: var(--text-muted);">信任等级: Lv.{user.trust_level}</span>'
    else:
        user_info = ''
    user_info_html = f'<div class="mt-1">{user_info}</div>' if user_info else ''

    page_template = '''<!DOCTYPE html>
<html lang="zh">
<head>__COMMON_HEAD__</head>
<body data-self-use="__BODY_SELF_USE_ATTR__">
  __COMMON_NAV__
  <main class="max-w-6xl mx-auto px-4 py-8">
    <div class="card mb-6 user-hero">
      <div class="flex flex-col sm:flex-row sm:items-center gap-4">
        __AVATAR_HTML__
        <div class="flex-1">
          <div class="flex items-center gap-2 flex-wrap">
            <h1 class="text-2xl font-bold">你好，__DISPLAY_NAME__</h1>
          </div>
          <p id="greetingText" class="text-sm" style="color: var(--text-muted);">欢迎回来，今天想先做什么？</p>
          __USER_INFO_HTML__
          <div class="flex flex-wrap gap-2 mt-3">
            <button type="button" onclick="showTab('tokens'); showTokenSubTab('mine'); showDonateModal();" class="btn-primary text-sm px-3 py-1.5">+ 添加 Token</button>
            <button type="button" onclick="showTab('keys'); generateKey();" class="text-sm px-3 py-1.5 rounded-lg" style="background: var(--bg-input); border: 1px solid var(--border);">生成 API Key</button>
            <a href="/playground" class="text-sm px-3 py-1.5 rounded-lg" style="background: var(--bg-input); border: 1px solid var(--border);">去测试</a>
          </div>
        </div>
        <div class="sm:ml-auto">
          <a href="/oauth2/logout" class="btn-primary">退出登录</a>
        </div>
      </div>
    </div>
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
      <div class="card text-center">
        <div class="text-3xl font-bold text-indigo-400" id="tokenCount">-</div>
        <div class="text-sm" style="color: var(--text-muted);">我的 Token</div>
      </div>
      <div class="card text-center public-only">
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
    <div id="userGuide" class="card mb-6">
      <div class="flex items-start gap-3">
        <div class="text-2xl">🧭</div>
        <div>
          <h2 id="guideTitle" class="font-bold">欢迎使用 KiroGate</h2>
          <p id="guideText" class="text-sm mt-1" style="color: var(--text-muted);">两步即可开始调用：先添加 Token，再生成 API Key。</p>
          <div id="guideActions" class="flex flex-wrap gap-2 mt-3">
            <button type="button" onclick="showTab('tokens'); showTokenSubTab('mine'); showDonateModal();" class="btn-primary text-sm px-3 py-1.5">添加 Token</button>
            <button type="button" onclick="showTab('keys'); generateKey();" class="text-sm px-3 py-1.5 rounded-lg" style="background: var(--bg-input); border: 1px solid var(--border);">生成 API Key</button>
            <a href="/docs" class="text-sm px-3 py-1.5 rounded-lg" style="background: var(--bg-input); border: 1px solid var(--border);">查看文档</a>
          </div>
        </div>
      </div>
    </div>
    <div class="card mb-6 self-use-only">
      <div class="flex items-start gap-3">
        <div class="text-2xl">🔒</div>
        <div>
          <h2 class="font-bold">已启用自用模式</h2>
          <p class="text-sm mt-1" style="color: var(--text-muted);">公开 Token 池与公开贡献已禁用，新用户注册已关闭。</p>
        </div>
      </div>
    </div>
    <div class="flex gap-2 mb-4 border-b" style="border-color: var(--border);">
      <button class="tab px-4 py-2 font-medium" onclick="showTab('tokens')" id="tab-tokens">🔑 Token 管理</button>
      <button class="tab px-4 py-2 font-medium" onclick="showTab('keys')" id="tab-keys">🗝️ API Keys</button>
    </div>
    <div id="panel-tokens" class="tab-panel">
      <div class="card">
        <!-- 可折叠的获取 Token 说明 -->
        <details class="mb-6 rounded-lg" style="background: linear-gradient(135deg, rgba(56, 189, 248, 0.12), rgba(34, 211, 238, 0.08)); border: 1px solid var(--primary);">
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
          <button onclick="showTokenSubTab('public')" id="subtab-public" class="subtab flex-1 px-4 py-2 rounded-md text-sm font-medium transition-all public-only">🌐 公开 Token 池</button>
        </div>

        <!-- 我的 Token 面板 -->
        <div id="subtab-panel-mine">
          <div class="flex flex-wrap items-center gap-3 mb-3 toolbar">
            <h2 class="text-lg font-bold">我的 Token</h2>
            <div class="flex-1 flex items-center gap-2 flex-wrap">
              <input type="text" id="tokensSearch" placeholder="搜索 ID 或状态..." oninput="filterTokens()" class="px-3 py-1.5 rounded-lg text-sm" style="background: var(--bg-input); border: 1px solid var(--border); min-width: 160px;">
              <select id="tokenVisibilityFilter" onchange="filterTokens()" class="px-3 py-1.5 rounded-lg text-sm" style="background: var(--bg-input); border: 1px solid var(--border);">
                <option value="">全部可见性</option>
                <option value="public" class="public-only">公开</option>
                <option value="private">私有</option>
              </select>
              <select id="tokenStatusFilter" onchange="filterTokens()" class="px-3 py-1.5 rounded-lg text-sm" style="background: var(--bg-input); border: 1px solid var(--border);">
                <option value="">全部状态</option>
                <option value="active">有效</option>
                <option value="invalid">无效</option>
                <option value="expired">已过期</option>
              </select>
              <select id="tokensPageSize" onchange="filterTokens()" class="px-3 py-1.5 rounded-lg text-sm" style="background: var(--bg-input); border: 1px solid var(--border);">
                <option value="10">10 条/页</option>
                <option value="20">20 条/页</option>
                <option value="50">50 条/页</option>
              </select>
              <button onclick="refreshTokens()" class="btn btn-primary text-sm px-3 py-1.5 rounded-lg" style="background: var(--primary); color: white;">刷新</button>
              <button onclick="batchDeleteTokens()" id="batchDeleteTokensBtn" class="btn btn-danger text-sm px-3 py-1.5 rounded-lg" style="background: #ef4444; color: white; display: none;">批量删除</button>
            </div>
            <button onclick="showDonateModal()" class="btn-primary">+ 添加 Token</button>
          </div>
          <div class="flex flex-wrap items-center gap-2 mb-4 text-xs">
            <span style="color: var(--text-muted);">可见性</span>
            <button type="button" class="filter-chip" data-group="visibility" data-value="" onclick="setTokenVisibility('')">全部</button>
            <button type="button" class="filter-chip public-only" data-group="visibility" data-value="public" onclick="setTokenVisibility('public')">公开</button>
            <button type="button" class="filter-chip" data-group="visibility" data-value="private" onclick="setTokenVisibility('private')">私有</button>
            <span class="ml-2" style="color: var(--text-muted);">状态</span>
            <button type="button" class="filter-chip" data-group="status" data-value="" onclick="setTokenStatus('')">全部</button>
            <button type="button" class="filter-chip" data-group="status" data-value="active" onclick="setTokenStatus('active')">有效</button>
            <button type="button" class="filter-chip" data-group="status" data-value="invalid" onclick="setTokenStatus('invalid')">无效</button>
            <button type="button" class="filter-chip" data-group="status" data-value="expired" onclick="setTokenStatus('expired')">已过期</button>
          </div>
          <div class="overflow-x-auto">
            <table class="w-full text-sm data-table">
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
                  <th class="text-left py-3 px-3">账号</th>
                  <th class="text-left py-3 px-3">额度</th>
                  <th class="text-left py-3 px-3">检测时间</th>
                  <th class="text-left py-3 px-3">操作</th>
                </tr>
              </thead>
              <tbody id="tokenTable">
                <tr><td colspan="10" class="py-6 text-center" style="color: var(--text-muted);">加载中...</td></tr>
              </tbody>
            </table>
          </div>
          <div id="tokensPagination" class="flex items-center justify-between mt-4 pt-4" style="border-top: 1px solid var(--border); display: none;">
            <span id="tokensInfo" class="text-sm" style="color: var(--text-muted);"></span>
            <div id="tokensPages" class="flex gap-1"></div>
          </div>
        </div>

        <!-- 公开 Token 池面板 -->
        <div id="subtab-panel-public" class="public-only" style="display: none;">
          <div class="flex flex-wrap items-center gap-3 mb-4 toolbar">
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
            <table class="w-full text-sm data-table">
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
          <p class="mt-4 text-sm public-only" style="color: var(--text-muted);">
            💡 公开 Token 池由社区成员自愿贡献，供所有用户共享使用。您也可以切换到"我的 Token"添加您的 Token。
          </p>
        </div>
      </div>
    </div>
    <div id="panel-keys" class="tab-panel" style="display: none;">
      <div class="card">
        <div class="flex flex-wrap justify-between items-center gap-4 mb-3 toolbar">
          <h2 class="text-lg font-bold">我的 API Keys</h2>
          <div class="flex items-center gap-2">
            <input type="text" id="keysSearch" placeholder="搜索 Key 或名称..." oninput="filterKeys()"
              class="px-3 py-2 rounded-lg text-sm w-40" style="background: var(--bg-input); border: 1px solid var(--border); color: var(--text);">
            <select id="keysActiveFilter" onchange="filterKeys()" class="px-3 py-2 rounded-lg text-sm" style="background: var(--bg-input); border: 1px solid var(--border); color: var(--text);">
              <option value="">全部状态</option>
              <option value="true">启用</option>
              <option value="false">停用</option>
            </select>
            <select id="keysPageSize" onchange="filterKeys()" class="px-3 py-2 rounded-lg text-sm" style="background: var(--bg-input); border: 1px solid var(--border); color: var(--text);">
              <option value="10" selected>10/页</option>
              <option value="20">20/页</option>
              <option value="50">50/页</option>
            </select>
            <button onclick="refreshKeys()" class="btn btn-primary text-sm">刷新</button>
            <button onclick="generateKey()" class="btn-primary text-sm">+ 生成新 Key</button>
          </div>
        </div>
        <div class="flex flex-wrap items-center gap-2 mb-4 text-xs">
          <span style="color: var(--text-muted);">状态</span>
          <button type="button" class="filter-chip" data-group="keys-active" data-value="" onclick="setKeysActive('')">全部</button>
          <button type="button" class="filter-chip" data-group="keys-active" data-value="true" onclick="setKeysActive('true')">启用</button>
          <button type="button" class="filter-chip" data-group="keys-active" data-value="false" onclick="setKeysActive('false')">停用</button>
        </div>
        <div class="overflow-x-auto">
            <table class="w-full text-sm data-table">
              <thead>
                <tr style="color: var(--text-muted); border-bottom: 1px solid var(--border);">
                  <th class="text-left py-3 px-3">
                    <input type="checkbox" id="selectAllKeys" onchange="toggleSelectAllKeys()" style="cursor: pointer;">
                  </th>
                  <th class="text-left py-3 px-3 cursor-pointer hover:text-indigo-400" onclick="sortKeys('key_prefix')">Key ↕</th>
                  <th class="text-left py-3 px-3 cursor-pointer hover:text-indigo-400" onclick="sortKeys('name')">名称 ↕</th>
                  <th class="text-left py-3 px-3 cursor-pointer hover:text-indigo-400" onclick="sortKeys('is_active')">状态 ↕</th>
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
            <button onclick="batchSetKeysActive(true)" class="text-xs px-3 py-1.5 rounded bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/30" id="batchEnableKeysBtn" style="display: none;">批量启用</button>
            <button onclick="batchSetKeysActive(false)" class="text-xs px-3 py-1.5 rounded bg-amber-500/20 text-amber-400 hover:bg-amber-500/30" id="batchDisableKeysBtn" style="display: none;">批量停用</button>
            <button onclick="batchDeleteKeys()" class="text-xs px-3 py-1.5 rounded bg-red-500/20 text-red-400 hover:bg-red-500/30" id="batchDeleteKeysBtn" style="display: none;">批量删除</button>
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
      <h3 class="text-lg font-bold mb-4">🎁 批量添加 Refresh Token</h3>

      <!-- 认证类型选择 -->
      <div class="mb-3">
        <label class="text-sm font-medium mb-2 block">🔐 认证类型</label>
        <div class="flex gap-2">
          <button onclick="setAuthType('social')" id="authType-social" class="auth-type-btn flex-1 px-4 py-2 rounded-lg text-sm font-medium transition-all" style="background: var(--primary); color: white; border: 1px solid var(--primary);">
            Social (默认)
          </button>
          <button onclick="setAuthType('idc')" id="authType-idc" class="auth-type-btn flex-1 px-4 py-2 rounded-lg text-sm font-medium transition-all" style="background: var(--bg-input); border: 1px solid var(--border);">
            IDC (Builder ID)
          </button>
        </div>
        <p class="text-xs mt-1" style="color: var(--text-muted);">💡 Social: Kiro 桌面端登录 | IDC: AWS Builder ID 登录</p>
      </div>

      <input type="hidden" id="donateAuthType" value="social">

      <!-- Token 输入区域 -->
      <div class="mb-3">
        <label class="text-sm font-medium mb-2 block">📝 粘贴 Token</label>
        <textarea id="donateTokens" class="w-full h-32 p-3 rounded-lg text-sm" style="background: var(--bg-input); border: 1px solid var(--border);" placeholder="支持以下格式：&#10;• 每行一个 Token&#10;• 逗号分隔：token1, token2, token3&#10;• 混合格式"></textarea>
        <p class="text-xs mt-1" style="color: var(--text-muted);">💡 支持多行或逗号分隔，自动去除空行和重复项</p>
      </div>

      <!-- IDC 额外字段（仅 IDC 模式显示） -->
      <div id="idcFields" class="mb-3 p-3 rounded-lg" style="background: var(--bg-input); border: 1px solid var(--border); display: none;">
        <p class="text-sm font-medium mb-2">🆔 IDC 认证信息</p>
        <div class="mb-2">
          <input type="text" id="donateClientId" class="w-full px-3 py-2 rounded-lg text-sm" style="background: var(--bg-card); border: 1px solid var(--border);" placeholder="Client ID">
        </div>
        <div>
          <input type="password" id="donateClientSecret" class="w-full px-3 py-2 rounded-lg text-sm" style="background: var(--bg-card); border: 1px solid var(--border);" placeholder="Client Secret">
        </div>
        <p class="text-xs mt-2" style="color: var(--text-muted);">可选：填写后将覆盖导入文件中的 Client ID/Secret；留空则使用每条 Token 自带凭证。</p>
      </div>

      <!-- 文件上传 -->
      <div class="mb-4">
        <label class="text-sm font-medium mb-2 block">📁 或上传 JSON 文件</label>
        <input id="donateFile" type="file" accept=".json" class="w-full text-sm p-2 rounded-lg" style="background: var(--bg-input); border: 1px solid var(--border);">
        <p class="text-xs mt-1" style="color: var(--text-muted);">支持 Kiro Account Manager 导出的 JSON 文件（自动识别 IDC 凭证）</p>
      </div>

      <!-- 可见性选择 -->
      <div class="mb-3">
        <label class="text-sm font-medium mb-2 block">🔒 可见性设置</label>
        <div class="flex gap-2">
          <button onclick="setDonateMode('private')" id="donateMode-private" class="donate-mode-btn flex-1 px-4 py-2 rounded-lg text-sm font-medium transition-all" style="background: var(--bg-input); border: 1px solid var(--border);">
            🔐 私有
          </button>
          <button onclick="setDonateMode('public')" id="donateMode-public" class="donate-mode-btn flex-1 px-4 py-2 rounded-lg text-sm font-medium transition-all public-only" style="background: var(--bg-input); border: 1px solid var(--border);">
            🌐 公开
          </button>
        </div>
      </div>

      <!-- 匿名选项（仅公开模式显示） -->
      <div id="anonymousOption" class="mb-4 p-3 rounded-lg public-only" style="background: var(--bg-input); border: 1px solid var(--border); display: none;">
        <label class="flex items-center gap-2 cursor-pointer">
          <input type="checkbox" id="donateAnonymous" class="w-4 h-4 rounded">
          <div class="text-sm">
            <span class="font-medium">匿名贡献</span>
            <p class="text-xs mt-0.5" style="color: var(--text-muted);">不显示您的用户名</p>
          </div>
        </label>
      </div>

      <input type="hidden" id="donateVisibility" value="private">

      <div class="flex justify-end gap-2 mt-4">
        <button onclick="hideDonateModal()" class="px-4 py-2 rounded-lg" style="background: var(--bg-input);">取消</button>
        <button onclick="submitTokens()" class="btn-primary">提交并导入</button>
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
  <!-- 账号信息弹窗 -->
  <div id="accountInfoModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" style="display: none;">
    <div class="card w-full max-w-md mx-4">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-bold">📊 账号信息</h3>
        <button onclick="hideAccountInfoModal()" class="text-2xl leading-none" style="color: var(--text-muted);">&times;</button>
      </div>
      <div id="accountInfoContent">
        <div class="text-center py-8" style="color: var(--text-muted);">
          <div class="animate-spin inline-block w-6 h-6 border-2 border-current border-t-transparent rounded-full mb-2"></div>
          <p>加载中...</p>
        </div>
      </div>
      <div class="flex justify-end mt-4">
        <button onclick="hideAccountInfoModal()" class="btn-primary px-4 py-2">关闭</button>
      </div>
    </div>
  </div>
  __COMMON_FOOTER__
  <style>
    .user-hero {{
      border: 1px solid rgba(56, 189, 248, 0.25);
      background: linear-gradient(135deg, rgba(56, 189, 248, 0.12), rgba(34, 211, 238, 0.08));
      position: relative;
      overflow: hidden;
    }}
    .user-hero::after {{
      content: '';
      position: absolute;
      inset: 0;
      background: radial-gradient(circle at 85% 10%, rgba(163, 230, 53, 0.18), transparent 45%);
      opacity: 0.6;
      pointer-events: none;
    }}
    .kpi-grid .card {{
      position: relative;
      overflow: hidden;
    }}
    .kpi-grid .card::after {{
      content: '';
      position: absolute;
      top: -40%;
      right: -30%;
      width: 120px;
      height: 120px;
      background: radial-gradient(circle, rgba(56, 189, 248, 0.25), transparent 60%);
      opacity: 0.6;
      pointer-events: none;
    }}
    .tab {{
      color: var(--text-muted);
      border-bottom: 2px solid transparent;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      font-size: 0.85rem;
    }}
    .tab.active {{
      color: var(--primary);
      border-bottom-color: var(--primary);
      text-shadow: 0 0 14px rgba(56, 189, 248, 0.45);
    }}
    .table-row:hover {{ background: var(--bg-hover); }}
    .subtab {{ color: var(--text-muted); }}
    .subtab.active {{
      background: linear-gradient(135deg, var(--primary), var(--accent));
      color: white;
      box-shadow: 0 12px 24px rgba(56, 189, 248, 0.25);
    }}
    .donate-mode-btn {{ color: var(--text-muted); }}
    .donate-mode-btn.active {{
      background: linear-gradient(135deg, var(--primary), var(--accent));
      color: white;
    }}
    .filter-chip {{
      border: 1px solid var(--border);
      border-radius: 999px;
      padding: 0.25rem 0.7rem;
      background: rgba(15, 23, 42, 0.04);
      color: var(--text-muted);
      transition: all 0.2s ease;
      backdrop-filter: blur(10px);
    }}
    [data-theme="dark"] .filter-chip {{
      background: rgba(15, 23, 42, 0.4);
    }}
    .filter-chip:hover {{ color: var(--text); border-color: var(--border-dark); }}
    .filter-chip.active {{
      background: linear-gradient(135deg, var(--primary), var(--accent));
      color: white;
      border-color: transparent;
      box-shadow: 0 10px 22px rgba(56, 189, 248, 0.25);
    }}
    details[open] .details-arrow {{ transform: rotate(180deg); }}
  </style>
  <script>
    let currentTab = 'tokens';
    let confirmCallback = null;
    let keyNameCallback = null;
    let userHasTokens = false;
    const SELF_USE_MODE = __SELF_USE_MODE__;

    // Token 表格状态
    let allTokens = [];
    let tokensCurrentPage = 1;
    let tokensSortField = 'id';
    let tokensSortAsc = false;
    let selectedTokenIds = new Set();

    function buildQuery(params) {{
      const qs = new URLSearchParams();
      Object.entries(params).forEach(([key, value]) => {{
        if (value === undefined || value === null || value === '') return;
        qs.append(key, String(value));
      }});
      const str = qs.toString();
      return str ? `?${{str}}` : '';
    }}

    async function fetchJson(url, options = {{}}) {{
      const r = await fetch(url, options);
      const text = await r.text();
      let data = {{}};
      try {{ data = text ? JSON.parse(text) : {{}}; }} catch (e) {{ data = {{}}; }}
      if (!r.ok) throw data;
      return data;
    }}

    function renderTokenStatus(status) {{
      if (status === 'active') return '<span class="text-green-400">有效</span>';
      if (status === 'invalid') return '<span class="text-red-400">无效</span>';
      if (status === 'expired') return '<span class="text-red-400">已过期</span>';
      return `<span class="text-red-400">${{status || '-'}}</span>`;
    }}

    function normalizeSuccessRate(rate) {{
      const value = Number(rate);
      if (!Number.isFinite(value)) return null;
      return value <= 1 ? value * 100 : value;
    }}

    function formatSuccessRate(rate, digits = 1) {{
      const percent = normalizeSuccessRate(rate);
      if (percent === null) return '-';
      return percent.toFixed(digits) + '%';
    }}

    function applySelfUseMode() {{
      if (!SELF_USE_MODE) return;
      const publicOption = document.querySelector('#tokenVisibilityFilter option[value="public"]');
      if (publicOption) publicOption.remove();
      const visibilityFilter = document.getElementById('tokenVisibilityFilter');
      if (visibilityFilter && visibilityFilter.value === 'public') visibilityFilter.value = '';
    }}

    function setTokenVisibility(value) {{
      const select = document.getElementById('tokenVisibilityFilter');
      if (!select) return;
      select.value = value;
      updateTokenChips();
      filterTokens();
    }}

    function setTokenStatus(value) {{
      const select = document.getElementById('tokenStatusFilter');
      if (!select) return;
      select.value = value;
      updateTokenChips();
      filterTokens();
    }}

    function updateTokenChips() {{
      const visibility = document.getElementById('tokenVisibilityFilter')?.value ?? '';
      const status = document.getElementById('tokenStatusFilter')?.value ?? '';
      document.querySelectorAll('.filter-chip[data-group="visibility"]').forEach(chip => {{
        chip.classList.toggle('active', chip.dataset.value === visibility);
      }});
      document.querySelectorAll('.filter-chip[data-group="status"]').forEach(chip => {{
        chip.classList.toggle('active', chip.dataset.value === status);
      }});
    }}

    function setKeysActive(value) {{
      const select = document.getElementById('keysActiveFilter');
      if (!select) return;
      select.value = value;
      updateKeysChips();
      filterKeys();
    }}

    function updateKeysChips() {{
      const activeValue = document.getElementById('keysActiveFilter')?.value ?? '';
      document.querySelectorAll('.filter-chip[data-group="keys-active"]').forEach(chip => {{
        chip.classList.toggle('active', chip.dataset.value === activeValue);
      }});
    }}

    function setGreeting() {{
      const el = document.getElementById('greetingText');
      if (!el) return;
      const hour = new Date().getHours();
      let text = '你好，今天想先做什么？';
      if (hour < 6) text = '夜深了，注意休息，想先做点什么？';
      else if (hour < 12) text = '早上好，今天想先做什么？';
      else if (hour < 18) text = '下午好，今天想先做什么？';
      else text = '晚上好，今天想先做什么？';
      el.textContent = text;
    }}

    function updateUserGuide(profile) {{
      const tokenCount = profile.token_count || 0;
      const keyCount = profile.api_key_count || 0;
      const guideTitle = document.getElementById('guideTitle');
      const guideText = document.getElementById('guideText');
      const guideActions = document.getElementById('guideActions');
      if (!guideTitle || !guideText || !guideActions) return;

      if (tokenCount === 0 && keyCount === 0) {{
        guideTitle.textContent = '新手引导：两步就绪';
        guideText.textContent = '先添加 Refresh Token，再生成 API Key，即可开始调用。';
        guideActions.innerHTML = `
          <button type="button" onclick="showTab('tokens'); showTokenSubTab('mine'); showDonateModal();" class="btn-primary text-sm px-3 py-1.5">添加 Token</button>
          <button type="button" onclick="showTab('keys'); generateKey();" class="text-sm px-3 py-1.5 rounded-lg" style="background: var(--bg-input); border: 1px solid var(--border);">生成 API Key</button>
          <a href="/docs" class="text-sm px-3 py-1.5 rounded-lg" style="background: var(--bg-input); border: 1px solid var(--border);">查看文档</a>
        `;
        return;
      }}

      if (tokenCount === 0) {{
        guideTitle.textContent = SELF_USE_MODE ? '自用模式需先添加 Token' : '补充 Token 获取更稳定体验';
        guideText.textContent = SELF_USE_MODE
          ? '自用模式下必须添加私有 Token 才能生成 API Key。'
          : '当前 API Key 将使用公开 Token 池，建议添加自己的 Token。';
        guideActions.innerHTML = `
          <button type="button" onclick="showTab('tokens'); showTokenSubTab('mine'); showDonateModal();" class="btn-primary text-sm px-3 py-1.5">添加 Token</button>
          ${{SELF_USE_MODE ? '' : '<button type="button" onclick="showTab(\\'tokens\\'); showTokenSubTab(\\'public\\');" class="text-sm px-3 py-1.5 rounded-lg public-only" style="background: var(--bg-input); border: 1px solid var(--border);">查看公开 Token 池</button>'}}
        `;
        return;
      }}

      if (keyCount === 0) {{
        guideTitle.textContent = '只差一步：生成 API Key';
        guideText.textContent = '你已经添加 Token，生成 Key 后即可调用接口。';
        guideActions.innerHTML = `
          <button type="button" onclick="showTab('keys'); generateKey();" class="btn-primary text-sm px-3 py-1.5">生成 API Key</button>
          <a href="/playground" class="text-sm px-3 py-1.5 rounded-lg" style="background: var(--bg-input); border: 1px solid var(--border);">去测试</a>
        `;
        return;
      }}

      guideTitle.textContent = '准备就绪';
      guideText.textContent = '你已具备调用条件，可以开始测试或继续管理 Token。';
      guideActions.innerHTML = `
        <a href="/playground" class="btn-primary text-sm px-3 py-1.5">去测试</a>
        <button type="button" onclick="showTab('tokens'); showTokenSubTab('mine');" class="text-sm px-3 py-1.5 rounded-lg" style="background: var(--bg-input); border: 1px solid var(--border);">管理 Token</button>
        <a href="/docs" class="text-sm px-3 py-1.5 rounded-lg" style="background: var(--bg-input); border: 1px solid var(--border);">查看文档</a>
      `;
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
        updateUserGuide(d);
      }} catch (e) {{ console.error(e); }}
    }}

    async function loadTokens() {{
      try {{
        const pageSize = parseInt(document.getElementById('tokensPageSize').value);
        const search = document.getElementById('tokensSearch').value.trim();
        const visibility = document.getElementById('tokenVisibilityFilter').value;
        const status = document.getElementById('tokenStatusFilter').value;
        const d = await fetchJson('/user/api/tokens' + buildQuery({{
          page: tokensCurrentPage,
          page_size: pageSize,
          search,
          visibility,
          status,
          sort_field: tokensSortField,
          sort_order: tokensSortAsc ? 'asc' : 'desc'
        }}));
        allTokens = d.tokens || [];
        const total = d.pagination?.total ?? allTokens.length;
        const totalPages = Math.ceil(total / pageSize) || 1;
        if (totalPages > 0 && tokensCurrentPage > totalPages) {{
          tokensCurrentPage = totalPages;
          return loadTokens();
        }}
        selectedTokenIds.clear();
        renderTokenTable(allTokens);
        renderTokensPagination(total, pageSize, totalPages);
        updateBatchDeleteTokenBtn();
        updateTokenChips();
      }} catch (e) {{ console.error(e); }}
    }}

    async function refreshTokens() {{
      await loadTokens();
    }}

    function filterTokens() {{
      tokensCurrentPage = 1;
      updateTokenChips();
      loadTokens();
    }}

    function sortTokens(field) {{
      if (tokensSortField === field) {{
        tokensSortAsc = !tokensSortAsc;
      }} else {{
        tokensSortField = field;
        tokensSortAsc = true;
      }}
      tokensCurrentPage = 1;
      loadTokens();
    }}

    function goTokensPage(page) {{
      tokensCurrentPage = page;
      loadTokens();
    }}

    function renderTokenTable(tokens) {{
      const tb = document.getElementById('tokenTable');
      if (!tokens || !tokens.length) {{
        tb.innerHTML = '<tr><td colspan="10" class="py-8 text-center" style="color: var(--text-muted);"><div class="mb-3">还没有 Token，先添加一个吧</div><button type="button" onclick="showDonateModal()" class="btn-primary text-sm px-3 py-1.5">+ 添加 Token</button></td></tr>';
        document.getElementById('tokensPagination').style.display = 'none';
        document.getElementById('selectAllTokens').checked = false;
        return;
      }}
      tb.innerHTML = tokens.map(t => {{
        const canToggle = !SELF_USE_MODE || t.visibility === 'public';
        const toggleTarget = t.visibility === 'public' ? 'private' : 'public';
        const toggleLabel = SELF_USE_MODE ? '设为私有' : '切换';
        const toggleBtn = canToggle
          ? `<button onclick="toggleVisibility(${{t.id}}, '${{toggleTarget}}')" class="text-xs px-2 py-1 rounded bg-indigo-500/20 text-indigo-400 mr-1">${{toggleLabel}}</button>`
          : '';
        // 账号信息显示
        const acctStatus = t.account_status;
        const acctStatusHtml = acctStatus
          ? (acctStatus === 'Active' ? '<span class="text-green-400">正常</span>' : '<span class="text-red-400">封禁</span>')
          : '<span style="color: var(--text-muted);">-</span>';
        const acctUsage = (t.account_usage !== null && t.account_limit !== null)
          ? `${{t.account_usage.toFixed(1)}}/${{t.account_limit.toFixed(1)}}`
          : '-';
        const acctChecked = t.account_checked_at
          ? new Date(t.account_checked_at * 1000).toLocaleString()
          : '-';
        return `
          <tr class="table-row">
            <td class="py-3 px-3">
              <input type="checkbox" class="token-checkbox" data-token-id="${{t.id}}" onchange="toggleTokenSelection(${{t.id}}, this.checked)" ${{selectedTokenIds.has(t.id) ? 'checked' : ''}} style="cursor: pointer;">
            </td>
            <td class="py-3 px-3">#${{t.id}}</td>
            <td class="py-3 px-3"><span class="${{t.visibility === 'public' ? 'text-green-400' : 'text-blue-400'}}">${{t.visibility === 'public' ? '公开' : '私有'}}</span></td>
            <td class="py-3 px-3">${{renderTokenStatus(t.status)}}</td>
            <td class="py-3 px-3">${{formatSuccessRate(t.success_rate)}}</td>
            <td class="py-3 px-3">${{t.last_used ? new Date(t.last_used).toLocaleString() : '-'}}</td>
            <td class="py-3 px-3">${{acctStatusHtml}}</td>
            <td class="py-3 px-3" style="color: var(--text-muted);">${{acctUsage}}</td>
            <td class="py-3 px-3" style="color: var(--text-muted); font-size: 0.75rem;">${{acctChecked}}</td>
            <td class="py-3 px-3">
              <button onclick="showTokenAccountInfo(${{t.id}})" class="text-xs px-2 py-1 rounded bg-cyan-500/20 text-cyan-400 mr-1">账户详情</button>
              ${{toggleBtn}}
              <button onclick="deleteToken(${{t.id}})" class="text-xs px-2 py-1 rounded bg-red-500/20 text-red-400">删除</button>
            </td>
          </tr>
        `;
      }}).join('');

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
      const btn = document.getElementById('batchDeleteTokensBtn');
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
        const pageSize = parseInt(document.getElementById('keysPageSize').value);
        const search = document.getElementById('keysSearch').value.trim();
        const activeValue = document.getElementById('keysActiveFilter').value;
        const isActive = activeValue === 'true' ? true : activeValue === 'false' ? false : undefined;
        const d = await fetchJson('/user/api/keys' + buildQuery({{
          page: keysCurrentPage,
          page_size: pageSize,
          search,
          is_active: isActive,
          sort_field: keysSortField,
          sort_order: keysSortAsc ? 'asc' : 'desc'
        }}));
        allKeys = d.keys || [];
        const total = d.pagination?.total ?? allKeys.length;
        const totalPages = Math.ceil(total / pageSize) || 1;
        if (totalPages > 0 && keysCurrentPage > totalPages) {{
          keysCurrentPage = totalPages;
          return loadKeys();
        }}
        selectedKeys.clear();
        renderKeysTable(allKeys);
        renderKeysPagination(total, pageSize, totalPages);
        updateBatchDeleteUI();
        updateSelectAllCheckbox();
        updateKeysChips();
      }} catch (e) {{ console.error(e); }}
    }}

    async function refreshKeys() {{
      await loadKeys();
    }}

    function filterKeys() {{
      keysCurrentPage = 1;
      updateKeysChips();
      loadKeys();
    }}

    function sortKeys(field) {{
      if (keysSortField === field) {{
        keysSortAsc = !keysSortAsc;
      }} else {{
        keysSortField = field;
        keysSortAsc = true;
      }}
      keysCurrentPage = 1;
      loadKeys();
    }}

    function goKeysPage(page) {{
      keysCurrentPage = page;
      loadKeys();
    }}

    function renderKeysTable(keys) {{
      const tb = document.getElementById('keyTable');
      if (!keys || !keys.length) {{
        tb.innerHTML = '<tr><td colspan="8" class="py-8 text-center" style="color: var(--text-muted);"><div class="mb-3">还没有 API Key，生成一个开始使用吧</div><button type="button" onclick="generateKey()" class="btn-primary text-sm px-3 py-1.5">+ 生成 API Key</button></td></tr>';
        document.getElementById('keysPagination').style.display = 'none';
        return;
      }}
      tb.innerHTML = keys.map(k => {{
        const keyPrefix = escapeHtml(k.key_prefix || '');
        const name = escapeHtml(k.name || '-');
        const nameTitle = escapeHtml(k.name || '');
        const isActive = Boolean(k.is_active);
        const statusBadge = isActive
          ? '<span class="text-green-400">启用</span>'
          : '<span class="text-gray-400">停用</span>';
        const nextActive = isActive ? 'false' : 'true';
        const toggleLabel = isActive ? '停用' : '启用';
        const toggleClass = isActive
          ? 'bg-amber-500/20 text-amber-400 hover:bg-amber-500/30'
          : 'bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/30';
        return `
        <tr class="table-row">
          <td class="py-3 px-3">
            <input type="checkbox" class="key-checkbox" data-key-id="${{k.id}}" onchange="toggleKeySelection(${{k.id}}, this.checked)" ${{selectedKeys.has(k.id) ? 'checked' : ''}} style="cursor: pointer;">
          </td>
          <td class="py-3 px-3 font-mono">${{keyPrefix}}</td>
          <td class="py-3 px-3">
            <span title="${{nameTitle}}" style="display: inline-block; max-width: 120px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; vertical-align: middle;">${{name}}</span>
          </td>
          <td class="py-3 px-3">${{statusBadge}}</td>
          <td class="py-3 px-3">${{k.request_count}}</td>
          <td class="py-3 px-3">${{k.last_used ? new Date(k.last_used).toLocaleString() : '-'}}</td>
          <td class="py-3 px-3">${{k.created_at ? new Date(k.created_at).toLocaleString() : '-'}}</td>
          <td class="py-3 px-3">
            <button onclick="setKeyActive(${{k.id}}, ${{nextActive}})" class="text-xs px-2 py-1 rounded ${{toggleClass}} mr-1">${{toggleLabel}}</button>
            <button onclick="deleteKey(${{k.id}})" class="text-xs px-2 py-1 rounded bg-red-500/20 text-red-400 hover:bg-red-500/30">删除</button>
          </td>
        </tr>
      `;
      }}).join('');
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
      const btn = document.getElementById('batchDeleteKeysBtn');
      const enableBtn = document.getElementById('batchEnableKeysBtn');
      const disableBtn = document.getElementById('batchDisableKeysBtn');
      const countSpan = document.getElementById('selectedKeysCount');
      if (count > 0) {{
        btn.style.display = 'inline-block';
        if (enableBtn) enableBtn.style.display = 'inline-block';
        if (disableBtn) disableBtn.style.display = 'inline-block';
        countSpan.style.display = 'inline';
        countSpan.textContent = `已选择 ${{count}} 个`;
      }} else {{
        btn.style.display = 'none';
        if (enableBtn) enableBtn.style.display = 'none';
        if (disableBtn) disableBtn.style.display = 'none';
        countSpan.style.display = 'none';
      }}
    }}

    async function setKeyActive(keyId, isActive) {{
      const fd = new FormData();
      fd.append('is_active', isActive ? 'true' : 'false');
      try {{
        await fetchJson('/user/api/keys/' + keyId, {{ method: 'PUT', body: fd }});
        loadKeys();
        loadProfile();
      }} catch (e) {{
        showConfirmModal({{
          title: '失败',
          message: e.error || e.message || '更新失败，请稍后重试',
          icon: '❌',
          confirmText: '好的',
          danger: false
        }});
      }}
    }}

    async function batchSetKeysActive(isActive) {{
      if (selectedKeys.size === 0) return;
      const actionLabel = isActive ? '启用' : '停用';
      const confirmed = await showConfirmModal({{
        title: `批量${{actionLabel}} API Keys`,
        message: `确定要${{actionLabel}}选中的 ${{selectedKeys.size}} 个 API Key 吗？`,
        icon: isActive ? '✅' : '⏸️',
        confirmText: actionLabel,
        danger: !isActive
      }});
      if (!confirmed) return;

      const promises = Array.from(selectedKeys).map(keyId => {{
        const fd = new FormData();
        fd.append('is_active', isActive ? 'true' : 'false');
        return fetch('/user/api/keys/' + keyId, {{ method: 'PUT', body: fd }});
      }});
      await Promise.all(promises);
      selectedKeys.clear();
      loadKeys();
      loadProfile();
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

    function showDonateModal() {{
      document.getElementById('donateModal').style.display = 'flex';
      if (SELF_USE_MODE) setDonateMode('private');
      setAuthType('social'); // 重置为默认认证类型
    }}

    function hideDonateModal() {{
      document.getElementById('donateModal').style.display = 'none';
      setDonateMode('private');
      setAuthType('social');
      document.getElementById('donateTokens').value = '';
      document.getElementById('donateFile').value = '';
      document.getElementById('donateAnonymous').checked = false;
      document.getElementById('donateClientId').value = '';
      document.getElementById('donateClientSecret').value = '';
    }}

    function setAuthType(type) {{
      const socialBtn = document.getElementById('authType-social');
      const idcBtn = document.getElementById('authType-idc');
      const idcFields = document.getElementById('idcFields');

      if (type === 'idc') {{
        socialBtn.style.background = 'var(--bg-input)';
        socialBtn.style.color = 'var(--text)';
        socialBtn.style.border = '1px solid var(--border)';
        idcBtn.style.background = 'var(--primary)';
        idcBtn.style.color = 'white';
        idcBtn.style.border = '1px solid var(--primary)';
        idcFields.style.display = 'block';
      }} else {{
        socialBtn.style.background = 'var(--primary)';
        socialBtn.style.color = 'white';
        socialBtn.style.border = '1px solid var(--primary)';
        idcBtn.style.background = 'var(--bg-input)';
        idcBtn.style.color = 'var(--text)';
        idcBtn.style.border = '1px solid var(--border)';
        idcFields.style.display = 'none';
      }}
      document.getElementById('donateAuthType').value = type;
    }}

    function setDonateMode(mode) {{
      if (SELF_USE_MODE && mode === 'public') mode = 'private';
      const privateBtn = document.getElementById('donateMode-private');
      const publicBtn = document.getElementById('donateMode-public');
      const anonOption = document.getElementById('anonymousOption');

      if (mode === 'private') {{
        privateBtn.classList.add('active');
        if (publicBtn) publicBtn.classList.remove('active');
        anonOption.style.display = 'none';
      }} else {{
        privateBtn.classList.remove('active');
        if (publicBtn) publicBtn.classList.add('active');
        anonOption.style.display = 'block';
      }}
      document.getElementById('donateVisibility').value = mode;
    }}

    function showKeyModal(key, usePublicPool) {{
      document.getElementById('generatedKey').textContent = key;
      document.getElementById('copyStatus').style.display = 'none';
      const infoEl = document.getElementById('tokenSourceInfo');
      if (usePublicPool && !SELF_USE_MODE) {{
        infoEl.innerHTML = '💡 <strong>提示：</strong>您尚未添加 Token，此 Key 将使用公开 Token 池。添加自己的 Token 可获得更稳定的服务。';
        infoEl.style.display = 'block';
        infoEl.style.background = 'rgba(245, 158, 11, 0.15)';
        infoEl.style.color = '#f59e0b';
      }} else {{
        infoEl.innerHTML = '✅ <strong>提示：</strong>此 Key 将优先使用您添加的私有 Token。';
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

    async function submitTokens() {{
      // 获取输入
      const tokensText = document.getElementById('donateTokens').value.trim();
      const fileInput = document.getElementById('donateFile');
      const file = fileInput?.files?.[0] || null;

      // 验证至少有一个输入
      if (!tokensText && !file) {{
        return showConfirmModal({{
          title: '提示',
          message: '请粘贴 Token 或上传 JSON 文件',
          icon: '💡',
          confirmText: '好的',
          danger: false
        }});
      }}

      // 获取设置
      const visibility = document.getElementById('donateVisibility').value;
      if (SELF_USE_MODE && visibility === 'public') {{
        return showConfirmModal({{
          title: '提示',
          message: '自用模式下禁止公开 Token，请选择个人使用。',
          icon: '🔒',
          confirmText: '好的',
          danger: false
        }});
      }}
      const anonymous = document.getElementById('donateAnonymous').checked;

      // 构建请求
      const fd = new FormData();
      if (file) {{
        fd.append('file', file);
      }} else {{
        fd.append('tokens_text', tokensText);
      }}
      fd.append('visibility', visibility);
      if (visibility === 'public' && anonymous) fd.append('anonymous', 'true');

      // 添加 IDC 认证参数
      const authType = document.getElementById('donateAuthType').value;
      fd.append('auth_type', authType);
      if (authType === 'idc') {{
        const clientId = document.getElementById('donateClientId').value.trim();
        const clientSecret = document.getElementById('donateClientSecret').value.trim();
        // 检查 JSON 中是否包含 client_id/client_secret（支持文本输入和文件上传）
        let jsonHasClientInfo = false;
        const hasClientInfoDeep = (obj) => {{
          if (!obj || typeof obj !== 'object') return false;
          if (Array.isArray(obj)) return obj.some(hasClientInfoDeep);
          const topLevelPair = (obj.client_id || obj.clientId) && (obj.client_secret || obj.clientSecret);
          const creds = obj.credentials || obj.credentials_kiro_rs || {{}};
          const nestedPair = (creds.client_id || creds.clientId) && (creds.client_secret || creds.clientSecret);
          if (topLevelPair || nestedPair) return true;
          return Object.values(obj).some(hasClientInfoDeep);
        }};
        const detectJsonClientInfo = (text) => {{
          if (!text) return false;
          try {{
            const parsed = JSON.parse(text);
            return hasClientInfoDeep(parsed);
          }} catch (e) {{
            return false;
          }}
        }};
        if (tokensText) {{
          jsonHasClientInfo = detectJsonClientInfo(tokensText);
        }} else if (file) {{
          try {{
            const fileText = await file.text();
            jsonHasClientInfo = detectJsonClientInfo(fileText);
          }} catch (e) {{}}
        }}
        // 只有当 JSON 中没有 client 信息时才强制要求手动填写
        if (!jsonHasClientInfo && (!clientId || !clientSecret)) {{
          return showConfirmModal({{
            title: '提示',
            message: 'IDC 模式下必须填写 Client ID 和 Client Secret（或在 JSON 中包含这些字段）',
            icon: '⚠️',
            confirmText: '好的',
            danger: false
          }});
        }}
        if (clientId) fd.append('client_id', clientId);
        if (clientSecret) fd.append('client_secret', clientSecret);
      }}

      // 提交
      try {{
        const r = await fetch('/user/api/tokens/import', {{ method: 'POST', body: fd }});
        const d = await r.json();
        if (r.ok && d.success) {{
          await showConfirmModal({{
            title: '导入完成',
            message: d.message || '导入成功',
            icon: '🎉',
            confirmText: '好的',
            danger: false
          }});
          hideDonateModal();
          loadTokens();
          loadProfile();
        }} else {{
          showConfirmModal({{
            title: '导入失败',
            message: d.error || d.message || '导入失败',
            icon: '❌',
            confirmText: '好的',
            danger: false
          }});
        }}
      }} catch (e) {{
        showConfirmModal({{
          title: '错误',
          message: '请求失败，请稍后重试',
          icon: '❌',
          confirmText: '好的',
          danger: false
        }});
      }}
    }}

    async function toggleVisibility(tokenId, newVisibility) {{
      if (SELF_USE_MODE && newVisibility === 'public') {{
        await showConfirmModal({{
          title: '自用模式',
          message: '自用模式下禁止将 Token 设为公开。',
          icon: '🔒',
          confirmText: '好的',
          danger: false
        }});
        return;
      }}
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

    // 账号信息弹窗相关函数
    function showAccountInfoModal() {{
      document.getElementById('accountInfoModal').style.display = 'flex';
    }}

    function hideAccountInfoModal() {{
      document.getElementById('accountInfoModal').style.display = 'none';
    }}

    function renderAccountInfo(data) {{
      const content = document.getElementById('accountInfoContent');

      // 账号状态
      const status = data.status || 'Active';
      const isSuspended = status !== 'Active';
      const statusColor = isSuspended ? 'text-red-400' : 'text-green-400';
      const statusText = isSuspended ? '已封禁' : '正常';

      // 订阅类型颜色
      const subTypeColors = {{
        'Pro_Plus': 'text-purple-400',
        'Pro': 'text-indigo-400',
        'Enterprise': 'text-amber-400',
        'Teams': 'text-blue-400',
        'Free': 'text-gray-400'
      }};
      const subColor = subTypeColors[data.subscription?.type] || 'text-gray-400';

      // 计算使用百分比
      const usage = data.usage || {{}};
      const percentUsed = usage.percentUsed || 0;
      const progressColor = percentUsed > 80 ? 'bg-red-500' : percentUsed > 50 ? 'bg-amber-500' : 'bg-green-500';

      // 格式化奖励额度
      let bonusHtml = '';
      if (usage.bonuses && usage.bonuses.length > 0) {{
        bonusHtml = usage.bonuses.map(b => `
          <div class="flex justify-between text-sm py-1">
            <span style="color: var(--text-muted);">${{b.name || b.code || '奖励额度'}}</span>
            <span>${{(b.current || 0).toFixed(1)}} / ${{(b.limit || 0).toFixed(1)}}</span>
          </div>
        `).join('');
      }}

      // 剩余天数显示
      const daysRemaining = data.subscription?.daysRemaining;
      const daysHtml = (daysRemaining !== undefined && daysRemaining !== null)
        ? `<span class="text-sm" style="color: var(--text-muted);">剩余 <strong class="text-amber-400">${{daysRemaining}}</strong> 天</span>`
        : '';

      content.innerHTML = `
        <div class="space-y-4">
          <!-- 账号状态 -->
          <div class="p-3 rounded-lg flex items-center justify-between" style="background: var(--bg-input);">
            <div>
              <div class="text-sm mb-1" style="color: var(--text-muted);">邮箱</div>
              <div class="font-medium">${{data.email || '-'}}</div>
            </div>
            <div class="text-right">
              <div class="text-sm mb-1" style="color: var(--text-muted);">状态</div>
              <div class="font-bold ${{statusColor}}">${{statusText}}</div>
            </div>
          </div>

          <!-- 订阅信息 -->
          <div class="p-3 rounded-lg" style="background: var(--bg-input);">
            <div class="text-sm mb-2" style="color: var(--text-muted);">订阅信息</div>
            <div class="flex items-center justify-between">
              <span class="font-bold ${{subColor}}">${{data.subscription?.title || 'Free'}}</span>
              ${{daysHtml}}
            </div>
          </div>

          <!-- 额度使用 -->
          <div class="p-3 rounded-lg" style="background: var(--bg-input);">
            <div class="text-sm mb-2" style="color: var(--text-muted);">额度使用</div>
            <div class="flex justify-between mb-2">
              <span>已使用 <strong>${{(usage.current || 0).toFixed(1)}}</strong></span>
              <span>总额度 <strong>${{(usage.limit || 0).toFixed(1)}}</strong></span>
            </div>
            <div class="w-full h-2 rounded-full" style="background: var(--bg-card);">
              <div class="h-full rounded-full ${{progressColor}}" style="width: ${{Math.min(percentUsed, 100)}}%;"></div>
            </div>
            <div class="text-right text-sm mt-1" style="color: var(--text-muted);">${{percentUsed.toFixed(1)}}%</div>
          </div>

          <!-- 额度明细 -->
          <div class="p-3 rounded-lg" style="background: var(--bg-input);">
            <div class="text-sm mb-2" style="color: var(--text-muted);">额度明细</div>
            <div class="flex justify-between text-sm py-1">
              <span style="color: var(--text-muted);">基础额度</span>
              <span>${{(usage.baseCurrent || 0).toFixed(1)}} / ${{(usage.baseLimit || 0).toFixed(1)}}</span>
            </div>
            ${{bonusHtml}}
          </div>

          <!-- 更新时间 -->
          <div class="text-xs text-right" style="color: var(--text-muted);">
            更新于 ${{data.lastUpdated ? new Date(data.lastUpdated).toLocaleString() : '-'}}
          </div>
        </div>
      `;
    }}

    function renderAccountInfoError(error) {{
      const content = document.getElementById('accountInfoContent');
      content.innerHTML = `
        <div class="text-center py-6">
          <div class="text-4xl mb-3">❌</div>
          <p class="text-red-400 mb-2">获取账号信息失败</p>
          <p class="text-sm" style="color: var(--text-muted);">${{error}}</p>
        </div>
      `;
    }}

    async function showTokenAccountInfo(tokenId) {{
      // 显示弹窗并重置为加载状态
      document.getElementById('accountInfoContent').innerHTML = `
        <div class="text-center py-8" style="color: var(--text-muted);">
          <div class="animate-spin inline-block w-6 h-6 border-2 border-current border-t-transparent rounded-full mb-2"></div>
          <p>加载中...</p>
        </div>
      `;
      showAccountInfoModal();

      try {{
        const response = await fetch('/user/api/tokens/' + tokenId + '/account-info');
        const data = await response.json();

        if (!response.ok) {{
          renderAccountInfoError(data.error || '未知错误');
          return;
        }}

        renderAccountInfo(data);
      }} catch (e) {{
        renderAccountInfoError(e.message || '网络错误');
      }}
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
        if (SELF_USE_MODE) {{
          await showConfirmModal({{
            title: '提示',
            message: '自用模式下必须先添加私有 Token 才能生成 API Key。',
            icon: '🔒',
            confirmText: '好的',
            danger: false
          }});
          return;
        }}
        const proceed = await showConfirmModal({{
          title: '提示',
          message: '您尚未添加任何 Token。生成的 API Key 将使用公开 Token 池，可能会有配额限制。\\n\\n建议先添加您的 Token 以获得更好的体验。\\n\\n是否继续生成？',
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
          showConfirmModal({{ title: '失败', message: d.error || d.message || '生成失败', icon: '❌', confirmText: '好的', danger: false }});
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
        if (publicBtn) publicBtn.classList.remove('active');
        minePanel.style.display = 'block';
        if (publicPanel) publicPanel.style.display = 'none';
      }} else {{
        if (SELF_USE_MODE || !publicBtn || !publicPanel) return;
        mineBtn.classList.remove('active');
        publicBtn.classList.add('active');
        minePanel.style.display = 'none';
        publicPanel.style.display = 'block';
        if (allPublicTokens.length === 0) loadPublicTokens();
      }}
    }}

    async function loadPublicTokens() {{
      try {{
        if (SELF_USE_MODE) return;
        const r = await fetch('/api/public-tokens');
        if (!r.ok) {{
          const tb = document.getElementById('publicTokenTable');
          if (tb) {{
            tb.innerHTML = '<tr><td colspan="6" class="py-6 text-center" style="color: var(--text-muted);">自用模式下不开放公开 Token 池</td></tr>';
          }}
          return;
        }}
        const d = await r.json();
        allPublicTokens = (d.tokens || []).map(t => ({{
          ...t,
          use_count: (t.success_count || 0) + (t.fail_count || 0)
        }}));
        document.getElementById('publicPoolCount').textContent = d.count || 0;
        if (allPublicTokens.length > 0) {{
          const avgRate = allPublicTokens.reduce((sum, t) => sum + (normalizeSuccessRate(t.success_rate) ?? 0), 0) / allPublicTokens.length;
          document.getElementById('publicPoolAvgRate').textContent = formatSuccessRate(avgRate, 1);
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
        tb.innerHTML = `<tr><td colspan="6" class="py-8 text-center" style="color: var(--text-muted);"><div class="mb-3">暂无公开 Token，欢迎一起贡献</div><button type="button" onclick="showTokenSubTab('mine'); showDonateModal();" class="text-sm px-3 py-1.5 rounded-lg" style="background: var(--bg-input); border: 1px solid var(--border);">去添加 Token</button></td></tr>`;
        return;
      }}
      tb.innerHTML = tokens.map((t, i) => {{
        const username = escapeHtml(t.username || '匿名');
        const rate = normalizeSuccessRate(t.success_rate) ?? 0;
        const rateClass = rate >= 80 ? 'text-green-400' : rate >= 50 ? 'text-yellow-400' : 'text-red-400';
        return `
        <tr class="table-row">
          <td class="py-3 px-3">${{(publicTokenCurrentPage - 1) * parseInt(document.getElementById('publicTokenPageSize').value) + i + 1}}</td>
          <td class="py-3 px-3">${{username}}</td>
          <td class="py-3 px-3">${{renderTokenStatus(t.status)}}</td>
          <td class="py-3 px-3"><span class="${{rateClass}}">${{formatSuccessRate(rate, 1)}}</span></td>
          <td class="py-3 px-3">${{t.use_count || 0}}</td>
          <td class="py-3 px-3">${{t.last_used ? new Date(t.last_used).toLocaleString() : '-'}}</td>
        </tr>
      `;
      }}).join('');
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

    applySelfUseMode();
    showTab('tokens');
    showTokenSubTab('mine');
    setGreeting();
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

    # Unescape doubled braces from the original f-string so JS/CSS renders correctly.
    page_template = page_template.replace("{{", "{").replace("}}", "}")
    replacements = {
        "__COMMON_HEAD__": COMMON_HEAD,
        "__BODY_SELF_USE_ATTR__": body_self_use_attr,
        "__COMMON_NAV__": COMMON_NAV,
        "__AVATAR_HTML__": avatar_html,
        "__DISPLAY_NAME__": display_name,
        "__USER_INFO_HTML__": user_info_html,
        "__COMMON_FOOTER__": COMMON_FOOTER,
        "__SELF_USE_MODE__": str(self_use_enabled).lower(),
    }
    for placeholder, value in replacements.items():
        page_template = page_template.replace(placeholder, value)
    return page_template


def render_tokens_page(user=None) -> str:
    """Render the public token pool page."""
    from kiro_gateway.metrics import metrics

    self_use_enabled = metrics.is_self_use_enabled()
    body_self_use_attr = "true" if self_use_enabled else "false"
    login_section = '<a href="/user" class="btn-primary">用户中心</a>' if user else '<a href="/login" class="btn-primary">登录添加</a>'
    return f'''<!DOCTYPE html>
<html lang="zh">
<head>{COMMON_HEAD}</head>
<body data-self-use="{body_self_use_attr}">
  {COMMON_NAV}
  <main class="max-w-4xl mx-auto px-4 py-8">
    <div class="card mb-6 self-use-only">
      <div class="flex items-start gap-3">
        <div class="text-2xl">🔒</div>
        <div>
          <h2 class="font-bold">自用模式已开启</h2>
          <p class="text-sm mt-1" style="color: var(--text-muted);">公开 Token 池暂不开放，请使用私有 Token。</p>
        </div>
      </div>
    </div>
    <div class="text-center mb-8 public-only">
      <h1 class="text-3xl font-bold mb-2">🌐 公开 Token 池</h1>
      <p style="color: var(--text-muted);">社区添加的 Refresh Token，供所有用户共享使用</p>
    </div>
    <div class="grid grid-cols-2 gap-4 mb-8 public-only">
      <div class="card text-center">
        <div class="text-4xl font-bold text-green-400" id="poolCount">-</div>
        <div style="color: var(--text-muted);">可用 Token</div>
      </div>
      <div class="card text-center">
        <div class="text-4xl font-bold text-indigo-400" id="avgRate">-</div>
        <div style="color: var(--text-muted);">平均成功率</div>
      </div>
    </div>
    <div class="card mb-6 public-only">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-bold">Token 列表</h2>
        {login_section}
      </div>
      <div class="table-responsive">
        <table class="w-full data-table">
          <thead>
            <tr style="border-bottom: 1px solid var(--border);">
              <th class="text-left py-3 px-3">#</th>
              <th class="text-left py-3 px-3">贡献者</th>
              <th class="text-left py-3 px-3">成功率</th>
              <th class="text-left py-3 px-3">最后使用</th>
            </tr>
          </thead>
          <tbody id="poolTable"></tbody>
        </table>
      </div>
    </div>
    <div class="card public-only">
      <h3 class="font-bold mb-3">💡 如何使用</h3>
      <ol class="list-decimal list-inside space-y-2" style="color: var(--text-muted);">
        <li>通过 LinuxDo 或 GitHub 登录本站</li>
        <li>在用户中心添加你的 Refresh Token</li>
        <li>选择"公开"以加入公共池</li>
        <li>生成 API Key (sk-xxx 格式)</li>
        <li>使用 API Key 调用本站接口</li>
      </ol>
    </div>
  </main>
  {COMMON_FOOTER}
  <script>
    const SELF_USE_MODE = {str(self_use_enabled).lower()};
    function normalizeSuccessRate(rate) {{
      const value = Number(rate);
      if (!Number.isFinite(value)) return null;
      return value <= 1 ? value * 100 : value;
    }}
    function formatSuccessRate(rate, digits = 1) {{
      const percent = normalizeSuccessRate(rate);
      if (percent === null) return '-';
      return percent.toFixed(digits) + '%';
    }}
    async function loadPool() {{
      try {{
        if (SELF_USE_MODE) return;
        const r = await fetch('/api/public-tokens');
        if (!r.ok) {{
          const tb = document.getElementById('poolTable');
          if (tb) {{
            tb.innerHTML = '<tr><td colspan="4" class="py-6 text-center" style="color: var(--text-muted);">自用模式下不开放公开 Token 池</td></tr>';
          }}
          return;
        }}
        const d = await r.json();
        document.getElementById('poolCount').textContent = d.count || 0;
        const tokens = d.tokens || [];
        if (tokens.length > 0) {{
          const avgRate = tokens.reduce((sum, t) => sum + (normalizeSuccessRate(t.success_rate) ?? 0), 0) / tokens.length;
          document.getElementById('avgRate').textContent = avgRate.toFixed(1) + '%';
        }} else {{ document.getElementById('avgRate').textContent = '-'; }}
        const tb = document.getElementById('poolTable');
        if (!tokens.length) {{
          tb.innerHTML = '<tr><td colspan="4" class="py-6 text-center" style="color: var(--text-muted);">暂无公开 Token</td></tr>';
          return;
        }}
        tb.innerHTML = tokens.map((t, i) => {{
          const username = escapeHtml(t.username || '匿名');
          const rate = normalizeSuccessRate(t.success_rate) ?? 0;
          const rateClass = rate >= 80 ? 'text-green-400' : rate >= 50 ? 'text-yellow-400' : 'text-red-400';
          return `
          <tr style="border-bottom: 1px solid var(--border);">
            <td class="py-3 px-3">${{i + 1}}</td>
            <td class="py-3 px-3">${{username}}</td>
            <td class="py-3 px-3"><span class="${{rateClass}}">${{formatSuccessRate(rate, 1)}}</span></td>
            <td class="py-3 px-3" style="color: var(--text-muted);">${{t.last_used ? new Date(t.last_used).toLocaleString() : '-'}}</td>
          </tr>
        `;
        }}).join('');
      }} catch (e) {{ console.error(e); }}
    }}
    loadPool();
    setInterval(loadPool, 30000);
  </script>
</body>
</html>'''


def _build_login_buttons(linuxdo_enabled: bool, github_enabled: bool) -> str:
    login_buttons = ""
    if linuxdo_enabled:
        login_buttons += '''
          <a href="/oauth2/login" class="btn-login btn-linuxdo">
            <img src="https://linux.do/uploads/default/optimized/4X/c/c/d/ccd8c210609d498cbeb3d5201d4c259348447562_2_32x32.png" width="24" height="24" alt="LinuxDo" style="border-radius: 6px; background: white; padding: 2px;">
            <span>LinuxDo 登录</span>
          </a>
        '''

    if github_enabled:
        login_buttons += '''
          <a href="/oauth2/github/login" class="btn-login btn-github">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/></svg>
            <span>GitHub 登录</span>
          </a>
        '''

    if not login_buttons:
        login_buttons = '''
          <div class="p-6 rounded-lg text-center" style="background: rgba(245, 158, 11, 0.12); border: 1px solid rgba(245, 158, 11, 0.35);">
            <div class="text-3xl mb-3">⚠️</div>
            <p class="font-medium mb-2" style="color: #d97706;">OAuth2 登录未配置</p>
            <p class="text-sm" style="color: var(--text-muted);">请在 .env 文件中配置 LinuxDo 或 GitHub OAuth2 凭证</p>
            <div class="mt-4 text-xs" style="color: var(--text-muted);">
              参考文档：<a href="/docs" class="text-indigo-400 hover:underline">配置指南</a>
            </div>
          </div>
        '''

    return login_buttons


def render_login_page(
    error: str = "",
    info: str = "",
    email: str = "",
    username: str = ""
) -> str:
    """Render the login selection page with multiple OAuth2 providers."""
    from kiro_gateway.metrics import metrics
    from kiro_gateway.config import OAUTH_CLIENT_ID, GITHUB_CLIENT_ID

    self_use_enabled = metrics.is_self_use_enabled()
    body_self_use_attr = "true" if self_use_enabled else "false"
    safe_error = html.escape(error) if error else ""
    safe_info = html.escape(info) if info else ""
    safe_email = html.escape(email or "")
    error_html = (
        f'<div class="mb-4 px-4 py-3 rounded-lg text-sm" '
        f'style="background: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.4); color: #f87171;">'
        f'{safe_error}</div>'
        if safe_error else ""
    )
    info_html = (
        f'<div class="mb-4 px-4 py-3 rounded-lg text-sm" '
        f'style="background: rgba(34, 197, 94, 0.12); border: 1px solid rgba(34, 197, 94, 0.35); color: #4ade80;">'
        f'{safe_info}</div>'
        if safe_info else ""
    )

    linuxdo_enabled = bool(OAUTH_CLIENT_ID)
    github_enabled = bool(GITHUB_CLIENT_ID)
    login_buttons = _build_login_buttons(linuxdo_enabled, github_enabled)
    if self_use_enabled:
        register_link_html = '<div class="text-xs" style="color: var(--text-muted);">自用模式下禁止新注册</div>'
    else:
        register_link_html = '<a href="/register" class="text-sm text-indigo-400 hover:underline">没有账号？去注册</a>'

    return f'''<!DOCTYPE html>
<html lang="zh">
<head>{COMMON_HEAD}
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Newsreader:wght@500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');
    body {{
      background:
        radial-gradient(1200px 600px at 10% 10%, rgba(16, 185, 129, 0.14), transparent),
        radial-gradient(900px 520px at 90% 20%, rgba(14, 165, 233, 0.16), transparent),
        radial-gradient(800px 500px at 50% 100%, rgba(245, 158, 11, 0.12), transparent),
        var(--bg-main);
      font-family: "Space Grotesk", "PingFang SC", "Microsoft YaHei", sans-serif;
    }}
    .auth-shell {{
      position: relative;
      overflow: hidden;
    }}
    .auth-shell::before {{
      content: "";
      position: absolute;
      inset: -10% 0 auto 0;
      height: 60%;
      background-image: radial-gradient(circle at 20% 20%, rgba(148, 163, 184, 0.16) 0, transparent 35%);
      opacity: 0.6;
      pointer-events: none;
    }}
    .auth-grid {{
      position: relative;
      display: grid;
      gap: 2.5rem;
      align-items: center;
    }}
    @media (min-width: 1024px) {{
      .auth-grid {{ grid-template-columns: 1.05fr 0.95fr; }}
    }}
    .auth-card {{
      background: linear-gradient(180deg, rgba(255, 255, 255, 0.9), rgba(255, 255, 255, 0.72));
      border: 1px solid rgba(148, 163, 184, 0.35);
      border-radius: 1.75rem;
      box-shadow: 0 32px 70px -40px rgba(15, 23, 42, 0.45);
      padding: 2rem;
      backdrop-filter: blur(18px);
    }}
    .dark .auth-card {{
      background: linear-gradient(180deg, rgba(15, 23, 42, 0.8), rgba(2, 6, 23, 0.82));
      border-color: rgba(148, 163, 184, 0.22);
    }}
    .auth-title {{
      font-family: "Newsreader", "Songti SC", serif;
      font-size: 2rem;
      letter-spacing: 0.02em;
    }}
    .auth-subtitle {{
      color: var(--text-muted);
    }}
    .auth-aside {{
      border-radius: 1.5rem;
      padding: 2rem;
      border: 1px solid rgba(148, 163, 184, 0.28);
      background: linear-gradient(135deg, rgba(14, 165, 233, 0.12), rgba(16, 185, 129, 0.1));
      box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.3);
    }}
    .dark .auth-aside {{
      background: linear-gradient(135deg, rgba(14, 165, 233, 0.18), rgba(16, 185, 129, 0.16));
    }}
    .auth-badge {{
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
      padding: 0.3rem 0.8rem;
      border-radius: 999px;
      font-size: 0.8rem;
      background: rgba(15, 23, 42, 0.9);
      color: #fff;
    }}
    .btn-login {{
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 12px;
      width: 100%;
      padding: 14px 24px;
      border-radius: 14px;
      font-weight: 600;
      font-size: 1rem;
      transition: all 0.3s ease;
      text-decoration: none;
    }}
    .btn-login:hover {{ transform: translateY(-2px); box-shadow: 0 12px 28px -12px rgba(15, 23, 42, 0.35); }}
    .btn-linuxdo {{ background: linear-gradient(135deg, #0ea5e9 0%, #22c55e 100%); color: white; }}
    .btn-linuxdo:hover {{ background: linear-gradient(135deg, #0284c7 0%, #16a34a 100%); }}
    .btn-github {{ background: #0f172a; color: white; }}
    .btn-github:hover {{ background: #111827; }}
    .auth-label {{ font-size: 0.85rem; color: var(--text-muted); }}
    .auth-input {{
      width: 100%;
      padding: 0.75rem 0.95rem;
      border-radius: 0.85rem;
      border: 1px solid var(--border);
      background: var(--bg-input);
      color: var(--text);
      transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }}
    .auth-input:focus {{
      outline: none;
      border-color: #0ea5e9;
      box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.18);
    }}
    .btn-auth {{
      width: 100%;
      padding: 0.85rem 1rem;
      border-radius: 0.9rem;
      font-weight: 600;
      transition: transform 0.2s ease, box-shadow 0.2s ease;
      border: none;
      cursor: pointer;
    }}
    .btn-auth:hover {{ transform: translateY(-1px); box-shadow: 0 12px 28px -16px rgba(15, 23, 42, 0.4); }}
    .btn-auth:disabled {{
      opacity: 0.6;
      cursor: not-allowed;
      transform: none;
      box-shadow: none;
    }}
    .feature-list {{
      display: grid;
      gap: 0.85rem;
      margin-top: 1.25rem;
      color: var(--text);
      font-size: 0.95rem;
    }}
    .feature-item {{
      display: flex;
      gap: 0.75rem;
      align-items: flex-start;
    }}
    .feature-icon {{
      width: 2rem;
      height: 2rem;
      border-radius: 0.8rem;
      display: grid;
      place-items: center;
      background: rgba(255, 255, 255, 0.65);
      border: 1px solid rgba(148, 163, 184, 0.3);
      font-size: 1.05rem;
    }}
    @keyframes bounce {{
      0%, 100% {{ transform: translateY(0); }}
      50% {{ transform: translateY(-10px); }}
    }}
  </style>
</head>
<body data-self-use="{body_self_use_attr}">
  {COMMON_NAV}

  <main class="auth-shell flex-1 py-12 px-4" style="min-height: calc(100vh - 200px);">
    <div class="max-w-5xl mx-auto">
      <div class="auth-grid">
        <div class="auth-card">
          <div class="mb-8">
            <span class="auth-badge">登录入口</span>
            <div class="mt-4">
              <div class="logo-bounce inline-block text-5xl mb-4">⚡</div>
              <h1 class="auth-title font-bold mb-2">欢迎回来</h1>
              <p class="auth-subtitle">用你熟悉的方式继续使用 KiroGate</p>
            </div>
          </div>
          {error_html}
          {info_html}
          <div class="self-use-only mb-6 px-4 py-3 rounded-lg text-sm" style="background: rgba(245, 158, 11, 0.12); border: 1px solid rgba(245, 158, 11, 0.35); color: #d97706;">
            自用模式已开启：仅限已注册用户登录。
          </div>

          <div class="space-y-4 mb-6">
            <form method="post" action="/auth/login" class="space-y-3">
              <div class="text-sm font-semibold">邮箱登录</div>
              <label class="auth-label" for="loginEmail">邮箱</label>
              <input id="loginEmail" name="email" type="email" class="auth-input" required value="{safe_email}">
              <label class="auth-label" for="loginPassword">密码</label>
              <input id="loginPassword" name="password" type="password" class="auth-input" required>
              <button type="submit" class="btn-auth" style="background: linear-gradient(135deg, #0ea5e9 0%, #22c55e 100%); color: #fff;">登录</button>
            </form>
            <div class="text-right">{register_link_html}</div>
          </div>

          <div class="space-y-4">
            {login_buttons}
          </div>
        </div>

        <div class="auth-aside">
          <div class="text-xl font-semibold mb-2">可信赖的 AI 入口</div>
          <p class="text-sm" style="color: var(--text-muted);">跨模型、跨租户、一站式接入。我们把复杂性留在后端。</p>
          <div class="feature-list">
            <div class="feature-item">
              <div class="feature-icon">🔒</div>
              <div>
                <div class="font-medium">安全会话</div>
                <div class="text-xs" style="color: var(--text-muted);">基于加密与风控策略的登录保护</div>
              </div>
            </div>
            <div class="feature-item">
              <div class="feature-icon">⚡</div>
              <div>
                <div class="font-medium">极速接入</div>
                <div class="text-xs" style="color: var(--text-muted);">一键接入 OpenAI / Anthropic 生态</div>
              </div>
            </div>
            <div class="feature-item">
              <div class="feature-icon">🎯</div>
              <div>
                <div class="font-medium">精细配额</div>
                <div class="text-xs" style="color: var(--text-muted);">清晰可控的 Token / Key 管理</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </main>

  {COMMON_FOOTER}
</body>
</html>'''


def render_register_page(
    error: str = "",
    info: str = "",
    email: str = "",
    username: str = ""
) -> str:
    """Render the register page."""
    from kiro_gateway.metrics import metrics
    from kiro_gateway.config import OAUTH_CLIENT_ID, GITHUB_CLIENT_ID

    self_use_enabled = metrics.is_self_use_enabled()
    body_self_use_attr = "true" if self_use_enabled else "false"
    require_approval = metrics.is_require_approval()
    safe_error = html.escape(error) if error else ""
    safe_info = html.escape(info) if info else ""
    safe_email = html.escape(email or "")
    safe_username = html.escape(username or "")
    error_html = (
        f'<div class="mb-4 px-4 py-3 rounded-lg text-sm" '
        f'style="background: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.4); color: #f87171;">'
        f'{safe_error}</div>'
        if safe_error else ""
    )
    info_html = (
        f'<div class="mb-4 px-4 py-3 rounded-lg text-sm" '
        f'style="background: rgba(34, 197, 94, 0.12); border: 1px solid rgba(34, 197, 94, 0.35); color: #4ade80;">'
        f'{safe_info}</div>'
        if safe_info else ""
    )
    register_disabled = "disabled" if self_use_enabled else ""

    linuxdo_enabled = bool(OAUTH_CLIENT_ID)
    github_enabled = bool(GITHUB_CLIENT_ID)
    login_buttons = _build_login_buttons(linuxdo_enabled, github_enabled)
    if self_use_enabled:
        login_link_html = '<div class="text-xs" style="color: var(--text-muted);">自用模式下禁止新注册</div>'
    else:
        login_link_html = '<a href="/login" class="text-sm text-indigo-400 hover:underline">已有账号？去登录</a>'

    return f'''<!DOCTYPE html>
<html lang="zh">
<head>{COMMON_HEAD}
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Newsreader:wght@500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');
    body {{
      background:
        radial-gradient(1200px 600px at 10% 10%, rgba(16, 185, 129, 0.14), transparent),
        radial-gradient(900px 520px at 90% 20%, rgba(14, 165, 233, 0.16), transparent),
        radial-gradient(800px 500px at 50% 100%, rgba(245, 158, 11, 0.12), transparent),
        var(--bg-main);
      font-family: "Space Grotesk", "PingFang SC", "Microsoft YaHei", sans-serif;
    }}
    .auth-shell {{
      position: relative;
      overflow: hidden;
    }}
    .auth-shell::before {{
      content: "";
      position: absolute;
      inset: -10% 0 auto 0;
      height: 60%;
      background-image: radial-gradient(circle at 20% 20%, rgba(148, 163, 184, 0.16) 0, transparent 35%);
      opacity: 0.6;
      pointer-events: none;
    }}
    .auth-grid {{
      position: relative;
      display: grid;
      gap: 2.5rem;
      align-items: center;
    }}
    @media (min-width: 1024px) {{
      .auth-grid {{ grid-template-columns: 1.05fr 0.95fr; }}
    }}
    .auth-card {{
      background: linear-gradient(180deg, rgba(255, 255, 255, 0.9), rgba(255, 255, 255, 0.72));
      border: 1px solid rgba(148, 163, 184, 0.35);
      border-radius: 1.75rem;
      box-shadow: 0 32px 70px -40px rgba(15, 23, 42, 0.45);
      padding: 2rem;
      backdrop-filter: blur(18px);
    }}
    .dark .auth-card {{
      background: linear-gradient(180deg, rgba(15, 23, 42, 0.8), rgba(2, 6, 23, 0.82));
      border-color: rgba(148, 163, 184, 0.22);
    }}
    .auth-title {{
      font-family: "Newsreader", "Songti SC", serif;
      font-size: 2rem;
      letter-spacing: 0.02em;
    }}
    .auth-subtitle {{
      color: var(--text-muted);
    }}
    .auth-aside {{
      border-radius: 1.5rem;
      padding: 2rem;
      border: 1px solid rgba(148, 163, 184, 0.28);
      background: linear-gradient(135deg, rgba(14, 165, 233, 0.12), rgba(16, 185, 129, 0.1));
      box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.3);
    }}
    .dark .auth-aside {{
      background: linear-gradient(135deg, rgba(14, 165, 233, 0.18), rgba(16, 185, 129, 0.16));
    }}
    .auth-badge {{
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
      padding: 0.3rem 0.8rem;
      border-radius: 999px;
      font-size: 0.8rem;
      background: rgba(15, 23, 42, 0.9);
      color: #fff;
    }}
    .btn-login {{
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 12px;
      width: 100%;
      padding: 14px 24px;
      border-radius: 14px;
      font-weight: 600;
      font-size: 1rem;
      transition: all 0.3s ease;
      text-decoration: none;
    }}
    .btn-login:hover {{ transform: translateY(-2px); box-shadow: 0 12px 28px -12px rgba(15, 23, 42, 0.35); }}
    .btn-linuxdo {{ background: linear-gradient(135deg, #0ea5e9 0%, #22c55e 100%); color: white; }}
    .btn-linuxdo:hover {{ background: linear-gradient(135deg, #0284c7 0%, #16a34a 100%); }}
    .btn-github {{ background: #0f172a; color: white; }}
    .btn-github:hover {{ background: #111827; }}
    .auth-label {{ font-size: 0.85rem; color: var(--text-muted); }}
    .auth-input {{
      width: 100%;
      padding: 0.75rem 0.95rem;
      border-radius: 0.85rem;
      border: 1px solid var(--border);
      background: var(--bg-input);
      color: var(--text);
      transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }}
    .auth-input:focus {{
      outline: none;
      border-color: #0ea5e9;
      box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.18);
    }}
    .btn-auth {{
      width: 100%;
      padding: 0.85rem 1rem;
      border-radius: 0.9rem;
      font-weight: 600;
      transition: transform 0.2s ease, box-shadow 0.2s ease;
      border: none;
      cursor: pointer;
    }}
    .btn-auth:hover {{ transform: translateY(-1px); box-shadow: 0 12px 28px -16px rgba(15, 23, 42, 0.4); }}
    .btn-auth:disabled {{
      opacity: 0.6;
      cursor: not-allowed;
      transform: none;
      box-shadow: none;
    }}
    .feature-list {{
      display: grid;
      gap: 0.85rem;
      margin-top: 1.25rem;
      color: var(--text);
      font-size: 0.95rem;
    }}
    .feature-item {{
      display: flex;
      gap: 0.75rem;
      align-items: flex-start;
    }}
    .feature-icon {{
      width: 2rem;
      height: 2rem;
      border-radius: 0.8rem;
      display: grid;
      place-items: center;
      background: rgba(255, 255, 255, 0.65);
      border: 1px solid rgba(148, 163, 184, 0.3);
      font-size: 1.05rem;
    }}
    @keyframes bounce {{
      0%, 100% {{ transform: translateY(0); }}
      50% {{ transform: translateY(-10px); }}
    }}
  </style>
</head>
<body data-self-use="{body_self_use_attr}">
  {COMMON_NAV}

  <main class="auth-shell flex-1 py-12 px-4" style="min-height: calc(100vh - 200px);">
    <div class="max-w-5xl mx-auto">
      <div class="auth-grid">
        <div class="auth-card">
          <div class="mb-8">
            <span class="auth-badge">注册入口</span>
            <div class="mt-4">
              <div class="logo-bounce inline-block text-5xl mb-4">✨</div>
              <h1 class="auth-title font-bold mb-2">创建新账号</h1>
              <p class="auth-subtitle">使用邮箱注册或选择 OAuth</p>
            </div>
          </div>
          {error_html}
          {info_html}
          <div class="self-use-only mb-6 px-4 py-3 rounded-lg text-sm" style="background: rgba(245, 158, 11, 0.12); border: 1px solid rgba(245, 158, 11, 0.35); color: #d97706;">
            自用模式已开启：仅限已注册用户登录。
          </div>

          <div class="space-y-4 mb-6">
            <form method="post" action="/auth/register" class="space-y-3">
              <div class="text-sm font-semibold">邮箱注册</div>
              <label class="auth-label" for="registerEmail">邮箱</label>
              <input id="registerEmail" name="email" type="email" class="auth-input" required value="{safe_email}">
              <label class="auth-label" for="registerUsername">用户名（可选）</label>
              <input id="registerUsername" name="username" type="text" class="auth-input" value="{safe_username}">
              <label class="auth-label" for="registerPassword">密码（至少 8 位）</label>
              <input id="registerPassword" name="password" type="password" class="auth-input" required minlength="8">
              <button type="submit" class="btn-auth" style="background: linear-gradient(135deg, #0f172a 0%, #1f2937 100%); color: #fff;" {register_disabled}>注册</button>
              <div class="text-xs" style="color: var(--text-muted);">
                {("注册后需管理员审核通过" if require_approval else "注册成功后可直接登录") if not self_use_enabled else "自用模式下禁止新注册"}
              </div>
            </form>
            <div class="text-right">{login_link_html}</div>
          </div>

          <div class="space-y-4">
            {login_buttons}
          </div>
        </div>

        <div class="auth-aside">
          <div class="text-xl font-semibold mb-2">加入协作网络</div>
          <p class="text-sm" style="color: var(--text-muted);">马上开启你的专属 Token 与 API Key 管理。</p>
          <div class="feature-list">
            <div class="feature-item">
              <div class="feature-icon">🧭</div>
              <div>
                <div class="font-medium">快速引导</div>
                <div class="text-xs" style="color: var(--text-muted);">注册后直接进入控制台引导</div>
              </div>
            </div>
            <div class="feature-item">
              <div class="feature-icon">📊</div>
              <div>
                <div class="font-medium">可视化面板</div>
                <div class="text-xs" style="color: var(--text-muted);">实时查看 Token 使用情况</div>
              </div>
            </div>
            <div class="feature-item">
              <div class="feature-icon">🛡️</div>
              <div>
                <div class="font-medium">审批机制</div>
                <div class="text-xs" style="color: var(--text-muted);">注册审批与权限一目了然</div>
              </div>
            </div>
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
